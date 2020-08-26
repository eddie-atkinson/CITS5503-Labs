#!/usr/bin/env python3
"""
__author__ = "Eddie Atkinson"
__copyright__ = "Copyright 2020"

Simple script to download files and folders from S3 preserving the folder structure
"""
import boto3
import hashlib
from pprint import pprint
from pathlib import Path


S3_ROOT_DIR="22487668-cloudstorage"

BUCKET_CONFIG = {'LocationConstraint': 'ap-southeast-2'}
RESTORE_PATH = "."


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

    try:
        file_contents = response["Contents"]
    except KeyError:
        print("No files in the S3 bucket specified")
        return
    file_names = [file["Key"] for file in file_contents]
    restore_dir = Path(RESTORE_PATH).absolute()
    for file in file_names:
        s3_obj = s3_resource.Object(S3_ROOT_DIR, file)
        cloud_hash = s3_obj.metadata["md5hash"]
        file_path = restore_dir / file
        if file_path.exists():
            if cloud_hash == md5_hash(str(file_path)):
                print(
                    f"Skipping {file_path}, it is unchanged"
                )
                continue
        if not file_path.parent.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)

        print(
            f"Restoring {file}"
        )
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
