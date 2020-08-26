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

def main():
    s3_client = boto3.client("s3")
    s3_resource = boto3.resource("s3")
    response = s3_client.list_objects(
        Bucket=S3_ROOT_DIR,
        Delimiter=","
    )

    file_contents = response["Contents"]
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


if __name__ == "__main__":
    main()
