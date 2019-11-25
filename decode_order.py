################################################3
#
# python decode_order.py -node-url http://localhost:8545 --inputCode <long input string> --fromAddress <hexAddress> --verbose
# --node-url can be skipped if an environment variable NODE_RPC_ENDPOINT is found
#
# SWAP ADDRESS for this script : 0xd9eef94131305538cd601aee42e57c554c1c1c92
#

import requests
from collections import namedtuple
import json
from web3 import Web3
import os
import sys
import argparse
from pprint import pprint

# Swap ABI to match address
with open(os.getcwd() + "/abi/Swap.json", "r") as json_data:
    SWAP_ABI = json.loads(json_data.read())["abi"]

# General erc20 abi
with open(os.getcwd() + "/abi/Token.json", "r") as json_data:
    TOKEN_ABI = json.loads(json_data.read())["abi"]

if "NODE_RPC_ENDPOINT" in os.environ:
    NODE_RPC_ENDPOINT = os.environ["NODE_RPC_ENDPOINT"]

EXCHANGE_CONTRACT = Web3.toChecksumAddress("0xd9eef94131305538cd601aee42e57c554c1c1c92")

def get_balance(tokenAddress, maker_address):
    try:
        web3_instance = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))
        withdrawer = EXCHANGE_CONTRACT
        tokenAbi = TOKEN_ABI
        contract = web3_instance.eth.contract(
            address=Web3.toChecksumAddress(tokenAddress), abi=tokenAbi
        )
        return int(contract.functions.balanceOf(maker_address).call())
    except Exception as e:
        return 0


def get_allowance(tokenAddress, maker_address):
    """
    get_allowance: determine how much allowance does exchange have\

    """
    try:
        web3_instance = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))
        withdrawer = EXCHANGE_CONTRACT
        tokenAbi = TOKEN_ABI
        contract = web3_instance.eth.contract(
            address=Web3.toChecksumAddress(tokenAddress), abi=tokenAbi
        )
        return int(contract.functions.allowance(maker_address, withdrawer).call())
    except Exception as e:
        return 0

def inputOrderCheck(trans, fromAddress, verbose):
    contract = w3.eth.contract(abi=SWAP_ABI)
    Party = namedtuple("Party", "wallet token param kind")
    Signature = namedtuple("Signature", "signer v r s version")
    (
        nonce,
        expiry,
        signerParty,
        senderParty,
        affiliateParty,
        signature,
    ) = contract.decode_function_input(trans)[1]["_order"]

    signerParty = Party(*signerParty)
    senderParty = Party(*senderParty)

    # if senderParty is not used, use the from address instead
    if senderParty.wallet == "0x0000000000000000000000000000000000000000":
        senderPartyWallet = fromAddress
    else:
        senderPartyWallet = senderParty.wallet

    if verbose:
        print("SIGNER PARTY")
        pprint(dict(signerParty._asdict()), indent=4)
        print("SENDER PARTY")
        pprint(dict(senderParty._asdict()), indent=4)
    # Signer Party checks
    signer_balance = get_balance(signerParty.token, signerParty.wallet)
    signer_allowance = get_allowance(signerParty.token, signerParty.wallet)

    # Check signer party balance is less than what they're sending
    signer_balance_check = signerParty.param <= signer_balance
    signer_allowance_check = signerParty.param <= signer_allowance

    if not signer_balance_check:
        print("Signer Balance is insufficient")
        if verbose:
            print(
                f"Current Balance {signer_balance} and requested balance {signerParty.param} diff {signerParty.param - signer_balance}"
            )
    if not signer_allowance_check:
        print("Signer Allowance is insufficient")
        if verbose:
            print(
                f"Current Allowance {signer_allowance} and requested balance {signerParty.param} diff {signerParty.param - signer_allowance}"
            )
    # Sender Party checks
    sender_balance = get_balance(senderParty.token, senderPartyWallet)
    sender_allowance = get_allowance(senderParty.token, senderPartyWallet)

    # Check sender party balance is less than what they're sending
    sender_balance_check = senderParty.param <= sender_balance
    sender_allowance_check = senderParty.param <= sender_allowance

    # Balance and Allowance Checks
    if not sender_balance_check:
        print("Sender Balance is insufficient")
        if verbose:
            print(
                f"Current Balance {sender_balance} and requested balance {senderParty.param} diff {senderParty.param - sender_balance}"
            )
    if not sender_allowance_check:
        print("Sender Allowance is insufficient")
        if verbose:
            print(
                f"Current Allowance {sender_allowance} and requested balance {senderParty.param} diff {senderParty.param - sender_allowance}"
            )


if __name__ == "__main__":
    global w3

    parser = argparse.ArgumentParser(
        description="Debug a failed transaction via inputCode."
    )
    parser.add_argument(
        "--nodeUrl",
        metavar="URL",
        type=str,
        help="Ethereum node URL: http://localhost:8545",
    )
    parser.add_argument(
        "--inputCode", type=str, action="store", help="Input byte code as a string"
    )
    parser.add_argument(
        "--fromAddress",
        type=str,
        action="store",
        help="Sending address of the transaction",
    )
    parser.add_argument(
        "--verbose",
        default=False,
        action="store_true",
        help="Will output a more verbose output",
    )
    print(f"USING SWAP ADDRESS {EXCHANGE_CONTRACT}")
    args = parser.parse_args()

    if args.nodeUrl is not None:
        NODE_RPC_ENDPOINT = args.nodeUrl

    w3 = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))

    inputOrderCheck(args.inputCode, args.fromAddress, args.verbose)
