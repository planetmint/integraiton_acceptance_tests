import json
import base58
from hashlib import sha3_256
from planetmint_cryptoconditions.types.zenroom import ZenroomSha256
from planetmint_driver.crypto import generate_keypair
from .helper.hosts import Hosts
from zenroom import zencode_exec
import time
from ipld import multihash, marshal

version = "3.0"

def test_zenroom_signing(
    fulfill_script_zencode,
    zenroom_data,
    condition_script_zencode,
    zenroom_script_input,
    zenroom_public_keys,
    alice,
):
    plnmnt_keypair = generate_keypair()

    zenroomscpt = ZenroomSha256(script=fulfill_script_zencode, data=zenroom_data, keys=zenroom_public_keys)
    print(f"zenroom is: {zenroomscpt.script}")

    # CRYPTO-CONDITIONS: generate the condition uri
    condition_uri_zen = zenroomscpt.condition.serialize_uri()
    print(f"\nzenroom condition URI: {condition_uri_zen}")

    # CRYPTO-CONDITIONS: construct an unsigned fulfillment dictionary
    unsigned_fulfillment_dict_zen = {
        "type": zenroomscpt.TYPE_NAME,
        "public_key": base58.b58encode(plnmnt_keypair.public_key).decode(),
    }
    output = {
        "amount": "10",
        "condition": {
            "details": unsigned_fulfillment_dict_zen,
            "uri": condition_uri_zen,
        },
        "public_keys": [
            plnmnt_keypair.public_key,
        ],
    }
    input_ = {
        "fulfillment": None,
        "fulfills": None,
        "owners_before": [
            plnmnt_keypair.public_key,
        ],
    }
    metadata = {"result": {"output": ["ok"]}}

    script_ = {
        "code": {
            "type": "zenroom",
            "raw": "test_string",
            "parameters": [{"obj": "1"}, {"obj": "2"}],
        },  # obsolete
        "state": "dd8bbd234f9869cab4cc0b84aa660e9b5ef0664559b8375804ee8dce75b10576",  #
        "input": zenroom_script_input,
        "output": ["ok"],
        "policies": {},
    }

    token_creation_tx = {
        "operation": "CREATE",
        "assets": [{"data": multihash(marshal({"test": "my asset"}))}],
        "metadata": multihash(marshal(metadata)),
        "script": script_,
        "outputs": [
            output,
        ],
        "inputs": [
            input_,
        ],
        "version": version,
        "id": None,
    }

    # JSON: serialize the transaction-without-id to a json formatted string
    tx = json.dumps(
        token_creation_tx,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    script_ = json.dumps(script_)
    # major workflow:
    # we store the fulfill script in the transaction/message (zenroom-sha)
    # the condition script is used to fulfill the transaction and create the signature
    #
    # the server should ick the fulfill script and recreate the zenroom-sha and verify the signature

    signed_input = zenroomscpt.sign(script_, condition_script_zencode, alice)

    input_signed = json.loads(signed_input)
    print(input_signed)
    input_signed["input"]["signature"] = input_signed["output"]["signature"]
    del input_signed["output"]["signature"]
    del input_signed["output"]["logs"]
    input_signed["output"] = ["ok"]  # define expected output that is to be compared
    input_msg = json.dumps(input_signed)

    assert zenroomscpt.validate(message=input_msg)

    tx = json.loads(tx)
    fulfillment_uri_zen = zenroomscpt.serialize_uri()

    tx["inputs"][0]["fulfillment"] = fulfillment_uri_zen
    tx["script"] = input_signed
    tx["id"] = None
    json_str_tx = json.dumps(tx, sort_keys=True, skipkeys=False, separators=(",", ":"))

    # SHA3: hash the serialized id-less transaction to generate the id
    shared_creation_txid = sha3_256(json_str_tx.encode()).hexdigest()
    tx["id"] = shared_creation_txid

    hosts = Hosts("/shared/hostnames")
    pm_alpha = hosts.get_connection()
    sent_transfer_tx = pm_alpha.transactions.send_commit(tx)
    time.sleep(1)
    # Assert that transaction is stored on both planetmint nodes
    hosts.assert_transaction(shared_creation_txid)
    print(f"\n\nstatus and result : + {sent_transfer_tx}")