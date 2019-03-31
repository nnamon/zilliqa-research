# Zilliqa DS Committee Selection Algorithm

## Problem Statement

Currently, the DS Committee is composed of nodes that are allowed to participate in the network as
orchestrators and hence, are allowed to remain in the network for a long period of time. The period
is at least 18 DS epochs assuming 600 nodes in a shard, 420 DS guard nodes and that 10 nodes are
retired every epoch. Due to the variability of a typical community nodes's capability, it is often
observed that approximately 30 community nodes are unreachable at any one time. This is in addition
to the DS nodes that are reachable but not participating in the consensus process. This can happen
when DS nodes get out of sync and have to wait until the next DS epoch to rejoin. The current
observations imply that at least 17% (v4.3.1 observation) of community nodes could be considered
Byzantine at all times.

## Impact

The problem jeopardises the ability for the network to run resiliently without guard nodes.

Since performance is not taken into account, a miner is not incentivised to participate in DS
consensus. A rational miner would recognise that since they are guaranteed 18 rounds of the base
reward without contributing any further resources, they could simply use those same resources to
earn more by generating new keys and attempting shard or DS Committee membership instead. In a
malicious scenario, it also allows an attacker to not put forward any additional resources to
maintain their membership in the DS Committee. This eases the objective of accruing the 1/3
requirement for stalling the network.

## Proposed Solution

The proposed solution is to require a minimum threshold percentage of co-signatures to be performed
by every DS node. If a node does not meet this requirement, it is prioritised for replacement. Up to
[`numOfElectedDSMembers`][3] non-performing nodes are selected this way (`n`), from the newest in
the network to the oldest.  If less than `numOfElectedDSMembers` were selected, the oldest
`numOfElectedDSMembers - n` nodes are added for replacement.

This ensures that the non-responsive or non-performant nodes are immediately removed and creates
additional competition between DS node owners. Selecting the newest non-performant node for removal
creates a penalisation bias towards newer nodes, allowing some tolerance for older nodes who have
proven themselves in previous rounds.

Currently, to deterministically produce the DS Committee composition, a `powWinners` field is
included in the DS Block. The algorithm is [simple][1], it places the new proof-of-work winners
after the guard nodes and shifts the old community nodes back. An existing DS node removes
[itself][2] from the committee in if its previous consensus ID plus the number of new proof-of-work
winners is greater than the committee size. The appendix contains an [annotated pseudocode
listing](#current-ds-committee-composition-update-pseudocode) of this process.

In order to implement the proposed solution without changing the DS Block structure, it is suggested
that the `powWinners` field be leveraged to contain the 'losers' as well as the proof-of-work
winners. If the current DS committee contains a public key in the `powWinners` field, that public
key is moved to the end of composition, effectively demoting it since it will fall past the DS
Committee size. Otherwise, the new proof-of-work winner is placed after the guard nodes as before.
This would allow for back-compatibility with the blocks before this change since it is guaranteed
that there are no existing DS Committee members in `powWinners`. It is suggested that the field be
renamed `powCandidates`. The appendix contains an [annotated pseudocode
listing](#proposed-ds-committee-composition-update-pseudocode) of this proposed process.

## Caveats

Since the solution places emphasis on performance, it might accentuate the geographical
centralisation problem we see in the DS Committee. Due to latency being a large factor in the pBFT
process, the proposal might provide extra disincentive for miners to setup nodes outside of the main
cluster in North America. Hence, the minimum threshold must be selected with care to avoid excluding
benign DS nodes that might act a little slower due to geographical latency in the interest of
decentralisation.

## Code Change Analysis

### Overview of Affected Components

We split the affected components into two logical parts:

1. PoW Candidate Selection - the period of time before a final DS Block is produced and the
   proof-of-work submissions are processed.
2. DS Committee Composition Update - the period after a final DS Block is produced and the DS
   Committee is updated.

Within these two logical parts, updates will be required to be made to how both DS and non-DS nodes
handle the change.

### PoW Candidate Selection

Only the DS nodes are affected for this part.

### DS Committee Composition Update

Both DS and non-DS nodes are affected for this part.

#### libDirectoryService

The pertient message is `DSInstructionType:DSBLOCKCONSENSUS` which invokes
[`DirectoryService::ProcessDSBlockConsensus`][4]. The function calls
[`DirectoryService::ProcessDSBlockConsensusWhenDone`][5] when the DS Committee has completed
consensus and is ready to process the DS Block.


```c++
void DirectoryService::ProcessDSBlockConsensusWhenDone() {
  ...
  UpdateDSCommiteeComposition();
  UpdateMyDSModeAndConsensusId();
  ...
  StartFirstTxEpoch();
}
```

These functions are affected by the proposed solution:

1. [`DirectoryService::UpdateDSCommiteeComposition`][6]
2. [`DirectoryService::UpdateMyDSModeAndConsensusId`][7]
3. [`DirectoryService::StartFirstTxEpoch`][8]

##### `DirectoryService::UpdateDSCommiteeComposition`

This function updates a DS Node's view of the DS Committee composition from the `powWinners` entries
in the finalised DS Block.

```c++
void DirectoryService::UpdateDSCommiteeComposition() {
  ...
  // Get the map of all pow winners from the DS Block.
  const map<PubKey, Peer> NewDSMembers =
      m_mediator.m_dsBlockChain.GetLastBlock().GetHeader().GetDSPoWWinners();
  DequeOfNode::iterator it;

  for (const auto& DSPowWinner : NewDSMembers) {
    // # Remove the pow winner's information from the map of all PoW network information.
    m_allPoWConns.erase(DSPowWinner.first);

    // # If the current iterated winner is my node.
    if (m_mediator.m_selfKey.second == DSPowWinner.first) {
      if (!GUARD_MODE) {
        // Place my node's information in front of the DS Committee
        // Peer() is required because my own node's network information is zeroed out.
        m_mediator.m_DSCommittee->emplace_front(m_mediator.m_selfKey.second,
                                                Peer());
      } else {
        // Calculate the position to insert the current winner.
        it = m_mediator.m_DSCommittee->begin() +
             (Guard::GetInstance().GetNumOfDSGuard());
        // Place my node's information in front of the DS Committee Community Nodes.
        m_mediator.m_DSCommittee->emplace(it, m_mediator.m_selfKey.second,
                                          Peer());
      }
    } else {
      if (!GUARD_MODE) {
        // Place the current winner node's information in front of the DS Committee.
        m_mediator.m_DSCommittee->emplace_front(DSPowWinner);
      } else {
        // Calculate the position to insert the current winner.
        it = m_mediator.m_DSCommittee->begin() +
             (Guard::GetInstance().GetNumOfDSGuard());
        // Place the winner's information in front of the DS Committee Community Nodes.
        m_mediator.m_DSCommittee->emplace(it, DSPowWinner);
      }
    }

    // Removes the last element, maintaining the size of the DS Committee.
    m_mediator.m_DSCommittee->pop_back();
  }
}
```

The proposed solution involves leveraging the `powWinners` field to contain the DS nodes prioritised
for removal. Existing DS members contained ('losers') in the the map of the `powWinners` are moved
to the end of the DS Committee deque while the winners are placed in the same manner as before.
The number of actual winners is tracked as the map is iterated through. This number of nodes are
removed from the back of the deque to maintain the size of the committee.

```c++
void DirectoryService::UpdateDSCommitteeComposition() {
  ...
  // Get the map of all pow winners from the DS Block.
  const map<PubKey, Peer> NewDSMembers =
      m_mediator.m_dsBlockChain.GetLastBlock().GetHeader().GetDSPoWWinners();
  DequeOfNode::iterator it;
  uint32_t NumWinners = 0;

  for (const auto& DSPowWinner : NewDSMembers) {
    // Check if the current pow candidate is an existing DS Committee member. ('loser')
    it = std::find(m_mediator.m_DSCommittee.begin(), m_mediator.m_DSCommittee.end(), DSPowWinner);
    if (it != m_mediator.m_DSCommittee.end()) {
      // Move the candidate to the back of the committee and continue processing other candidates.
      m_mediator.m_DSCommittee.erase(it)
      // Only reorders the Committee. The size is not changed.
      m_mediator.m_DSCommittee.emplace_back(DSPowWinner)
      continue;
    }

    // Otherwise, the candidate is a winner.
    // Remove the pow winner's information from the map of all PoW network information.
    m_allPoWConns.erase(DSPowWinner.first);

    // If the current iterated winner is my node.
    if (m_mediator.m_selfKey.second == DSPowWinner.first) {
      if (!GUARD_MODE) {
        // Place my node's information in front of the DS Committee
        // Peer() is required because my own node's network information is zeroed out.
        m_mediator.m_DSCommittee->emplace_front(m_mediator.m_selfKey.second,
                                                Peer());
      } else {
        // Calculate the position to insert the current winner.
        it = m_mediator.m_DSCommittee->begin() +
             (Guard::GetInstance().GetNumOfDSGuard());
        // Place my node's information in front of the DS Committee Community Nodes.
        m_mediator.m_DSCommittee->emplace(it, m_mediator.m_selfKey.second,
                                          Peer());
      }
    } else {
      if (!GUARD_MODE) {
        // Place the current winner node's information in front of the DS Committee.
        m_mediator.m_DSCommittee->emplace_front(DSPowWinner);
      } else {
        // Calculate the position to insert the current winner.
        it = m_mediator.m_DSCommittee->begin() +
             (Guard::GetInstance().GetNumOfDSGuard());
        // Place the winner's information in front of the DS Committee Community Nodes.
        m_mediator.m_DSCommittee->emplace(it, DSPowWinner);
      }
    }

    // Keep a count of the number of winners.
    ++NumWinners;
  }

  // Remove one node for every winner, maintaining the size of the DS Committee.
  for (auto i = 0; i < NumWinners; i++) {
    // One item is always removed every winner, with removal priority given to 'loser' candidates
    // before expiring nodes.
    m_mediator.m_DSCommittee->pop_back();
  }
}
```

##### `DirectoryService::UpdateMyDSModeAndConsensusId`


##### `DirectoryService::StartFirstTxEpoch`

## Appendix

### Current DS Committee Composition Update Pseudocode

```python
# Mediator Reference to the DS Committee
m_DSCommittee: DequeOfNode

# Number of DS Guards
NUMBER_OF_DS_GUARDS: int

# Mediator Reference to the Node's Key Pair
m_selfKey: PairOfKey

# DirectoryService Reference to all PoW Network Information
m_allPoWConns: Map[PubKey, Peer]

# Update DS Committee Composition

def DirectoryService_UpdateDSCommitteeComposition():
    # Get the map of all pow winners from the DS Block.
    NewDSMembers: Map[PubKey, Peer] = GetDSPoWWinners()
    it: DequeOfNodeIterator

    for DSPowWinner in NewDSMembers.items():
        # Remove the pow winner's information from the map of all PoW network information.
        m_allPoWConns.erase(DSPowWinner.first)

        # If the current iterated winner is my node.
        if m_self.pubkey == DSPowWinner.first:
            if not GUARD_MODE:
                # Place my node's information in front of the DS Committee.
                # Peer() is required because my own node's network information is zeroed out.
                m_DSCommittee.emplace_front(m_selfKey.pubkey, Peer())
            else:
                # Calculate the position to insert the current winner.
                it = m_DSCommittee.begin() + NUMBER_OF_DS_GUARDS

                # Place my node's information in front of the DS Committee Community Nodes.
                m_DSCommittee.emplace(it, m_selfKey.pubkey, Peer())
        else:
            if not GUARD_MODE:
                # Place the current winner node's information in front of the DS Committee.
                m_DSCommittee.emplace_front(DSPowWinner)
            else:
                # Calculate the position to insert the current winner.
                it = m_DSCommittee.begin() + NUMBER_OF_DS_GUARDS

                # Place the winner's information in front of the DS Committee Community Nodes.
                m_DSCommittee.emplace(it, DSPowWinner)

        # Removes the last element, maintaining the size of the DS Committee.
        m_DSCommittee.pop_back() # One item is always removed every winner.
```

### Proposed DS Committee Composition Update Pseudocode

```python
# Mediator Reference to the DS Committee
m_DSCommittee: DequeOfNode

# Number of DS Guards
NUMBER_OF_DS_GUARDS: int

# Mediator Reference to the Node's Key Pair
m_selfKey: PairOfKey

# DirectoryService Reference to all PoW Network Information
m_allPoWConns: Map[PubKey, Peer]

# Update DS Committee Composition
def DirectoryService_UpdateDSCommitteeComposition():
    # Get the map of all pow candidates from the DS Block.
    NewDSMembers: Map[PubKey, Peer] = GetDSPoWCandidates()
    it: DequeOfNodeIterator
    numWinners: int = 0

    for DSPowCandidate in NewDSMembers.items():
        # Check if the current pow candidate is an existing DS Committee member. ('loser')
        if DSPowCandidate in m_DSCommittee:
            # Move the candidate to the back of the committee and continue processing other
            # candidates.
            it = m_DSCommittee.begin() + m_DSCommitee.index(DSPowCandidate)
            m_DSCommittee.erase(it)
            # Only reorders the Committee. The size is not changed.
            m_DSCommittee.emplace_back(DSPowCandidate)
            continue

        # Otherwise, the candidate is a winner.
        # Remove the pow winner's information from the map of all PoW network information.
        m_allPoWConns.erase(DSPowCandidate.first)

        # If the current iterated winner is my node.
        if m_self.pubkey == DSPowWinner.first:
            if not GUARD_MODE:
                # Place my node's information in front of the DS Committee.
                # Peer() is required because my own node's network information is zeroed out.
                m_DSCommittee.emplace_front(m_selfKey.pubkey, Peer())
            else:
                # Calculate the position to insert the current winner.
                it = m_DSCommittee.begin() + NUMBER_OF_DS_GUARDS

                # Place my node's information in front of the DS Committee Community Nodes.
                m_DSCommittee.emplace(it, m_selfKey.pubkey, Peer())
        else:
            if not GUARD_MODE:
                # Place the current winner node's information in front of the DS Committee.
                m_DSCommittee.emplace_front(DSPowWinner)
            else:
                # Calculate the position to insert the current winner.
                it = m_DSCommittee.begin() + NUMBER_OF_DS_GUARDS

                # Removes the last element, maintaining the size of the DS Committee.
                m_DSCommittee.emplace(it, DSPowWinner)

            # Keep a count of the number of winners.
            numWinners += 1

    # Remove one node for every winner, maintaining the size of the DS Committee.
    for i in range(numWinners):
        # One item is always removed every winner, with removal priority given to 'loser'
        # candidates before expiring nodes.
        m_DSCommittee.pop_back()
```


[//]: # (References)
[1]: https://github.com/Zilliqa/Zilliqa/blob/tag/v4.4.0/src/libDirectoryService/DSBlockPostProcessing.cpp#L290
[2]: https://github.com/Zilliqa/Zilliqa/blob/tag/v4.4.0/src/libDirectoryService/DSBlockPostProcessing.cpp#L238
[3]: https://github.com/Zilliqa/Zilliqa/blob/tag/v4.4.0/src/libDirectoryService/DSBlockPreProcessing.cpp#L61
[4]: https://github.com/Zilliqa/Zilliqa/blob/tag/v4.4.0/src/libDirectoryService/DSBlockPostProcessing.cpp#L622
[5]: https://github.com/Zilliqa/Zilliqa/blob/tag/v4.4.0/src/libDirectoryService/DSBlockPostProcessing.cpp#L479
[6]: https://github.com/Zilliqa/Zilliqa/blob/tag/v4.4.0/src/libDirectoryService/DSBlockPostProcessing.cpp#L290
[7]: https://github.com/Zilliqa/Zilliqa/blob/tag/v4.4.0/src/libDirectoryService/DSBlockPostProcessing.cpp#L214
[8]: https://github.com/Zilliqa/Zilliqa/blob/tag/v4.4.0/src/libDirectoryService/DSBlockPostProcessing.cpp#L330
