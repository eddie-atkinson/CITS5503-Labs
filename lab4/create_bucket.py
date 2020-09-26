import boto3

BUCKET_NAME ="22487668-test"

s3 = boto3.client("s3")
location = {
    "LocationConstraint": "ap-southeast-2"
}
s3.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration=location)

