from tkinter import SINGLE
from brownie import accounts, FreedomAgent, FreedomFactory, Contract, web3

SINGLETON_FACTORY_ADDRESS = '0xce0042B868300000d44A59004Da54A005ffdcf9f'

SINGLETON_FACTORY_ABI = [
    {
        "constant": False,
        "inputs": [
            {
                "internalType": "bytes",
                "name": "_initCode",
                "type": "bytes"
            },
            {
                "internalType": "bytes32",
                "name": "_salt",
                "type": "bytes32"
            }
        ],
        "name": "deploy",
        "outputs": [
            {
                "internalType": "address payable",
                "name": "createdContract",
                "type": "address"
            }
        ],
        "payable": False,
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

def main():
    # https://eips.ethereum.org/EIPS/eip-2470

    factorySalt = '0x0000000000000000000000000000000000000000000000000000000000000000'
    deterministicFactory = predetermined_address(SINGLETON_FACTORY_ADDRESS, FreedomFactory.bytecode, factorySalt)
    assert deterministicFactory == '0x10843bC70f2F1aD601cE7Fb41BF838075A5b0CC7'

    singletonFactory = Contract.from_abi('SingletonFactory', SINGLETON_FACTORY_ADDRESS, SINGLETON_FACTORY_ABI)

    deployer = accounts.load('fjb_admin')
    singletonFactory.deploy(FreedomFactory.bytecode, factorySalt, { 'from': deployer, 'gas_limit': 1000000 })

def predetermined_address(deployer, bytecode, salt):
    return web3.toChecksumAddress(
        web3.solidityKeccak(
            ("bytes", "address", "bytes32", "bytes32"),
            ("0xff", deployer, salt, web3.keccak(hexstr=bytecode)),
        )[12:]
    )
