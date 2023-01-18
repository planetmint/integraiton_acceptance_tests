# Copyright © 2020 Interplanetary Database Association e.V.,
# Planetmint and IPDB software contributors.
# SPDX-License-Identifier: (Apache-2.0 AND CC-BY-4.0)
# Code is Apache-2.0 and docs are CC-BY-4.0

import pytest
import json
from zenroom import zencode_exec
from os import environ

CONDITION_SCRIPT = """Scenario 'ecdh': create the signature of an object
    Given I have the 'keyring'
    Given that I have a 'string dictionary' named 'houses'
    When I create the signature of 'houses'
    Then print the 'signature'"""

FULFILL_SCRIPT = """Scenario 'ecdh': Bob verifies the signature from Alice
    Given I have a 'ecdh public key' from 'Alice'
    Given that I have a 'string dictionary' named 'houses'
    Given I have a 'signature' named 'signature'
    When I verify the 'houses' has a signature in 'signature' by 'Alice'
    Then print the string 'ok'"""

SK_TO_PK = """Scenario 'ecdh': Create the keypair
    Scenario 'reflow': Create the key
    Given that I am known as '{}'
    Given I have the 'keyring'
    When I create the ecdh public key
    When I create the bitcoin address
    When I create the reflow public key
    Then print my 'ecdh public key'
    Then print my 'bitcoin address'
    Then print my 'reflow public key'"""

GENERATE_KEYPAIR_ = """Scenario 'ecdh': Create the keypair
    Scenario 'reflow': Create the key
    Given that I am known as 'Pippo'
    When I create the ecdh key
    When I create the bitcoin key
    When I create the reflow key
    Then print keyring"""

INITIAL_STATE = {"also": "more data"}
SCRIPT_INPUT = {
    "houses": [
        {
            "name": "Harry",
            "team": "Gryffindor",
        },
        {
            "name": "Draco",
            "team": "Slytherin",
        },
    ],
}

metadata = {"units": 300, "type": "KG"}

ZENROOM_DATA = {"that": "is my data"}


@pytest.fixture
def gen_key_zencode():
    return GENERATE_KEYPAIR_


@pytest.fixture
def secret_key_to_private_key_zencode():
    return SK_TO_PK


@pytest.fixture
def fulfill_script_zencode():
    return FULFILL_SCRIPT


@pytest.fixture
def condition_script_zencode():
    return CONDITION_SCRIPT


@pytest.fixture
def zenroom_house_assets():
    return SCRIPT_INPUT


@pytest.fixture
def zenroom_script_input():
    return SCRIPT_INPUT


@pytest.fixture
def zenroom_data():
    return ZENROOM_DATA


@pytest.fixture
def alice(gen_key_zencode):
    alice = json.loads(zencode_exec(gen_key_zencode).output)
    return alice


@pytest.fixture
def bob(gen_key_zencode):
    bob = json.loads(zencode_exec(gen_key_zencode).output)
    return bob


@pytest.fixture
def zenroom_public_keys(gen_key_zencode, secret_key_to_private_key_zencode, alice, bob):
    zen_public_keys = json.loads(
        zencode_exec(secret_key_to_private_key_zencode.format("Alice"), keys=json.dumps(alice)).output
    )
    zen_public_keys.update(
        json.loads(zencode_exec(secret_key_to_private_key_zencode.format("Bob"), keys=json.dumps(bob)).output)
    )
    return zen_public_keys


@pytest.fixture
def bdb_host():
    return environ.get("PLANETMINT_ENDPOINT", "localhost")


@pytest.fixture
def bdb_port():
    return environ.get("BDB_PORT", "9984")


@pytest.fixture
def bdb_node(bdb_host, bdb_port):
    return "http://{host}:{port}".format(host=bdb_host, port=bdb_port)


@pytest.fixture
def get_reflow_seal():
    return """Scenario 'reflow': creation of reflow seal
        Given I have a 'reflow public key array' named 'public keys'
        Given I have a 'string dictionary' named 'Sale'
        When I aggregate the reflow public key from array 'public keys'
        When I create the reflow identity of 'Sale'
        When I rename the 'reflow identity' to 'SaleIdentity'
        When I create the reflow seal with identity 'SaleIdentity'
        Then print the 'reflow seal'"""


@pytest.fixture
def sign_reflow_seal():
    return """Scenario 'reflow': sign the reflow seal 
        Given I am 'Alice'
        Given I have my 'credentials'
        Given I have my 'keyring'
        Given I have a 'reflow seal'
        Given I have a 'issuer public key' from 'The Authority'

        # Here the participant is producing a signature, which will later 
        # be added to the reflow seal, along with the other signatures  
        When I create the reflow signature
        Then print the 'reflow signature'"""


@pytest.fixture
def driver(bdb_node):
    from planetmint_driver.driver import Planetmint

    return Planetmint(bdb_node)
