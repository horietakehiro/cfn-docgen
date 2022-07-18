# cfn-docgen

![buildbadge](https://codebuild.ap-northeast-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoidERrRjdNRERUMWRqWGc5TW1VTGREYXJkQ1BKc2JremZsRS8vK21jdThTeWlTeEpaVTRJSHU0aVBVTHE2aDJudStCUXF6c2tFWlZQSnFiLzhta216dk1nPSIsIml2UGFyYW1ldGVyU3BlYyI6Ik95ZGR1VHBOZ0pqZUJXZWkiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=release)

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

| ResourceId   | ResourceType   | ResourceNote                    | Property           | Value              | UserNote                                            | Required    | Type        | UpdateType      | Description                                                                                                                                                                                                                                                                                                                                                                                                                                      | IsOmittable   | Filename   |
|:-------------|:---------------|:--------------------------------|:-------------------|:-------------------|:----------------------------------------------------|:------------|:------------|:----------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------|:-----------|
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | CidrBlock          | 10.0.0.0/16        | This is a note for CidrBlock prop                   | Conditional | String      | Replacement     | The IPv4 network range for the VPC, in CIDR notation. For example, 10.0.0.0/16. We modify the specified CIDR block to its canonical form; for example, if you specify 100.68.0.18/18, we modify it to 100.68.0.0/18.                                                                                                                                                                                                                             | False         | vpc.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | EnableDnsHostnames |                    |                                                     | No          | Boolean     | No interruption | Indicates whether the instances launched in the VPC get DNS hostnames. If enabled, instances in the VPC get DNS hostnames; otherwise, they do not. Disabled by default for nondefault VPCs. For more information, see DNS attributes in your VPC.                                                                                                                                                                                                | True          | vpc.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | EnableDnsSupport   | True               |                                                     | No          | Boolean     | No interruption | Indicates whether the DNS resolution is supported for the VPC. If enabled, queries to the Amazon provided DNS server at the 169.254.169.253 IP address, or the reserved IP address at the base of the VPC network range "plus two" succeed. If disabled, the Amazon provided DNS service in the VPC that resolves public DNS hostnames to IP addresses is not enabled. Enabled by default. For more information, see DNS attributes in your VPC. | False         | vpc.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | InstanceTenancy    |                    |                                                     | No          | String      | No interruption | The allowed tenancy of instances launched into the VPC.                                                                                                                                                                                                                                                                                                                                                                                          | True          | vpc.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | Ipv4IpamPoolId     |                    |                                                     | Conditional | String      | Replacement     | The ID of an IPv4 IPAM pool you want to use for allocating this VPC's CIDR. For more information, see What is IPAM? in the Amazon VPC IPAM User Guide.                                                                                                                                                                                                                                                                                           | True          | vpc.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | Ipv4NetmaskLength  |                    |                                                     | No          | Integer     | Replacement     | The netmask length of the IPv4 CIDR you want to allocate to this VPC from an Amazon VPC IP Address Manager (IPAM) pool. For more information about IPAM, see What is IPAM? in the Amazon VPC IPAM User Guide.                                                                                                                                                                                                                                    | True          | vpc.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | Tags               |                    |                                                     | No          | List of Tag | No interruption | The tags for the VPC.                                                                                                                                                                                                                                                                                                                                                                                                                            | False         | vpc.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | Tags[0].Key        | ENV                |                                                     | Yes         | String      |                 | The key name of the tag. You can specify a value that's 1 to 128 Unicode characters in length and can't be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.                                                                                                                                                                                                | False         | vpc.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | Tags[0].Value      | {'Ref': 'EnvType'} |                                                     | Yes         | String      |                 | The value for the tag. You can specify a value that's 1 to 256 characters in length.                                                                                                                                                                                                                                                                                                                                                             | False         | vpc.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | Tags[1].Key        | Name               |                                                     | Yes         | String      |                 | The key name of the tag. You can specify a value that's 1 to 128 Unicode characters in length and can't be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.                                                                                                                                                                                                | False         | vpc.yaml   |
| VPC          | AWS::EC2::VPC  | This is a note for VPC resource | Tags[1].Value      | SampleVpc          | This is a note for Value prop of 2nd Tags list prop | Yes         | String      |                 | The value for the tag. You can specify a value that's 1 to 256 characters in length.                                                                                                                                                                                                                                                                                                                                                             | False         | vpc.yaml   |



The key features of this tool are,

- All of the properties of each resource, including ones you omit to define, are listed in generated file.
  - In the example above, properties `EnableDnsHostnames`, `InstanceTenancy`, `Ipv4IpamPoolId`, and `Ipv4NetmaskLength` are omitted in original cfn template file, but listed in generated file.
- References for each resource and property listed at [official User Guide](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) are merged in generated file as columns `Required`, `Type`, `UpdateType`, and `Description`.
- You can add custom notes for each resource and property at `Metadata` section in each resource.
  - You can add custom note for a resource at `Metadata.UserNotes.ResourceNote`
  - You can add custom notes for properties at `Metadata.UserNotes.PropNotes.{PropertyName}`
    - For nested or list properties, you can specify `PropertyName` like `Tags[1].Value` .
- Not only `Resources` section in cfn template, this tool can also generate definitions of other sections, including `Parameters`, `Mappings`, and `Outputs` and resource policies like `CreationPolicy`, `UpdatePolicy`, `UpdateReplacePlocy`, `DeletionPolicy`, and `DependsOn`.
- You can generate files as excel, md, csv, or html format.
  - In excel format, all of definitions are separated by sheets. 
  - In other format, all of definitions are separated by files.

Full example is in [sample](./sample) directory.

---

## Requirements
- python3.8
- Linux OS
- AWS CLI

---

## Installation
```Bash
$ pip install cfn-docgen
```


---

## Command usage
```Bash
$ cfn-docgen --help
Usage: cfn-docgen [OPTIONS]

  Document generator from cfn template files

Options:
  --in TEXT                 Input cfn template file path (yaml/json)
                            [required]
  --fmt [xlsx|md|csv|html]  Output file format.  [default: xlsx]
  --omit                    If set, optional properties whose actual values
                            are not set in input template file will not be
                            written in output file.
  --refresh                 If set, fristly remove all existing cache files
                            and download them again.
  --region TEXT             AWS region name for referencing resource specs. If
                            not set, the value set as environment variable
                            `CFN_DOCGEN_AWS_REGION` is used. If the
                            environment variable is not set, use the value of
                            AWS CLI default profile
  --verbose                 If set, stdout DEBUG level logs
  --help                    Show this message and exit.


# example command usage
$ cfn-docgen --in sample/sample-template.json --fmt html
```

