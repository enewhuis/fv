// SPDX-License-Identifier: MIT
pragma solidity ^0.8.16;

import "./FreedomWallet.sol";

contract FreedomFactory {

  // Returns the address of the newly deployed contract
  function deploy(address owner_, uint256 salt_)
    public
    payable
    returns (address)
  {
    // This syntax is a newer way to invoke create2 without assembly, you just need to pass salt
    // https://docs.soliditylang.org/en/latest/control-structures.html#salted-contract-creations-create2
    return address(new FreedomWallet{salt: bytes32(salt_)}(owner_));
  }

  // 1. Get bytecode of contract to be deployed
  function getBytecode(address owner_)
      public
      pure
      returns (bytes memory)
  {
      bytes memory bytecode = type(FreedomWallet).creationCode;
      return abi.encodePacked(bytecode, abi.encode(owner_));
  }

  /** 2. Compute the address of the contract to be deployed
      params:
          _salt: random unsigned number to identify instance
  */ 
  function getAddress(address owner_, uint256 salt_)
      public
      view
      returns (address)
  {
      // Get a hash concatenating args passed to encodePacked
      bytes32 hash = keccak256(
          abi.encodePacked(
              bytes1(0xff), // 0
              address(this), // address of factory contract
              salt_, // a random salt
              keccak256(getBytecode(owner_)) // the wallet contract bytecode
              
          )
      );
      // Cast last 20 bytes of hash to address
      return address(uint160(uint256(hash)));
  }
}