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
from flask import Flask, request

# The following line is actually about the permissions
# you might be using for the transaction.
# You can find all the permissions here:
# https://iroha.readthedocs.io/en/main/develop/api/permissions.html
from iroha.primitive_pb2 import can_set_my_account_detail
import sys

app = Flask(__name__)

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
iroha = Iroha(ADMIN_ACCOUNT_ID)

# Defining the nets for each node
net = IrohaGrpc('{}:{}'.format(IROHA_HOST_ADDR, IROHA_PORT))

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
    tracer.__name__ = func.__name__
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

        
### NEW COMMANDS ###
@app.route('/getdetails/<acc_id>/<domain>')
@trace
def get_account_details(acc_id, domain):
    """
    Get all the kv-storage entries for username@domain
    """
    query = iroha.query('GetAccountDetail', account_id=acc_id+'@'+domain)
    IrohaCrypto.sign_query(query, ADMIN_PRIVATE_KEY)

    response = net.send_query(query)
    data = response.account_detail_response
    print('Account id = {}, details = {}'.format(acc_id, data.detail))
    return data


@app.route('/newdomain/<domain>')
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
    return tx


@app.route('/newasset/<domain>/<asset>')
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
    return tx


# This account is created with the new admin under the healthcare domain
@app.route('/createaccount/<username>/<acc_domain>')
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
    return temp_private_key, temp_public_key, tx

                        
@app.route('/appendrole/<acc_id>/<role>')
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
    return tx


@app.route('/addehr/<acc_id>/<domain>/<detail>/<ehr_reference>')
@trace
def add_ehr(acc_id, domain, detail, ehr_reference):
    """
    Add the EHR reference number as an account detail (setting account detail)
    """
    tx = iroha.transaction([
        iroha.command('SetAccountDetail', account_id=acc_id + '@' + domain, key=detail, value=ehr_reference)
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)
    return tx


@app.route('/addpeer/<peerIP>/<peerkey>')
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
    return tx


@app.route('/cansetmydetails/<acc_id>/<myacc_id>')
@trace
def cansetmydetails(acc_id, myacc_id):
    """
    Give an account permission to set and get the user's account details
    """
    tx1 = iroha.transaction([iroha.command('GrantPermission', account_id=acc_id, permission=primitive_pb2.can_set_my_account_detail)], creator_account=myacc_id)
    IrohaCrypto.sign_transaction(tx1, ADMIN_PRIVATE_KEY)
    tx1 = iroha.transaction([iroha.command('GrantPermission', account_id=acc_id, permission=primitive_pb2.can_get_my_account_detail)], creator_account=myacc_id)
    IrohaCrypto.sign_transaction(tx2, ADMIN_PRIVATE_KEY)
    return tx1, tx2


########### custom commands #############

# Python program to use
# main for function call.
if __name__ == "__main__":
    # Define a domain
    domain_to_define = 'healthcare'
    # creating doctor account in healthcare
    doctor_1_private_key, doctor_1_public_key, tx = create_account('alice', 'healthcare')
    append_role('alice@healthcare', 'provider')

    # creating patient account in healthcare (no need to append role since user is default)
    patient_1_private_key, patient_1_public_key, tx = create_account('bob', 'healthcare')
    print("Printing out bob's keys for testing purposes")
    print("bob's public key: ", patient_1_public_key)
    print("bob's private key ", patient_1_private_key)
    # Adding an EHR to a patient's account
    add_ehr('bob', 'hospital', 'ehr1', '308F3B37')

    print('done with preset commands')
    
    ################### MENU COMMANDS ########################
    print("---------- Login Page -----------")
    username = input("Username: ")
    password = input("Private Key: ")
    # Uses local public and private key files
    while username.lower() != "admin":
        print("Invalid user " + username)
        username = input("Username: ")
        input_domain = ""
        input_asset = ""
        input_role = ""
        input_ehr_ref = ""
        input_account = ""
        input_key = ""
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
            print("Create new Domain")
            input_domain = input('Create New Domain: ')
            create_specific_domain(input_domain)
        elif choice == "2":
            print("Create new Asset")
            input_asset = input('Create New Asset: ')
            input_domain = input('Name of Domain: ')
            create_specific_asset(input_domain, input_asset)
        elif choice == "3":
            print('Append a Role')
            input_role = input('Role to Append: ')
            input_account = input('Account to add role to: ')
            append_role(input_account, input_role)
        elif choice == "4":
            print('Add Account Detail: Example Account is alice@healthcare')
            input_account = input('Account Name: ')
            input_domain = input('Domain of Account: ')
            input_key = input('Name of Detail: ')
            input_ehr_ref = input('Account Detail to Add: ')
            add_ehr(input_account, input_domain, input_key, input_ehr_ref)
        elif choice == "5":
            print('Create New Account')
            input_account = input('New Account Name: ')
            input_domain = input('Domain of New Account: ')
            temp_public_key, temp_private_key = create_account(input_account, input_domain)
            print("Public Key: ", temp_public_key)
            print("Private Key: ", temp_private_key)
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
        elif choice == "q" or choice == "quit":
            print("Goodbye!")
        else:
            print('Invalid Option Selected')
