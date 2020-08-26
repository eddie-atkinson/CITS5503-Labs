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

def pull_files(s3_client, s3_resource):
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
    table = dynamo.Table("CloudFiles")
    item = {
        "userId": "54de66f5229dba51d8baf49a5f7501bdfeec4596711c7f01ab2bb822348788",
        "fileName": "blah.txt",
        "path": "blah.txt",
        "lastUpdated": "yesterday",
        "owner": "david glance",
        "permissions": ""
    }
    # pprint(table.put_item(Item=item))
    response = table.get_item(
        Key={
            "userId": "54de66f5229dba51d8baf49a5f7501bdfeec4596711c7f01ab2bb822348788",
            "path": "blah.txt"
        }
    )
    pprint(response)

    # pull_files(s3_client, s3_resource)





if __name__ == "__main__":
    main()
