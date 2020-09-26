#!/usr/bin/env python3
"""
Simple script for applying bucket policies and encryption to S3 buckets

__author__ = "Eddie Atkinson"
__copyright__ = "Copyright 2020"
"""
import boto3
import json


BUCKET_NAME = "22487668-test"

s3 = boto3.client("s3")
bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "AllowAllS3ActionsInUserFolderForUserOnly",
        "Effect": "Deny",
        "Principal": "*",
        "Action": "s3:*",
        "Resource": f"arn:aws:s3:::{BUCKET_NAME}/rootdir/*",
        "Condition": {
            "StringNotLike": {
                "aws:username": "22487668@student.uwa.edu.au"
            }
        }
    }]
}

bucket_policy = json.dumps(bucket_policy)
s3.put_bucket_policy(Bucket=BUCKET_NAME, Policy=bucket_policy)

print(s3.get_bucket_policy(Bucket=BUCKET_NAME))