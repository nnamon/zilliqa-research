#!/usr/bin/env python

import struct
import socket
import messages

START_BYTE_NORMAL = 0x11
START_BYTE_BROADCAST = 0x22
START_BYTE_GOSSIP = 0x33
HDR_LEN = 6
HASH_LEN = 32
GOSSIP_MSGTYPE_LEN = 1
GOSSIP_ROUND_LEN = 4
GOSSIP_SNDR_LISTNR_PORT_LEN = 4

MSG_VERSION = 1

# Network

def send_message(host, port, message):
    s = socket.socket()
    s.connect((host, port))
    s.sendall(message)
    s.close()

# Node Instructions

def node_submit_transaction(submit_txn_type, msg_block_num, txn_array_message):
    msg = ""
    if msg_block_num is not None:
        msg += struct.pack('B', submit_txn_type)
    msg += struct.pack('>Q', msg_block_num)
    msg += txn_array_message
    return create_instruction(
            messages.MessageType['NODE'],
            messages.NodeInstructionType['SUBMITTRANSACTION'], msg)

# Instruction

def create_instruction(msg_type, instruction_type, message):
    msg = ""
    msg += struct.pack('B', msg_type)
    msg += struct.pack('B', instruction_type)
    msg += message
    return msg

# P2P Layer

def create_normal_message(message):
    msg = create_message(START_BYTE_NORMAL, message)
    return msg

def create_message(start_byte, message):
    length = len(message)

    msg = ""
    msg += struct.pack('B', MSG_VERSION)
    msg += struct.pack('B', start_byte)
    msg += struct.pack('>I', length)
    msg += message

    return msg

def main():
    host = "127.0.0.1"
    port = 5008
    send_message(host, port, create_normal_message(node_submit_transaction(1, 5000, "")))

if __name__ == '__main__':
    main()
