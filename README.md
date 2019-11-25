## decode_input script

### To setup:

Make sure you are using pythoh 3.6+

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

#### It is possible to have the nodeUrl already setup as an environment variable called NODE_RPC_ENDPOINT so that you do not need to input every time.

```
NODE_RPC_ENDPOINT='http://localhost:8545' python decode_order.py 
--inputCode <> --fromAddress <> --verbose
```

## Usage

```
python decode_order.py 
--node-url http://localhost:8545 
--inputCode <long input string> 
--fromAddress <hexAddress> --verbose
--node-url can be skipped if an environment variable NODE_RPC_ENDPOINT is found
```

```bash
 python decode_order.py --help
USING SWAP ADDRESS 0xD9EEf94131305538cD601aeE42e57C554c1c1C92
usage: decode_order.py [-h] [--nodeUrl n] [--inputCode INPUTCODE]
                       [--fromAddress FROMADDRESS] [--verbose]

Debug a failed transaction via inputCode.

optional arguments:
  -h, --help            show this help message and exit
  --nodeUrl n           Ethereum node URL: http://localhost:8545
  --inputCode INPUTCODE
                        Input byte code as a string
  --fromAddress FROMADDRESS
                        Sending address of the transaction
  --verbose             Will output a more verbose output
```
