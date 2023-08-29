from web3 import Web3


# Procedure to send the transaction on GOERLI TEST NET
def sendTransaction(message):
    w3 = Web3(
        Web3.HTTPProvider(
            "https://goerli.infura.io/v3/ecadd76dd30247b4bf4fd9238723bba2"
        )
    )
    address = "0x3eDb1E13ae5D632a555128E57052B7662106DEa6"
    privateKey = os.getenv("privateKey")
    nonce = w3.eth.get_transaction_count(address, "pending")
    # w3.eth.get_transaction_count(address)
    gasPrice = w3.eth.gas_price
    value = w3.to_wei(0, "ether")
    signedTx = w3.eth.account.sign_transaction(
        dict(
            nonce=nonce,
            gasPrice=gasPrice,
            gas=100000,
            to="0x0000000000000000000000000000000000000000",
            value=value,
            data=message.encode("utf-8"),
        ),
        privateKey,
    )

    tx = w3.eth.send_raw_transaction(signedTx.rawTransaction)
    txId = w3.to_hex(tx)
    return txId
