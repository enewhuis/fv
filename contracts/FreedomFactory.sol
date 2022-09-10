// SPDX-License-Identifier: MIT
pragma solidity ^0.8.16;

import "./FreedomWallet.sol";

contract FreedomFactory {

  // Deploys a FreedomWallet contract returning its address matching that returned by getAddress()
  // For a given owner address and salt, the deployed contract must have the same address regardless
  // of which chain it is deployed on.  This is desireable to enable recovery of tokens accidentally
  // transferred on the wrong chain.
  //
  function deploy(address owner_, uint256 salt_)
    public
    payable
    returns (address)
  {
    // https://docs.soliditylang.org/en/latest/control-structures.html#salted-contract-creations-create2
    return address(new FreedomWallet{salt: bytes32(salt_)}(owner_));
  }

  // Returns the creation bytecode of the FreedomWallet contract.
  function getBytecode(address owner_)
      public
      pure
      returns (bytes memory)
  {
      bytes memory bytecode = type(FreedomWallet).creationCode;
      return abi.encodePacked(bytecode, abi.encode(owner_));
  }

  // Returns the deterministic address for a FreedomWallet with the given owner and salt.
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