#!/usr/bin/env python3
"""
Simple script for traversing a directory's file tree and uploading all files
to S3 preserving the structure using S3 filenames.

Now includes the option for server side encryption

__author__ = "Eddie Atkinson"
__copyright__ = "Copyright 2020"
"""
from datetime import datetime
import os
import getopt
import sys
import hashlib
import boto3

ROOT_DIR = '.'
ROOT_S3_DIR = '22487668-enc'
SHORT_ARGS = "ihe:"
LONG_ARGS = ["initialise", "help", "encrypt="]


bucket_config = {'LocationConstraint': 'ap-southeast-2'}


def md5_hash(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as infile:
        for chunk in iter(lambda: infile.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def upload_file(s3_resource, path, file_hash, modtime, extra_args=None):
    print(f"Uploading  { path }")
    metadata = {
        "Metadata": {
            "ModificationTime": modtime,
            "Md5Hash": file_hash
        }
    }
    if extra_args:
        args = {**extra_args, **metadata}
    else:
        args = metadata
    s3_resource.meta.client.upload_file(
        Filename=path,
        Bucket=ROOT_S3_DIR,
        Key=path,
        ExtraArgs=args
    )


def print_help():
    print(
        "Usage cloudstorage.py [OPTION]\n"
        "Uploads the files in a given directory to S3\n"
        "-i, --initialise\tCreate a new S3 bucket\n"
        "-h, --help\tDisplay this help menu then quit\n"
    )


def create_bucket(s3_client):
    try:
        s3_client.create_bucket(
            ACL='private',
            Bucket=ROOT_S3_DIR,
            CreateBucketConfiguration=bucket_config
        )
        return True
    except s3_client.exceptions.BucketAlreadyExists:
        print(f"Bucket {ROOT_S3_DIR} already exists")
        return False
    except s3_client.exceptions.BucketAlreadyOwnedByYou:
        print(f"Bucket {ROOT_S3_DIR} has already been created by you")
        return False


def main():
    opts = getopt.getopt(sys.argv[1:], SHORT_ARGS, LONG_ARGS)[0]
    initialise = False
    enc_key_alias = ""
    extra_args = {}
    s3_client = boto3.client("s3")
    s3_resource = boto3.resource("s3")
    kms = boto3.client("kms")
    for opt in opts:
        if opt[0] == '-i' or opt[0] == '--initalise':
            initialise = True
        elif opt[0] == '-h' or opt[0] == '--help':
            print_help()
            return
        elif opt[0] == '-e' or opt[0] == '--encrypt':
            enc_key_alias = opt[1]

    if initialise:
        if not create_bucket(s3_client):
            return

    # Fetch the KMS key for encrypting files if required
    if enc_key_alias:
        keys = kms.list_keys()["Keys"]
        for key in keys:
            key_id = key["KeyId"]
            aliases = kms.list_aliases(KeyId=key_id)["Aliases"]
            aliases = [alias["AliasName"] for alias in aliases]
            if f"alias/{enc_key_alias}" in aliases:
                extra_args["ServerSideEncryption"] = "aws:kms"
                extra_args["SSEKMSKeyId"] = key_id

    # parse directory and upload files

    for dir_name, subdir, file_list in os.walk(ROOT_DIR, topdown=True):
        if dir_name != ROOT_DIR:
            for fname in file_list:
                path = f"{dir_name[2:]}/{fname}"
                print(path + '\n')
                modtime = datetime.fromtimestamp(
                    os.stat(path).st_mtime
                ).strftime("%c")
                file_hash = md5_hash(path)
                upload_file(s3_resource, path, file_hash, modtime, extra_args)
    print("done")


if __name__ == "__main__":
    main()
