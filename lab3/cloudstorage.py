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


s3 = boto3.client("s3")

bucket_config = {'LocationConstraint': 'ap-southeast-2'}

def upload_file(folder_name, file, file_name):

    print("Uploading %s" % file)


# Main program
# Insert code to create bucket if not there

def main():
    opts, args = getopt.getopt(sys.argv[1:], SHORT_ARGS, LONG_ARGS)
    print(opts, args)

    # try:

    #     print(response)
    # except Exception as error:
    #     pass


    # # parse directory and upload files

    # for dir_name, subdir_list, file_list in os.walk(ROOT_DIR, topdown=True):
    #     if dir_name != ROOT_DIR:
    #         for fname in file_list:
    #             upload_file("%s/" % dir_name[2:], "%s/%s" % (dir_name, fname), fname)


    print("done")

if __name__ == "__main__":
    main()
