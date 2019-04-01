#!/usr/bin/env python

  #// Reception format:
  #// 0x01 ~ 0xFF - version, defined in constant file
  #// 0x11 - start byte
  #// 0xLL 0xLL 0xLL 0xLL - 4-byte length of message
  #// <message>

  #// 0x01 ~ 0xFF - version, defined in constant file
  #// 0x22 - start byte (broadcast)
  #// 0xLL 0xLL 0xLL 0xLL - 4-byte length of hash + message
  #// <32-byte hash> <message>

  #// 0x01 ~ 0xFF - version, defined in constant file
  #// 0x33 - start byte (gossip)
  #// 0xLL 0xLL 0xLL 0xLL - 4-byte length of message
  #// 0x01 ~ 0x04 - Gossip_Message_Type
  #// <4-byte Age> <message>

  #// 0x01 ~ 0xFF - version, defined in constant file
  #// 0x33 - start byte (report)
  #// 0x00 0x00 0x00 0x01 - 4-byte length of message
  #// 0x00


def forge_reception(version, message):
    pass

def forge_broadcast(version, message):
    pass

def forge_gossip(version, message):
    pass

def forge_report(version, message):
    pass

def main():
    pass

if __name__ == '__main__':
    main()
