#!/usr/bin/env python3

import sys
import string

import scapy.all

import bline.zstream
import struct
import crc8


BIRD_MSG_TYPE = {
    'UNKNOWN'            : 0x00,
    'BIND_REQ'           : 0x01,
    'BIND_RES'           : 0x02,
    'REBIND_REQ'         : 0x03,
    'REBIND_RES'         : 0x04,
    'NETINFO'            : 0x05,
    'SELECT'             : 0x06,
    'HEARTBEAT'          : 0x07,
    'P2P_COMMAND'        : 0x08,
    'P2P_CHECK_REQ'      : 0x09,
    'P2P_CHECK_RES'      : 0x0A,
    'MEDIA_ARTP'         : 0x0B,
    'MEDIA_VRTP'         : 0x0C,
    'MEDIA_ARTCP'        : 0x0D,
    'MEDIA_VRTCP'        : 0x0E,
    'SERV_CONFIG'        : 0x10,
    'SERV_PUSH'          : 0x11,
    'EN_BIND_REQ'        : 0x12,
    'EN_BIND_RES'        : 0x13,
    'EN_REBIND_REQ'      : 0x14,
    'EN_REBIND_RES'      : 0x15,
    'MEDIA_STRM_CONTROL' : 0x17,
    'ROUTE'              : 0x16,
    'SEC_EN_BIND_REQ'    : 0x18,
}

BIRD_MSG_TYPE_HAS_CRC = {
    0x01: True,
    0x02: True,
    0x03: True,
    0x04: True,
    0x05: True,
    0x06: False,
    0x07: False,
    0x08: True,
    0x09: True,
    0x0A: True,
    0x0B: False,
    0x0C: False,
    0x0D: False,
    0x0E: False,
    0x0F: False,
    0x10: True,
    0x11: True,
    0x12: True,
    0x13: True,
    0x14: True,
    0x15: True,
    0x16: True,
    0x17: False,
    0x18: True,
}

BIRD_TYPE_TO_MSG = {}
for k, v in BIRD_MSG_TYPE.items():
    BIRD_TYPE_TO_MSG[v] = k


u16 = lambda x: struct.unpack('>H', x)[0]


def pp(ba, n=32):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    alphabet = alphabet.encode('ascii')

    ba = ba[:n]
    printable = bytearray([c if c in alphabet else ord('.') for c in ba])
    ba = ba.hex().upper()
    ret = []
    for i in range(0, len(ba), 2):
        ret.append(ba[i:i+2])
        if (i + 2) % 8 == 0:
            ret.append('')
    pre  = ' '.join(ret)
    post = ' - ' + printable.decode('ascii').replace('\r', '.')
    return pre + ' ' * (103 - len(pre)) + post


def main(fp):
    pcap = scapy.all.rdpcap(fp)
    for p in pcap:
        src_ip = p['IP'].src
        dst_ip = p['IP'].dst
        src_port = p['UDP'].sport
        dst_port = p['UDP'].dport

        payload = bytearray(p['UDP'].load)
        
        assert payload[0] == 0xB6
        payload = payload[1:]

        idx = 0
        while payload:
            typ = payload[0]
            payload = payload[1:]

            length = u16(payload[0:2])
            payload = payload[2:]

            calc_crc = None
            crc      = None
            if BIRD_MSG_TYPE_HAS_CRC[typ]:
                crc = payload[0]
                payload = payload[1:]

                calc_crc = crc8.crc8()
                calc_crc.update(payload[:length - 1])
                calc_crc = calc_crc.digest()[0] ^ 0x55
                length -= 1

            data = payload[:length]

            typ = BIRD_TYPE_TO_MSG[typ] + '({:02X})'.format(typ)
            if crc is not None:
                crc = '{:02X}/{:02X}'.format(crc, calc_crc)
            else:
                crc = 'xx/xx'

            print('{:>15}[{}] {:<20s}{:04X}\t{}\t{}'.format(src_ip, idx, typ, length, crc, pp(data)))

            payload = payload[length:]
            idx += 1


main(sys.argv[1])

