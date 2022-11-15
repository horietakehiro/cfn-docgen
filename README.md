# cfn-docgen

<!-- ![buildbadge](https://codebuild.ap-northeast-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoidERrRjdNRERUMWRqWGc5TW1VTGREYXJkQ1BKc2JremZsRS8vK21jdThTeWlTeEpaVTRJSHU0aVBVTHE2aDJudStCUXF6c2tFWlZQSnFiLzhta216dk1nPSIsIml2UGFyYW1ldGVyU3BlYyI6Ik95ZGR1VHBOZ0pqZUJXZWkiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=release) -->

---

cfn-docgen is a command line tool that generates the table formatted CloudFormation(cfn) definition file from the original, yaml or json formatted template file. 

---

## Example
If you have a yaml cfn template file like below, 
```Yaml
AWSTemplateFormatVersion: 2010-09-09
Description: sample vpc template
Parameters:
  EnvType:
    Description: env type
    Type: String
    Default: dev
Resources: 
  VPC:
    Type: AWS::EC2::VPC
    Metadata:
      UserNotes:
        ResourceNote: This is a note for VPC resource
        PropNotes:
          CidrBlock: This is a note for CidrBlock prop
          Tags[1].Value: This is a note for Value prop of 2nd Tags list prop
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsSupport: true
      Tags:
        - Key: ENV
          Value: !Ref EnvType
        - Key: Name
          Value: SampleVpc
```
you can generate a content like below.

| ResourceId   | ResourceType   | ResourceNote                    | Property           | Value              | UserNote                                            | Required   | Type        | UpdateType   | Description                                                                                     | IsOmittable   | Filename   |
|:-------------|:---------------|:--------------------------------|:-------------------|:-------------------|:----------------------------------------------------|:-----------|:------------|:-------------|:------------------------------------------------------------------------------------------------|:--------------|:-----------|
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | CidrBlock          | 10.0.0.0/16        | This is a note for CidrBlock prop                   | False      | String      | Immutable    | http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html         | False         | cfn.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | EnableDnsHostnames |                    |                                                     | False      | Boolean     | Mutable      | http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html         | True          | cfn.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | EnableDnsSupport   | True               |                                                     | False      | Boolean     | Mutable      | http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html         | False         | cfn.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | InstanceTenancy    |                    |                                                     | False      | String      | Mutable      | http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html         | True          | cfn.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | Ipv4IpamPoolId     |                    |                                                     | False      | String      | Immutable    | http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html         | True          | cfn.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | Ipv4NetmaskLength  |                    |                                                     | False      | Integer     | Immutable    | http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html         | True          | cfn.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | Tags               |                    |                                                     | False      | List of Tag | Mutable      | http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-ec2-vpc.html         | False         | cfn.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | Tags[0].Key        | ENV                |                                                     | True       | String      | Mutable      | http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html | False         | cfn.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | Tags[0].Value      | {'Ref': 'EnvType'} |                                                     | True       | String      | Mutable      | http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html | False         | cfn.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | Tags[1].Key        | Name               |                                                     | True       | String      | Mutable      | http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html | False         | cfn.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | Tags[1].Value      | SampleVpc          | This is a note for Value prop of 2nd Tags list prop | True       | String      | Mutable      | http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-resource-tags.html | False         | cfn.yaml   |



The key features of this tool are,

- All of the properties of each resource, including ones you omit to define, are listed in generated file.
  - In the example above, properties `EnableDnsHostnames`, `InstanceTenancy`, `Ipv4IpamPoolId`, and `Ipv4NetmaskLength` are omitted in original cfn template file, but listed in generated file.
<!-- - References for each resource and property listed at [official User Guide](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) are merged in generated file as columns `Required`, `Type`, `UpdateType`, and `Description`. -->
- You can add custom notes for each resource and property at `Metadata` section in each resource.
  - You can add custom note for a resource at `Metadata.UserNotes.ResourceNote`
  - You can add custom notes for properties at `Metadata.UserNotes.PropNotes.{PropertyName}`
    - For nested or list properties, you can specify `PropertyName` like `Tags[1].Value` .
- Not only `Resources` section in cfn template, this tool can also generate definitions of other sections, including `Parameters`, `Mappings`, and `Outputs` and resource policies like `CreationPolicy`, `UpdatePolicy`, `UpdateReplacePlocy`, `DeletionPolicy`, and `DependsOn`.
- You can generate files as excel, md, csv, or html format.
  - In excel format, all of definitions are separated by sheets. 
  - In other format, all of definitions are separated by files.

For more example, see [sample](./sample) directory.

---

## Basic command usage

```Bash
$ cfn-docgen --in sample/sample-template.json --fmt xlsx
```


---

## How to use

---

### CLI(Linux/Windows)

- Prerequirements
  - python>=3.8

```Bash
$ pip install cfn-docgen
```

---

### Docker

We also provide cfn-docgen as Docker image.

```Bash
# pull image from DockerHub
$ docker pull horietakehiro/cfn-docgen:latest

# local directory(before)
$ tree /tmp/sample/
/tmp/sample/
└── sample-template.json

0 directories, 1 files

# run as command
$ docker run \
  -v /tmp/sample/:/tmp/ \
  -v ~/.cfn-docgen/:/root/.cfn-docgen/ \
  horietakehiro/cfn-docgen:latest --in /tmp/sample-template.json --fmt xlsx

# local directory(after)
$ tree /tmp/sample/
/tmp/sample/
├── sample-template.json
└── sample-template.xlsx

0 directories, 2 files
```

---

### GUI(Windows only)

We also provide cfn-docgen as GUI application [here](https://github.com/horietakehiro/cfn-docgen-gui).

---

### serverless
You can also use cfn-docgen on AWS Cloud as serverless application.

You can deploy resources at [AWS Serverless Application Repository](https://ap-northeast-1.console.aws.amazon.com/lambda/home?region=ap-northeast-1#/create/app?applicationId=arn:aws:serverlessrepo:ap-northeast-1:382098889955:applications/cfn-docgen-serverless).

Once deployed, tha S3 bucket named `cfn-docgen-${AWS::AccountId}-${AWS::Region}` is created on your account. 

When you upload cfn template json/yaml files  at `templates/` folder of the bucket, cfn-docgen-serverless automatically will be triggered and generates excel docments for them.

---

### API

You can directry handle data as pandas DataFrame.

```Python
import pandas as pd
from cfn_docgen import cfn_def
cfn_template = cfn_def.CfnTemplate("./sample/sample-template.json")
property_df = cfn_template.to_df(cfn_template.resources, "Resources_Property")
assert isinstance(property_df, pd.DataFrame)
```

---