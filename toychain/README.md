# toychain: Toy blockchain

## Architecture
Every node is represented by a ``Node`` object. It has its own *(host, port)* and must have a *consensus* a initialisation parameter.


##### Required methods to implement a new consensus

Every consensus needs the following methods/attributes:

- ``verify_chain(chain, previous_state)``: Method that verifies that the specified ``chain`` respects the consensus. The ``previous_state`` is the state of the previous block.
- ``self.block_generation``: Specified in the constructor, this is a thread object that will produce the blocks respecting the consensus.
- ``self.genesis``: Genesis block that will be the first block of every node using this consensus.

### Custom Timer
The whole project is based on a custom timer. Each node possess its own ``CustomTimer``. At each control step of one robot, the timer is incremented by 1. 



## Options

### Consensus options
The consensus options are contained in their own file

##### Proof of work
``MINING_DIFFICULTY``: This represents the difficulty of mining and is thus related to the time taken to produce a block

``ProofOfWork.trust``: Determines if the state should be checked or not when verifying a chain 

##### Proof of authority
``BLOCK_PERIOD``: Minimum difference between two consecutive block’s timestamps.

``DIFF_INTURN``: Block score (difficulty) for blocks containing in-turn signatures (by the preferred producer of this turn)

``DIFF_NOTURN``: Block score (difficulty) for blocks containing out-of-turn signatures (not by the preferred producer of this turn)

``ProofOfAuth.trust``: Determines if the state should be checked or not when verifying a chain 

The __genesis block__ is organised this way:

- miner_id contains the authorised signers list
### Other options
All the other options are contained in the ``constants.py`` file.

``MEMPOOL_SYNC_INTERVAL``: Time interval between two synchronisation process in the ``MempoolPinger``

``CHAIN_SYNC_INTERVAL``: Time interval between two synchronisation process in the ``ChainPinger``







