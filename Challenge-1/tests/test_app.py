import io
import sqlite3
import unittest
from contextlib import redirect_stdout
from scapy.all import Ether, IP, IPv6, TCP, UDP, ARP, Raw, fragment
from scapy.layers.inet6 import IPv6ExtHdrHopByHop, ICMPv6EchoRequest
from app import SCHEMA, packet_record, save_packet, statistics


class TrafficTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.db.execute(SCHEMA)

    def tearDown(self):
        self.db.close()

    def test_fields_and_ipv6(self):
        p = Ether(src='02:00:00:00:00:01', dst='02:00:00:00:00:02')/IP(src='192.0.2.1', dst='198.51.100.1')/UDP()/Raw(b'x')
        save_packet(self.db, p, 'eth0')
        row = self.db.execute('SELECT interface,src_ip,dst_ip,protocol,size_bytes FROM packets').fetchone()
        self.assertEqual(row, ('eth0','192.0.2.1','198.51.100.1','UDP',len(p)))
        p6 = Ether(src='02:00:00:00:00:01', dst='02:00:00:00:00:02')/IPv6(src='2001:db8::1',dst='2001:db8::2')/IPv6ExtHdrHopByHop()/ICMPv6EchoRequest()
        self.assertEqual(packet_record(p6,'eth0')[4], 'ICMPv6')

    def test_non_ip_preserved(self):
        save_packet(self.db,Ether(src='02:00:00:00:00:01', dst='02:00:00:00:00:02')/ARP(),'eth0')
        self.assertEqual(self.db.execute('SELECT src_ip,dst_ip,protocol FROM packets').fetchone(), (None,None,'ARP'))

    def test_rank_uses_bytes_and_limits_to_five(self):
        for i in range(1,8):
            save_packet(self.db, Ether(src='02:00:00:00:00:01', dst='02:00:00:00:00:02')/IP(src=f'192.0.2.{i}',dst=f'198.51.100.{i}')/TCP()/Raw(b'x'*i*10),'eth0')
        output = io.StringIO()
        with redirect_stdout(output):
            statistics(self.db)
        src = output.getvalue().split('TOP 5 IPs DE ORIGEM POR BYTES')[1].split('TOP 5 IPs DE DESTINO')[0]
        self.assertEqual(len(src.strip().splitlines()),5)
        self.assertTrue(src.strip().startswith('192.0.2.7:'))
        self.assertNotIn('192.0.2.1:',src)
        dst = output.getvalue().split('TOP 5 IPs DE DESTINO POR BYTES')[1]
        self.assertEqual(len(dst.strip().splitlines()),5)
        self.assertTrue(dst.strip().startswith('198.51.100.7:'))

    def test_totals_protocols_and_empty_database(self):
        output=io.StringIO()
        with redirect_stdout(output): statistics(self.db)
        self.assertIn('TOTAL: 0 pacotes | 0 bytes',output.getvalue())
        for p in [Ether(src='02:00:00:00:00:01', dst='02:00:00:00:00:02')/IP()/TCP(),Ether(src='02:00:00:00:00:01', dst='02:00:00:00:00:02')/IP()/UDP(),Ether(src='02:00:00:00:00:01', dst='02:00:00:00:00:02')/IP()/TCP()]:
            save_packet(self.db,p,'lo')
        output=io.StringIO()
        with redirect_stdout(output): statistics(self.db)
        self.assertIn('TOTAL: 3 pacotes',output.getvalue())
        self.assertIn('TCP: 2',output.getvalue())
        self.assertIn('UDP: 1',output.getvalue())


if __name__ == '__main__': unittest.main()
