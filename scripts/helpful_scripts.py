from brownie import accounts, network, config, MockV3Aggregator, VRFCoordinatorMock, LinkToken, Contract, interface
from web3 import Web3

DECIMALS = 8
STARTING_PRICE = 400000000000
LOCAL_BLOCKCHAIN_ENV = ["development", "ganache-local"]
FORKED_LOCAL_ENV = ["mainnet-fork", "mainnet-fork-dev"]

def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)

    if(network.show_active() in LOCAL_BLOCKCHAIN_ENV) \
        or network.show_active() in FORKED_LOCAL_ENV : 
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])

def deploy_mocks(decimals=DECIMALS, initial_value=STARTING_PRICE):
    if len(MockV3Aggregator) <= 0:
            MockV3Aggregator.deploy(
                decimals, 
                initial_value, 
                {"from" : get_account()})
    link_token = LinkToken.deploy({"from" : get_account()})
    VRFCoordinatorMock.deploy(link_token, {"from" : get_account()})

contract_to_mock = {
    "eth_usd_price_feed" : MockV3Aggregator,
    "vrf_coordinator" : VRFCoordinatorMock,
    "link_token" : LinkToken
    }

def get_contract(contract_name):
    """
    grab the contract address from the brownie config
    otherwise deploy the mock version of the contract and return the contract to caller

    Args:
        contract_name (string)
    
    Returns:
        brownie.
    """

    contract_type = contract_to_mock[contract_name]

    if network.show_active() in LOCAL_BLOCKCHAIN_ENV:
        if len(contract_type) <= 0:
                deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)

    return contract

def fund_with_link(contract_address, account=None, link_token=None, amount=100000000000000000):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from" : account})
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.transfer(contract_address, amount, {"from" : amount})
    tx.wait(1)
    print("Link token transferred")
    return tx
