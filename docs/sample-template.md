# sample-template.yaml

| | |
|-|-|
|AWSTemplateFormatVersion|2010-09-09|
|Description|This template creates 1 vpc and 2 public subnets.|
|Transform|-|

---

## Table of Contents


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
|&nbsp;&nbsp;[0]Value|{<br/>&nbsp;&nbsp;"Fn::Sub": "${AppName}-${EnvType}-igw"<br/>}|-|String|true|Mutable|

---

### PublicRoute (AWS::EC2::Route)
### PublicRouteTable (AWS::EC2::RouteTable)
### PublicSubnet1 (AWS::EC2::Subnet)
### PublicSubnet2 (AWS::EC2::Subnet)
### PublicRtAssociation1 (AWS::EC2::SubnetRouteTableAssociation)
### PublicRtAssociation2 (AWS::EC2::SubnetRouteTableAssociation)

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
|&nbsp;&nbsp;[0]Value|{<br/>&nbsp;&nbsp;"Fn::Sub": "${AppName}-${EnvType}-vpc"<br/>}|-|String|true|Mutable|



---

## Outputs