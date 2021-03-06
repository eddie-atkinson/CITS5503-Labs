#!/usr/bin/env python3
"""
Simple boto script for interaction with EC2.

Creates N EC2 instances, prints their IP addresses, stops and terminates them.


__author__ = "Eddie Atkinson"
__copyright__ = "Copyright 2020"


"""
from time import sleep
import boto3
from namesgenerator import get_random_name

KEY_NAME = "YOUR KEY HERE"
SG_NAME = "YOUR SECURITY GROUP HERE"

def create_instances(ec2_resource, n_instances):
    """Creates n EC2 t2.micro instances in a given security group
    """
    instances = ec2_resource.create_instances(
        ImageId="ami-d38a4ab1",
        MinCount=1,
        MaxCount=n_instances,
        InstanceType="t2.micro",
        KeyName=KEY_NAME,
        SecurityGroups=[SG_NAME]
    )
    for instance in instances:
        instance.wait_until_running()
        instance.create_tags(
            Tags=[{"Key": "Name", "Value": f"{get_random_name()}"}]
        )
        print(f"{instance.id}\t{instance.tags[0]['Value']} is running")

    return instances


def stop_instances(ec2_resource, ec2_client, instances=None):
    """Stops all running EC2 instances in a given security group
    """
    print()
    if not instances:
        instances = list_instances(ec2_resource, ec2_client, "running")
    ids = [instance.id for instance in instances]
    # If there are no running instances return immediately
    if not ids:
        print("No running instances to stop")
        return
    response = ec2_client.stop_instances(InstanceIds=ids)
    print(
        f"Stop request status "
        f"{ response['ResponseMetadata']['HTTPStatusCode'] }"
    )



def list_instances(ec2_resource, ec2_client, state=""):
    """Prints and returns all instances in your security group
    in a given state or all instances if no state is specified
    """
    if state:
        instances = ec2_client.describe_instances(
            Filters=[
                {"Name": "instance.group-name", "Values": [SG_NAME]},
                {"Name": "instance-state-name", "Values": [state]}
            ]
        )
    else:
        instances = ec2_client.describe_instances(
            Filters=[
                {"Name": "instance.group-name", "Values": [SG_NAME]}
            ]
        )

    instances = instances["Reservations"]
    ids = [instances[i]["Instances"][0]["InstanceId"] for i in range(len(instances))]
    instance_objs = ec2_resource.instances.filter(
        InstanceIds=ids
    )
    return instance_objs


def terminate_stopped_instances(ec2_resource, ec2_client, instances=None):
    """Terminates all stopped instances in your security group
    """
    if not instances:
        instances = list_instances(ec2_resource, ec2_client, "stopped")
    for instance in instances:
        response = instance.terminate()
        status_code = response["ResponseMetadata"]["HTTPStatusCode"]
        if instance.tags:
            name = instance.tags[0]["Value"]
        else:
            name = "No name"
        print(
            f"Terminated instance {name} ({instance.id}) "
            f"with success status {status_code}"
        )

def print_public_ips(ec2_resource, ec2_client, instances=None):
    """Prints the public IP addresses of all running instances in your
    security group
    """
    print(
        f"\nPublic IP addresses for instances:\n"
    )
    if not instances:
        instances = list_instances(ec2_resource, ec2_client, "running")
    for instance in instances:
        if instance.tags:
            name = instance.tags[0]["Value"]
        else:
            name = "No name"
        print(
            f"{instance.id}\t"
            f"{name}\t"
            f"{instance.classic_address.public_ip}"
        )

def main():
    """ Starting point of execution for the program
    """
    ec2_resource = boto3.resource("ec2")
    ec2_client = boto3.client("ec2")
    create_instances(ec2_resource, 1)
    list_instances(ec2_resource, ec2_client)
    print_public_ips(ec2_resource, ec2_client)
    stop_instances(ec2_resource, ec2_client)
    terminate_stopped_instances(ec2_resource, ec2_client)


if __name__ == "__main__":
    main()
