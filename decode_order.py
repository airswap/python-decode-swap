################################################3
#
# python decode_order.py -node-url http://localhost:8545 --inputCode <long input string> --fromAddress <hexAddress> --verbose
# --node-url can be skipped if an environment variable NODE_RPC_ENDPOINT is found
#
# SWAP ADDRESS for this script : 0xd9eef94131305538cd601aee42e57c554c1c1c92
#
import argparse
from collections import namedtuple
import json
import os
from pprint import pprint
import time
from web3 import Web3

# Swap ABI to match address
with open(os.getcwd() + "/abi/Swap.json", "r") as json_data:
    SWAP_ABI = json.loads(json_data.read())["abi"]

# General erc20 abi
with open(os.getcwd() + "/abi/Token.json", "r") as json_data:
    TOKEN_ABI = json.loads(json_data.read())["abi"]

if "NODE_RPC_ENDPOINT" in os.environ:
    NODE_RPC_ENDPOINT = os.environ["NODE_RPC_ENDPOINT"]

EXCHANGE_CONTRACT = Web3.toChecksumAddress("0xd9eef94131305538cd601aee42e57c554c1c1c92")


def get_balance(tokenAddress, maker_address, blockNumber):
    try:
        web3_instance = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))
        withdrawer = EXCHANGE_CONTRACT
        tokenAbi = TOKEN_ABI
        contract = web3_instance.eth.contract(
            address=Web3.toChecksumAddress(tokenAddress), abi=tokenAbi
        )
        return int(
            contract.functions.balanceOf(maker_address).call(
                block_identifier=blockNumber
            )
        )
    except Exception as e:
        print(e)
        return 0


def get_allowance(tokenAddress, maker_address, blockNumber):
    """
    get_allowance: determine how much allowance does exchange have\

    """
    try:
        web3_instance = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))
        withdrawer = EXCHANGE_CONTRACT
        tokenAbi = TOKEN_ABI
        contract = web3_instance.eth.contract(
            address=Web3.toChecksumAddress(tokenAddress), abi=tokenAbi,
        )
        return int(
            contract.functions.allowance(maker_address, withdrawer).call(
                block_identifier=blockNumber
            )
        )
    except Exception as e:
        print(e)
        return 0


def check_nonce(makerAddress, nonce, blockNumber):
    """
    check_nonce: determine nonce in order is valid

    """
    try:
        web3_instance = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))
        contract = web3_instance.eth.contract(
            address=Web3.toChecksumAddress(EXCHANGE_CONTRACT), abi=SWAP_ABI
        )
        status = int.from_bytes(
            contract.functions.makerOrderStatus(makerAddress, nonce).call(
                block_identifier=blockNumber
            ),
            "big",
        )
        minNonce = contract.functions.makerMinimumNonce(makerAddress).call(
            block_identifier=blockNumber
        )
        returnMsg = ""
        if status != 0:
            returnMsg += "\nNonce has already been used"
        if nonce < minNonce:
            returnMsg += (
                f"\nNonce is below the min nonce threshold {minNonce} for signer"
            )
        return returnMsg
    except Exception as e:
        print(e)
        return ""


def check_expiry(makerAddress, expiry, blockNumber):
    """
    check_expiry: determine nonce in order is valid

    """
    try:
        web3_instance = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))
        contract = web3_instance.eth.contract(
            address=Web3.toChecksumAddress(EXCHANGE_CONTRACT), abi=SWAP_ABI
        )
        status = int.from_bytes(
            contract.functions.makerOrderStatus(makerAddress, nonce).call(
                block_identifier=blockNumber
            ),
            "big",
        )
        minNonce = contract.functions.makerMinimumNonce(makerAddress).call(
            block_identifier=blockNumber
        )
        returnMsg = ""
        if status != 0:
            returnMsg += "\nNonce has already been used"
        if nonce < minNonce:
            returnMsg += (
                f"\nNonce is below the min nonce threshold {minNonce} for signer"
            )
        return returnMsg
    except Exception as e:
        print(e)
        return ""


def inputOrderCheck(trans, fromAddress, blockNumber, verbose):
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

    nonceMessages = check_nonce(signerParty.wallet, nonce, blockNumber)
    print(nonceMessages)

    # check_expiry
    curtime = int(time.time())
    if int(time.time()) > expiry:
        print("Order has expired")
        if verbose:
            print(f"Order expired with times: {curtime} > {expiry} expired")
    # Signer Party checks
    signer_balance = get_balance(signerParty.token, signerParty.wallet, blockNumber)
    signer_allowance = get_allowance(signerParty.token, signerParty.wallet, blockNumber)

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
    sender_balance = get_balance(senderParty.token, senderPartyWallet, blockNumber)
    sender_allowance = get_allowance(senderParty.token, senderPartyWallet, blockNumber)

    # Check sender party balance is less than what they're sending
    sender_balance_check = senderParty.param <= sender_balance
    sender_allowance_check = senderParty.param <= sender_allowance

    if verbose:
        print("SIGNER PARTY")
        print(f"Token balance {sender_balance}")
        print(f"Token allowance {sender_allowance}")
        print(f"Param to send {senderParty.param}")
        print("SENDER PARTY")
        print(f"Token balance {signer_balance}")
        print(f"Token allowance {signer_allowance}")
        print(f"Param to send {signerParty.param}")

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
        "--blockNumber",
        default="latest",
        action="store",
        help="Block number to fetch state from (infura works) not sure about light nodes",
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

    inputOrderCheck(args.inputCode, args.fromAddress, args.blockNumber, args.verbose)
