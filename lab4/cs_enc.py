#!/usr/bin/env python3
"""
Simple script for traversing a directory's file tree and uploading all files
to S3 preserving the structure using S3 filenames

Encrypted client side using AES-256

Borrows some code from David Glance's example code here:

https://github.com/uwacsp/cits5503/blob/master/Labs/src/fileencrypt.py

__author__ = "Eddie Atkinson"
__copyright__ = "Copyright 2020"
"""
from datetime import datetime
import os
import random
import struct
import getopt
import base64
import sys
import hashlib
import boto3
from Crypto.Cipher import AES
from Crypto import Random

ROOT_DIR = '.'
ROOT_S3_DIR = '22487668-enc'
SHORT_ARGS = "ih"
LONG_ARGS = ["initialise", "help"]
BLOCK_SIZE = 64 * 1024
CHUNK_SIZE = 16
password = "kitty and the kat"

bucket_config = {'LocationConstraint': 'ap-southeast-2'}


def md5_hash(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as infile:
        for chunk in iter(lambda: infile.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def upload_file(s3_resource, path, file_hash, modtime):
    print(f"Uploading  { path }")
    metadata = {
        "Metadata": {
            "ModificationTime": modtime,
            "Md5Hash": file_hash
        }
    }
    s3_resource.meta.client.upload_file(
        Filename=path,
        Bucket=ROOT_S3_DIR,
        Key=path,
        ExtraArgs=metadata
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


def encrypt_file(password, in_filename, out_filename):

    key = hashlib.sha256(password.encode("utf-8")).digest()

    iv = Random.new().read(AES.block_size)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    filesize = os.path.getsize(in_filename)

    with open(in_filename, 'rb') as infile:
        with open(out_filename, 'wb') as outfile:
            outfile.write(struct.pack('<Q', filesize))
            outfile.write(iv)

            while True:
                chunk = infile.read(CHUNK_SIZE)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += ' '.encode("utf-8") * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))


def decrypt_file(password, in_filename, out_filename):

    key = hashlib.sha256(password.encode("utf-8")).digest()

    with open(in_filename, 'rb') as infile:
        origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
        iv = infile.read(16)
        decryptor = AES.new(key, AES.MODE_CBC, iv)

        with open(out_filename, 'wb') as outfile:
            while True:
                chunk = infile.read(CHUNK_SIZE)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))

            outfile.truncate(origsize)


def main():
    opts = getopt.getopt(sys.argv[1:], SHORT_ARGS, LONG_ARGS)[0]
    initialise = False
    s3_client = boto3.client("s3")
    s3_resource = boto3.resource("s3")
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
                encrypt_file(password, path, f"{path}.enc")
                upload_file(s3_resource, f"{path}.enc", file_hash, modtime)
    print("done")


if __name__ == "__main__":
    main()
