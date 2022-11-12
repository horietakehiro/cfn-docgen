from copy import deepcopy
import os
import requests
import json
# from bs4 import BeautifulSoup
# import re
# import boto3

from cfn_docgen import util

logger = util.get_module_logger(__name__, util.get_verbose())

class FeatureSuppressError(Exception):
    pass


class CfnOutput(object):
    def __init__(self) -> None:
        pass
    
    def get_document_url(self):
        return "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/outputs-section-structure.html"

    def get_definition(self):
        return {
            "Description": {
                "Required": False,
                "Type": "String"
            },
            "Value": {
                "Required": True,
                "Type": "String",
            },
            "ExportName": {
                "Required": False,
                "Type": "String",
            }
        }

class CfnParameter(object):
    def __init__(self) -> None:
        pass
    
    def get_document_url(self):
        return "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/parameters-section-structure.html"

    def get_definition(self):
        return {
            "Description": {
                "Required": False,
                "Type": "String"
            },
            "MaxValue": {
                "Required": False,
                "Type": "Number"
            },
            "MinValue": {
                "Required": False,
                "Type": "Number"
            },
            "MaxLength": {
                "Required": False,
                "Type": "Number"
            },
            "MinLength": {
                "Required": False,
                "Type": "Number"
            },
            "AllowedPattern": {
                "Required": False,
                "Type": "String"
            },
            "AllowedValues": {
                "Required": False,
                "Type": "List"
            },
            "ConstraintDescription": {
                "Required": False,
                "Type": "String"
            },
            "Default": {
                "Required": False,
                "Type": "String"
            },
            "NoEcho": {
                "Required": False,
                "Type": "String"
            },
            "Type": {
                "Required": True,
                "Type": "String"
            }
        }

    def list_allowed_types(self):
        return [
            "String",
            "Number",
            "CommaDelimitedList",
            "List<Number>",
            "AWS::EC2::AvailabilityZone::Name",
            "AWS::SSM::Parameter::Name",
            "AWS::SSM::Parameter::Value<String>",
            "AWS::SSM::Parameter::Value<List<String>>",
            "AWS::SSM::Parameter::Value<CommaDelimitedList>",
            "AWS::EC2::Image::Id",
            "AWS::EC2::Instance::Id",
            "AWS::EC2::KeyPair::KeyName",
            "AWS::EC2::SecurityGroup::GroupName",
            "AWS::EC2::SecurityGroup::Id",
            "AWS::EC2::Subnet::Id",
            "AWS::EC2::VPC::Id",
            "AWS::Route53::HostedZone::Id",
            "List<AWS::EC2::AvailabilityZone::Name>",
            "List<AWS::EC2::Image::Id>",
            "List<AWS::EC2::Instance::Id>",
            "List<AWS::EC2::SecurityGroup::GroupName>",
            "List<AWS::EC2::SecurityGroup::Id>",
            "List<AWS::EC2::Subnet::Id>",
            "AWS::EC2::Volume::Id",
            "List<AWS::EC2::Volume::Id>",
            "List<AWS::EC2::VPC::Id>",
            "List<AWS::Route53::HostedZone::Id>",
            "AWS::SSM::Parameter::Value<AWS::EC2::AvailabilityZone::Name>",
            "AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>",
            "AWS::SSM::Parameter::Value<AWS::EC2::Instance::Id>",
            "AWS::SSM::Parameter::Value<AWS::EC2::KeyPair::KeyName>",
            "AWS::SSM::Parameter::Value<AWS::EC2::SecurityGroup::GroupName>",
            "AWS::SSM::Parameter::Value<AWS::EC2::SecurityGroup::Id>",
            "AWS::SSM::Parameter::Value<AWS::EC2::Subnet::Id>",
            "AWS::SSM::Parameter::Value<AWS::EC2::Volume::Id>",
            "AWS::SSM::Parameter::Value<AWS::EC2::VPC::Id>",
            "AWS::SSM::Parameter::Value<AWS::Route53::HostedZone::Id>",
            "AWS::SSM::Parameter::Value<List<AWS::EC2::AvailabilityZone::Name>>",
            "AWS::SSM::Parameter::Value<List<AWS::EC2::Image::Id>>",
            "AWS::SSM::Parameter::Value<List<AWS::EC2::Instance::Id>>",
            "AWS::SSM::Parameter::Value<List<AWS::EC2::KeyPair::KeyName>>",
            "AWS::SSM::Parameter::Value<List<AWS::EC2::SecurityGroup::GroupName>>",
            "AWS::SSM::Parameter::Value<List<AWS::EC2::SecurityGroup::Id>>",
            "AWS::SSM::Parameter::Value<List<AWS::EC2::Subnet::Id>>",
            "AWS::SSM::Parameter::Value<List<AWS::EC2::Volume::Id>>",
            "AWS::SSM::Parameter::Value<List<AWS::EC2::VPC::Id>>",
            "AWS::SSM::Parameter::Value<List<AWS::Route53::HostedZone::Id>>",
        ]

class CfnResourceAttribute(object):

    doc_url = "https://docs.aws.amazon.com/ja_jp/AWSCloudFormation/latest/UserGuide/aws-product-attribute-reference.html"

    def __init__(self) -> None:
        # self.doc = self._load_doc()
        self.allowrd_resources = self.get_allowed_resources()

    def _load_doc(self) -> str:
        raise NotImplementedError

        # local_filepath = os.path.join(util.CACHE_BASE_DIR, os.path.basename(self.doc_url))
        # if not os.path.exists(local_filepath):
        #     resp = requests.get(self.doc_url)
        #     with open(local_filepath, "w", encoding="utf-8") as fp:
        #         fp.write(resp.content.decode())
        
        # with open(local_filepath, "r", encoding="utf-8") as fp:
        #     raw = fp.read()
        # return raw


    def get_allowed_resources(self) -> list:
        raise NotImplementedError

        # soup = BeautifulSoup(self.doc, "html.parser")

        # list_items = soup.find_all("li", {"class": "listitem"})
        # resources = []
        # for item in list_items:
        #     resources.append(item.get_text(strip=True))

        # return resources

    def get_definition(self):
        raise NotImplementedError


class CfnUpdatePolicy(CfnResourceAttribute):

    doc_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatepolicy.html"

    def __init__(self) -> None:
        # self.doc = self._load_doc()
        self.allowed_resources = self.get_allowed_resources()

    def get_allowed_resources(self) -> list:
        return [
            "AWS::AppStream::Fleet",
            "AWS::AutoScaling::AutoScalingGroup",
            "AWS::ElastiCache::ReplicationGroup",
            "AWS::OpenSearchService::Domain",
            "AWS::Elasticsearch::Domain",
            "AWS::Lambda::Alias",
        ]



    def get_definition(self, resource_type:str) -> dict:
        if not resource_type in self.allowed_resources:
            return None
        
        if resource_type == "AWS::AppStream::Fleet":
            return {
                "StopBeforeUpdate": {
                    "Type": {
                        "Type": "Boolean",
                        "Required": "No",
                        "Default": "",
                        "Description": "",
                    },
                    "Description": "Stops the specified fleet before the update."
                },
                "StartAfterUpdate": {
                    "Type": {
                        "Type": "Boolean",
                        "Required": "No",
                        "Default": "",
                        "Description": "",
                    },
                    "Description": "Starts the specified fleet after the update."
                },
            }

        if resource_type == "AWS::AutoScaling::AutoScalingGroup":
            return {
                "AutoScalingReplacingUpdate" : {
                    "WillReplace" : {
                        "Type": "Boolean",
                        "Required": "No",
                        "Defaul": "",
                        "Description": "Specifies whether an Auto Scaling group and the instances it contains are replaced during an update. During replacement, CloudFormation retains the old group until it finishes creating the new one. If the update fails, CloudFormation can roll back to the old Auto Scaling group and delete the new Auto Scaling group. While CloudFormation creates the new group, it doesn't detach or attach any instances. After successfully creating the new Auto Scaling group, CloudFormation deletes the old Auto Scaling group during the cleanup process. When you set the WillReplace parameter, remember to specify a matching CreationPolicy. If the minimum number of instances (specified by the MinSuccessfulInstancesPercent property) don't signal success within the Timeout period (specified in the CreationPolicy policy), the replacement update fails and AWS CloudFormation rolls back to the old Auto Scaling group.",
                    },
                    "Description": "To specify how AWS CloudFormation handles replacement updates for an Auto Scaling group, use the AutoScalingReplacingUpdate policy. This policy enables you to specify whether AWS CloudFormation replaces an Auto Scaling group with a new one or replaces only the instances in the Auto Scaling group.",
                },
                "AutoScalingRollingUpdate" : {
                    "MaxBatchSize" : {
                        "Type": "Integer",
                        "Required": "No",
                        "Defaul": 1,
                        "Description": "Specifies the maximum number of instances that CloudFormation updates.",
                    },
                    "MinInstancesInService" : {
                        "Type": "Integer",
                        "Required": "No",
                        "Defaul": 0,
                        "Description": "Specifies the minimum number of instances that must be in service within the Auto Scaling group while CloudFormation updates old instances. This value must be less than the MaxSize of the Auto Scaling group.",
                    },
                    "MinSuccessfulInstancesPercent" : {
                        "Type": "Integer",
                        "Required": "No",
                        "Defaul": 100,
                        "Description": "Specifies the percentage of instances in an Auto Scaling rolling update that must signal success for an update to succeed. You can specify a value from 0 to 100. CloudFormation rounds to the nearest tenth of a percent. For example, if you update five instances with a minimum successful percentage of 50, three instances must signal success. If an instance doesn't send a signal within the time specified in the PauseTime property, CloudFormation assumes that the instance wasn't updated. If you specify this property, you must also enable the WaitOnResourceSignals and PauseTime properties. The MinSuccessfulInstancesPercent parameter applies only to instances only for signaling purpose. To specify the number of instances in your autoscaling group, see the MinSize, MaxSize, and DesiredCapacity properties for the AWS::AutoScaling::AutoScalingGroup resource.",
                    },
                    "PauseTime" : {
                        "Type": "String",
                        "Required": "No",
                        "Defaul": "PT0S (0 seconds). If the WaitOnResourceSignals property is set to true, the default is PT5M.",
                        "Description": "The amount of time that CloudFormation pauses after making a change to a batch of instances to give those instances time to start software applications. For example, you might need to specify PauseTime when scaling up the number of instances in an Auto Scaling group. If you enable the WaitOnResourceSignals property, PauseTime is the amount of time that CloudFormation should wait for the Auto Scaling group to receive the required number of valid signals from added or replaced instances. If the PauseTime is exceeded before the Auto Scaling group receives the required number of signals, the update fails. For best results, specify a time period that gives your applications sufficient time to get started. If the update needs to be rolled back, a short PauseTime can cause the rollback to fail. Specify PauseTime in the ISO8601 duration format (in the format PT#H#M#S, where each # is the number of hours, minutes, and seconds, respectively). The maximum PauseTime is one hour (PT1H)",
                    },
                    "SuspendProcesses" : {
                        "Type": "List of Auto Scaling processes",
                        "Required": "No",
                        "Defaul": "",
                        "Description": "Specifies the Auto Scaling processes to suspend during a stack update. Suspending processes prevents Auto Scaling from interfering with a stack update. For example, you can suspend alarming so that Amazon EC2 Auto Scaling doesn't initiate scaling policies associated with an alarm. For valid values, see the ScalingProcesses.member.N parameter for the SuspendProcesses action in the Amazon EC2 Auto Scaling API Reference.",
                    },
                    "WaitOnResourceSignals" : {
                        "Type": "Boolean",
                        "Required": "Conditional. If you specify the MinSuccessfulInstancesPercent property, you must also enable the WaitOnResourceSignals and PauseTime properties.",
                        "Defaul": False,
                        "Description": "Specifies whether the Auto Scaling group waits on signals from new instances during an update. Use this property to ensure that instances have completed installing and configuring applications before the Auto Scaling group update proceeds. AWS CloudFormation suspends the update of an Auto Scaling group after new EC2 instances are launched into the group. AWS CloudFormation must receive a signal from each new instance within the specified PauseTime before continuing the update. To signal the Auto Scaling group, use the cfn-signal helper script or SignalResource API. To have instances wait for an Elastic Load Balancing health check before they signal success, add a health-check verification by using the cfn-init helper script. For an example, see the verify_instance_health command in the Auto Scaling rolling updates sample template.",
                    },
                    "Description": "To specify how CloudFormation handles rolling updates for an Auto Scaling group, use the AutoScalingRollingUpdate policy. Rolling updates enable you to specify whether AWS CloudFormation updates instances that are in an Auto Scaling group in batches or all at once.",
                },
                "AutoScalingScheduledAction": {
                    "IgnoreUnmodifiedGroupSizeProperties" : {
                        "Type": "Boolean",
                        "Required": "No",
                        "Defaul": False,
                        "Description": "If true, AWS CloudFormation ignores differences in group size properties between your current Auto Scaling group and the Auto Scaling group described in the AWS::AutoScaling::AutoScalingGroup resource of your template during a stack update. If you modify any of the group size property values in your template, AWS CloudFormation uses the modified values and updates your Auto Scaling group.",
                    },
                    "Description": "To specify how AWS CloudFormation handles updates for the MinSize, MaxSize, and DesiredCapacity properties when the AWS::AutoScaling::AutoScalingGroup resource has an associated scheduled action, use the AutoScalingScheduledAction policy. With scheduled actions, the group size properties of an Auto Scaling group can change at any time. When you update a stack with an Auto Scaling group and scheduled action, CloudFormation always sets the group size property values of your Auto Scaling group to the values that are defined in the AWS::AutoScaling::AutoScalingGroup resource of your template, even if a scheduled action is in effect. If you don't want CloudFormation to change any of the group size property values when you have a scheduled action in effect, use the AutoScalingScheduledAction update policy and set IgnoreUnmodifiedGroupSizeProperties to true to prevent CloudFormation from changing the MinSize, MaxSize, or DesiredCapacity properties unless you have modified these values in your template.",
                },
            }
        
        if resource_type == "AWS::ElastiCache::ReplicationGroup":
            return {
                "UseOnlineResharding": {
                    "UseOnlineResharding": {
                        "Type": "Boolean",
                        "Required": "No",
                        "Default": "",
                        "Description": "To modify a replication group's shards by adding or removing shards, rather than replacing the entire AWS::ElastiCache::ReplicationGroup resource, use the UseOnlineResharding update policy.",
                    },
                    "Description": "To modify a replication group's shards by adding or removing shards, rather than replacing the entire AWS::ElastiCache::ReplicationGroup resource, use the UseOnlineResharding update policy."
                }
            }

        if resource_type in ["AWS::OpenSearchService::Domain", "AWS::Elasticsearch::Domain"]:
            return {
                "EnableVersionUpgrade": {
                    "EnableVersionUpgrade": {
                        "Type": "Boolean",
                        "Required": "No",
                        "Default": "",
                        "Description": "To upgrade an OpenSearch Service domain to a new version of OpenSearch or Elasticsearch rather than replacing the entire AWS::OpenSearchService::Domain or AWS::Elasticsearch::Domain resource, use the EnableVersionUpgrade update policy.",
                    },
                    "Description": "To upgrade an OpenSearch Service domain to a new version of OpenSearch or Elasticsearch rather than replacing the entire AWS::OpenSearchService::Domain or AWS::Elasticsearch::Domain resource, use the EnableVersionUpgrade update policy.",
                }
            }
        
        if resource_type == "AWS::Lambda::Alias":
            return {
                "CodeDeployLambdaAlias": {
                    "Description": "To perform an CodeDeploy deployment when the version changes on an AWS::Lambda::Alias resource, use the CodeDeployLambdaAliasUpdate update policy.",
                    "AfterAllowTrafficHook": {
                        "Type": "String",
                        "Required": "No",
                        "Default": "",
                        "Description": "The name of the Lambda function to run after traffic routing completes.",
                    },
                    "ApplicationName": {
                        "Type": "String",
                        "Required": "Yes",
                        "Default": "",
                        "Description": "The name of the CodeDeploy application.",
                    },
                    "BeforeAllowTrafficHook": {
                        "Type": "String",
                        "Required": "No",
                        "Default": "",
                        "Description": "The name of the Lambda function to run before traffic routing starts.",
                    },
                    "DeploymentGroupName": {
                        "Type": "String",
                        "Required": "No",
                        "Default": "",
                        "Description": "The name of the CodeDeploy deployment group. This is where the traffic-shifting policy is set.",
                    },
                }
            }



class CfnDeletionPolicy(CfnResourceAttribute):

    doc_url = "https://docs.aws.amazon.com/ja_jp/AWSCloudFormation/latest/UserGuide/aws-attribute-deletionpolicy.html"

    def __init__(self) -> None:
        # self.doc = self._load_doc()
        self.allowed_resources = self.get_allowed_resources()

    def get_allowed_resources(self) -> list:
        return [
            "AWS::EC2::Volume",
            "AWS::ElastiCache::CacheCluster",
            "AWS::ElastiCache::ReplicationGroup",
            "AWS::Neptune::DBCluster",
            "AWS::RDS::DBCluster",
            "AWS::RDS::DBInstance",
            "AWS::Redshift::Cluster",
        ]

    def get_definition(self, resource_type:str) -> dict:
        if not resource_type in self.allowed_resources:
            return None
        
        return {
            "Delete": {
                "Description": "CloudFormation deletes the resource and all its content if applicable during stack deletion. You can add this deletion policy to any resource type. By default, if you don't specify a DeletionPolicy, CloudFormation deletes your resources. However, be aware of the following considerations: For AWS::RDS::DBCluster resources, the default policy is Snapshot. For AWS::RDS::DBInstance resources that don't specify the DBClusterIdentifier property, the default policy is Snapshot. For Amazon S3 buckets, you must delete all objects in the bucket for deletion to succeed.",
            },
            "Retain": {
                "Description": "CloudFormation keeps the resource without deleting the resource or its contents when its stack is deleted. You can add this deletion policy to any resource type. When CloudFormation completes the stack deletion, the stack will be in Delete_Complete state; however, resources that are retained continue to exist and continue to incur applicable charges until you delete those resources. For update operations, the following considerations apply: If a resource is deleted, the DeletionPolicy retains the physical resource but ensures that it's deleted from CloudFormation's scope. If a resource is updated such that a new physical resource is created to replace the old resource, then the old resource is completely deleted, including from CloudFormation's scope.",
            },
            "Snapshot": {
                "Description": "For resources that support snapshots, CloudFormation creates a snapshot for the resource before deleting it. When CloudFormation completes the stack deletion, the stack will be in the Delete_Complete state; however, the snapshots that are created with this policy continue to exist and continue to incur applicable charges until you delete those snapshots.",
            }
        }


class CfnCreationPolicy(CfnResourceAttribute):

    doc_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-creationpolicy.html"

    def __init__(self) -> None:
        # self.doc = self._load_doc()
        self.allowed_resources = self.get_allowed_resources()

    def get_allowed_resources(self) -> list:
        return [
            "AWS::AppStream::Fleet",
            "AWS::AutoScaling::AutoScalingGroup",
            "AWS::EC2::Instance",
            "AWS::CloudFormation::WaitCondition",
        ]



    def get_definition(self, resource_type:str) -> dict:
        if not resource_type in self.allowed_resources:
            return None
        
        if resource_type == "AWS::AppStream::Fleet":
            return {
                "StartFleet": {
                    "Type": {
                        "Type": "Boolean",
                        "Required": "No",
                        "Default": "",
                        "Description": "",
                    },
                    "Description": "Starts the specified fleet."
                }
            }

        return {
            "AutoScalingCreationPolicy": {
                "MinSuccessfulInstancesPercent": {
                    "Type": "Integer",
                    "Required": "No",
                    "Default": 100,
                    "Description": "Specifies the percentage of instances in an Auto Scaling replacement update that must signal success for the update to succeed. You can specify a value from 0 to 100. CloudFormation rounds to the nearest tenth of a percent. For example, if you update five instances with a minimum successful percentage of 50, three instances must signal success. If an instance doesn't send a signal within the time specified by the Timeout property, CloudFormation assumes that the instance wasn't created.",
                },
                "Description": "For an Auto Scaling group replacement update, specifies how many instances must signal success for the update to succeed."
            },
            "ResourceSignal": {
                "Count": {
                    "Type": "Integer",
                    "Required": "No",
                    "Default": 1,
                    "Description": "The number of success signals CloudFormation must receive before it sets the resource status as CREATE_COMPLETE. If the resource receives a failure signal or doesn't receive the specified number of signals before the timeout period expires, the resource creation fails and CloudFormation rolls the stack back.",
                },
                "Timeout": {
                    "Type": "String",
                    "Required": "No",
                    "Default": "PT5M",
                    "Description": "The length of time that CloudFormation waits for the number of signals that was specified in the Count property. The timeout period starts after CloudFormation starts creating the resource, and the timeout expires no sooner than the time you specify but can occur shortly thereafter. The maximum time that you can specify is 12 hours. The value must be in ISO8601 duration format, in the form: PT#H#M#S, where each # is the number of hours, minutes, and seconds, respectively. For best results, specify a period of time that gives your instances plenty of time to get up and running. A shorter timeout can cause a rollback.",
                },
                "Description": "When CloudFormation creates the associated resource, configures the number of required success signals and the length of time that CloudFormation waits for those signals."
            }
        }



class CfnUpdateReplacePolicy(CfnResourceAttribute):

    doc_url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatereplacepolicy.html"

    def __init__(self) -> None:
        # self.doc = self._load_doc()
        self.allowed_resources = self.get_allowed_resources()
    
    def get_allowed_resources(self) -> list:
        return [
            "AWS::EC2::Volume",
            "AWS::ElastiCache::CacheCluster",
            "AWS::ElastiCache::ReplicationGroup",
            "AWS::Neptune::DBCluster",
            "AWS::RDS::DBCluster",
            "AWS::RDS::DBInstance",
            "AWS::Redshift::Cluster",
        ]


    def get_definition(self, resource_type:str) -> dict:
        if not resource_type in self.allowed_resources:
            return None
        
        return {
            "Delete": {
                "Description": "CloudFormation deletes the resource and all its content if applicable during resource replacement. You can add this policy to any resource type. By default, if you don't specify an UpdateReplacePolicy, CloudFormation deletes your resources. However, be aware of the following consideration: For Amazon S3 buckets, you must delete all objects in the bucket for deletion to succeed.",
            },
            "Retain": {
                "Description": "CloudFormation keeps the resource without deleting the resource or its contents when the resource is replaced. You can add this policy to any resource type. Resources that are retained continue to exist and continue to incur applicable charges until you delete those resources. If a resource is replaced, the UpdateReplacePolicy retains the old physical resource but removes it from CloudFormation's scope.",
            },
            "Snapshot": {
                "Description": "For resources that support snapshots, CloudFormation creates a snapshot for the resource before deleting it. Snapshots that are created with this policy continue to exist and continue to incur applicable charges until you delete those snapshots.",
            }
        }



class CfnSpecification(object):

    spec_url_by_region = {
        "us-east-2": "https://dnwj8swjjbsbt.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "us-east-1": "https://d1uauaxba7bl26.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "us-west-1": "https://d68hl49wbnanq.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "us-west-2": "https://d201a2mn26r7lk.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "af-south-1": "https://cfn-resource-specifications-af-south-1-prod.s3.af-south-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-east-1": "https://cfn-resource-specifications-ap-east-1-prod.s3.ap-east-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-southeast-3": "https://cfn-resource-specifications-ap-southeast-3-prod.s3.ap-southeast-3.amazonaws.com/latest/CloudFormationResourceSpecification.json",
        "ap-south-1": "https://d2senuesg1djtx.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-northeast-2": "https://d1ane3fvebulky.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-southeast-1": "https://doigdx0kgq9el.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-southeast-2": "https://d2stg8d246z9di.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-northeast-1": "https://d33vqc0rt9ld30.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "ap-northeast-3": "https://d2zq80gdmjim8k.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "ca-central-1": "https://d2s8ygphhesbe7.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "cn-north-1": "https://cfn-resource-specifications-cn-north-1-prod.s3.cn-north-1.amazonaws.com.cn/latest/gzip/CloudFormationResourceSpecification.json",
        "cn-northwest-1": "https://cfn-resource-specifications-cn-northwest-1-prod.s3.cn-northwest-1.amazonaws.com.cn/latest/gzip/CloudFormationResourceSpecification.json",
        "eu-central-1": "https://d1mta8qj7i28i2.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "eu-west-1": "https://d3teyb21fexa9r.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "eu-west-2": "https://d1742qcu2c1ncx.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "eu-west-3": "https://d2d0mfegowb3wk.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "eu-north-1": "https://diy8iv58sj6ba.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "eu-south-1": "https://cfn-resource-specifications-eu-south-1-prod.s3.eu-south-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json",
        "me-south-1": "https://cfn-resource-specifications-me-south-1-prod.s3.me-south-1.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json",
        "sa-east-1": "https://d3c9jyj3w509b0.cloudfront.net/latest/gzip/CloudFormationResourceSpecification.json",
        "us-gov-east-1": "https://s3.us-gov-east-1.amazonaws.com/cfn-resource-specifications-us-gov-east-1-prod/latest/CloudFormationResourceSpecification.json",
        "us-gov-west-1": "https://s3.us-gov-west-1.amazonaws.com/cfn-resource-specifications-us-gov-west-1-prod/latest/CloudFormationResourceSpecification.json",
    }

    spec_cach_by_region = dict()


    def __init__(self, filepath:str=None, region_name:str=None) -> None:
        self.filepath = filepath
        self.region_name = self.get_region_name(region_name)
        self.spec = dict()
        self.spec = self.load_spec()
        # try:
        #     self.spec = self.spec_cach_by_region[self.region_name]
        # except KeyError:
        #     self.spec_cach_by_region[self.region_name] = self.load_spec()
        #     self.spec = self.spec_cach_by_region[self.region_name]

        logger.info(f"spec for {self.region_name} loaded")

        self.html_cache = dict()


    def get_region_name(self, region_name:str):
        """
        if region_name are given, use it.
        if region_name are not given, firstly check the environment variable AWS_REGION,
        secondly, check the aws cli profile
        """
        if region_name:
            logger.debug(f"get region name from argument: {region_name}")
            return region_name
        
        region_name = os.environ.get("CFN_DOCGEN_AWS_REGION", "ap-northeast-1")
        logger.debug(f"get region name from environment variable CFN_DOCGEN_AWS_REGION : {region_name}")
        return region_name


    def load_spec(self) -> dict:
        """
        load spec file from local file.
        if local file does not specified, default is '~/.cfn-docgen/cache/AWS_REGION/CloudFormationResourceSpecification.json'.
        if local filep does not exists, firstly download it.
        """
        if self.filepath is None:
            cache_dir = os.path.join(util.CACHE_BASE_DIR, self.region_name)
            self.filepath = os.path.join(cache_dir, "CloudFormationResourceSpecification.json")
        
        # make sure the directory already created
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        
        if not os.path.exists(self.filepath):
            url = self.spec_url_by_region[self.region_name]
            resp = requests.get(url)

            with open(self.filepath, "w", encoding="utf-8") as fp:
                fp.write(resp.content.decode())
            logger.debug(f"download cfn spec file from {url}")

        with open(self.filepath, "r", encoding="utf-8") as fp:
            spec =  json.load(fp)
        logger.debug(f"load cfn spec from {self.filepath}")
        return spec


    def get_custom_resource_spec(self, name:str, defs:dict):
        base_spec = self.spec["ResourceTypes"]["AWS::CloudFormation::CustomResource"]
        base_spec = self.get_detailed_resource_spec("AWS::CloudFormation::CustomResource", base_spec)

        custom_spec = deepcopy(base_spec)
        for key in defs["Properties"].keys():
            if key == "ServiceToken":
                continue
            custom_spec["Properties"][key] = {}

        return custom_spec


    def get_resource_spec(self, resource_name:str, resource_def:dict=None) -> dict:
        """
        return a specified resource spec
        """
        try:
            if resource_name.startswith("Custom::") or resource_name == "AWS::CloudFormation::CustomResource":
                custom_resource_spec = self.get_custom_resource_spec(resource_name, resource_def)
                return custom_resource_spec
            
            ret_spec = self.spec["ResourceTypes"][resource_name]
            ret_spec = self.get_detailed_resource_spec(resource_name, ret_spec)
            return ret_spec

        except Exception as ex:
            logger.error(f"get resource spec for {resource_name} failed : {type(ex)} {ex}")
            raise ex
        

    def get_property_spec(self, resource_name:str, property_name:str=None) -> dict:
        """
        return a property spec of specified resource
        property_name, if specified, must be the format like 'AWS::S3::Bucket.CorsRule'
        """
        try:
            if property_name is not None:
                try:
                    ret_spec = {property_name: self.spec["PropertyTypes"][property_name]}
                    # return {property_name: self.spec["PropertyTypes"][property_name]["Properties"]}
                except KeyError:
                    return {property_name: {"Properties": {}}}
            else:
                match_keys = filter(
                    lambda key: key.startswith(f"{resource_name}."),
                    self.spec["PropertyTypes"].keys()
                )
                ret_spec = {key: self.spec["PropertyTypes"][key] for key in match_keys}

            ret_spec = self.get_detailed_prop_spec(resource_name, ret_spec, property_name)
        except Exception as ex:
            logger.error(f"get property spec for {resource_name}/{property_name} failed : {type(ex)} {ex}")
            raise ex
        return ret_spec



    def get_attribute_spec(self, resource_name:str) -> dict:
        """
        return a specified resource attribute spec
        """
        try:
            if resource_name.startswith("Custom::") or resource_name == "AWS::CloudFormation::CustomResource":
                return {}
            
            ret_spec = self.spec["ResourceTypes"][resource_name]["Attributes"]
            return ret_spec
        except KeyError as ex:
            logger.warning(f"resource attribute for {resource_name} not found : {type(ex)} {ex}")
            return {}

        except Exception as ex:
            logger.error(f"get resource spec for {resource_name} failed : {type(ex)} {ex}")
            raise ex
        

    # def load_html(self, doc_url:str):
    #     """
    #     load the html file and return it as BeautifulSoup object
    #     if the html file does not exist, downalod it from the url
    #     if the BeautifulSoup object of the html file cached in memory, return it
    #     """
    #     try:
    #         soup = self.html_cache[doc_url]
    #     except KeyError:
    #         filepath = os.path.join(
    #             util.CACHE_BASE_DIR, os.path.basename(doc_url),
    #         )
    #         if not os.path.exists(filepath):
    #             resp = requests.get(doc_url)
    #             with open(filepath, "w", encoding="utf-8") as fp:
    #                 fp.write(resp.content.decode())
    #             logger.debug(f"download cfn reference file from {doc_url}")        
    #         with open(filepath, "r", encoding="utf-8") as fp:
    #             doc_body = fp.read()
    #         soup = BeautifulSoup(doc_body, "html.parser")
    #         self.html_cache[doc_url] = soup
    #     return soup

    def is_except_resource(self, resource_type:str, prop_type:str) -> bool:
        if resource_type == "AWS::IoTWireless::TaskDefinition" and prop_type == "LoRaWANUpdateGatewayTaskEntry":
            return True
        if resource_type == "AWS::IoTWireless::TaskDefinition" and prop_type == "TaskDefinitionType":
            return True
        if resource_type == "AWS::OpsWorks::Instance.EbsBlockDevice":
            return True
        if resource_type == "AWS::SageMaker::ModelBiasJobDefinition" and prop_type == "EndpointName":
            return True
        if resource_type == "AWS::SageMaker::ModelQualityJobDefinition" and prop_type == "EndpointName":
            return True
        if resource_type == "AWS::SageMaker::DataQualityJobDefinition" and prop_type == "EndpointName":
            return True
        if resource_type == "AWS::SageMaker::ModelExplainabilityJobDefinition" and prop_type == "EndpointName":
            return True
        if resource_type == "AWS::ApplicationInsights::Application" and prop_type == "GroupingType":
            return True
        if resource_type.startswith("AWS::SageMaker::EndpointConfig.Clarify"):
            return True
        if resource_type == "AWS::ElasticLoadBalancingV2::Listener.AuthenticateOidcConfig" and prop_type == "UseExistingClientSecret":
            return True

    def get_detailed_resource_spec(self, resource_name:str, resource_spec:dict) -> dict:
        """
        add detailed spec information from its CloudFormation User Guide page
        """

        
        if os.environ.get("CFN_DOCGEN_GET_DETAIL", "FALSE") != "TRUE":
            doc_url = resource_spec.get("Documentation", "-")
            new_prop_spec = dict()
            for prop_id, prop in resource_spec["Properties"].items():
                prop["DocDescription"] = doc_url
                prop["DocRequired"] = prop.get("Required", "-")
                prop["DocUpdate requires"] = prop.get("UpdateType", "-")
                if prop.get("PrimitiveType", ""):
                    prop["DocType"] = prop["PrimitiveType"]
                elif prop.get("Type", ""):
                    if prop.get("PrimitiveItemType", ""):
                        prop["DocType"] = prop["Type"] + " of " + prop["PrimitiveItemType"]
                    elif prop.get("ItemType", ""):
                        prop["DocType"] = prop["Type"] + " of " + prop["ItemType"]
                    else:
                        prop["DocType"] = prop["Type"]
                else:
                    prop["DocType"] = "-"

                new_prop_spec[prop_id] = prop
            
            resource_spec["Properties"] = new_prop_spec

            return resource_spec

        else:
            raise FeatureSuppressError("The feature about CFN_DOCGEN_GET_DETAIL is now suppressed.")
            

        # # load html 
        # doc_url = resource_spec["Documentation"]
        # doc_url = self.modify_doc_url(resource_name, doc_url)
        # soup = self.load_html(doc_url)
        
        # new_prop_spec = dict()
        # prop_id, prop_html_id, = None, None
        # try:
        #     for prop_id, prop in resource_spec["Properties"].items():
        #         prop_html_id = prop["Documentation"].split("#")[-1]
        #         try:
        #             paragraphs = soup.find("a", {"id": prop_html_id}).parent.next_sibling.find_all("p")
        #         except AttributeError:
        #             try:
        #                 paragraphs = soup.find("a", {"id": prop_html_id}).parent.next_sibling.next_sibling.find_all("p")
        #             except AttributeError as ex:
        #                 # if self.is_except_resource(resource_name, prop_id):
        #                 #     continue
        #                 # else:
        #                 #     raise ex
        #                 fail_msg = f"get detailed resource spec for {resource_name}/{prop_id}/{prop_html_id} from {doc_url} failed"
        #                 logger.warning(fail_msg)
        #                 prop["DocDescription"] = fail_msg
        #                 paragraphs = ""
        #         for i, p in enumerate(paragraphs):
        #             # get description
        #             if i == 0:
        #                 description = p.get_text()
        #                 description = re.sub(r"\s\s+", " ", description.replace("\n", ""))
        #                 key, value = "Description", description
        #             else:
        #                 try:
        #                     key, value = p.get_text().split(": ")
        #                 except ValueError:
        #                     continue
        #             prop[f"Doc{key}"] = value
        #         new_prop_spec[prop_id] = prop
        #     resource_spec["Properties"] = new_prop_spec
        # except Exception as ex:
        #     logger.error(f"get detailed resource spec for {resource_name}/{prop_id}/{prop_html_id} from {doc_url} failed : {type(ex)} {ex}")
        #     raise ex
        
        # return resource_spec


    def modify_doc_url(self, property_type:str, doc_url:str) ->str:
        prev_url = doc_url
        if property_type == "AWS::EC2::SecurityGroup.Ingress":
            doc_url = doc_url.replace(".html", "-1.html")

        if property_type == "AWS::AutoScaling::AutoScalingGroup.LaunchTemplateOverrides":
            doc_url = doc_url.replace(
                "cfn-as-mixedinstancespolicy-launchtemplateoverrides.html",
                "aws-properties-autoscaling-autoscalinggroup-launchtemplateoverrides.html",
            )
        if property_type == "AWS::AutoScaling::AutoScalingGroup.InstancesDistribution":
            doc_url = doc_url.replace(
                "cfn-as-mixedinstancespolicy-instancesdistribution.html",
                "aws-properties-autoscaling-autoscalinggroup-instancesdistribution.html",
            )
        if property_type == "AWS::AutoScaling::AutoScalingGroup.InstanceRequirements":
            doc_url = doc_url.replace(
                "cfn-as-mixedinstancespolicy-instancerequirements.html",
                "aws-properties-autoscaling-autoscalinggroup-instancerequirements.html",
            )
        if property_type == "AWS::AutoScaling::AutoScalingGroup.MixedInstancesPolicy":
            doc_url = doc_url.replace(
                "cfn-as-group-mixedinstancespolicy.html",
                "aws-properties-autoscaling-autoscalinggroup-mixedinstancespolicy.html",
            )
        if property_type == "AWS::AutoScaling::AutoScalingGroup.LaunchTemplate":
            doc_url = doc_url.replace(
                "cfn-as-mixedinstancespolicy-launchtemplate.html",
                "aws-properties-autoscaling-autoscalinggroup-launchtemplate.html",
            )

        if property_type == "AWS::RDS::DBParameterGroup":
            doc_url = doc_url.replace(
                "aws-properties-rds-dbparametergroup.html",
                "aws-resource-rds-dbparametergroup.html"
            )

        if property_type == "AWS::EC2::CustomerGateway":
            doc_url = doc_url.replace(
                "aws-resource-ec2-customergateway.html",
                "aws-resource-ec2-customer-gateway.html",
            )

        if prev_url != doc_url:
            logger.debug(f"modify doc url from {prev_url} to {doc_url}")
        return doc_url


    def modify_html_id(self, html_id:str, resource_type:str=None) -> str:
        prev_html_id = html_id
        if html_id == "cfn-as-group-launchtemplate":
            html_id = "cfn-as-group-launchtemplate-launchtemplatespecification"
        elif html_id == "cfn-as-mixedinstancespolicy-overrides":
            html_id = "cfn-as-group-launchtemplate-overrides"
        elif html_id == "cfn-route53-recordset-geolocation-continentcode":
            html_id = "cfn-route53-recordsetgroup-geolocation-continentcode"

        if resource_type is not None and resource_type != "AWS::WAF::ByteMatchSet":

            if html_id == "cfn-waf-sizeconstraintset-sizeconstraint-fieldtomatch-data":
                html_id = "cfn-waf-bytematchset-bytematchtuples-fieldtomatch-data"
            elif html_id == "cfn-waf-sizeconstraintset-sizeconstraint-fieldtomatch-type":
                html_id = "cfn-waf-bytematchset-bytematchtuples-fieldtomatch-type"
            elif html_id == "cfn-waf-bytematchset-bytematchtuples-fieldtomatch-data":
                html_id = "cfn-waf-sizeconstraintset-sizeconstraint-fieldtomatch-data"
            elif html_id == "cfn-waf-bytematchset-bytematchtuples-fieldtomatch-type":
                html_id = "cfn-waf-sizeconstraintset-sizeconstraint-fieldtomatch-type"



        elif html_id == "cfn-opsworks-custcookbooksource-pw":
            html_id = "cfn-opsworks-custcookbooksource-password"

        if prev_html_id != html_id:
            logger.debug(f"modify html id from {prev_html_id} to {html_id}")
        return html_id


    def get_detailed_prop_spec(self, resource_name:str, prop_spec:dict, property_name:str=None) -> dict:
        """
        add detailed spec information from cfn reference pages
        """
        if os.environ.get("CFN_DOCGEN_GET_DETAIL", "FALSE") != "TRUE":
            new_prop_spec = dict()
            property_type, prop_id, prop_html_id = None, None, None
            for property_type, properties in prop_spec.items():
                new_prop = dict()
                new_prop["Properties"] = dict()

                doc_url = properties.get("Documentation", "-")
                if properties.get("Properties") is None:
                    prop_id = property_type.split(".")[-1]
                    properties["DocDescription"] = doc_url
                    properties["DocRequired"] = properties.get("Required", "-")
                    properties["DocUpdate requires"] = properties.get("UpdateType", "-")
                    if properties.get("PrimitiveType", ""):
                        properties["DocType"] = properties["PrimitiveType"]
                    elif properties.get("Type", ""):
                        if properties.get("PrimitiveItemType", ""):
                            properties["DocType"] = properties["Type"] + " of " + properties["PrimitiveItemType"]
                        elif properties.get("ItemType", ""):
                            properties["DocType"] = properties["Type"] + " of " + properties["ItemType"]
                        else:
                            properties["DocType"] = properties["Type"]

                    else:
                        properties["DocType"] = "-"

                    new_prop["Properties"][prop_id] = properties
                    new_prop_spec[property_type] = deepcopy(new_prop)
                else:
                    for prop_id, prop in properties["Properties"].items():
                        prop["DocDescription"] = doc_url
                        prop["DocRequired"] = prop.get("Required", "-")
                        prop["DocUpdate requires"] = prop.get("UpdateType", "-")
                        if prop.get("PrimitiveType", ""):
                            prop["DocType"] = prop["PrimitiveType"]
                        elif prop.get("Type", ""):
                            if prop.get("PrimitiveItemType", ""):
                                prop["DocType"] = prop["Type"] + " of " + prop["PrimitiveItemType"]
                            elif prop.get("ItemType", ""):
                                prop["DocType"] = prop["Type"] + " of " + prop["ItemType"]
                            else:
                                prop["DocType"] = prop["Type"]
                        else:
                            prop["DocType"] = "-"

                        properties["Properties"][prop_id] = prop

                    
                    new_prop_spec[property_type] = properties
            return new_prop_spec

        else:
            raise FeatureSuppressError("The feature about CFN_DOCGEN_GET_DETAIL is now suppressed.")


        # new_prop_spec = dict()
        # property_type, prop_id, prop_html_id = None, None, None
        # for property_type, properties in prop_spec.items():

        #     try:
        #         doc_url = properties["Documentation"]
        #         doc_url = self.modify_doc_url(property_type, doc_url)

        #         soup = self.load_html(doc_url)

        #         if properties.get("Properties") is None:
        #             prop = deepcopy(properties)
        #             prop_id = property_type.split(".")[-1]
        #             # prop["Properties"] = dict()
        #             new_prop = dict()
        #             new_prop["Properties"] = dict()
        #             prop_html_id = os.path.basename(prop["Documentation"]).split(".")[0]
        #             prop_html_id = self.modify_html_id(prop_html_id, resource_name)

        #             try:
        #                 paragraphs = soup.find("h1", {"id": prop_html_id}).next_sibling.next_siblings
        #             except AttributeError as ex:
        #                 # if self.is_except_resource(property_type, prop_id):
        #                 #     continue
        #                 # else:
        #                 #     logger.error(f"get detailed property spec for {resource_name}/{property_name}/{property_type}/{prop_id}/{prop_html_id} : {type(ex)} {ex}")
        #                 #     raise ex
        #                 fail_msg = f"get detailed property spec for {resource_name}/{property_name}/{property_type}/{prop_id}/{prop_html_id} from {doc_url} failed"
        #                 logger.warning(fail_msg)
        #                 prop["DocDescription"] = fail_msg
        #                 paragraphs = ""

        #             for i, p in enumerate(paragraphs):
        #                 # get description
        #                 if i == 0:
        #                     description = p.get_text()
        #                     description = re.sub(r"\s\s+", " ", description.replace("\n", ""))
        #                     key, value = "Description", description
        #                 else:
        #                     try:
        #                         text = p.get_text()
        #                         key, value = text.split(": ")
        #                     except ValueError as ex:
        #                         additional_description = re.sub(r"\s\s+", " ", text.replace("\n", ""))
        #                         key, value = "Description", prop.get("DocDescription", "") + "\n" + additional_description
        #                         pass
        #                 prop[f"Doc{key}"] = value
        #             new_prop["Properties"][prop_id] = prop
        #             new_prop_spec[property_type] = deepcopy(new_prop)
        #         else:

        #             for prop_id, prop in properties["Properties"].items():
        #                 prop_html_id = prop["Documentation"].split("#")[-1]
        #                 prop_html_id = self.modify_html_id(prop_html_id, resource_name)

        #                 # logger.debug(f"{property_type}/{prop_id}")

        #                 try:
        #                     paragraphs = soup.find("a", {"id": prop_html_id}).parent.next_sibling.find_all("p")
        #                 except AttributeError:
        #                     try:
        #                         paragraphs = soup.find("a", {"id": prop_html_id}).parent.next_sibling.next_sibling.find_all("p")
        #                     except AttributeError as ex:
        #                         # if self.is_except_resource(property_type, prop_id):
        #                         #     continue
        #                         # else:
        #                         #     logger.error(f"get detailed property spec for {resource_name}/{property_name}/{property_type}/{prop_id}/{prop_html_id} : {type(ex)} {ex}")
        #                         #     raise ex
        #                         fail_msg = f"get detailed property spec for {resource_name}/{property_name}/{property_type}/{prop_id}/{prop_html_id} from {doc_url} failed"
        #                         logger.warning(fail_msg)
        #                         prop["DocDescription"] = fail_msg
        #                         paragraphs = ""
        #                 for i, p in enumerate(paragraphs):
        #                     # get description
        #                     if i == 0:
        #                         description = p.get_text()
        #                         description = re.sub(r"\s\s+", " ", description.replace("\n", ""))
        #                         key, value = "Description", description
        #                     else:
        #                         try:
        #                             text = p.get_text()
        #                             key, value = text.split(": ")
        #                         except ValueError as ex:
        #                             # logger.debug(f"a skippable error occured {resource_name}/{property_name}/{property_type}/{prop_id} : {type(ex)} {ex}")
        #                             additional_description = re.sub(r"\s\s+", " ", text.replace("\n", ""))
        #                             key, value = "Description", prop.get("DocDescription", "") + "\n" + additional_description
        #                             pass
        #                     prop[f"Doc{key}"] = value
        #                 properties["Properties"][prop_id] = prop

                    
        #             new_prop_spec[property_type] = properties
        #     except Exception as ex:
        #         logger.error(f"get detailed property spec for {resource_name}/{property_name}/{property_type}/{prop_id}/{prop_html_id} from {doc_url} failed : {type(ex)} {ex}")
        #         raise ex
            
        # return new_prop_spec


