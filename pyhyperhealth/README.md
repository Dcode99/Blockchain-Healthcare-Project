# api.py
requires the user's API key to be included in each command

# adminapi.py
does not ask for a key, it uses an example admin key. This is not going to be available in any real environment, but allows quick testing in development.

# main.py
does not allow APIs, it uses a python menu to ask the user for their commands.

# keygen.py
will be used by a peer who wishes to connect to generate a random public and private key. The public key will be given to the admin to add the peer to the network.
