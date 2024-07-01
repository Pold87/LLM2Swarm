// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract MarketForaging {

  uint constant max_workers = MAXWORKERS;
  uint constant max_stakers = MAXSTAKERS;


    struct resource {
    address scout;
    address[max_workers] workers;
    address[max_stakers] stakers;
    uint[max_stakers] stakes;
    uint stake;

    // For average time cost calculations
    uint lastT;
    uint meanT;
    uint bestT;
    uint count;

    int x;
    int y;
    uint qtty;
    uint util;
    string qlty;
    string json; 
  } 

 
  resource[] public resources;
  resource[] public resources_depleted;

  address[max_workers] public workers_empty;
  address[max_stakers] public stakers_empty;
  uint[max_stakers] public stakes_empty;

  mapping(address => uint) public balances;

  function updateMean(uint old_mean, uint new_value, uint N) private pure returns (uint) {
    return (old_mean*N + new_value) / (N+1);
  }

  function max(uint256 a, uint256 b) private pure returns (uint256) {
    return a >= b ? a : b;
  }

  function min(uint256 a, uint256 b) private pure returns (uint256) {
    return a < b ? a : b;
  }

  function sellResource(uint _util) public {
    balances[msg.sender] += _util;
  } 

  function updatePatch(int _x, int _y, uint _qtty, uint _util, string memory _qlty, string memory _json) public {
    bool unique = true;
    bool depleted = false;

    // If patch is not unique
    for (uint i=0; i < resources.length; i++) {
      if (_x == resources[i].x && _y == resources[i].y ) {
        unique = false;

        // Update patch information
        resources[i].meanT  = updateMean(resources[i].meanT, block.timestamp-resources[i].lastT, resources[i].count);
        resources[i].bestT  = min(resources[i].bestT, block.timestamp-resources[i].lastT);
        resources[i].lastT  = block.timestamp;

        resources[i].count += 1;
      
        resources[i].json   = _json;
        resources[i].qtty   = _qtty;

        // Remove patch if quantity is 0
        if (resources[i].qtty < 1) {
          resources_depleted.push(resources[i]);
          resources[i] = resources[resources.length - 1];
          resources.pop();
        }
        break;
      }
    } 

    // Is patch depleted
    for (uint i=0; i < resources_depleted.length; i++) {
      if (_x == resources_depleted[i].x && _y == resources_depleted[i].y ) {
        depleted = true;
        break;
      }
    }

    // If patch is unique
    if (unique && !depleted) {
      // Append the new resource to the list
            resources.push(resource({
                                scout: msg.sender,
                                workers: workers_empty,
                                stakers: stakers_empty,
                                stakes:  stakes_empty,
                                stake:   0,
                                lastT:   block.timestamp,
                                meanT:   0,
                                bestT:   9999999999,
                                count:   0,
                                x: _x, 
                                y: _y, 
                                qtty: _qtty, 
                                util: _util,
                                qlty: _qlty, 
                                json: _json
                              }));
    }

  } 

  function assignPatch() public {

    // Buy resource with maximum util
    uint res_index = 0;
    uint rec_index = 0;
    uint max_util = 0;
  
    bool is_recruit = false;
    uint my_res_index = 0;
    uint my_rec_index = 0;

    for (uint i=0; i < resources.length; i++) {
      for (uint j=0; j < max_workers; j++) {

        if (resources[i].workers[j] == msg.sender) {
          is_recruit = true;
          my_res_index = i;
          my_rec_index = j;
        } 
        
        if (resources[i].workers[j] == address(0) && resources[i].util > max_util) {
          max_util = resources[i].util;
          res_index = i;
          rec_index = j;
        }

      }    
    }

    require(max_util > 0, "No resources for sale");

    if (is_recruit && resources[my_res_index].util < max_util) {
      resources[my_res_index].workers[my_rec_index] = address(0);
      is_recruit = false;
    }

    // Update resource recruit
    if (!is_recruit) {
      resources[res_index].workers[rec_index] = msg.sender;
    }
  }

  // function foragePatch(int _x, int _y) public {


  //   // Robot can only forage one patch
  //   require(bytes(getMyResource()).length > 0, "Already recruit!");

  //   for (uint i=0; i < resources.length; i++) {
  //     if (_x == resources[i].x && _y == resources[i].y ) {

  //       for (uint j=0; j < max_workers; j++) {
          
  //         if (resources[i].workers[j] == address(0)) {
  //           resources[i].workers[j] = msg.sender;
  //         }
  //       }    
  //     }
  //   }
  // }


  function getResources() public view returns (resource[] memory){
    return resources;
  }

  function getMyResource() public view returns (string memory){

    for (uint i=0; i < resources.length; i++) {

      for (uint j=0; j < max_workers; j++) {

        if (resources[i].workers[j] == msg.sender) { 
           return resources[i].json; 
        }
      }
    }
    return "";    
  }


  
}

