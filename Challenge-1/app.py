"""Captura de pacotes e estatísticas persistidas em SQLite."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
import sys

from scapy.all import IP, IPv6, TCP, UDP, ICMP, ARP, get_if_list, sniff
from scapy.error import Scapy_Exception

SCHEMA = """
CREATE TABLE IF NOT EXISTS packets (
    id INTEGER PRIMARY KEY,
    captured_at TEXT NOT NULL,
    interface TEXT NOT NULL,
    src_ip TEXT,
    dst_ip TEXT,
    protocol TEXT NOT NULL,
    size_bytes INTEGER NOT NULL CHECK(size_bytes >= 0)
);
"""


def connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(path)
    db.execute(SCHEMA)
    db.commit()
    return db


def packet_record(packet, interface):
    # Only outer IP addresses are recorded; non-IP frames keep NULL addresses.
    network = packet.getlayer(IP) or packet.getlayer(IPv6)
    src, dst = (network.src, network.dst) if network is not None else (None, None)
    if network is not None:
        # Follow the immediate IPv6 extension chain, not a tunneled inner IP.
        transport = network.payload
        if isinstance(network, IPv6):
            while transport.__class__.__name__.startswith('IPv6ExtHdr'):
                transport = transport.payload
        if isinstance(transport, TCP):
            protocol = 'TCP'
        elif isinstance(transport, UDP):
            protocol = 'UDP'
        elif isinstance(transport, ICMP):
            protocol = 'ICMP'
        elif transport.__class__.__name__.startswith('ICMPv6'):
            protocol = 'ICMPv6'
        else:
            protocol = f'IP-{network.proto}' if isinstance(network, IP) else 'IPv6-OTHER'
    else:
        protocol = 'ARP' if ARP in packet else 'NON-IP'
    captured_at = datetime.fromtimestamp(float(packet.time), timezone.utc).isoformat()
    return captured_at, interface, src, dst, protocol, len(packet)


def save_packet(db, packet, interface):
    db.execute('INSERT INTO packets (captured_at, interface, src_ip, dst_ip, protocol, size_bytes) VALUES (?, ?, ?, ?, ?, ?)',
               packet_record(packet, interface))
    db.commit()


def statistics(db):
    total, size = db.execute('SELECT COUNT(*), COALESCE(SUM(size_bytes),0) FROM packets').fetchone()
    print(f'\nTOTAL: {total} pacotes | {size} bytes')
    print('\nPACOTES POR PROTOCOLO')
    for protocol, count in db.execute('SELECT protocol, COUNT(*) FROM packets GROUP BY protocol ORDER BY COUNT(*) DESC, protocol'):
        print(f'{protocol}: {count}')
    for column, label in [('src_ip', 'ORIGEM'), ('dst_ip', 'DESTINO')]:
        print(f'\nTOP 5 IPs DE {label} POR BYTES')
        rows = db.execute(f'SELECT {column}, SUM(size_bytes), COUNT(*) FROM packets WHERE {column} IS NOT NULL GROUP BY {column} ORDER BY SUM(size_bytes) DESC, {column} ASC LIMIT 5').fetchall()
        for address, size, count in rows:
            print(f'{address}: {size} bytes | {count} pacotes')
        if not rows:
            print('(nenhum pacote IP)')


def positive(value):
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError('Informe um inteiro maior que zero.')
    return number


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', default='data/traffic.db', help='Banco SQLite (padrão: data/traffic.db).')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('interfaces', help='Listar interfaces visíveis.')
    sub.add_parser('stats', help='Consultar todos os registros do banco.')
    capture = sub.add_parser('capture', help='Capturar pacotes de uma interface.')
    capture.add_argument('--interface', required=True)
    capture.add_argument('--duration', type=positive, default=30, help='Duração em segundos (padrão: 30).')
    capture.add_argument('--count', type=positive, help='Parar ao atingir esta quantidade ou a duração.')
    read = sub.add_parser('read', help='Importar PCAP para demonstração/teste.')
    read.add_argument('pcap')
    args = parser.parse_args(argv)
    try:
        if args.command == 'interfaces':
            print('\n'.join(get_if_list()))
            return 0
        if args.command == 'capture' and args.interface not in get_if_list():
            parser.error('Interface inexistente. Consulte: python app.py interfaces')
        if args.command == 'read' and not Path(args.pcap).is_file():
            parser.error('Arquivo PCAP inexistente.')
        with closing(connect(args.db)) as db:
            if args.command in ('capture', 'read'):
                interface = args.interface if args.command == 'capture' else f'pcap:{Path(args.pcap).name}'
                before = db.execute('SELECT COUNT(*) FROM packets').fetchone()[0]
                callback = lambda packet: save_packet(db, packet, interface)
                print(f'Origem: {interface} | banco: {args.db}', flush=True)
                try:
                    if args.command == 'capture':
                        sniff(iface=args.interface, timeout=args.duration, count=args.count or 0,
                              prn=callback, store=False, promisc=False)
                    else:
                        sniff(offline=args.pcap, prn=callback, store=False)
                except KeyboardInterrupt:
                    print('\nCaptura interrompida pelo usuário.')
                after = db.execute('SELECT COUNT(*) FROM packets').fetchone()[0]
                print(f'Pacotes registrados nesta execução: {after - before}')
            statistics(db)
        return 0
    except (OSError, sqlite3.Error, ValueError, Scapy_Exception) as error:
        print(f'Erro: {error}. Verifique caminho, permissões e interface.', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
