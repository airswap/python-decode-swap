################################################3
#
# python decode_order.py -node-url http://localhost:8545 --inputCode <long input string> --fromAddress <hexAddress> --verbose
# --node-url can be skipped if an environment variable NODE_RPC_ENDPOINT is found --network rinkeby
#
#
import argparse
from collections import namedtuple
import json
import os
from pprint import pprint
import time
from web3 import Web3

# Swap ABI to match address
with open(os.getcwd() + "/abi/Swap.txt", "r") as json_data:
    SWAP_ABI = json_data.read()

# PreSwap ABI to match address
with open(os.getcwd() + "/abi/PreSwapChecker.txt", "r") as json_data:
    PRESWAP_ABI = json_data.read()

# Wrapper ABI to match address
with open(os.getcwd() + "/abi/Wrapper.txt", "r") as json_data:
    WRAPPER_ABI = json_data.read()

PRESWAP = {
    "rinkeby": "0x062CbA74439aFfD967ef981B6177232791698C7B"
}

SWAP_CONTRACT = {
    "mainnet": "0x4572f2554421Bd64Bef1c22c8a81840E8D496BeA",
    "rinkeby": "0x2e7373D70732E0F37F4166D8FD9dBC89DD5BC476"
}

WRAPPER = {
    "mainnet": "0x28de5C5f56B6216441eE114e832808D5B9d4A775",
    "rinkeby": "0x8C80e2c9C5244C2283Da85396dde6b7af4ebaA31"
}

# General erc20 abi
with open(os.getcwd() + "/abi/Token.json", "r") as json_data:
    TOKEN_ABI = json.loads(json_data.read())["abi"]

if "NODE_RPC_ENDPOINT" in os.environ:
    NODE_RPC_ENDPOINT = os.environ["NODE_RPC_ENDPOINT"]

def get_balance(tokenAddress, maker_address, network, blockNumber):
    try:
        web3_instance = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))
        withdrawer = SWAP_CONTRACT[network]
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


def get_allowance(tokenAddress, maker_address, network, blockNumber):
    """
    get_allowance: determine how much allowance does exchange have\

    """
    try:
        web3_instance = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))
        withdrawer = SWAP_CONTRACT[network]
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


def check_nonce(makerAddress, network, nonce, blockNumber):
    """
    check_nonce: determine nonce in order is valid

    """
    try:
        web3_instance = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))
        contract = web3_instance.eth.contract(
            address=Web3.toChecksumAddress(SWAP_CONTRACT[network]), abi=SWAP_ABI
        )
        status = int.from_bytes(
            contract.functions.signerNonceStatus(makerAddress, nonce).call(
                block_identifier=blockNumber
            ),
            "big",
        )
        minNonce = contract.functions.signerMinimumNonce(makerAddress).call(
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


def check_expiry(makerAddress, network, expiry, blockNumber):
    """
    check_expiry: determine nonce in order is valid

    """
    try:
        web3_instance = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))
        contract = web3_instance.eth.contract(
            address=Web3.toChecksumAddress(SWAP_CONTRACT[network]), abi=SWAP_ABI
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


def call_preswap_wrapper_checker(order, fromAddress, network):
    """
    check_expiry: determine nonce in order is valid

    """
    try:
        web3_instance = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))
        contract = web3_instance.eth.contract(
            address=Web3.toChecksumAddress(PRESWAP[network]), abi=PRESWAP_ABI
        )
        status = contract.functions.checkSwapWrapper(order, fromAddress, WRAPPER[network]).call()
        errorArray = []
        if status[0] > 0:
            print("PreSwap Wrapper Errors Found")
            for i in range(status[0]):
                errorArray.append((status[1][i]).decode("utf-8").replace('\x00', ''))
        else:
            print("PreSwap Wrapper  No Errors")
        return errorArray

    except Exception as e:
        print(e)


def call_preswap_checker(order, network):
    """
    check_expiry: determine nonce in order is valid

    """
    try:
        web3_instance = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))
        contract = web3_instance.eth.contract(
            address=Web3.toChecksumAddress(PRESWAP[network]), abi=PRESWAP_ABI
        )
        status = contract.functions.checkSwapSwap(order, False).call()
        errorArray = []
        if status[0] > 0:
            print("PreSwap Errors Found")
            for i in range(status[0]):
                errorArray.append((status[1][i]).decode("utf-8").replace('\x00', ''))
        else:
            print("PreSwap No Errors")
        return errorArray

    except Exception as e:
        print(e)
        return ""


def inputOrderCheck(trans, fromAddress, blockNumber, network, verbose):
    contract = w3.eth.contract(abi=WRAPPER_ABI)
    Party = namedtuple("Party", "kind wallet token amount id")
    Signature = namedtuple("Signature", "signatory validator version v r s ")
    parsedOrder = contract.decode_function_input(trans)[1]['order']
    (
        nonce,
        expiry,
        signerParty,
        senderParty,
        affiliateParty,
        signature,
    ) = parsedOrder

    signerParty = Party(*signerParty)
    senderParty = Party(*senderParty)
    affiliateParty = Party(*affiliateParty)

    preSwapChecker = True
    if preSwapChecker:
        wrapperError = call_preswap_wrapper_checker(parsedOrder, fromAddress, network)
        print(wrapperError)
        return

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

    nonceMessages = check_nonce(signerParty.wallet, network, nonce, blockNumber)
    print(nonceMessages)

    # check_expiry
    curtime = int(time.time())
    if int(time.time()) > expiry:
        print("Order has expired")
        if verbose:
            print(f"Order expired with times: {curtime} > {expiry} expired")
    # Signer Party checks
    signer_balance = get_balance(signerParty.token, signerParty.wallet, network, blockNumber)
    signer_allowance = get_allowance(signerParty.token, signerParty.wallet, network, blockNumber)

    # Check signer party balance is less than what they're sending
    signer_balance_check = signerParty.amount <= signer_balance
    signer_allowance_check = signerParty.amount <= signer_allowance

    if not signer_balance_check:
        print("Signer Balance is insufficient")
        if verbose:
            print(
                f"Current Balance {signer_balance} and requested balance {signerParty.amount} diff {signerParty.amount - signer_balance}"
            )
    if not signer_allowance_check:
        print("Signer Allowance is insufficient")
        if verbose:
            print(
                f"Current Allowance {signer_allowance} and requested balance {signerParty.amount} diff {signerParty.amount - signer_allowance}"
            )
    # Sender Party checks
    sender_balance = get_balance(senderParty.token, senderPartyWallet, network, blockNumber)
    sender_allowance = get_allowance(senderParty.token, senderPartyWallet, network, blockNumber)

    # Check sender party balance is less than what they're sending
    sender_balance_check = senderParty.amount <= sender_balance
    sender_allowance_check = senderParty.amount <= sender_allowance

    if verbose:
        print("SIGNER PARTY")
        print(f"Token balance {sender_balance}")
        print(f"Token allowance {sender_allowance}")
        print(f"Param to send {senderParty.amount}")
        print("SENDER PARTY")
        print(f"Token balance {signer_balance}")
        print(f"Token allowance {signer_allowance}")
        print(f"Param to send {signerParty.amount}")

    # Balance and Allowance Checks
    if not sender_balance_check:
        print("Sender Balance is insufficient")
        if verbose:
            print(
                f"Current Balance {sender_balance} and requested balance {senderParty.amount} diff {senderParty.amount - sender_balance}"
            )
    if not sender_allowance_check:
        print("Sender Allowance is insufficient")
        if verbose:
            print(
                f"Current Allowance {sender_allowance} and requested balance {senderParty.amount} diff {senderParty.amount - sender_allowance}"
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
        "--network",
        default="rinkeby",
        action="store",
        help="Network by name either rinkeby (4) or mainnet (1)",
    )
    parser.add_argument(
        "--verbose",
        default=False,
        action="store_true",
        help="Will output a more verbose output",
    )

    parser.add_argument(
        "--wrapper",
        default=False,
        action="store_true",
        help="Indicate whether a wrapper contract was used",
    )

    args = parser.parse_args()
    print(f"USING SWAP ADDRESS {SWAP_CONTRACT[args.network]}")
    if args.nodeUrl is not None:
        NODE_RPC_ENDPOINT = args.nodeUrl

    w3 = Web3(Web3.HTTPProvider(NODE_RPC_ENDPOINT))
    if args.wrapper:
        # do some wrappery checkes
        inputWrapperCheck(args.inputCode, args.fromAddress)
    inputOrderCheck(args.inputCode, Web3.toChecksumAddress(args.fromAddress), args.blockNumber, args.network, args.verbose)
