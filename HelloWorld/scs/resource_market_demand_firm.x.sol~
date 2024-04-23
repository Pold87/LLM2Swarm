// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract MarketForaging {

  uint constant quota         = ${QUOTA};
  uint constant fuel_cost     = ${FUELCOST};
  uint constant maxw          = ${MAXWORKERS};
  uint constant lim_assign    = ${LIMITASSIGN};
  uint constant demandA       = ${DEMAND_A};
  uint constant demandB       = ${DEMAND_B};

  function Token_key() public pure returns (string[2] memory){
    return ["robots", "supply"];
  }
  struct Token {
    uint robots;
    uint supply;
  }

  function Robot_key() public pure returns (string[5] memory){
    return ["isRegistered", "efficiency", "revenue", "balance", "task"];
  }
  struct Robot {
    bool isRegistered;
    uint efficiency;
    uint revenue;
    uint balance;
    uint task;
  }

  function Epoch_key() public pure returns (string[6] memory){
    return ["number", "start", "Q", "TC", "ATC", "price"];
  }
  struct Epoch {
    uint number;
    uint start;
    uint[] Q; 
    uint[] TC; 
    uint[] ATC;
    uint price;
  }


  function Patch_key() public pure returns (string[11] memory){
    return ["x", "y", "qtty", "util", "qlty", "json", "id", "max", "tot", "last_assign", "epoch"];
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
    uint maxw;
    uint totw;
    uint last_assign;

    Epoch epoch;
  } 

  mapping(address => Robot) public robot;
  Token public token;
  Epoch[] public  epochs;
  Patch[] private patches;
  
  

  // Epoch private epoch0 = ; 
  uint id_nonce;

  function linearDemand(uint Q) public pure returns (uint){
    uint P = 0;
    if (demandB>demandA*Q) {
      P = demandB-demandA*Q;
    } 
    return P;
  }

  function register(uint eff) public {
    if (!robot[msg.sender].isRegistered) {
      robot[msg.sender].isRegistered = true;
      robot[msg.sender].efficiency   = eff;
      robot[msg.sender].revenue       = 0;
      robot[msg.sender].balance      = 20000;
      token.supply += 20000;
      token.robots += 1;

      for (uint i=0; i < patches.length; i++) {
        if (patches[i].totw < patches[i].maxw && robot[msg.sender].task == 0) {
          patches[i].totw++;
          robot[msg.sender].task = patches[i].id;
        }
      }
    }
  }

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

      patches.push(Patch({
                          x: _x, 
                          y: _y, 
                          qtty: _qtty, 
                          util: _util,
                          qlty: _qlty, 
                          json: _json,
                          id:   id_nonce,
                          maxw:   maxw,
                          totw:   0,
                          last_assign:   0,
                          epoch: Epoch({
                                number: 1, 
                                start: block.number, 
                                Q: new uint[](0),
                                TC: new uint[](0),
                                ATC: new uint[](0),
                                price: linearDemand(0)
                    })
                        }));
    }
  } 

  function buyFuel(uint duration) internal {

    // uint tokens_consumed = robot[msg.sender].efficiency * duration * fuel_cost / 10000;
    uint tokens_consumed = duration;

    // efficiency:  amps/block     -- robot internal parameter
    // duration:    centi-seconds  -- duration of trip
    // fuel_cost:   tokens/amp     -- cost of 1 amp

    if (robot[msg.sender].balance < tokens_consumed) {
      token.supply -= robot[msg.sender].balance;
      robot[msg.sender].balance = 0;
    }
    else {
      robot[msg.sender].balance -= tokens_consumed;
      token.supply -= tokens_consumed;
    }
  }
    
  function sellUnits(uint patch_index, uint _Q) internal {

    uint i = patch_index;

    uint payout = _Q*patches[i].util*patches[i].epoch.price;
    robot[msg.sender].revenue += payout;
    robot[msg.sender].balance += payout;
    token.supply              += payout;
  }

  function dropResource(int _x, int _y, uint _qtty, uint _util, string memory _qlty, string memory _json, uint _Q, uint _TC) public {

    uint i = findByPos(_x, _y);

    if (i < 9999 && robot[msg.sender].task == patches[i].id) {

      // Update patch information
      updatePatch(_x, _y, _qtty, _util, _qlty, _json);

      // Pay the robot
      sellUnits(i, _Q);

      // Fuel purchase
      buyFuel(_TC);

      // Robot deposits the item and purchases more fuel
      patches[i].epoch.Q.push(_Q);
      patches[i].epoch.TC.push(_TC);
      patches[i].epoch.ATC.push(_TC/_Q);

      if (patches[i].epoch.Q.length >= patches[i].totw) {

        uint TQ = 0;
        for (uint j=0; j < patches[i].epoch.Q.length; j++) {
          TQ += patches[i].epoch.Q[j];
        }

        // Init new epoch
        epochs.push(patches[i].epoch);
        patches[i].epoch.number++;
        patches[i].epoch.start = block.number;
        patches[i].epoch.Q     = new uint[](0);
        patches[i].epoch.TC    = new uint[](0);
        patches[i].epoch.ATC   = new uint[](0);
        patches[i].epoch.price  = linearDemand(TQ);

        // Establish entry in market
        // 
      }
    }
  }

  function joinPatch(int _x, int _y) public {

    uint i = findByPos(_x, _y);

    // Assign robot to chosen patch
    if (robot[msg.sender].task == 0 && block.number >= lim_assign+patches[i].last_assign){
      patches[i].totw++;
      patches[i].last_assign = block.number;
      robot[msg.sender].task = patches[i].id;
    }
  }

  function leavePatch(int _x, int _y) public {

    uint i = findByPos(_x, _y);

    // Unassign robot to chosen patch
    if (robot[msg.sender].task == patches[i].id){
      patches[i].totw--;
      robot[msg.sender].task = 0;
    }
  }

  function assignPatch() public {

    // Limit foragers algorithm
    uint i = findAvailiable();

    // Assign new foraging task
    if (i < patches.length) {
      patches[i].totw++;
      patches[i].last_assign = block.number;
      robot[msg.sender].task = patches[i].id;
    }
  }

  function findAvailiable() public view returns (uint) {

    uint index = 9999;

    for (uint i=0; i < patches.length; i++) {
      if (patches[i].totw < patches[i].maxw 
        && robot[msg.sender].task != patches[i].id
        && block.number >= lim_assign+patches[i].last_assign) {
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
      if (patches[i].id == robot[msg.sender].task) return patches[i];
    }   
  }

  function getMyPatch() public view returns (string memory){

    uint task_id = robot[msg.sender].task;

    if (task_id == 0) return "";

    for (uint i=0; i < patches.length; i++) {
      if (patches[i].id == task_id) return patches[i].json;
    } 
  }

  function getBalance() public view returns (uint){
    return robot[msg.sender].balance;
  }

}
  

// function runningMean(uint previous, uint current, uint N) private pure returns (uint) {
//   return (previous*N + current) / (N+1);
//   }



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