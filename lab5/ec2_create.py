#!/usr/bin/env python3
"""
Simple script for creating two EC2 instances in two different
AZs and removing them

__author__ = "Eddie Atkinson"
__copyright__ = "Copyright 2020"
"""
import pprint
import boto3

# Set your keyname, security group name and VPC ID below

KEY_NAME = ""
SG_NAME = ""
VPC_ID = ""


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


def get_subnet_ids(ec2_client, instance_ids):
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
                "Values": [SG_NAME]
            }
        ]
    )["SecurityGroups"]
    if len(resp) == 0:
        return None
    else:
        return resp[0]["GroupId"]


def create_elb(elb, subnet_ids, sg_id):
    resp = elb.create_load_balancer(
        Name="22487668-lb",
        Subnets=subnet_ids,
        SecurityGroups=[sg_id],
    )["LoadBalancers"][0]
    return resp["LoadBalancerArn"]


def set_target_group(elb, instance_ids):
    resp = elb.create_target_group(
        Name="22487668-targetgroup",
        Protocol="HTTP",
        Port=80,
        VpcId=VPC_ID
    )["TargetGroups"]
    tg_arn = resp[0]["TargetGroupArn"]
    targets = [{"Id": id} for id in instance_ids]
    elb.register_targets(
        TargetGroupArn=tg_arn,
        Targets=targets
    )
    return tg_arn


def attach_listener(elb, elb_arn, tg_arn):
    resp = elb.create_listener(
        LoadBalancerArn=elb_arn,
        Protocol="HTTP",
        Port=80,
        DefaultActions=[{
            "Type": "forward",
            "TargetGroupArn": tg_arn
        }]
    )
    pprint.pprint(resp)


def main():
    ec2_resource = boto3.resource("ec2")
    ec2_client = boto3.client("ec2")
    elbv2 = boto3.client("elbv2")

    instance_ids = []
    instance_ids.append(*create_instances(ec2_resource, "c"))
    instance_ids.append(*create_instances(ec2_resource, "b"))
    subnet_ids = get_subnet_ids(ec2_client, instance_ids)
    try:
        sg_id = get_sg_id(ec2_client)
        elb_arn = create_elb(elbv2, subnet_ids, sg_id)
        tg_arn = set_target_group(elbv2, instance_ids)
        attach_listener(elbv2, elb_arn, tg_arn)
    except Exception as e:
        print(e)
        stop_instances(ec2_client, instance_ids)


if __name__ == "__main__":
    main()

