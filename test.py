from iroha import Iroha, IrohaCrypto, IrohaGrpc

iroha = Iroha('alice@test')
net = IrohaGrpc('127.0.0.1:50051')

alice_key = IrohaCrypto.private_key()
alice_tx = iroha.transaction(
    [iroha.command(
        'TransferAsset', 
        src_account_id='alice@test', 
        dest_account_id='bob@test', 
        asset_id='bitcoin#test',
        description='test',
        amount='1'
    )]
)
IrohaCrypto.sign_transaction(alice_tx, alice_key)
net.send_tx(alice_tx)

for status in net.tx_status_stream(alice_tx):
    print(status)
