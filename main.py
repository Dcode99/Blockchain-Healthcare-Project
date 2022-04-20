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
IROHA_HOST_ADDR = os.getenv('IROHA_HOST_ADDR', 'localhost')
IROHA_PORT = os.getenv('IROHA_PORT', '50051')
ADMIN_ACCOUNT_ID = os.getenv('ADMIN_ACCOUNT_ID', 'admin@test')
ADMIN_PRIVATE_KEY = os.getenv(
    'ADMIN_PRIVATE_KEY', 'f101537e319568c765b2cc89698325604991dca57b9716b58016b253506cab70')

# Here we will create user keys
user_private_key = IrohaCrypto.private_key()
user_public_key = IrohaCrypto.derive_public_key(user_private_key)
iroha = Iroha(ADMIN_ACCOUNT_ID)
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

    return tracer


# Let's start defining the commands:
@trace
def send_transaction_and_print_status(transaction):
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
    for asset in data:
        print('Asset id = {}, balance = {}'.format(
            asset.asset_id, asset.balance))


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
        iroha.command('CreateDomain', domain_id=domain, default_role='patient')
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
        iroha.command('CreateDomain', domain_id=domain, default_role='patient'),
        iroha.command('CreateAsset', asset_name=asset,
                      domain_id=domain, precision=2)
    ]
# And sign the transaction using the keys from earlier:
    tx = IrohaCrypto.sign_transaction(
        iroha.transaction(commands), ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)


@trace
def create_role(role, perms):
    """
    Create role from given information
    """
    command = [
        iroha.command('CreateRole', role_name=role, permissions=perms)
    ]
# And sign the transaction using the keys from earlier:
    tx = IrohaCrypto.sign_transaction(
        iroha.transaction(command), ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)


@trace
def create_account(username, domain):
    """
    Create an account in the form of 'username@domain'
    """
    # Creating the user Keys for this account
    private_key = IrohaCrypto.private_key()
    public_key = IrohaCrypto.derive_public_key(user_private_key)

    tx = iroha.transaction([
        iroha.command('CreateAccount', account_name=username, domain_id=domain,
                      public_key=user_public_key)
    ])
    IrohaCrypto.sign_transaction(tx, ADMIN_PRIVATE_KEY)
    send_transaction_and_print_status(tx)
    return private_key, public_key


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


def add_ehr(acc_id, ehr_reference):
    """
    Add the EHR reference number as an account detail (setting account detail)
    """
    tx = iroha.transaction([
        iroha.command('SetAccountDetail', account_id=acc_id, key="EHR", value=ehr_reference)
    ])


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

# define role permissions
root_perms = [primitive_pb2.root]
healthcare_worker_perms = [primitive_pb2.can_create_account, primitive_pb2.can_set_detail,
                           primitive_pb2.can_set_my_account_detail, primitive_pb2.can_create_asset,
                           primitive_pb2.can_receive, primitive_pb2.can_transfer, primitive_pb2.can_transfer_my_assets,
                           primitive_pb2.can_add_asset_qty, primitive_pb2.can_subtract_asset_qty,
                           primitive_pb2.can_add_domain_asset_qty, primitive_pb2.can_subtract_domain_asset_qty,
                           primitive_pb2.can_get_my_acc_detail, primitive_pb2.can_get_my_account,
                           primitive_pb2.can_get_my_acc_ast, primitive_pb2.can_get_my_acc_ast_txs,
                           primitive_pb2.can_get_my_acc_txs, primitive_pb2.can_read_assets,
                           primitive_pb2.can_get_my_signatories, primitive_pb2.can_get_my_txs]
patient_perms = [primitive_pb2.can_set_my_account_detail, primitive_pb2.can_receive,
                 primitive_pb2.can_transfer_my_assets, primitive_pb2.can_get_my_acc_detail,
                 primitive_pb2.can_get_my_account, primitive_pb2.can_get_my_acc_ast,
                 primitive_pb2.can_get_my_acc_ast_txs, primitive_pb2.can_get_my_acc_txs,
                 primitive_pb2.can_get_my_signatories, primitive_pb2.can_get_my_txs]

# create_role root
create_role('root', root_perms)
# create_role healthcare_worker
create_role('healthcare_worker', healthcare_worker_perms)
# create_role patient
create_role('patient', patient_perms)

# Create correct domain and asset
domain_to_define = 'Healthcare_Organization'
asset_to_define = 'Patient_Records'
create_specific_domain(domain_to_define)
create_specific_asset(domain_to_define, asset_to_define)

# creating admin account in hospital
hospital_admin_1_private_key, hospital_admin_1_public_key = create_account('admin', 'Healthcare_Organization')
append_role('admin@hospital', 'root')

# creating doctor account in hospital
doctor_1_private_key, doctor_1_public_key = create_account('Alice', 'Healthcare_Organization')
append_role('Alice@hospital', 'healthcare_worker')

# creating patient account in hospital (no need to append role since patient is default)
patient_1_private_key, patient_1_public_key = create_account('Bob', 'Healthcare_Organization')

# Adding an EHR to a patient's account
add_ehr('Alice@hospital', '308F3B37')

print('done')
