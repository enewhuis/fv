from brownie import web3, reverts
from conftest import sign2

def test_agent_transfer(accounts, factory, token, FreedomWallet, agent1, chain):
    admin = accounts[0]
    sender = accounts[0]
    owner = accounts.add()
    receiver = accounts[1]
    operator = accounts[2]

    agent1.grantRole(agent1.AGENT_ROLE(), operator, {'from': accounts[0]})

    amount = 2e6 #100e18
    netAmount = 1e6 #90e18 # 10e18 fee
    fee = amount - netAmount

    # Sender has some tokens
    token.mint(sender, amount)

    # Determine the FreedomWallet address from the owner address and the owner's instance id (salt)
    instance = 0
    walletAddress = factory.getAddress(owner, instance)

    # Transfer tokens to the FreedomWallet address 
    token.transfer(walletAddress, amount, {'from': sender})

    # for later comparison since admin is also sender...
    admin_balance = token.balanceOf(admin)

    # Owner sign a transaction that transfers netAmount+fee tokens to receiver/operator
    tx = dict(destination = token.address,
              value = 0,
              data = token.transfer.encode_input(agent1.address, amount),
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
    assert token.balanceOf(walletAddress) == 0
    assert token.balanceOf(receiver) == netAmount
    assert token.balanceOf(operator) == 0
    assert token.balanceOf(admin) == admin_balance + fee
