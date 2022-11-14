#!/usr/bin/env python3
#
# Copyright Soramitsu Co., Ltd. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#


# Here are Iroha dependencies.
# Python library generally consists of 3 parts:
# Iroha, IrohaCrypto and IrohaGrpc which we need to import:
import os
import binascii
from iroha import IrohaCrypto
from iroha import Iroha, IrohaGrpc
from iroha import primitive_pb2

# The following line is actually about the permissions
# you might be using for the transaction.
# You can find all the permissions here:
# https://iroha.readthedocs.io/en/main/develop/api/permissions.html
from iroha.primitive_pb2 import can_set_my_account_detail
import sys

if sys.version_info[0] < 3:
    raise Exception('Python 3 or a more recent version is required.')

# Here is the information about the environment and admin account information:

# Iroha peers
IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', '128.163.181.53')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
# IROHA_HOST_ADDR_2 = os.getenv('IROHA_HOST_ADDR', '128.163.181.54')
# IROHA_PORT_2 = os.getenv('IROHA_PORT', '50051')

ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'admin@test')
ADMIN_PRIVATE_KEY = os.getenv(
    'ADMIN_PRIVATE_KEY', 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70')
print(ADMIN_ACCOUNT_ID)

# Here we will create user keys
user_private_key = IrohaCrypto.private_key()
user_public_key = IrohaCrypto.derive_public_key(user_private_key)
# Creating the user Keys for this account
new_private_key = IrohaCrypto.private_key()
new_public_key = IrohaCrypto.derive_public_key(new_private_key)

# Creating admin keys for the domain
# admin_private_key = IrohaCrypto.private_key()
# admin_public_key = IrohaCrypto.derive_public_key(user_private_key)

# writing admin key to a file
# with open('admin@healthcare.priv', 'wb') as f:
# f.write(admin_private_key)

# with open('admin@healthcare.pub', 'wb') as f:
# f.write(admin_public_key)

iroha = Iroha(ADMIN_ACCOUNT_ID)

# Defining the nets for each node
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))
# net_2 = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR_2, IROHA_PORT_2))

def trace(func):
    """
    A decorator for tracing methods' begin/end execution points
    """

    def tracer(*args, **kwargs):
        name = func.__name__
        print('\tEntering "{}"'.format(name))
        result = func(*args, **kwargs)
        print('\tLeaving "{}"'.format(name))
        return result

    return tracer


# Defining the commands:
@trace
def send_transaction_and_print_status(transaction):
    hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
    print('Transaction hash = {}, creator = {}'.format(
        hex_hash, transaction.payload.reduced_payload.creator_account_id))
    net.send_tx(transaction)
    for status in net.tx_status_stream(transaction):
        print(status)


@trace
def send_2_transaction_and_print_status(transaction):
    hex_hash = binascii.hexlify(IrohaCrypto.hash(transaction))
    print('Transaction hash = {}, creator = {}'.format(
        hex_hash, transaction.payload.reduced_payload.creator_account_id))
    net.send_tx(transaction)
    for status in net.tx_status_stream(transaction):
        print(status)


# For example, below we define a transaction made of 2 commands:
# CreateDomain and CreateAsset.
# Each of Iroha commands has its own set of parameters and there are many commands.
# You can check out all of them here:
# https://iroha.readthedocs.io/en/main/develop/api/commands.html
@trace
def create_domain_and_asset():
    """
    Create domain 'domain' and asset 'coin#domain' with precision 2
    """
    commands = [
        iroha.command('CreateDomain', domain_id='domain', default_role='user'),
        iroha.command('CreateAsset', asset_name='coin',
                      domain_id='domain', precision=2)
    ]
    # And sign the transaction using the keys from earlier:
    tx = IrohaCrypto.sign_transaction(
        iroha.transaction(commands), ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)


# You can define queries
# (https://iroha.readthedocs.io/en/main/develop/api/queries.html)
# the same way.


@trace
def add_coin_to_admin():
    """
    Add 1000.00 units of 'coin#domain' to 'admin@test'
    """
    tx = iroha.transaction([
        iroha.command('AddAssetQuantity',
                      asset_id='coin#domain', amount='1000.00')
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)


@trace
def create_account_userone():
    """
    Create account 'userone@domain'
    """
    tx = iroha.transaction([
        iroha.command('CreateAccount', account_name='userone', domain_id='domain',
                      public_key=user_public_key)
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)
    print(tx)


@trace
def transfer_coin_from_admin_to_userone():
    """
    Transfer 2.00 'coin#domain' from 'admin@test' to 'userone@domain'
    """
    tx = iroha.transaction([
        iroha.command('TransferAsset', src_account_id='admin@test', dest_account_id='userone@domain',
                      asset_id='coin#domain', description='init top up', amount='2.00')
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)


@trace
def userone_grants_to_admin_set_account_detail_permission():
    """
    Make admin@test able to set detail to userone@domain
    """
    tx = iroha.transaction([
        iroha.command('GrantPermission', account_id='admin@test',
                      permission=can_set_my_account_detail)
    ], creator_account='userone@domain')
    IrohaCrypto.sign_transaction(tx, user_private_key)
    send_transaction_and_print_status(tx)


@trace
def set_age_to_userone():
    """
    Set age to userone@domain by admin@test
    """
    tx = iroha.transaction([
        iroha.command('SetAccountDetail',
                      account_id='userone@domain', key='age', value='18')
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)


@trace
def get_coin_info():
    """
    Get asset info for coin#domain
    :return:
    """
    query = iroha.query('GetAssetInfo', asset_id='coin#domain')
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)

    response = net.send_query(query)
    data = response.asset_response.asset
    print('Asset id = {}, precision = {}'.format(data.asset_id, data.precision))


@trace
def get_account_assets():
    """
    List all the assets of userone@domain
    """
    query = iroha.query('GetAccountAssets', account_id='userone@domain')
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)

    response = net.send_query(query)
    data = response.account_assets_response.account_assets
    for ast in data:
        print('Asset id = {}, balance = {}'.format(
            ast.asset_id, ast.balance))


@trace
def get_userone_details():
    """
    Get all the kv-storage entries for userone@domain
    """
    query = iroha.query('GetAccountDetail', account_id='userone@domain')
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)

    response = net.send_query(query)
    data = response.account_detail_response
    print('Account id = {}, details = {}'.format('userone@domain', data.detail))


### NEW COMMANDS ###
@trace
def get_account_details(acc_id, domain):
    """
    Get all the kv-storage entries for username@domain
    """
    query = iroha.query('GetAccountDetail', account_id='userone@domain')
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)

    response = net.send_query(query)
    data = response.account_detail_response
    print('Account id = {}, details = {}'.format(acc_id, data.detail))


@trace
def create_specific_domain(domain):
    """
    Create domain and asset with precision 2 from given information
    """
    command = [
        iroha.command('CreateDomain', domain_id=domain, default_role='user')
    ]
    print(command)
    # And sign the transaction using the keys from earlier:
    tx = IrohaCrypto.sign_transaction(
        iroha.transaction(command), ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)


@trace
def create_specific_asset(domain, asset):
    """
    Create domain and asset with precision 2 from given information
    """
    command = [
        iroha.command('CreateAsset', asset_name=asset,
                      domain_id=domain, precision=2)
    ]
    # And sign the transaction using the keys from earlier:
    tx = IrohaCrypto.sign_transaction(
        iroha.transaction(command), ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)


@trace
def create_specific_domain_and_asset(domain, asset):
    """
    Create domain and asset with precision 2 from given information
    """
    commands = [
        iroha.command('CreateDomain', domain_id=domain, default_role='user'),
        iroha.command('CreateAsset', asset_name=asset,
                      domain_id=domain, precision=2)
    ]
    # And sign the transaction using the keys from earlier:
    tx = IrohaCrypto.sign_transaction(
        iroha.transaction(commands), ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)


@trace
def create_role(defined_role, perms):
    """
    Create role from given information
    """
    command = [
        iroha.command('CreateRole', role_name=defined_role, permissions=perms)
    ]
    # And sign the transaction using the keys from earlier:
    tx = IrohaCrypto.sign_transaction(
        iroha.transaction(command), ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)


# This account is created with the new admin under the healthcare domain
@trace
def create_account(username, acc_domain):
    """
    Create an account in the form of 'username@domain'
    """
    # Creating the user Keys for this account
    temp_private_key = IrohaCrypto.private_key()
    temp_public_key = IrohaCrypto.derive_public_key(temp_private_key)

    tx = iroha.transaction([
        iroha.command('CreateAccount', account_name=username, domain_id=acc_domain,
                       public_key=temp_public_key)
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)
    # print(tx)
    return temp_private_key, temp_public_key


@trace
def create_account_alice():
    """
    Create account 'userone@domain'
    """
    tx = iroha.transaction([
        iroha.command('CreateAccount', account_name='alice', domain_id='test',
                      public_key=new_public_key)
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)
    # print(tx)


@trace
def append_role(acc_id, role):
    """
    Create an account in the form of 'username@domain'
    """
    tx = iroha.transaction([
        iroha.command('AppendRole', account_id=acc_id, role_name=role)
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)

    
@trace
def add_ehr(acc_id, ehr_reference):
    """
    Add the EHR reference number as an account detail (setting account detail)
    """
    tx = iroha.transaction([
        iroha.command('SetAccountDetail', account_id=acc_id, key="ehr", value=ehr_reference)
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)

    
@trace
def add_peer(peerIP, peerkey):
    """
    Add a peer to the network given an IP address
    """
    peer0 = primitive_pb2.Peer()
    peer0.address = peerIP
    peer0.peer_key = peerkey
    tx = iroha.transaction([iroha.command('AddPeer', peer=peer0)])
    # And sign the transaction using the keys from earlier:
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)

    
# Let's run the commands defined previously:
# create_domain_and_asset()
# add_coin_to_admin()
# create_account_userone()
# transfer_coin_from_admin_to_userone()
# userone_grants_to_admin_set_account_detail_permission()
# set_age_to_userone()
# get_coin_info()
# get_account_assets()
# get_userone_details()

########### custom commands #############

### First commands were before Genesis Block implementation ###
# Create correct domain and asset
domain_to_define = 'healthcare'
asset_to_define = 'PatientRecords'
# create_specific_domain(domain_to_define)
# create_specific_asset(domain_to_define, asset_to_define)
# creating admin account in hospital (now defined in genesis.block)
# hospital_admin_1_private_key, hospital_admin_1_public_key = create_account('admin', 'healthcare')
# append_role('admin@hospital', 'admin')

# testing create account functions
# create_account_alice()

# creating doctor account in hospital
doctor_1_private_key, doctor_1_public_key = create_account('alice', 'healthcare')
append_role('alice@healthcare', 'provider')

# creating patient account in hospital (no need to append role since user is default)
patient_1_private_key, patient_1_public_key = create_account('bob', 'healthcare')

# Adding an EHR to a patient's account
# add_ehr('Bob@hospital', '308F3B37')

print('done with preset commands')

################### MENU COMMANDS ########################
print("---------- Login Page -----------")
username = input("Username: ")
# Uses local public and private key files
while username.lower() != "admin":
    print("Invalid user " + username)
    username = input("Username: ")
    input_domain = ""
    input_asset = ""
    input_role = ""
    input_ehr_ref = ""
    input_account = ""
    input_peer = ""
    input_peer_IP = ""
    input_peer_port = ""

################ EXECUTING COMMANDS ######################
# Command list: get account details, create domain, create asset, create role, create account, append role, add ehr
choice = "example"
while choice != "q" and choice != "quit":
    print('Choose a command, "q" or "quit" to quit:')
    print('1. Create Specific Domain')
    print('2. Create Specific Asset')
    print('3. Append Role to an account')
    print('4. Add EHR')
    print('5. Create New Account')
    print('6. Get account details')
    print('7. Add Peer')
    choice = input()
    # Creating a new role is not allowed yet due to needing to define all permissions
    if choice == "1":
        input_domain = input('Create New Domain: ')
        create_specific_domain(input_domain)
    elif choice == "2":
        input_asset = input('Create New Asset: ')
        input_domain = input('Name of Domain: ')
        create_specific_asset(input_domain, input_asset)
    elif choice == "3":
        input_role = input('Role to Append: ')
        input_account = input('Account to add role to: ')
        append_role(input_account, input_role)
    elif choice == "4":
        print('Add EHR')
        input_account = input('Account Name: ')
        input_ehr_ref = input('EHR Reference Number: ')
        add_ehr(input_account, input_ehr_ref)
    elif choice == "5":
        print('Create New Account')
        input_account = input('New Account Name: ')
        input_domain = input('Domain of New Account: ')
        create_account(input_account, input_domain)
    elif choice == "6":
        print('Get Account Details')
        input_account = input('Account Name: ')
        input_domain = input('Domain of Account: ')
        get_account_details(input_account, input_domain)
    elif choice == "7":
        print('Add New Peer')
        input_peer_IP = input("Peer IP: ")
        input_peer_port = "10001"
        input_peerkey = input("Peer Public Key: ")
        input_peer = input_peer_IP + ":" + input_peer_port
        add_peer(input_peer, input_peerkey)
    elif choice == "q":
        print("Goodbye!")
    else:
        print('Invalid Option Selected')
