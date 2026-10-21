"""Gera PCAP sintético ou tráfego UDP local, sem serviços externos."""
import argparse
from pathlib import Path
import socket
from scapy.all import Ether, IP, IPv6, TCP, UDP, ICMP, ARP, Raw, wrpcap


def packets():
    return [
        Ether(src='02:00:00:00:00:01', dst='02:00:00:00:00:02')/IP(src='192.0.2.1', dst='198.51.100.1')/TCP()/Raw(b'a'*20),
        Ether(src='02:00:00:00:00:01', dst='02:00:00:00:00:02')/IP(src='192.0.2.1', dst='198.51.100.2')/UDP()/Raw(b'b'*10),
        Ether(src='02:00:00:00:00:01', dst='02:00:00:00:00:02')/IP(src='192.0.2.2', dst='198.51.100.1')/ICMP(),
        Ether(src='02:00:00:00:00:01', dst='02:00:00:00:00:02')/IPv6(src='2001:db8::1', dst='2001:db8::2')/TCP(),
        Ether(src='02:00:00:00:00:01', dst='02:00:00:00:00:02')/ARP(psrc='192.0.2.1', pdst='192.0.2.2'),
        Ether(src='02:00:00:00:00:01', dst='02:00:00:00:00:02')/IP(src='192.0.2.3', dst='198.51.100.3')/UDP()/Raw(b'c'*100),
    ]


def udp():
    # Both endpoints are loopback inside the same container/network namespace.
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver:
        receiver.bind(('127.0.0.1', 9999))
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:
            for _ in range(10):
                sender.sendto(b'challenge-demo', ('127.0.0.1', 9999))
                receiver.recvfrom(1024)
    print('10 datagramas UDP locais enviados e recebidos.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--udp', action='store_true')
    parser.add_argument('--output', default='data/demo.pcap')
    args = parser.parse_args()
    if args.udp:
        udp()
    else:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        wrpcap(args.output, packets())
        print(f'6 pacotes sintéticos gravados em {args.output}')
