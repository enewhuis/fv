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

    # hard-coded FJB Admin account 2nd constructor arg:
    initCode = FreedomAgent.bytecode + '000000000000000000000000' + deterministicFactory[2:] + '00000000000000000000000076a17266Cc3c2d7531E988E43a15e4e0D7CAb3E2'

    agentSalt = '0x0000000000000000000000000000000000000000000000000000000000000004'
    deterministicAgent = predetermined_address(SINGLETON_FACTORY_ADDRESS, initCode, agentSalt)
    print(deterministicAgent)
    assert deterministicAgent == '0x1230B541221717b53CF5d0B4142927aDa571f134'

    deployer = accounts.load('fjb_admin')
    singletonFactory.deploy(initCode, agentSalt, { 'from': deployer, 'gas_limit': 1000000 })

def predetermined_address(deployer, bytecode, salt):
    return web3.toChecksumAddress(
        web3.solidityKeccak(
            ("bytes", "address", "bytes32", "bytes32"),
            ("0xff", deployer, salt, web3.keccak(hexstr=bytecode)),
        )[12:]
    )
