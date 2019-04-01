#!/usr/bin/env python

# Derived from src/libRumorSpreading/Message.h

MessageOffset = { 'TYPE': 0, 'INST': 1, 'BODY': 2 }

NumberSign = { 'POSITIVE': 0x00, 'NEGATIVE': 0x01 }

MessageType = {
        'PEER': 0x00,
        'DIRECTORY': 0x01,
        'NODE': 0x02,
        'CONSENSUSUSER': 0x03,
        'LOOKUP': 0x04
        }

DSInstructionType = {
        'SETPRIMARY': 0x00,
        'POWSUBMISSION': 0x01,
        'DSBLOCKCONSENSUS': 0x02,
        'MICROBLOCKSUBMISSION': 0x03,
        'FINALBLOCKCONSENSUS': 0x04,
        'VIEWCHANGECONSENSUS': 0x05,
        'VCPUSHLATESTDSTXBLOCK': 0x06,
        'POWPACKETSUBMISSION': 0x07,
        'NEWDSGUARDIDENTITY': 0x08
        }

NodeInstructionType = {
        'STARTPOW': 0x00,
        'DSBLOCK': 0x01,
        'SUBMITTRANSACTION': 0x02,
        'MICROBLOCKCONSENSUS': 0x03,
        'FINALBLOCK': 0x04,
        'MBNFORWARDTRANSACTION': 0x05,
        'VCBLOCK': 0x06,
        'DOREJOIN': 0x07,
        'FORWARDTXNPACKET': 0x08,
        'FALLBACKCONSENSUS': 0x09,
        'FALLBACKBLOCK': 0x0A,
        'PROPOSEGASPRICE': 0x0B,
        'DSGUARDNODENETWORKINFOUPDATE': 0x0C,
        }

LookupInstructionType =  {
        'GETDSINFOFROMSEED': 0x00,
        'SETDSINFOFROMSEED': 0x01,
        'GETDSBLOCKFROMSEED': 0x02,
        'SETDSBLOCKFROMSEED': 0x03,
        'GETTXBLOCKFROMSEED': 0x04,
        'SETTXBLOCKFROMSEED': 0x05,
        'GETSTATEFROMSEED': 0x06,
        'SETSTATEFROMSEED': 0x07,
        'SETLOOKUPOFFLINE': 0x08,
        'SETLOOKUPONLINE': 0x09,
        'GETOFFLINELOOKUPS': 0x0A,
        'SETOFFLINELOOKUPS': 0x0B,
        'RAISESTARTPOW': 0x0C,
        'GETSTARTPOWFROMSEED': 0x0D,
        'SETSTARTPOWFROMSEED': 0x0E,
        'GETSHARDSFROMSEED': 0x0F,
        'SETSHARDSFROMSEED': 0x10,
        'GETMICROBLOCKFROMLOOKUP': 0x11,
        'SETMICROBLOCKFROMLOOKUP': 0x12,
        'GETTXNFROMLOOKUP': 0x13,
        'SETTXNFROMLOOKUP': 0x14,
        'GETDIRBLOCKSFROMSEED': 0x15,
        'SETDIRBLOCKSFROMSEED': 0x16,
        'GETSTATEDELTAFROMSEED': 0x17,
        'SETSTATEDELTAFROMSEED': 0x18,
        'VCGETLATESTDSTXBLOCK': 0x19,
        'FORWARDTXN': 0x1A,
        'GETGUARDNODENETWORKINFOUPDATE': 0x1B,
        'SETHISTORICALDB': 0x1C
        }

TxSharingMode =  {
        'IDLE': 0x00,
        'SEND_ONLY': 0x01,
        'DS_FORWARD_ONLY': 0x02,
        'NODE_FORWARD_ONLY': 0x03,
        'SEND_AND_FORWARD': 0x04
        }

