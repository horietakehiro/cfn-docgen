import os
import json
import glob
from typing import List
from cfn_docgen import cfn_spec

def create_template_per_resources(save_dir:str)->List[str]:
    files = glob.glob(os.path.join(save_dir, "*.json"))
    if len(files):
        return files

    spec = cfn_spec.CfnSpecification()
    resource_types = [r for r in spec.spec["ResourceTypes"]]
    empty_template = {
        "AWSTemplateFormatVersion": "2010-09-09",
        "Description": "AWS CloudFormation Sample Template ElasticBeanstalk_in_VPC: Sample template showing how to create an Elastic Beanstalk environment in a VPC. The stack contains 2 subnets: the first subnet is public and contains the load balancer, a NAT device for internet access from the private subnet and a bastion host to allow SSH access to the Elastic Beanstalk hosts. The second subnet is private and contains the Elastic Beanstalk instances. You will be billed for the AWS resources used if you create a stack from this template.",
        "Resources": [],
    }
    resources = dict()
    for resource_type in resource_types:
        resources[resource_type.replace(":", "")] = {
            "Type": resource_type,
            "Properties": {}
        }

    os.makedirs(save_dir, exist_ok=True)
    for key, val in resources.items():
        path = os.path.join(save_dir, f"{key}.json") 
        empty_template["Resources"] = {key: val}
        with open(path, "w") as fp:
            json.dump(empty_template, fp, indent=4)    

    files = glob.glob(os.path.join(save_dir, "*.json"))
    return files
