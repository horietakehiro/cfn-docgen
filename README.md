# cfn-docgen - AWS CloudFormation Document Generator

<p align="left">
    <a href="https://pypi.org/project/cfn-docgen/">
        <img alt="AWS CodeBuild status" src="https://codebuild.ap-northeast-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiOXljK25KclpqNzR3Zks0TFRQYTJvMWIvblNnenFDMDA4Z05NQitRUDI0aHZhMGNvckU2MWMrbkpMcVBBZldVQ1hSWHp0RVpuSkI4dE5wRWMxTm1HL0tjPSIsIml2UGFyYW1ldGVyU3BlYyI6IkRGMjUzSHZKMStNdWsxUFUiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=release">
    </a>
    <a href="https://codecov.io/github/horietakehiro/cfn-docgen" > 
        <img src="https://codecov.io/github/horietakehiro/cfn-docgen/graph/badge.svg?token=A5GN5Y4IQO"/> 
   </a>
    <a href="https://pypi.org/project/cfn-docgen/">
        <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/cfn-docgen">
    </a>
    <a href="https://pypi.org/project/cfn-docgen/">
        <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/cfn-docgen">
    </a>
    <a href="https://hub.docker.com/r/horietakehiro/cfn-docgen/tags">
        <img alt="Docker Image Version (latest semver)" src="https://img.shields.io/docker/v/horietakehiro/cfn-docgen?label=docker">
    </a>
    <a href="https://pypi.org/project/cfn-docgen/">
        <img alt="PyPI - License" src="https://img.shields.io/pypi/l/cfn-docgen">
    </a>
</p>


**Generate human-readable documents from AWS CloudFormation yaml/json templates.**

---

## Notice

***We have made breaking changes from [v0.7](https://github.com/horietakehiro/cfn-docgen/tree/v0.7) to current versions.***

---

## Example

Given that you created some cfn template yaml file. When you use cfn-docgen cli. Then, you can generate markdown document. 

```Bash
$ cfn-docgen docgen \
    --format markdown \
    --source docs/sample-template.yaml \
    --dest ./docs/
[INFO] successfully generate document [./docs/sample-template.md] from template [docs/sample-template.yaml]
```

The left image is a source cfn template file and the right image is a generated document markdown.

For full example, see [docs folder](./docs/)

![template-source-and-document-dest](./docs/images/source-template-and-dest-document.png)

---

## Install and How to use

### CLI

```Bash
$ pip install cfn-docgen

# you can also geenrate a document from a template at S3 bucket and upload it directory.
$ cfn-docgen docgen \
  --source s3://bucket/prefix/sample-template.yaml \
  --dest s3://bucket/prefix/sample-template.md
[INFO] successfully generate document [s3://bucket/prefix/sample-template.md] from template [s3://bucket/prefix/sample-template.yaml]

# and you can generate multiple documents from templates in direcotry(or s3 bucket prefix) at once
$ tree ./templates/
./templates/
├── sample-template-1.yaml
└── subfolder
    └── sample-template-2.yaml

1 directory, 2 files
$ cfn-docgen docgen \
    --source ./templates/ \
    --dest s3://bucket/documents/
[INFO] successfully generate document [s3://bucket/documents/sample-template-1.md] from template [./templates/sample-template-1.yaml]
[INFO] successfully generate document [s3://bucket/documents/subfolder/sample-template-2.md] from template [./templates/subfolder/sample-template-2.yaml]
```

---

### Docker Image

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
  horietakehiro/cfn-docgen:latest docgen \
    --source /tmp/sample-template.json \
    --dest /tmp/
[INFO] successfully generate document [/tmp/sample-template.md] from template [/tmp/sample-template.json]

# local directory(after)
$ tree /tmp/sample/
/tmp/sample/
├── sample-template.json
└── sample-template.md

0 directories, 2 files
```

---

### API

```python
from cfn_docgen import (
    CfnDocgenService, CfnDocgenServiceCommandInput,
    CfnTemplateSource, CfnDocumentDestination
)
service = CfnDocgenService.with_default()
service.main(
    command_input=CfnDocgenServiceCommandInput(
        template_source=CfnTemplateSource("s3://bucket/template.yaml", service.context),
        document_dest=CfnDocumentDestination("s3://bucket/document.md", service.context),
        fmt="markdown",
    )
)
```

---

### Serverless

You can also use cfn-docgen on AWS Cloud as serverless application.

You can deploy resources at [AWS Serverless Application Repository](https://ap-northeast-1.console.aws.amazon.com/lambda/home?region=ap-northeast-1#/create/app?applicationId=arn:aws:serverlessrepo:ap-northeast-1:382098889955:applications/cfn-docgen-serverless).

Once deployed, tha S3 bucket named `cfn-docgen-${AWS::AccountId}-${AWS::Region}` is created on your account.

When you upload cfn template json/yaml files at `templates/` folder of the bucket, cfn-docgen-serverless automatically will be triggered and generates markdown docments for them at `documents/` folder.

---

## Embedding Descirptions

---

### Top level descriptions

You can embed description for the template at top level `Metadata` section like this, then markdown document will be generated from it.

```Yaml
Metadata:
  CfnDocgen:
    Description: |
      このテンプレートファイル東京リージョン上で以下のリソースを作成します
      - VPC
      - パブリックサブネット(2AZに1つずつ)

      ![Archtecture](./images/sample-template.drawio.png)


      **注意点**
      - このテンプレートファイルは**東京リージョン**上でのみの使用に制限しています
      - このテンプレートファイルを使用する前に、[東京リージョン上に作成可能なVPCの最大数の設定](https://ap-northeast-1.console.aws.amazon.com/servicequotas/home/services/vpc/quotas/L-F678F1CE)を確認することを推奨します(デフォルトは5VPC)**
```

Then, the generated description will be like below.

![top-level-description](./docs/images/top-level-description.png)

You can also embed descriptions for each sections - Mappings, Conditions, Rules.

```Yaml
Metadata:
  CfnDocgen:
    Mappings:
      CidrBlockMap: CidrBlocks for each environment
    Conditions:
      EnvCondition: Check if the value of parameter `EnvType` is `prod`
    Rules:
      RegionRule: This template is available only in ap-northeast-1
```

Then, the generated description will be like below.

![each-section-description](./docs/images/each-section-description.png)

### Resources and Properties description

You can embed descriptions for resources and their properties in `Metadata` section in each resources.

```Yaml
Resources: 
  VPC:
    Metadata:
      CfnDocgen:
        Description: アプリケーションサーバを稼働させるために使用するVPC
        Properties:
          EnableDnsHostnames: アプリケーションサーバのホスト名でパブリックIPを名前解決できるように有効化する
    Type: AWS::EC2::VPC
    Properties: 
      CidrBlock: ...
```

Then, the generated description will be like below.

![resource-level-description](./docs/images/resource-level-description.png)

---

## Integration with AWS CDK

cfn-docgen can generate documents from AWS-CDK-generated templates, and you can also embed descriptions in cdk codes like below.

```Python
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    
)
from constructs import Construct
from typing import Any
from cfn_docgen.domain.model.cfn_template import (
    CfnTemplateMetadataCfnDocgenDefinition as Metadata,
    CfnTemplateResourceMetadataDefinition as ResourceMetadata,
    CfnTemplateResourceMetadataCfnDocgenDefinition as CfnDocgen
)
class CfnDocgenSampleCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs:Any) -> None:
        super().__init__(scope, construct_id, **kwargs)
        # top-level description for the stack
        self.add_metadata(
            "CfnDocgen", Metadata(
                Description="top-level-description"
            ).model_dump(),
        )
        self.vpc_construct = ec2.Vpc(self, "VpcConstruct", max_azs=1)
        # resource-level descriptions
        self.vpc_construct.node.default_child.cfn_options.metadata = ResourceMetadata(
            CfnDocgen=CfnDocgen(Description="resource-level-description")
        ).model_dump()

```

Then, the table of contents of generated document will be like below.

![](./docs/images/table-of-contents-from-cdk-generated-template.png)