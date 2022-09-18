from brownie import web3, reverts
from conftest import sign2

WEI = 10**18
INITIAL_BALANCE = 1000 * WEI

def test_native_transfer_before_deploy(accounts, factory, FreedomWallet, chain):
    sender = accounts[0]
    owner = accounts.add()
    receiver = accounts[1]
    operator = accounts[2]

    # Determine the FreedomWallet address from the owner address and the owner's instance id (salt)
    walletAddress = factory.getAddress(owner, 0)

    amount = 50 * WEI

    # Transfer tokens to the FreedomWallet address 
    sender.transfer(walletAddress, 2 * amount)

    # Deploy the FreedomWallet for the owner; the address should match.
    instance = 0
    tx_deploy = factory.deploy(owner, instance)
    wallet = FreedomWallet.at(tx_deploy.return_value)
    assert wallet.address == walletAddress

    # Owner sign a transaction that transfers 50 tokens to receiver
    tx = dict(destination = receiver.address,
              value = amount,
              data = '0x00',
              nonce = wallet.nonce(),
              executor = operator.address,
              gasLimit = 1000000)

    # FreedomWallet owner signs the transaction for the operator to execute.
    signed = sign2(factory, owner, instance, chain.id, tx)

    # Operator broadcast signed transaction paying for gas on behalf of owner
    wallet.execute(
        signed.v, signed.r, signed.s,
        tx['destination'],
        tx['value'],
        tx['data'],
        tx['executor'],
        tx['gasLimit'],
        {'from': operator, 'gasLimit': tx['gasLimit']})

    # Did the tokens arrive?
    assert receiver.balance() == INITIAL_BALANCE + amount

    # Owner should still have 50 remaining in the FreedomWallet.
    assert wallet.balance() == amount


def test_agent_native_transfer(accounts, factory, FreedomWallet, agent1, chain):
    admin = accounts[0]
    sender = accounts[0]
    owner = accounts.add()
    receiver = accounts[3]
    operator = accounts[4]

    agent1.grantRole(agent1.AGENT_ROLE(), operator, {'from': accounts[0]})

    amount    = 100 * WEI
    netAmount =  90 * WEI
    fee       =  10 * WEI

    # Determine the FreedomWallet address from the owner address and the owner's instance id (salt)
    instance = 0
    walletAddress = factory.getAddress(owner, instance)

    # Transfer to the FreedomWallet address 
    sender.transfer(walletAddress, amount)
    # for later comparison since admin is also sender...
    admin_balance = admin.balance()

    # Owner sign a transaction that transfers netAmount+fee tokens to receiver/operator
    tx = dict(destination = agent1.address,
              value = amount,
              data = agent1.receive_it.encode_input(),
              nonce = 0, # should be the first time used
              executor = agent1.address,
              gasLimit = 1000000)

    # FreedomWallet owner signs the transaction for the operator to execute.
    signed = sign2(factory, owner, instance, chain.id, tx)

    # Operator broadcast signed transaction paying for gas on behalf of owner
    agent1.transfer(
        owner.address,
        instance,
        receiver,
        netAmount,
        signed.v, signed.r, signed.s,
        tx['destination'],
        tx['value'],
        tx['nonce'],
        tx['data'],
        tx['gasLimit'],
        {'from': operator, 'gasLimit': tx['gasLimit']})

    # Did the tokens arrive?
    #assert token.balanceOf(walletAddress) == 0
    assert receiver.balance() == INITIAL_BALANCE + netAmount
    assert operator.balance() == INITIAL_BALANCE
    assert admin.balance() == admin_balance + fee
