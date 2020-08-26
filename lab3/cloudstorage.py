#!/usr/bin/env python3
"""
Simple script for traversing a directory's file tree and uploading all files
to S3 preserving the structure using S3 filenames

__author__ = "Eddie Atkinson"
__copyright__ = "Copyright 2020"
"""
import os
import boto3
import base64
import getopt
import sys

ROOT_DIR = '.'
ROOT_S3_DIR = '22487668-cloudstorage'
SHORT_ARGS = "ih"
LONG_ARGS = ["initialise", "help"]

bucket_config = {'LocationConstraint': 'ap-southeast-2'}

def upload_file(folder_name, file, file_name):

    print("Uploading %s" % file)


def print_help():
    print(
        f"Usage cloudstorage.py [OPTION]\n"
        f"Uploads the files in a given directory to S3\n"
        f"-i, --initialise\tCreate a new S3 bucket\n"
        f"-h, --help\tDisplay this help menu then quit\n"
    )


def main():
    opts, args = getopt.getopt(sys.argv[1:], SHORT_ARGS, LONG_ARGS)
    initialise = False
    s3_client = boto3.client("s3")
    s3_resource = boto3.resource("s3")
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
                print(
                    f"{dir_name[2:]}/{fname}"
                )
                path = f"{dir_name[2:]}/{fname}"
                s3_resource.meta.client.upload_file(
                    Filename=path,
                    Bucket=ROOT_S3_DIR,
                    Key=path
                )
    print("done")

if __name__ == "__main__":
    main()
