#!/usr/bin/env python3
"""
Simple script for creating a key using KMS and applying a policy to it

__author__ = "Eddie Atkinson"
__copyright__ = "Copyright 2020"
"""
import boto3
import json

KEY_DESC = "22487668-testkey"
ALIAS = "22487668blah"
key_exists = False
JSON_FILE = "policy.json"
policy = ""
kms = boto3.client("kms")

with open(JSON_FILE, "r") as infile:
    policy = json.dumps(json.load(infile))


def apply_policy(alias, kms):
    keys = kms.list_keys()["Keys"]
    desired_key_id = ""
    for key in keys:
        key_id = key["KeyId"]
        aliases = kms.list_aliases(KeyId=key_id)["Aliases"]
        aliases = [alias["AliasName"] for alias in aliases]
        if f"alias/{alias}" in aliases:
            desired_key_id = key_id
            break
    if not desired_key_id:
        raise Exception(f"Can't find a key id for the alias {alias}")

    resp = kms.put_key_policy(
        KeyId=desired_key_id,
        PolicyName="22487668KeyPolicy",
        Policy=policy,
        BypassPolicyLockoutSafetyCheck=False
    )
    print(resp)


def create_key(kms):
    resp = kms.create_key(
        Description=KEY_DESC,
        KeyUsage="ENCRYPT_DECRYPT",
        Origin="AWS_KMS",
        Policy=policy
    )
    kid = resp["KeyMetadata"]["KeyId"]
    arn = resp["KeyMetadata"]["Arn"]
    kms.create_alias(
        AliasName=f"alias/{ALIAS}",
        TargetKeyId=kid
    )
    return kid, arn

create_key(kms)
# apply_policy(ALIAS, kms)
