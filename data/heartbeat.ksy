meta:
  id: hb
  # file-extension: bin
  endian: be
seq:
  - id: version
    type: b2
  - id: type
    type: b1
    enum: pkt_type
  - id: filter
    type: b5
  - id: seq
    type: u1
  - id: payload_length
    type: u2
  - id: payload
    type: hb_payload
    repeat: eos
    if: payload_length > 0
enums:
  pkt_type:
    0: req
    1: res
types:
  hb_payload:
    seq:
      - id: type
        type: u2
        enum: hb_message_type
      - id: length
        type: u2
      - id: value
        size: length
        type:
          switch-on: type
          cases:
            'hb_message_type::mid': hb_mid
            'hb_message_type::cpa_req': hb_cpa_req
            'hb_message_type::cpa_rsp': hb_cpa_rsp
    types:
      hb_mid:
        seq:
          - id: mid
            type: str
            size: _parent.length
            encoding: ascii
      hb_cpa_req:
        seq:
          - id: req
            size: _parent.length
      hb_cpa_rsp:
        seq:
          - id: address_family
            type: u2
            enum: address_family
          - id: port
            type: u2
          - id: ip
            doc: Client public IP
            type:
              switch-on: address_family
              cases:
                'address_family::af_inet': ipv4
                'address_family::af_inet6': ipv6
        enums:
          address_family:
            0x01: af_inet
            0x02: af_inet6
    enums:
      hb_message_type:
        0xFE01: mid
        0xFE03: cpa_req
        0xFE04: cpa_rsp
  ipv4:
    seq:
      - id: value
        size: 4
  ipv6:
    seq:
      - id: value
        size: 16
  string:
    seq:
      - id: length
        type: u2
      - id: content
        size: length
