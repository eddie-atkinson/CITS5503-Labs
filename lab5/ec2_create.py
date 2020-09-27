#!/usr/bin/env python3
"""
Simple script for creating two EC2 instances in two different
AZs and removing them

__author__ = "Eddie Atkinson"
__copyright__ = "Copyright 2020"
"""
import boto3
from namesgenerator import get_random_name
import pprint
from time import sleep


KEY_NAME = "22487668-key"
SG_NAME = "22487668-sg"
VPC_ID = "vpc-03c9fef49916d386a"


def stop_instances(ec2_client, instance_ids):
    print(f"Stopping {', '.join(instance_ids)}")
    ec2_client.stop_instances(InstanceIds=instance_ids)


def create_instances(ec2_resource, az):
    instances = ec2_resource.create_instances(
        ImageId="ami-d38a4ab1",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName=KEY_NAME,
        SecurityGroups=[SG_NAME],
        Placement={
            "AvailabilityZone": f"ap-southeast-2{az}"
        }
    )
    instance_ids = []
    for instance in instances:
        instance.wait_until_running()
        instance.create_tags(
            Tags=[{"Key": "Name", "Value": f"22487668_{az}"}]
        )
        instance_ids.append(instance.id)
        print(f"{instance.id}\t{instance.tags[0]['Value']} is running")
    return instance_ids


def get_subnet_ids(ec2_client, ids):
    subnet_ids = []
    instances = ec2_client.describe_instances(
        InstanceIds=instance_ids
    )["Reservations"]
    for instance in instances:
        instance = instance["Instances"][0]
        subnet_ids.append(instance["SubnetId"])
    return(subnet_ids)


def get_sg_id(ec2_client):
    resp = ec2_client.describe_security_groups(
        Filters=[
            {
                "Name": "group-name",
                "Values": SG_NAME
            }
        ]
    )
    print(resp)

def create_elb(elb, subnet_ids):
    resp = elb.create_load_balancer(
        Name="22487668-lb",
        Subnets=subnet_ids,
        SecurityGroups=[SG_NAME],
    )
    pprint.pprint(resp)


ec2_resource = boto3.resource("ec2")
ec2_client = boto3.client("ec2")
elbv2 = boto3.client("elbv2")


# instance_ids = []
# instance_ids.append(*create_instances(ec2_resource, "c"))
# instance_ids.append(*create_instances(ec2_resource, "b"))
# subnet_ids = get_subnet_ids(ec2_client, instance_ids)
# print(subnet_ids)
# try:
#     create_elb(elbv2, subnet_ids)
#     stop_instances(ec2_client, instance_ids)
# except Exception as e:
#     print(e)
#     stop_instances(ec2_client, instance_ids)

get_sg_id(ec2_client)



