#!/usr/bin/env python3
"""
Simple script for traversing a directory's file tree and uploading all files
to S3 preserving the structure using S3 filenames

__author__ = "Eddie Atkinson"
__copyright__ = "Copyright 2020"
"""
from datetime import datetime
import os
import boto3
import base64
import getopt
import sys
from pprint import pprint
import hashlib
from botocore.exceptions import ClientError

ROOT_DIR = '.'
ROOT_S3_DIR = '22487668-test'
SHORT_ARGS = "ih"
LONG_ARGS = ["initialise", "help"]
DYNAMO_URL = "http://localhost:8000"
TABLE_NAME = "CloudFiles"
OWNER = 'david.glance'

bucket_config = {'LocationConstraint': 'ap-southeast-2'}

def md5_hash(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as infile:
        for chunk in iter(lambda: infile.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def upload_file(s3_resource, path, hash, modtime):
    print(f"Uploading  { path }")
    s3_resource.meta.client.upload_file(
                        Filename=path,
                        Bucket=ROOT_S3_DIR,
                        Key=path,
                        ExtraArgs={
                            "Metadata": {
                                "ModificationTime": modtime,
                                "Md5Hash": hash
                            }
                        }
                    )


def print_help():
    print(
        f"Usage cloudstorage.py [OPTION]\n"
        f"Uploads the files in a given directory to S3\n"
        f"-i, --initialise\tCreate a new S3 bucket\n"
        f"-h, --help\tDisplay this help menu then quit\n"
    )


def create_item(table, modtime, path, hash, fname):
    print(f"Creating DB entry for {path}")
    item = {
        "owner": OWNER,
        "path": path,
        "lastUpdated": modtime,
        "permissions": "",
        "fileName": fname,
        "md5Hash": hash
    }
    table.put_item(Item=item)

def update_item(table, modtime, path, hash):
    key = {
        "owner": OWNER,
        "path": path
    }
    resp = table.get_item(Key=key)
    item = resp["Item"]
    print(
        f"Updating {path}"
    )
    table.update_item(
        Key=key,
        UpdateExpression="set md5Hash=:h, lastUpdated=:l",
        ExpressionAttributeValues={
            ":h": hash,
            ":l": modtime
        },
        ReturnValues="UPDATED_NEW"
    )


def changes_made(table, modtime, path, hash, fname):
    resp = table.get_item(
        Key={
            "owner": OWNER,
            "path": path
        }
    )
    try:
        item = resp["Item"]
        if item["md5Hash"] == hash:
            # Nothing has changed, return False
            print(f"{path} is unchanged no need to upload")
            return False
        else:
            update_item(table, modtime, path, hash)
    except KeyError:
        # Theres no DB entry for the item, create one
        create_item(table, modtime, path, hash, fname)
        return True
    return True

def main():
    opts, args = getopt.getopt(sys.argv[1:], SHORT_ARGS, LONG_ARGS)
    initialise = False
    s3_client = boto3.client("s3")
    s3_resource = boto3.resource("s3")
    dynamo = boto3.resource("dynamodb", endpoint_url=DYNAMO_URL)
    table = dynamo.Table(TABLE_NAME)
    for opt in opts:
        if opt[0] == '-i' or opt[0] == '--initalise':
            initialise = True
        elif opt[0] == '-h' or opt[0] == '--help':
            print_help()
            return

    try:
        if initialise:
            s3_client.create_bucket(
                ACL='private',
                Bucket=ROOT_S3_DIR,
                CreateBucketConfiguration=bucket_config
            )
    except s3_client.exceptions.BucketAlreadyExists:
        print(f"Bucket {ROOT_S3_DIR} already exists")
        return
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket {ROOT_S3_DIR} has already been created by you")
        return

    # parse directory and upload files

    for dir_name, subdir_list, file_list in os.walk(ROOT_DIR, topdown=True):
        if dir_name != ROOT_DIR:
            for fname in file_list:
                path = f"{dir_name[2:]}/{fname}"
                print(path + '\n')
                modtime = datetime.fromtimestamp(
                    os.stat(path).st_mtime
                ).strftime("%c")
                hash = md5_hash(path)
                if changes_made(table, modtime, path, hash, fname):
                    upload_file(s3_resource, path, hash, modtime)
    print("done")

if __name__ == "__main__":
    main()
