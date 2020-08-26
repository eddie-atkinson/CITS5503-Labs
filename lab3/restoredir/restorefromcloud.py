#!/usr/bin/env python3
"""
__author__ = "Eddie Atkinson"
__copyright__ = "Copyright 2020"

Simple script to download files and folders from S3 preserving the folder structure
"""
import boto3
from pprint import pprint
from pathlib import Path


S3_ROOT_DIR="22487668-cloudstorage"

BUCKET_CONFIG = {'LocationConstraint': 'ap-southeast-2'}



def md5_hash(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as infile:
        for chunk in iter(lambda: infile.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def pull_files(s3_client, s3_resource, dynamo):
    response = s3_client.list_objects(
        Bucket=S3_ROOT_DIR,
        Delimiter=","
    )

    pprint(response)
    return
    try:
        file_contents = response["Contents"]
    except KeyError:
        print("No files in the S3 bucket specified")
        return
    file_names = [file["Key"] for file in file_contents]
    current_dir = Path.cwd()
    for file in file_names:
        file_path = current_dir / file
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
        response = s3_resource.meta.client.download_file(
            Bucket=S3_ROOT_DIR,
            Key=file,
            Filename=str(file_path)
        )


def main():
    s3_client = boto3.client("s3")
    s3_resource = boto3.resource("s3")
    dynamo = boto3.resource("dynamodb", endpoint_url="http://localhost:8000")
    pull_files(s3_client, s3_resource, dynamo)





if __name__ == "__main__":
    main()
