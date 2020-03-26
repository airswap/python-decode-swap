#!/usr/bin/env python
# python decode_order.py -node-url http://localhost:8545 --inputCode <long input string> --fromAddress <hexAddress> --verbose
# --node-url can be skipped if an environment variable NODE_RPC_ENDPOINT is found --network <networkName>


import argparse
from collections import namedtuple
import os
from pprint import pprint
from web3 import Web3
import sys
import json

# Swap ABI to match address
with open(os.getcwd() + "/abi/Swap.txt", "r") as json_data:
    SWAP_ABI = json_data.read()

# Validator ABI to match address
with open(os.getcwd() + "/abi/Validator.txt", "r") as json_data:
    VALIDATOR_ABI = json_data.read()

# Wrapper ABI to match address
with open(os.getcwd() + "/abi/Wrapper.txt", "r") as json_data:
    WRAPPER_ABI = json_data.read()

# Delegate ABI to match address
with open(os.getcwd() + "/abi/Delegate.txt", "r") as json_data:
    DELEGATE_ABI = json_data.read()

# Validator Reasons from airswap-protocols repo
with open(os.getcwd() + "/reasons/validatorReasons.json", "r") as json_data:
    REASONS = json.loads(json_data.read())

NETWORKS = {"mainnet": "1", "rinkeby": "4", "goerli": "5", "kovan": "42"}

VALIDATOR = {
    "1": "0x0c8d551c52206F1C16043F1dCD9B7bc6A45fc02C",
    "4": "0x2D8849EAaB159d20Abf10D4a80c97281A12448CC",
    "5": "0xE5E7116AB49666e9791f53aeD4f5B7207770879D",
    "42": "0x5EB4EfDC20fFF121dDe66BCbf5987786B3587f01",
}

SWAP_CONTRACT = {
    "1": "0x4572f2554421Bd64Bef1c22c8a81840E8D496BeA",
    "4": "0x2e7373D70732E0F37F4166D8FD9dBC89DD5BC476",
    "5": "0x18C90516a38Dd7B779A8f6C19FA698F0F4Efc7FC",
    "42": "0x79fb4604f2D7bD558Cda0DFADb7d61D98b28CA9f",
}

WRAPPER = {
    "1": "0x28de5C5f56B6216441eE114e832808D5B9d4A775",
    "4": "0x8C80e2c9C5244C2283Da85396dde6b7af4ebaA31",
    "5": "0x982A916882Fb26e9408993b9d03247d44Fb4E8D4",
    "42": "0xE5E7116AB49666e9791f53aeD4f5B7207770879D",
}

ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"

if "NODE_RPC_ENDPOINT" in os.environ:
    NODE_RPC_ENDPOINT = os.environ["NODE_RPC_ENDPOINT"]


def checkWrappedSwap(validatorContract, order, fromAddress, network):
    """
    checkWrappedSwap: calling Validator.checkWrapperSwap
    """
    try:
        status = validatorContract.functions.checkWrappedSwap(
            order, fromAddress, WRAPPER[network]
        ).call()
        errorArray = []
        if status[0] > 0:
            print("Validator Errors Found: Wrapper.swap")
            for i in range(status[0]):
                errorArray.append((status[1][i]).decode("utf-8").replace("\x00", ""))
        else:
            print("Validator No Errors: Wrapper.swap")
        return errorArray

    except Exception as e:
        print(e)
        return []


def checkWrappedDelegate(validatorContract, order, delegateAddress, network):
    """checkWrappedDelegate: calling Validator.checkWrapperSwap."""
    try:
        status = validatorContract.functions.checkWrappedDelegate(
            order, delegateAddress, WRAPPER[network]
        ).call()
        errorArray = []
        if status[0] > 0:
            print("Validator Errors Found: Wrapper.provideDelegateOrder")
            for i in range(status[0]):
                errorArray.append((status[1][i]).decode("utf-8").replace("\x00", ""))
        else:
            print("Validator No Errors: Wrapper.provideDelegateOrder")
        return errorArray

    except Exception as e:
        print(e)
        return []


def checkSwap(validatorContract, order):
    """checkSwap: calling Validator.checkSwap."""
    try:
        status = validatorContract.functions.checkSwap(order).call()
        errorArray = []
        if status[0] > 0:
            print("Validator Errors Found: Swap.swap")
            for i in range(status[0]):
                errorArray.append((status[1][i]).decode("utf-8").replace("\x00", ""))
        else:
            print("Validator No Errors: Swap.swap")
        return errorArray

    except Exception as e:
        print(e)
        return []


def checkDelegate(validatorContract, order, delegateAddress):
    """checkDelegate: calling Validator.checkDelegate."""
    try:
        status = validatorContract.functions.checkDelegate(
            order, Web3.toChecksumAddress(delegateAddress)
        ).call()
        errorArray = []
        if status[0] > 0:
            print("Validator Errors Found: Delegate.provideOrder")
            for i in range(status[0]):
                errorArray.append((status[1][i]).decode("utf-8").replace("\x00", ""))
        else:
            print("Validator No Errors: Delegate.provideOrder")
        return errorArray

    except Exception as e:
        print(e)
        return []


def fetchTransactionFromHash(
    validatorContract, trxnHash, blockNumber, network, verbose
):
    """fetchTransactionFromHash: fetches the transaction details from hash."""
    global w3

    fetchedTrxn = w3.eth.getTransaction(trxnHash)
    trans = fetchedTrxn["input"]
    fromAddress = fetchedTrxn["from"]
    toAddress = fetchedTrxn["to"]
    wrapper = False
    delegate = False
    delegateAddress = None
    if toAddress == WRAPPER[network]:
        contract = w3.eth.contract(abi=WRAPPER_ABI)
        wrapper = True
    elif toAddress == SWAP_CONTRACT[network]:
        contract = w3.eth.contract(abi=SWAP_ABI)
    else:
        contract = w3.eth.contract(abi=DELEGATE_ABI)
        delegateAddress = toAddress

    try:
        parsedOrder = contract.decode_function_input(trans)
        methodName = parsedOrder[0].function_identifier
        if methodName == "provideDelegateOrder":
            delegateAddress = parsedOrder[1]["delegate"]
    except Exception as e:
        print("Failed to decode transaction with error")
        print(e)
        sys.exit(1)

    return inputOrderCheck(
        validatorContract,
        parsedOrder,
        fromAddress,
        blockNumber,
        network,
        wrapper,
        delegate,
        delegateAddress,
        verbose,
    )


def parsingRawInputData(
    validatorContract,
    trans,
    fromAddress,
    blockNumber,
    network,
    delegateAddress,
    verbose,
):
    """parsingRawInputData: parses raw inputa data and matches it to a known AirSwap contract."""
    global w3
    try:
        contract = w3.eth.contract(abi=DELEGATE_ABI)
        parsedOrder = contract.decode_function_input(trans)
        methodName = parsedOrder[0].function_identifier
        wrapper = False
        delegate = True
    except Exception as e:
        # no-op
        delegate = False

    try:
        contract = w3.eth.contract(abi=WRAPPER_ABI)
        parsedOrder = contract.decode_function_input(trans)
        methodName = parsedOrder[0]
        wrapper = True
        if methodName == "provideDelegateOrder":
            delegate = True
        else:
            delegate = False
    except Exception as e:
        # no-op
        wrapper = False

    if not wrapper and not delegate:
        try:
            contract = w3.eth.contract(abi=SWAP_ABI)
            parsedOrder = contract.decode_function_input(trans)
            methodName = parsedOrder[0]
            delegate = False
            wrapper = False
        except Exception as e:
            # no-op
            print("Failed to decode data as Delegate, Wrapper, or Swap transactions")
            sys.exit(1)

    return inputOrderCheck(
        validatorContract,
        parsedOrder,
        fromAddress,
        blockNumber,
        network,
        wrapper,
        delegate,
        delegateAddress,
        verbose,
    )


def inputOrderCheck(
    validatorContract,
    parsedOrder,
    fromAddress,
    blockNumber,
    network,
    wrapper,
    delegate,
    delegateAddress=None,
    verbose=True,
):
    """inputOrderCheck: runs a Validator check and outputs errors to std.out"""
    global w3
    method = (parsedOrder[0]).function_identifier
    parsedOrder = parsedOrder[1]["order"]
    (nonce, expiry, signerParty, senderParty, affiliateParty, signature,) = parsedOrder

    Party = namedtuple("Party", "kind wallet token amount id")
    Signature = namedtuple("Signature", "signatory validator version v r s ")
    signerParty = Party(*signerParty)
    senderParty = Party(*senderParty)
    affiliateParty = Party(*affiliateParty)
    signature = Signature(*signature)
    if verbose:
        print("SIGNER PARTY")
        pprint(dict(signerParty._asdict()), indent=4)
        print("SENDER PARTY")
        pprint(dict(senderParty._asdict()), indent=4)
        print("AFFILIATE PARTY")
        pprint(dict(affiliateParty._asdict()), indent=4)
        print("SIGNATURE")
        pprint(dict(signature._asdict()), indent=4)
        print("R: " + w3.toHex(signature.r))
        print("S: " + w3.toHex(signature.s))
        print()

    error = None

    if method == "provideOrder":
        error = checkDelegate(validatorContract, parsedOrder, delegateAddress)
    elif method == "provideDelegateOrder":
        error = checkWrappedDelegate(
            validatorContract, parsedOrder, delegateAddress, network
        )
    elif wrapper and method == "swap":
        error = checkWrappedSwap(validatorContract, parsedOrder, fromAddress, network)
    elif method == "swap":
        error = checkSwap(validatorContract, parsedOrder)
    else:
        print("Unrecognized method " + method)
        sys.exit(1)

    if verbose:
        print([REASONS[e] for e in error])
    else:
        print(error)


if __name__ == "__main__":
    global w3

    parser = argparse.ArgumentParser(
        description="Debug a failed transaction via inputData."
    )
    parser.add_argument(
        "--nodeUrl",
        metavar="URL",
        type=str,
        help="Ethereum node URL: http://localhost:8545",
    )
    parser.add_argument(
        "--inputData",
        type=str,
        default=None,
        action="store",
        help="Input byte code as a string",
    )
    parser.add_argument(
        "--trxnHash",
        type=str,
        default=None,
        action="store",
        help="Transaction hash of failed transaction",
    )
    parser.add_argument(
        "--fromAddress",
        type=str,
        default=ZERO_ADDRESS,
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
        "--network",
        default="rinkeby",
        action="store",
        help="Network by name either mainnet, rinkeby, goerli, or kovan",
    )
    parser.add_argument(
        "--delegateAddress",
        default=ZERO_ADDRESS,
        action="store",
        help="Indicate the delegate used in provideOrder",
    )
    parser.add_argument(
        "--verbose",
        default=False,
        action="store_true",
        help="Will output a more verbose output",
    )

    args = parser.parse_args()
    if args.nodeUrl is not None:
        NODE_RPC_ENDPOINT = args.nodeUrl
    if args.inputData is None and args.trxnHash is None:
        print("--inputCode or --trxnHash must be provided. Exiting!")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))
    validatorContract = w3.eth.contract(
        address=Web3.toChecksumAddress(VALIDATOR[NETWORKS[args.network]]),
        abi=VALIDATOR_ABI,
    )
    if args.trxnHash is not None:
        fetchTransactionFromHash(
            validatorContract,
            args.trxnHash,
            args.blockNumber,
            NETWORKS[args.network],
            args.verbose,
        )
    else:
        parsingRawInputData(
            validatorContract,
            args.inputData,
            Web3.toChecksumAddress(args.fromAddress),
            args.blockNumber,
            NETWORKS[args.network],
            args.delegateAddress,
            args.verbose,
        )
