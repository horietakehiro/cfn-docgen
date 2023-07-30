- [sample-template.yaml](#sample-templateyaml)
  - [Description](#description)
  - [Parameters](#parameters)
    - [General Params](#general-params)
      - [AppName](#appname)
      - [EnvType](#envtype)
  - [Mappings](#mappings)
    - [CidrBlockMap](#cidrblockmap)
  - [Conditions](#conditions)
    - [EnvCondition](#envcondition)
  - [Rules](#rules)
    - [RegionRule](#regionrule)
  - [Resources](#resources)
    - [IGW (AWS::EC2::VPC)](#igw-awsec2vpc)
    - [PublicRoute (AWS::EC2::Route)](#publicroute-awsec2route)
    - [PublicRouteTable (AWS::EC2::RouteTable)](#publicroutetable-awsec2routetable)
    - [PublicSubnet1 (AWS::EC2::Subnet)](#publicsubnet1-awsec2subnet)
    - [PublicSubnet2 (AWS::EC2::Subnet)](#publicsubnet2-awsec2subnet)
    - [PublicRtAssociation1 (AWS::EC2::SubnetRouteTableAssociation)](#publicrtassociation1-awsec2subnetroutetableassociation)
    - [PublicRtAssociation2 (AWS::EC2::SubnetRouteTableAssociation)](#publicrtassociation2-awsec2subnetroutetableassociation)
    - [VPC (AWS::EC2::VPC)](#vpc-awsec2vpc)
    - [IgwAttachment (AWS::EC2::VPCGatewayAttachment)](#igwattachment-awsec2vpcgatewayattachment)
  - [Outputs](#outputs)
    - [VpcId](#vpcid)
    - [PublicSubnetId1](#publicsubnetid1)
    - [PublicSubnetId2](#publicsubnetid2)
    - [ProdMessage](#prodmessage)

---

# sample-template.yaml

| | |
|-|-|
|AWSTemplateFormatVersion|2010-09-09|
|Description|This template creates 1 vpc and 2 public subnets.|
|Transform|-|

---

## Description

このテンプレートファイル東京リージョン上で以下のリソースを作成します
- VPC
- パブリックサブネット(2AZに1つずつ)

![Archtecture](./images/sample-template.drawio.png)


**注意点**
- このテンプレートファイルは**東京リージョン**上でのみの使用に制限しています
- このテンプレートファイルを使用する前に、[東京リージョン上に作成可能なVPCの最大数の設定](https://ap-northeast-1.console.aws.amazon.com/servicequotas/home/services/vpc/quotas/L-F678F1CE)を確認することを推奨します(デフォルトは5VPC)**

---

## Parameters

---

### General Params

---

#### AppName

This value is used as a part of each resources' name

|Type|Default|AllowedValues|AllowedPattern|NoEcho|MinValue|MaxValue|MinLength|MaxLength|ConstraintDescription|
|-|-|-|-|-|-|-|-|-|-|
|String|sample-app|-|-|false|-|-|1|20|-|-|

---

#### EnvType

This value is used as a part of each resources' name

|Type|Default|AllowedValues|AllowedPattern|NoEcho|MinValue|MaxValue|MinLength|MaxLength|ConstraintDescription|
|-|-|-|-|-|-|-|-|-|-|
|String|dev|<ul><li>dev</li><li>prod</li>|-|false|-|-|-|-|-|-|

---

## Mappings

---

### CidrBlockMap

CidrBlocks for each environment

|Map|Key|Value|
|-|-|-|
|dev|VPC|10.0.0.0/16|
|dev|PublicSubnet1|10.0.0.0/24|
|dev|PublicSubnet2|10.0.1.0/24|
|prod|VPC|10.10.0.0/16|
|prod|PublicSubnet1|10.10.0.0/24|
|prod|PublicSubnet2|10.10.1.0/24|

---

## Conditions

---

### EnvCondition

Check if the value of parameter `EnvType` is `prod`

|Condition|
|-|
|{<br/>&nbsp;&nbsp;"Fn::Equals": [<br/>&nbsp;&nbsp;&nbsp;&nbsp;{<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Ref": "EnvType"<br/>&nbsp;&nbsp;&nbsp;&nbsp;},<br/>&nbsp;&nbsp;&nbsp;&nbsp;"prod"<br/>&nbsp;&nbsp;]<br/>}|

---

## Rules

### RegionRule

This template is available only in ap-northeast-1

|RuleCondition|
|-|
|-|

|Assert|AssertDescription|
|-|-|
|{<br/>&nbsp;&nbsp;"Assert": {<br/>&nbsp;&nbsp;&nbsp;&nbsp;"Fn::Equals": [<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"AWS::Region",<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"ap-northeast-1"<br/>&nbsp;&nbsp;&nbsp;&nbsp;]<br/>&nbsp;&nbsp;}<br/>}|This template is available only in ap-northeast-1|

---

## Resources

---

### IGW (AWS::EC2::VPC)



https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-internetgateway.html

|DependsOn|Condition|CreationPolicy|UpdatePolicy|UpdateReplacePolicy|DeletionPolicy|
|-|-|-|-|-|-|
|-|-|-|-|Delete|Delete|

|Property|Value|Comment|Type|Required|UpdateType|
|-|-|-|-|-|-|
|Tags|-|-|List of Tag|false|Mutable|
|&nbsp;&nbsp;[0]Key|Name|-|String|true|Mutable|
|&nbsp;&nbsp;[0]Value|{<br/>&nbsp;&nbsp;"Fn::Sub": "\${AppName}-\${EnvType}-igw"<br/>}|-|String|true|Mutable|

---

### PublicRoute (AWS::EC2::Route)



https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-route.html

|DependsOn|Condition|CreationPolicy|UpdatePolicy|UpdateReplacePolicy|DeletionPolicy|
|-|-|-|-|-|-|
|-|-|-|-|Delete|Delete|

|Property|Value|Comment|Type|Required|UpdateType|
|-|-|-|-|-|-|
|CarrierGatewayId|-|-|String|false|Mutable|
|DestinationCidrBlock|0.0.0.0/0|-|String|true|Immutable|
|DestinationIpv6CidrBlock|-|-|String|false|Mutable|
|EgressOnlyInternetGatewayId|-|-|String|false|Mutable|
|GatewayId|{<br/>&nbsp;&nbsp;"Ref": "IGW"<br/>}|-|String|false|Mutable|
|InstanceId|-|-|String|false|Mutable|
|LocalGatewayId|-|-|String|false|Mutable|
|NatGatewayId|-|-|String|false|Mutable|
|NetworkInterfaceId|-|-|String|false|Mutable|
|RouteTableId|{<br/>&nbsp;&nbsp;"Ref": "PublicRouteTable"<br/>}|-|String|true|Immutable|
|TransitGatewayId|-|-|String|false|Mutable|
|VpcEndpointId|-|-|String|false|Mutable|
|VpcPeeringConnectionId|-|-|String|false|Mutable|

### PublicRouteTable (AWS::EC2::RouteTable)



https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-routetable.html

|DependsOn|Condition|CreationPolicy|UpdatePolicy|UpdateReplacePolicy|DeletionPolicy|
|-|-|-|-|-|-|
|<ul><li>IgwAttachment</li></ul>|-|-|-|Delete|Delete|

|Property|Value|Comment|Type|Required|UpdateType|
|-|-|-|-|-|-|
|Tags|-|-|List of Tag|false|Mutable|
|&nbsp;&nbsp;[0]Key|Name|-|String|true|Mutable|
|&nbsp;&nbsp;[0]Value|{<br/>&nbsp;&nbsp;"Fn::Sub": "\${AppName}-\${EnvType}-public-rt"<br/>}|-|String|true|Mutable|
|VpcId|{<br/>&nbsp;&nbsp;"Ref": "VPC"<br/>}|-|String|true|Immutable|

### PublicSubnet1 (AWS::EC2::Subnet)



https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html

|DependsOn|Condition|CreationPolicy|UpdatePolicy|UpdateReplacePolicy|DeletionPolicy|
|-|-|-|-|-|-|
|-|-|-|-|Delete|Delete|

|Property|Value|Comment|Type|Required|UpdateType|
|-|-|-|-|-|-|
|AssignIpv6AddressOnCreation|-|-|Boolean|false|Mutable|
|AvailabilityZone|{<br/>&nbsp;&nbsp;"Fn::Select": [<br/>&nbsp;&nbsp;&nbsp;&nbsp;0,<br/>&nbsp;&nbsp;&nbsp;&nbsp;{<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Fn::GetAZs": ""<br/>&nbsp;&nbsp;&nbsp;&nbsp;}<br/>&nbsp;&nbsp;]<br/>}|-|String|false|Immutable|
|AvailabilityZoneId|-|-|String|false|Immutable|
|CidrBlock|{<br/>&nbsp;&nbsp;"Fn::FindInMap": [<br/>&nbsp;&nbsp;&nbsp;&nbsp;"CidrBlockMap",<br/>&nbsp;&nbsp;&nbsp;&nbsp;{<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Ref": "EnvType"<br/>&nbsp;&nbsp;&nbsp;&nbsp;},<br/>&nbsp;&nbsp;&nbsp;&nbsp;"PublicSubnet1"<br/>&nbsp;&nbsp;]<br/>}|-|String|false|Immutable|
|EnableDns64|-|-|Boolean|false|Mutable|
|Ipv6CidrBlock|-|-|String|false|Immutable|
|Ipv6Native|-|-|Boolean|false|Immutable|
|MapPublicIpOnLaunch|true|-|Boolean|false|Mutable|
|OutpostArn|-|-|String|false|Immutable|
|PrivateDnsNameOptionsOnLaunch|-|-|PrivateDnsNameOptionsOnLaunch|false|Mutable|
|&nbsp;&nbsp;EnableResourceNameDnsAAAARecord|-|-|Boolean|false|Mutable|
|&nbsp;&nbsp;EnableResourceNameDnsARecord|-|-|Boolean|false|Mutable|
|&nbsp;&nbsp;HostnameType|-|-|String|false|Mutable|
|Tags|-|-|List of Tag|false|Mutable|
|&nbsp;&nbsp;[0]Key|Name|-|String|true|Mutable|
|&nbsp;&nbsp;[0]Value|{<br/>&nbsp;&nbsp;"Fn::Sub": "\${AppName}-\${EnvType}-public-subnet-1"<br/>}|-|String|true|Mutable|
|VpcId|{<br/>&nbsp;&nbsp;"Ref": "VPC"<br/>}|-|String|true|Immutable|

### PublicSubnet2 (AWS::EC2::Subnet)



https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnet.html

|DependsOn|Condition|CreationPolicy|UpdatePolicy|UpdateReplacePolicy|DeletionPolicy|
|-|-|-|-|-|-|
|-|-|-|-|Delete|Delete|

|Property|Value|Comment|Type|Required|UpdateType|
|-|-|-|-|-|-|
|AssignIpv6AddressOnCreation|-|-|Boolean|false|Mutable|
|AvailabilityZone|{<br/>&nbsp;&nbsp;"Fn::Select": [<br/>&nbsp;&nbsp;&nbsp;&nbsp;1,<br/>&nbsp;&nbsp;&nbsp;&nbsp;{<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Fn::GetAZs": ""<br/>&nbsp;&nbsp;&nbsp;&nbsp;}<br/>&nbsp;&nbsp;]<br/>}|-|String|false|Immutable|
|AvailabilityZoneId|-|-|String|false|Immutable|
|CidrBlock|{<br/>&nbsp;&nbsp;"Fn::FindInMap": [<br/>&nbsp;&nbsp;&nbsp;&nbsp;"CidrBlockMap",<br/>&nbsp;&nbsp;&nbsp;&nbsp;{<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;"Ref": "EnvType"<br/>&nbsp;&nbsp;&nbsp;&nbsp;},<br/>&nbsp;&nbsp;&nbsp;&nbsp;"PublicSubnet2"<br/>&nbsp;&nbsp;]<br/>}|-|String|false|Immutable|
|EnableDns64|-|-|Boolean|false|Mutable|
|Ipv6CidrBlock|-|-|String|false|Immutable|
|Ipv6Native|-|-|Boolean|false|Immutable|
|MapPublicIpOnLaunch|true|-|Boolean|false|Mutable|
|OutpostArn|-|-|String|false|Immutable|
|PrivateDnsNameOptionsOnLaunch|-|-|PrivateDnsNameOptionsOnLaunch|false|Mutable|
|&nbsp;&nbsp;EnableResourceNameDnsAAAARecord|-|-|Boolean|false|Mutable|
|&nbsp;&nbsp;EnableResourceNameDnsARecord|-|-|Boolean|false|Mutable|
|&nbsp;&nbsp;HostnameType|-|-|String|false|Mutable|
|Tags|-|-|List of Tag|false|Mutable|
|&nbsp;&nbsp;[0]Key|Name|-|String|true|Mutable|
|&nbsp;&nbsp;[0]Value|{<br/>&nbsp;&nbsp;"Fn::Sub": "\${AppName}-\${EnvType}-public-subnet-2"<br/>}|-|String|true|Mutable|
|VpcId|{<br/>&nbsp;&nbsp;"Ref": "VPC"<br/>}|-|String|true|Immutable|

### PublicRtAssociation1 (AWS::EC2::SubnetRouteTableAssociation)



https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnetroutetableassociation.html

|DependsOn|Condition|CreationPolicy|UpdatePolicy|UpdateReplacePolicy|DeletionPolicy|
|-|-|-|-|-|-|
|-|-|-|-|Delete|Delete|

|Property|Value|Comment|Type|Required|UpdateType|
|-|-|-|-|-|-|
|RouteTableId|{<br/>&nbsp;&nbsp;"Ref": "PublicRouteTable"<br/>}|-|String|true|Immutable|
|SubnetId|{<br/>&nbsp;&nbsp;"Ref": "PublicSubnet1"<br/>}|-|String|true|Immutable|

### PublicRtAssociation2 (AWS::EC2::SubnetRouteTableAssociation)



https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-subnetroutetableassociation.html

|DependsOn|Condition|CreationPolicy|UpdatePolicy|UpdateReplacePolicy|DeletionPolicy|
|-|-|-|-|-|-|
|-|-|-|-|Delete|Delete|

|Property|Value|Comment|Type|Required|UpdateType|
|-|-|-|-|-|-|
|RouteTableId|{<br/>&nbsp;&nbsp;"Ref": "PublicRouteTable"<br/>}|-|String|true|Immutable|
|SubnetId|{<br/>&nbsp;&nbsp;"Ref": "PublicSubnet2"<br/>}|-|String|true|Immutable|

---

### VPC (AWS::EC2::VPC)

アプリケーションサーバを稼働させるために使用するVPC

https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html

|DependsOn|Condition|CreationPolicy|UpdatePolicy|UpdateReplacePolicy|DeletionPolicy|
|-|-|-|-|-|-|
|-|-|-|-|Delete|Delete|

|Property|Value|Comment|Type|Required|UpdateType|
|-|-|-|-|-|-|
CidrBlock|{<br/>&nbsp;&nbsp;"Fn::FindInMap": [<br/>&nbsp;&nbsp;&nbsp;&nbsp;"CidrBlockMap",<br/>&nbsp;&nbsp;&nbsp;&nbsp;"EnvType",<br/>&nbsp;&nbsp;&nbsp;&nbsp;"VPC"<br/>&nbsp;&nbsp;]<br/>}|-|String|false|Immutable|
|EnableDnsHostnames|true|アプリケーションサーバのホスト名でパブリックIPを名前解決できるように有効化する|Boolean|false|Mutable|
|EnableDnsSupport|true|-|Boolean|false|Mutable|
|InstanceTenancy|-|-|String|false|Conditional|
|Ipv4IpamPoolId|-|-|String|false|Immutable|
|Ipv4NetmaskLength|-|-|Integer|false|Immutable|
|Tags|-|-|List of Tag|false|Mutable|
|&nbsp;&nbsp;[0]Key|Name|-|String|true|Mutable|
|&nbsp;&nbsp;[0]Value|{<br/>&nbsp;&nbsp;"Fn::Sub": "\${AppName}-\${EnvType}-vpc"<br/>}|-|String|true|Mutable|

---

### IgwAttachment (AWS::EC2::VPCGatewayAttachment)


https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc-gateway-attachment.html

|DependsOn|Condition|CreationPolicy|UpdatePolicy|UpdateReplacePolicy|DeletionPolicy|
|-|-|-|-|-|-|
|-|-|-|-|Delete|Delete|

|Property|Value|Comment|Type|Required|UpdateType|
|-|-|-|-|-|-|
|InternetGatewayId|{<br/>&nbsp;&nbsp;"Ref": "IGW"<br/>}|-|String|false|Mutable|
|VpcId|{<br/>&nbsp;&nbsp;"Ref": "VPC"<br/>}|-|String|true|Mutable|
|VpnGatewayId|-|-|String|false|Mutable|


---

## Outputs

---

### VpcId

vpc id

|Value|ExportName|Condition|
|-|-|-|
|{<br/>&nbsp;&nbsp;"Ref": "VPC"<br/>}|{<br/>&nbsp;&nbsp;"Fn::Sub": "\${AppName}-\${EnvType}-vpc-id"<br/>}|-|

---

### PublicSubnetId1

public subnet id 1

|Value|ExportName|Condition|
|-|-|-|
|{<br/>&nbsp;&nbsp;"Ref": "PublicSubnet1"<br/>}|-|-|

---

### PublicSubnetId2

public subnet id 2

|Value|ExportName|Condition|
|-|-|-|
|{<br/>&nbsp;&nbsp;"Ref": "PublicSubnet2"<br/>}|-|-|

---

### ProdMessage

public subnet id 1

|Value|ExportName|Condition|
|-|-|-|
|This template is deployed for PROD environment|-|EnvCondition|

---