#!/usr/bin/env python3
#
# Copyright Soramitsu Co., Ltd. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0
#


# Here are Iroha dependencies.
# Python library generally consists of 3 parts:
# Iroha, IrohaCrypto and IrohaGrpc which we need to import:
import os
import re
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

ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'admin@test')
ADMIN_PRIVATE_KEY = os.getenv(
    'ADMIN_PRIVATE_KEY', 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70')
print(ADMIN_ACCOUNT_ID)
iroha = Iroha(ADMIN_ACCOUNT_ID)
print(iroha)

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
    result = "REJECTED\n"
    for status in net.tx_status_stream(transaction):
        print(status)
        if re.search('COMMITTED', str(status)):
            result = "COMMITTED\n"
    return result

        
### NEW COMMANDS ###
@app.route('/getdetails/<acc_id>/<domain>/<apikey>')
@trace
def get_account_details(acc_id, domain):
    """
    Get all the kv-storage entries for username@domain
    """
    query = iroha.query('GetAccountDetail', account_id=acc_id+'@'+domain)
    IrohaCrypto.sign_query(query, apikey)

    response = net.send_query(query)
    data = response.account_detail_response
    s = 'Account id = {}, details = {}'.format(acc_id, data.detail)
    print(s)
    return s


@app.route('/newdomain/<domain>/<apikey>')
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
        iroha.transaction(command), apikey)
    result = send_transaction_and_print_status(tx)
    return result


@app.route('/newasset/<domain>/<asset>/<apikey>')
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
        iroha.transaction(command), apikey)
    result = send_transaction_and_print_status(tx)
    return result


# This account is created with the new admin under the healthcare domain
@app.route('/createaccount/<username>/<acc_domain>/<apikey>')
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
    IrohaCrypto.sign_transaction(tx, apikey)
    result = send_transaction_and_print_status(tx)
    print(temp_private_key, temp_public_key, result)
    return  'Private Key: {} \nPublic Key: {} \nSuccess: {}'.format(temp_private_key, temp_public_key, result)

                        
@app.route('/appendrole/<acc_id>/<role>/<apikey>')
@trace
def append_role(acc_id, role):
    """
    Create an account in the form of 'username@domain'
    """
    tx = iroha.transaction([
        iroha.command('AppendRole', account_id=acc_id, role_name=role)
    ])
    IrohaCrypto.sign_transaction(tx, apikey)
    result = send_transaction_and_print_status(tx)
    return result


@app.route('/addehr/<acc_id>/<domain>/<detail>/<ehr_reference>/<apikey>')
@trace
def add_ehr(acc_id, domain, detail, ehr_reference):
    """
    Add the EHR reference number as an account detail (setting account detail)
    """
    tx = iroha.transaction([
        iroha.command('SetAccountDetail', account_id=acc_id + '@' + domain, key=detail, value=ehr_reference)
    ])
    IrohaCrypto.sign_transaction(tx, apikey)
    result = send_transaction_and_print_status(tx)
    return result


@app.route('/addpeer/<peerIP>/<peerport>/<peerkey>/<apikey>')
@trace
def add_peer(peerIP, peerport, peerkey):
    """
    Add a peer to the network given an IP address
    """
    peer0 = primitive_pb2.Peer()
    peer0.address = peerIP + ":" + peerport
    peer0.peer_key = peerkey
    tx = iroha.transaction([iroha.command('AddPeer', peer=peer0)])
    # And sign the transaction using the keys from earlier:
    IrohaCrypto.sign_transaction(tx, apikey)
    result = send_transaction_and_print_status(tx)
    return result


@app.route('/cansetmydetails/<acc_id>/<myacc_id>/<apikey>')
@trace
def cansetmydetails(acc_id, myacc_id):
    """
    Give an account permission to set and get the user's account details
    """
    tx1 = iroha.transaction([iroha.command('GrantPermission', account_id=acc_id, permission=primitive_pb2.can_set_my_account_detail)], creator_account=myacc_id)
    IrohaCrypto.sign_transaction(tx1, apikey)
    result1 = send_transaction_and_print_status(tx1)
    tx2 = iroha.transaction([iroha.command('GrantPermission', account_id=acc_id, permission=primitive_pb2.can_get_my_account_detail)], creator_account=myacc_id)
    IrohaCrypto.sign_transaction(tx2, apikey)
    result2 = send_transaction_and_print_status(tx2)
    return '{} {}'.format(result1, result2)
