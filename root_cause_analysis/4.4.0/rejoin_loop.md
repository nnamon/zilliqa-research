# The Rejoin Loop

## The Problem

Shortly after v4.4.0 went live, multiple miners encountered a problem with their nodes being stuck
in an infinite loop, continuously attempting to resync. This caused the size of their logs to expand
very quickly hitting tens of gigabytes in days. The following snippet was typically observed in the
logs:

```
[INFO][ 1072][19-03-30T12:43:03.025][work/P2PComm.cpp:307][DoSend              ] <54.189.101.208:33133> is blacklisted - blocking all messages
[WARN][ 1544][19-03-30T12:43:03.240][work/P2PComm.cpp:209][SendMessageSocketCor] Socket connect failed. Code = 110 Desc: Connection timed out. IP address: <172.107.177.220:9163>
[WARN][ 1544][19-03-30T12:43:03.240][work/P2PComm.cpp:214][SendMessageSocketCor] [blacklist] Encountered 110 (Connection timed out). Adding 172.107.177.220 to blacklist
[WARN][ 2419][19-03-30T12:43:03.891][oWProcessing.cpp:183][operator()          ] [Epoch 57300] Time out while waiting for DS Block
[INFO][ 2419][19-03-30T12:43:03.891][ookup/Lookup.cpp:610][ComposeGetDSBlockMes] BEG
[INFO][ 2419][19-03-30T12:43:03.891][e/Messenger.cpp:5068][SetLookupGetDSBlockF] BEG
[INFO][ 2419][19-03-30T12:43:03.891][e/Messenger.cpp:5068][SetLookupGetDSBlockF] END
[INFO][ 2419][19-03-30T12:43:03.891][ookup/Lookup.cpp:610][ComposeGetDSBlockMes] END
[INFO][ 2419][19-03-30T12:43:03.891][ookup/Lookup.cpp:930][SendMessageToRandomS] BEG
[INFO][ 2419][19-03-30T12:43:03.896][ookup/Lookup.cpp:930][SendMessageToRandomS] END
[INFO][    1][19-03-30T12:43:03.965][work/P2PComm.cpp:588][EventCallback       ] Incoming normal <52.13.221.208:41044> (Len=13814): 0111000035F004030A826B08B90410BE041AD0120ADE070A460801122025...
[INFO][  374][19-03-30T12:43:03.966][okup/Lookup.cpp:3475][Execute             ] BEG
[INFO][  374][19-03-30T12:43:03.966][okup/Lookup.cpp:1711][ProcessSetDSBlockFro] BEG
[INFO][  374][19-03-30T12:43:03.966][e/Messenger.cpp:5153][GetLookupSetDSBlockF] BEG
[INFO][  374][19-03-30T12:43:03.972][e/Messenger.cpp:5153][GetLookupSetDSBlockF] END
[INFO][ 2419][19-03-30T12:43:03.972][oWProcessing.cpp:186][operator()          ] DS block created, means I lost PoW
[INFO][ 2419][19-03-30T12:43:03.972][ibNode/Node.cpp:1643][RejoinAsNormal      ] BEG
[INFO][ 2419][19-03-30T12:43:03.972][ibNode/Node.cpp:1643][RejoinAsNormal      ] END
[INFO][  374][19-03-30T12:43:03.973][okup/Lookup.cpp:1711][ProcessSetDSBlockFro] END
[INFO][  374][19-03-30T12:43:03.973][okup/Lookup.cpp:3475][Execute             ] END
[INFO][ 2420][19-03-30T12:43:03.973][okup/Lookup.cpp:3879][SetSyncType         ] [Epoch 57300] Set sync type to 2
[INFO][ 2420][19-03-30T12:43:03.973][/AccountStore.cpp:52][InitSoft            ] BEG
[INFO][ 2420][19-03-30T12:43:03.973][/AccountStore.cpp:81][InitRevertibles     ] BEG
[INFO][ 2420][19-03-30T12:43:03.973][tractStorage.cpp:226][InitRevertibles     ] BEG
[INFO][ 2420][19-03-30T12:43:03.973][tractStorage.cpp:226][InitRevertibles     ] END
[INFO][ 2420][19-03-30T12:43:03.973][/AccountStore.cpp:81][InitRevertibles     ] END
[INFO][ 2420][19-03-30T12:43:03.974][/AccountStore.cpp:70][InitTemp            ] BEG
[INFO][ 2420][19-03-30T12:43:03.974][tractStorage.cpp:364][InitTempState       ] BEG
[INFO][ 2420][19-03-30T12:43:03.974][tractStorage.cpp:364][InitTempState       ] END
[INFO][ 2420][19-03-30T12:43:03.974][/AccountStore.cpp:70][InitTemp            ] END
[INFO][ 2420][19-03-30T12:43:03.974][/AccountStore.cpp:52][InitSoft            ] END
[INFO][ 2420][19-03-30T12:43:03.975][ibNode/Node.cpp:1750][CleanCreatedTransact] BEG
[INFO][ 2420][19-03-30T12:43:03.975][ibNode/Node.cpp:1750][CleanCreatedTransact] END
[INFO][ 2420][19-03-30T12:43:03.975][work/P2PComm.cpp:920][InitializeRumorManag] BEG
[INFO][ 2420][19-03-30T12:43:03.975][RumorManager.cpp:107][StopRounds          ] BEG
[INFO][ 2118][19-03-30T12:43:03.975][/RumorManager.cpp:98][operator()          ] Stopping round now..
[INFO][ 2420][19-03-30T12:43:03.975][RumorManager.cpp:107][StopRounds          ] END
[INFO][ 2420][19-03-30T12:43:03.975][RumorManager.cpp:119][Initialize          ] BEG
[INFO][ 2420][19-03-30T12:43:03.976][RumorManager.cpp:681][PrintStatistics     ] BEG
[INFO][ 2420][19-03-30T12:43:03.976][RumorManager.cpp:681][PrintStatistics     ] END
[INFO][ 2420][19-03-30T12:43:03.977][RumorManager.cpp:119][Initialize          ] END
[INFO][ 2420][19-03-30T12:43:03.978][RumorManager.cpp:182][SpreadBufferedRumors] BEG
...
[WARN][ 2557][19-03-30T13:59:25.172][libNode/Node.cpp:725][StartRetrieveHistory] Node xxxx is not in network, apply re-join process instead
[INFO][ 2557][19-03-30T13:59:25.178][libNode/Node.cpp:472][StartRetrieveHistory] END
[INFO][ 2557][19-03-30T13:59:25.178][libNode/Node.cpp:302][AddGenesisInfo      ] BEG
[INFO][ 2557][19-03-30T13:59:25.178][libNode/Node.cpp:265][Init                ] BEG
[INFO][ 2557][19-03-30T13:59:25.178][lockStorage.cpp:1125][ResetDB             ] BEG
[INFO][ 2557][19-03-30T13:59:25.204][lockStorage.cpp:1125][ResetDB             ] END
[INFO][ 2557][19-03-30T13:59:25.208][lockStorage.cpp:1125][ResetDB             ] BEG
... repeats forever
```

## Analysis

It appears the issue shows up after a failed POW attempt.

`RejoinAsNormal` is called
[here](https://github.com/Zilliqa/Zilliqa/blob/v4.4.0/src/libNode/PoWProcessing.cpp#L191) and
[here](https://github.com/Zilliqa/Zilliqa/blob/v4.4.0/src/libNode/PoWProcessing.cpp#L268) in
`Node::StartPoW`.

Both instances involve handling what happens after POW is lost.

`RejoinAsNormal` contains a `while (true)` loop that repeatedly attempts installing a new normal
node. The terminating condition in `RejoinAsNormal` is
[here](https://github.com/Zilliqa/Zilliqa/blob/v4.4.0/src/libNode/Node.cpp#L1659).

```c++
void Node::RejoinAsNormal(bool rejoiningAfterRecover) {
  if (LOOKUP_NODE_MODE) {
    LOG_GENERAL(
        WARNING,
        "Node::RejoinAsNormal not expected to be called from LookUp node.");
    return;
  }

  LOG_MARKER();
  if (m_mediator.m_lookup->GetSyncType() == SyncType::NO_SYNC) {
    auto func = [this, rejoiningAfterRecover]() mutable -> void {
      while (true) {
        m_mediator.m_lookup->SetSyncType(SyncType::NORMAL_SYNC);
        this->CleanVariables();
        this->m_mediator.m_ds->CleanVariables();
        while (!this->DownloadPersistenceFromS3()) {
          LOG_GENERAL(
              WARNING,
              "Downloading persistence from S3 has failed. Will try again!");
          this_thread::sleep_for(chrono::seconds(RETRY_REJOINING_TIMEOUT));
        }
        BlockStorage::GetBlockStorage().RefreshAll();
        AccountStore::GetInstance().RefreshDB();
        if (this->Install(SyncType::NORMAL_SYNC, true, rejoiningAfterRecover)) {
          break;
        };
        this_thread::sleep_for(chrono::seconds(RETRY_REJOINING_TIMEOUT));
      }
      this->StartSynchronization();
    };
    DetachedFunction(1, func);
  }
}
```

It only terminates if the `this->Install(SyncType::NORMAL_SYNC, true, rejoiningAfterRecover)` call
returns true.

Since the `toRetrieveHistory` flag is set, `this->Install` returns `false` if
`!StartRetrieveHistory(syncType, rejoiningAfterRecover)` has the `StartRetrieveHistory` [call
returning `false`](https://github.com/Zilliqa/Zilliqa/blob/v4.4.0/src/libNode/Node.cpp#L168).

```c++
bool Node::Install(const SyncType syncType, const bool toRetrieveHistory,
                   bool rejoiningAfterRecover) {
  LOG_MARKER();

  m_txn_distribute_window_open = false;

  // m_state = IDLE;
  bool runInitializeGenesisBlocks = true;

  if (syncType == SyncType::DB_VERIF) {
    m_mediator.m_dsBlockChain.Reset();
    m_mediator.m_txBlockChain.Reset();

    m_synchronizer.InitializeGenesisBlocks(m_mediator.m_dsBlockChain,
                                           m_mediator.m_txBlockChain);
    const auto& dsBlock = m_mediator.m_dsBlockChain.GetBlock(0);
    m_mediator.m_blocklinkchain.AddBlockLink(0, 0, BlockType::DS,
                                             dsBlock.GetBlockHash());

    return true;
  }

  if (toRetrieveHistory) {
    if (!StartRetrieveHistory(syncType, rejoiningAfterRecover)) {
      AddGenesisInfo(SyncType::NO_SYNC);
      this->Prepare(runInitializeGenesisBlocks);
      return false;
    }
...
```

`StartRetrieveHistory` returns `false` because the node lost POW and [does not belong to a
shard](https://github.com/Zilliqa/Zilliqa/blob/v4.4.0/src/libNode/Node.cpp#L726).


```c++
bool Node::StartRetrieveHistory(const SyncType syncType,
                                bool rejoiningAfterRecover) {
...
  if (REJOIN_NODE_NOT_IN_NETWORK && !LOOKUP_NODE_MODE && !bDS &&
      !bInShardStructure) {
    LOG_GENERAL(WARNING,
                "Node " << m_mediator.m_selfKey.second
                        << " is not in network, apply re-join process instead");
    return false;
  }
...
```

Hence, the `RejoinAsNormal` loop never terminates and the resync continues ad infinitum.

