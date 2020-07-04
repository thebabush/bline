#!/usr/bin/env python3

import sys

import scapy.all

import bline.zstream


def main(fp):
    pcap = scapy.all.rdpcap(fp)
    for p in pcap:
        src_ip = p['IP'].src
        dst_ip = p['IP'].dst
        src_port = p['UDP'].sport
        dst_port = p['UDP'].dport

        print('='*30 + ' {}:{}\t=>\t{}:{} \t'.format(src_ip, src_port, dst_ip, dst_port) + '=' * 30)

        payload = p['UDP'].load
        if payload[:2] == b'\xA7\xD7':
            print(bline.zstream.uncompress_str(payload))
        # print(p)
        # bline.zstream.uncompress_str(p)


main(sys.argv[1])

