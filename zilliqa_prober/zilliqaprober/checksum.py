#!/usr/bin/env python

import hashlib

ACC_ADDR_SIZE = 20

def GetCheckSumedAddress(orig_address):
    if len(orig_address) not in (ACC_ADDR_SIZE*2, ACC_ADDR_SIZE*2 + 2):
        return ""

    if len(orig_address) == (ACC_ADDR_SIZE*2 + 2):
        if orig_address[:2] != "0x":
            return ""
        orig_address = orig_address[2:]

    orig_address = orig_address.lower()

    address_bytes = bytearray.fromhex(orig_address)

    hashed = hashlib.sha256(address_bytes).hexdigest()
    v = int(hashed, 16)
    checksummed = ""
    for i in range(len(orig_address)):
        if orig_address[i].isdigit():
            checksummed += orig_address[i]
        else:
            if (v & (1 << 255 - 6 * i)):
                checksummed += orig_address[i].upper()
            else:
                checksummed += orig_address[i]

    return checksummed


def main():
    address = "4BAF5faDA8e5Db92C3d3242618c5B47133AE003C"
    checksum = GetCheckSumedAddress(address.lower())
    assert checksum == address


if __name__ == '__main__':
    main()
