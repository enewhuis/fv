from tkinter import SINGLE
from brownie import accounts, FreedomAgentV1, FreedomFactory, Contract, web3
import sys

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
    print('factory', deterministicFactory)
    assert deterministicFactory == '0x10843bC70f2F1aD601cE7Fb41BF838075A5b0CC7'

    singletonFactory = Contract.from_abi('SingletonFactory', SINGLETON_FACTORY_ADDRESS, SINGLETON_FACTORY_ABI)

    # hard-coded FJB Admin account 2nd constructor arg:
    initCode = FreedomAgentV1.bytecode + '000000000000000000000000' + deterministicFactory[2:] + '00000000000000000000000076a17266Cc3c2d7531E988E43a15e4e0D7CAb3E2'

    agentSalt = '0x000000000000000000000000aC9Cd67946F5D6D5236bF7370BEce7E1e8910CfB'
    deterministicAgent = predetermined_address(SINGLETON_FACTORY_ADDRESS, initCode, agentSalt)
    print(deterministicAgent)
    
    # vanity
    while not deterministicAgent.startswith('0xFBD1'):
        agentSalt = '0x000000000000000000000000' + deterministicAgent[2:]
        deterministicAgent = predetermined_address(SINGLETON_FACTORY_ADDRESS, initCode, agentSalt)
        print(deterministicAgent)

    assert deterministicAgent == '0xFBD14c743651719442332Fa589979fA6eb8da174'

    deployer = accounts.load('fjb_admin')
    singletonFactory.deploy(initCode, agentSalt, { 'from': deployer, 'gas_limit': 2000000 })

    AGENT_1 = '0x5b97b2deed27875b160c93ed7bbc365f4384ccfc'
    fa = FreedomAgentV1.at(deterministicAgent)
    fa.grantRole(fa.AGENT_ROLE(), AGENT_1, {'from': deployer})


def predetermined_address(deployer, bytecode, salt):
    return web3.toChecksumAddress(
        web3.solidityKeccak(
            ("bytes", "address", "bytes32", "bytes32"),
            ("0xff", deployer, salt, web3.keccak(hexstr=bytecode)),
        )[12:]
    )
