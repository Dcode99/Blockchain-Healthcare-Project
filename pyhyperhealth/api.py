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

# acc_id is the account ID without the domain
# domain is the domain of the account
# user is the account ID and the domain of the user submitting the request
# apikey is the api key of the user submitting the request
### NEW COMMANDS ###
@app.route('/getdetails/<acc_id>/<domain>/<user>/<userdomain>/<apikey>')
@trace
def get_account_details(acc_id, domain, user, userdomain, apikey):
    """
    Get all the kv-storage entries for username@domain
    """
    ACCOUNT_ID = user + "@" + userdomain
    iroha = Iroha(ACCOUNT_ID)
    query = iroha.query('GetAccountDetail', account_id=acc_id+'@'+domain)
    IrohaCrypto.sign_query(query, apikey)

    response = net.send_query(query)
    data = response.account_detail_response
    s = 'Account id = {}, details = {}'.format(acc_id, data.detail)
    print(s)
    return s


@app.route('/newdomain/<domain>/<user>/<userdomain>/<apikey>')
@trace
def create_specific_domain(domain, user, userdomain, apikey):
    """
    Create domain and asset with precision 2 from given information
    """
    ACCOUNT_ID = user + "@" + userdomain
    iroha = Iroha(ACCOUNT_ID)
    command = [
        iroha.command('CreateDomain', domain_id=domain, default_role='user')
    ]
    print(command)
    # And sign the transaction using the keys from earlier:
    tx = IrohaCrypto.sign_transaction(
        iroha.transaction(command), apikey)
    result = send_transaction_and_print_status(tx)
    return result


@app.route('/newasset/<domain>/<asset>/<user>/<userdomain>/<apikey>')
@trace
def create_specific_asset(domain, asset, user, userdomain, apikey):
    """
    Create domain and asset with precision 2 from given information
    """
    ACCOUNT_ID = user + "@" + userdomain
    iroha = Iroha(ACCOUNT_ID)
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
@app.route('/createaccount/<newusername>/<acc_domain>/<user>/<userdomain>/<apikey>')
@trace
def create_account(newusername, acc_domain, user, userdomain, apikey):
    """
    Create an account in the form of 'username@domain'
    """
    ACCOUNT_ID = user + "@" + userdomain
    iroha = Iroha(ACCOUNT_ID)
    # Creating the user Keys for this account
    temp_private_key = IrohaCrypto.private_key()
    temp_public_key = IrohaCrypto.derive_public_key(temp_private_key)

    tx = iroha.transaction([
        iroha.command('CreateAccount', account_name=newusername, domain_id=acc_domain,
                      public_key=temp_public_key)
    ])
    IrohaCrypto.sign_transaction(tx, apikey)
    result = send_transaction_and_print_status(tx)
    print(temp_private_key, temp_public_key, result)
    return  'Private Key: {} \nPublic Key: {} \nSuccess: {}'.format(temp_private_key, temp_public_key, result)

                        
@app.route('/appendrole/<acc_id>/<acc_domain>/<role>/<user>/<userdomain>/<apikey>')
@trace
def append_role(acc_id, acc_domain, role, user, userdomain, apikey):
    """
    Create an account in the form of 'username@domain'
    """
    ACCOUNT_ID = user + "@" + userdomain
    iroha = Iroha(ACCOUNT_ID)
    acc_id = acc_id + "@" + acc_domain
    tx = iroha.transaction([
        iroha.command('AppendRole', account_id=acc_id, role_name=role)
    ])
    IrohaCrypto.sign_transaction(tx, apikey)
    result = send_transaction_and_print_status(tx)
    return result


@app.route('/addehr/<acc_id>/<domain>/<detail>/<ehr_reference>/<user>/<userdomain>/<apikey>')
@trace
def add_ehr(acc_id, domain, detail, ehr_reference, user, userdomain, apikey):
    """
    Add the EHR reference number as an account detail (setting account detail)
    """
    ACCOUNT_ID = user + "@" + userdomain
    iroha = Iroha(ACCOUNT_ID)
    acc_id = acc_id + "@" + domain
    tx = iroha.transaction([
        iroha.command('SetAccountDetail', account_id=acc_id, key=detail, value=ehr_reference)
    ])
    IrohaCrypto.sign_transaction(tx, apikey)
    result = send_transaction_and_print_status(tx)
    return result


@app.route('/addpeer/<peerIP>/<peerport>/<peerkey>/<user>/<userdomain>/<apikey>')
@trace
def add_peer(peerIP, peerport, peerkey, user, userdomain, apikey):
    """
    Add a peer to the network given an IP address
    """
    ACCOUNT_ID = user + "@" + userdomain
    iroha = Iroha(ACCOUNT_ID)
    peer0 = primitive_pb2.Peer()
    peer0.address = peerIP + ":" + peerport
    peer0.peer_key = peerkey
    tx = iroha.transaction([iroha.command('AddPeer', peer=peer0)])
    # And sign the transaction using the keys from earlier:
    IrohaCrypto.sign_transaction(tx, apikey)
    result = send_transaction_and_print_status(tx)
    return result


@app.route('/cansetmydetails/<acc_id>/<acc_domain>/<user>/<userdomain>/<apikey>')
@trace
def cansetmydetails(acc_id, myacc_id, user, userdomain, apikey):
    """
    Give an account permission to set and get the user's account details
    """
    acc_id = acc_id + "@" + acc_domain
    ACCOUNT_ID = user + "@" + userdomain
    iroha = Iroha(ACCOUNT_ID)
    tx = iroha.transaction([
        iroha.command('GrantPermission', account_id=acc_id, 
                      permission=can_set_my_account_detail)
    ], creator_account=myacc_id)
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    result = send_transaction_and_print_status(tx)
    print(result)
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
