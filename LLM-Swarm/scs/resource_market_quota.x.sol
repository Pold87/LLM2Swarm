// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract MarketForaging {

  int[4] Demand       = [int(0), 0, -1, 6];
  uint constant quota = QUOTA;


  struct Epoch {
    uint number;
    uint start;
    uint duration;
    uint supply;
    uint consumption;
  }

  struct Patch {

    // Details 
    int x;
    int y;
    uint qtty;
    uint util;
    string qlty;
    string json; 

    // Identifier
    uint id;

    // Assignment
    uint max_workers;
    uint tot_workers;

    Epoch epoch;
  } 

  Patch[] private patches;
  Epoch[] public  epochs;

  uint id_nonce;
  mapping(address => uint) tasks;
  mapping(address => uint) drops;
  mapping(address => uint) lastD;

  function updatePatch(int _x, int _y, uint _qtty, uint _util, string memory _qlty, string memory _json) public {

    uint i = findByPos(_x, _y);

    // If patch is already known
    if (i < 9999) { 
      patches[i].qtty  = _qtty;
      patches[i].util  = _util;
      patches[i].qlty  = _qlty;
      patches[i].json  = _json;
    }

    // If patch is new
    else {

      // Increment unique patch id
      id_nonce++;

      // Append new patch to list
      Epoch memory new_epoch = Epoch({
                          number: 1, 
                          start: block.number, 
                          duration: 0,
                          supply: 0,
                          consumption: 0
                        }); 

      patches.push(Patch({
                          x: _x, 
                          y: _y, 
                          qtty: _qtty, 
                          util: _util,
                          qlty: _qlty, 
                          json: _json,
                          id:      id_nonce,
                          max_workers:   1,
                          tot_workers:   0,
                          epoch: new_epoch
                        }));
    }
  } 

  function dropResource(int _x, int _y, uint _qtty, uint _util, string memory _qlty, string memory _json) public {

    uint i = findByPos(_x, _y);

    if (i < 9999 && tasks[msg.sender] == patches[i].id) {

      // New good in current epoch
      patches[i].epoch.supply++;
    
      // Update patch information
      updatePatch(_x, _y, _qtty, _util, _qlty, _json);

      if (patches[i].epoch.supply == patches[i].tot_workers) {


        // Finalize previous epoch
        patches[i].epoch.duration = block.number - patches[i].epoch.start;
        patches[i].epoch.consumption = 1000*patches[i].epoch.supply/patches[i].epoch.duration;

        if (patches[i].epoch.consumption < quota) {
          patches[i].max_workers++;
        }


        // Init new epoch
        epochs.push(patches[i].epoch);
        patches[i].epoch.number++;
        patches[i].epoch.start = block.number;
        patches[i].epoch.supply = 0;
        // patches[i].epoch.duration
        // patches[i].epoch.consumption

      }
    }
  }

  function assignPatch() public {

    // Limit foragers algorithm
    uint i = findAvailiable();

    // Assign new foraging task
    if (i < patches.length) {
      patches[i].tot_workers++;
      tasks[msg.sender] = patches[i].id;
    }
  }

  function findAvailiable() private view returns (uint) {

    uint index = 9999;

    for (uint i=0; i < patches.length; i++) {
      if (patches[i].tot_workers < patches[i].max_workers && tasks[msg.sender] != patches[i].id) {
        index = i;
      }
    }
      return index;    
  }

  function findByID(uint id) private view returns (uint) {
    for (uint i=0; i < patches.length; i++) {
      if (patches[i].id == id) {
        return i;
      }
    } 
    return 9999;
  }

  function findByPos(int _x, int _y) private view returns (uint) {
    for (uint i=0; i < patches.length; i++) {
      if (_x == patches[i].x && _y == patches[i].y) {
        return i;
      }
    } 
    return 9999;
  }

  function getPatches() public view returns (Patch[] memory){
    return patches;
  }

  function getEpochs() public view returns (Epoch[] memory){
    return epochs;
  }

  function getPatch() public view returns (Patch memory){

    for (uint i=0; i < patches.length; i++) {
      if (patches[i].id == tasks[msg.sender]) return patches[i];
    }   
  }

  function getMyPatch() public view returns (string memory){

    uint task_id = tasks[msg.sender];

    if (task_id == 0) return "";

    for (uint i=0; i < patches.length; i++) {
      if (patches[i].id == task_id) return patches[i].json;
    }   

  }  
}

  // function updateMean(uint previous, uint current, uint N) private pure returns (uint) {
  //   return (previous*N + current) / (N+1);
  // }

  // function random(uint mod) private view returns (uint) {
  //   return uint(keccak256(abi.encode(block.timestamp))) % mod;
  // }

  // function coinFlip(uint odds) private view returns (bool) {
  //   if (random(100) < odds) {
  //     return true;
  //   }
  //   return false;
  // }




// Backups
// && patches[i].qtty > patches[i].worker_count