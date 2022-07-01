# cfn-docgen

![buildbadge](https://codebuild.ap-northeast-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoidERrRjdNRERUMWRqWGc5TW1VTGREYXJkQ1BKc2JremZsRS8vK21jdThTeWlTeEpaVTRJSHU0aVBVTHE2aDJudStCUXF6c2tFWlZQSnFiLzhta216dk1nPSIsIml2UGFyYW1ldGVyU3BlYyI6Ik95ZGR1VHBOZ0pqZUJXZWkiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=release)

---

cfn-docgen is a command line tool that generates the table-formatted CloudFormation(cfn) definition file from the original, yaml or json formatted template file. 
ALl the definitions of each sections of cfn template, listed below, are flattened as table format, and listed in each sheets(in xlsx) or each files(in other format).
- Parameters
- Mappings
- Resources
  - Properties
    - Summary
    - Detail
  - CreationPolicy
  - UpdatePolicy
  - UpdateReplacePolicy
  - DeletionPolicy
  - DependsOn
- Outputs

Additionally, you can add your own comments to each resources and each properties. How to do is written at [Adding your own comments](#adding-your-own-comments) section.

---

## Requirements
- python3.8
- Linux OS
- AWS CLI

---

## How to usage

---

### Command usage
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
```

### example(output as xlsx file)

```Bash
$ cfn-docgen --in sample/sample-template.json
# stdout some log messages...
$ ls ./sample
sample-template.json  sample-template.xlsx
```

### example(output as other format file)

```Bash
$ cfn-docgen --in sample/sample-template.json --fmt md
# stdout some log messages...
$ ls ./sample
sample-template.json           sample-template_Resources_CreationPolicy.md  sample-template_Resources_UpdatePolicy.md
sample-template_Mappings.md    sample-template_Resources_DeletionPolicy.md  sample-template_Resources_UpdateReplacePolicy.md
sample-template_Outputs.md     sample-template_Resources_DependsOn.md
sample-template_Parameters.md  sample-template_Resources_Property_Summary.md
sample-template_Resources_Property_Detail.md
```

---

### Adding your own comments
You can add your own comment for each resources and each properties by adding commnets in resources' `Metadata` sections with the format below.

```Json
{
    "Resources": {
        "VPC": {
            "Type": "AWS::EC2::VPC",
            "Metadata": {
                "UserNotes": {
                    "ResourceNote": "This is a comments for VPC resource.",
                    "PropNotes": {
                        "CidrBlock": "This is a comment for CidrBlock property",
                        "Tags[1].Key": "This is a comment for second Key property of Tags property"
                    }
                }
            },
            "Properties": {
                "CidrBlock": {
                    "Fn::FindInMap": [
                        "SubnetConfig",
                        "VPC",
                        "CIDR"
                    ]
                },
                "Tags": [
                    {
                        "Key": "Application",
                        "Value": {
                            "Ref": "AWS::StackId"
                        }
                    },
                    {
                        "Key": "Network",
                        "Value": "Public"
                    }
                ]
            }
        },
}
```
Then, the comments are listed in output file like below.

| ResourceId | ResourceType  | ResourceNote                         | Property           | Value                                              | UserNote                                                   | Description                                                                                                                                                                                                                                                                                                                                                                                                                                      | Required    | Type        | UpdateType      | IsTruncated | Filename       |
| :--------- | :------------ | :----------------------------------- | :----------------- | :------------------------------------------------- | :--------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :---------- | :---------- | :-------------- | :---------- | :------------- |
| AWSEC2VPC  | AWS::EC2::VPC | This is a comments for VPC resource. | CidrBlock          | {'Fn::FindInMap': ['SubnetConfig', 'VPC', 'CIDR']} | This is a comment for CidrBlock property                   | The IPv4 network range for the VPC, in CIDR notation. For example, 10.0.0.0/16. We modify the specified CIDR block to its canonical form; for example, if you specify 100.68.0.18/18, we modify it to 100.68.0.0/18.                                                                                                                                                                                                                             | Conditional | String      | Replacement     | False       | AWSEC2VPC.json |
| AWSEC2VPC  | AWS::EC2::VPC | This is a comments for VPC resource. | EnableDnsHostnames |                                                    |                                                            | Indicates whether the instances launched in the VPC get DNS hostnames. If enabled, instances in the VPC get DNS hostnames; otherwise, they do not. Disabled by default for nondefault VPCs. For more information, see DNS attributes in your VPC.                                                                                                                                                                                                | No          | Boolean     | No interruption | True        | AWSEC2VPC.json |
| AWSEC2VPC  | AWS::EC2::VPC | This is a comments for VPC resource. | EnableDnsSupport   |                                                    |                                                            | Indicates whether the DNS resolution is supported for the VPC. If enabled, queries to the Amazon provided DNS server at the 169.254.169.253 IP address, or the reserved IP address at the base of the VPC network range "plus two" succeed. If disabled, the Amazon provided DNS service in the VPC that resolves public DNS hostnames to IP addresses is not enabled. Enabled by default. For more information, see DNS attributes in your VPC. | No          | Boolean     | No interruption | True        | AWSEC2VPC.json |
| AWSEC2VPC  | AWS::EC2::VPC | This is a comments for VPC resource. | InstanceTenancy    |                                                    |                                                            | The allowed tenancy of instances launched into the VPC.                                                                                                                                                                                                                                                                                                                                                                                          | No          | String      | No interruption | True        | AWSEC2VPC.json |
| AWSEC2VPC  | AWS::EC2::VPC | This is a comments for VPC resource. | Ipv4IpamPoolId     |                                                    |                                                            | The ID of an IPv4 IPAM pool you want to use for allocating this VPC's CIDR. For more information, see What is IPAM? in the Amazon VPC IPAM User Guide.                                                                                                                                                                                                                                                                                           | Conditional | String      | Replacement     | True        | AWSEC2VPC.json |
| AWSEC2VPC  | AWS::EC2::VPC | This is a comments for VPC resource. | Ipv4NetmaskLength  |                                                    |                                                            | The netmask length of the IPv4 CIDR you want to allocate to this VPC from an Amazon VPC IP Address Manager (IPAM) pool. For more information about IPAM, see What is IPAM? in the Amazon VPC IPAM User Guide.                                                                                                                                                                                                                                    | No          | Integer     | Replacement     | True        | AWSEC2VPC.json |
| AWSEC2VPC  | AWS::EC2::VPC | This is a comments for VPC resource. | Tags               |                                                    |                                                            | The tags for the VPC.                                                                                                                                                                                                                                                                                                                                                                                                                            | No          | List of Tag | No interruption | False       | AWSEC2VPC.json |
| AWSEC2VPC  | AWS::EC2::VPC | This is a comments for VPC resource. | Tags[0].Key        | Application                                        |                                                            | The key name of the tag. You can specify a value that's 1 to 128 Unicode characters in length and can't be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.                                                                                                                                                                                                | Yes         | String      |                 | False       | AWSEC2VPC.json |
| AWSEC2VPC  | AWS::EC2::VPC | This is a comments for VPC resource. | Tags[0].Value      | {'Ref': 'AWS::StackId'}                            |                                                            | The value for the tag. You can specify a value that's 1 to 256 characters in length.                                                                                                                                                                                                                                                                                                                                                             | Yes         | String      |                 | False       | AWSEC2VPC.json |
| AWSEC2VPC  | AWS::EC2::VPC | This is a comments for VPC resource. | Tags[1].Key        | Network                                            | This is a comment for second Key property of Tags property | The key name of the tag. You can specify a value that's 1 to 128 Unicode characters in length and can't be prefixed with aws:. You can use any of the following characters: the set of Unicode letters, digits, whitespace, _, ., /, =, +, and -.                                                                                                                                                                                                | Yes         | String      |                 | False       | AWSEC2VPC.json |
| AWSEC2VPC  | AWS::EC2::VPC | This is a comments for VPC resource. | Tags[1].Value      | Public                                             |                                                            | The value for the tag. You can specify a value that's 1 to 256 characters in length.                                                                                                                                                                                                                                                                                                                                                             | Yes         | String      |                 | False       | AWSEC2VPC.json |