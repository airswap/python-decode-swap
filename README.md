## decode_order script

This python script will help debug transactions from the AirSwap Protocol. The script serves as a wrapper around the Validator contract. More information can be found at the (AirSwap Docs)[https://docs.airswap.io/reference/validator].

### To setup:

Make sure you are using Python 3.6+

```bash
virtualenv venv --python=python3.6
```
```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

```bash
python decode_order.py ARGS
```
samples are provided below

#### It is possible to have the nodeUrl already setup as an environment variable called NODE_RPC_ENDPOINT so that you do not need to input every time.

```
NODE_RPC_ENDPOINT='http://localhost:8545' python decode_order.py 
--inputData <> --fromAddress <> --delegateAddress <> --blockNumber <> --verbose
```

```
NODE_RPC_ENDPOINT='http://localhost:8545' python decode_order.py 
--trxnHash <> --blockNumber <> --verbose
```

## Usage

Use with transactionHash
```
python decode_order.py 
--nodeUrl http://localhost:8545 
--trxnHash <0x> 
--verbose
--blockNumber <>
--network <>
```

Use with inputData from transaction
```
python decode_order.py 
--nodeUrl http://localhost:8545 
--inputData <long input string> 
--fromAddress <hexAddress> --verbose
--blockNumber <>
--network <>
--delegateAddress ""
```

node-url can be skipped if an environment variable NODE_RPC_ENDPOINT is found
blockNumber if skipped will default to latest 

```bash
usage: decode_order.py [-h] [--nodeUrl URL] [--inputData INPUTDATA]
                       [--trxnHash TRXNHASH] [--fromAddress FROMADDRESS]
                       [--blockNumber BLOCKNUMBER] [--network NETWORK]
                       [--delegateAddress DELEGATEADDRESS] [--verbose]

Debug a failed transaction via inputData.

optional arguments:
  -h, --help            show this help message and exit
  --nodeUrl URL         Ethereum node URL: http://localhost:8545
  --inputData INPUTDATA
                        Input byte code as a string
  --trxnHash TRXNHASH   Transaction hash of failed transaction
  --fromAddress FROMADDRESS
                        Sending address of the transaction
                        Defaults to ZERO_ADDRESS
  --blockNumber BLOCKNUMBER
                        Block number to fetch state from (infura works) not
                        sure about light nodes
                        Defaults to 'latest'
  --network NETWORK     Network by name either mainnet, rinkeby, goerli, or
                        kovan
                        Defaults to rinkeby
  --delegateAddress DELEGATEADDRESS
                        Indicate the delegate used in provideOrder
                        Defaults to ZERO_ADDRESS
  --verbose             Will output a more verbose output

```

## AirSwap Resources

- Docs → https://docs.airswap.io/
- Website → https://www.airswap.io/
- Blog → https://blog.airswap.io/
- Support → https://support.airswap.io/
