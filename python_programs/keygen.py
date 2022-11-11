# This is an example script to generate new keys in Hyperledger Iroha
# From their documentation here: 
# https://iroha.readthedocs.io/en/main/getting_started/python-guide.html#creating-your-own-key-pairs-with-python-library
from iroha import IrohaCrypto

# these first two lines are enough to create the keys
private_key = IrohaCrypto.private_key()
public_key = IrohaCrypto.derive_public_key(private_key)

# the rest of the code writes them into the file
with open('keypair.priv', 'wb') as f:
    f.write(private_key)

with open('keypair.pub', 'wb') as f:
    f.write(public_key)
