# cfn-docgen

**Generate human-readable documents from AWS CloudFormation yaml/json templates.**

<p align="left">
    <a href="https://pypi.org/project/cfn-docgen/">
        <img alt="AWS CodeBuild status" src="https://codebuild.ap-northeast-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiMFdPYkd4WU5JaGdNUTNrVlE1aDlYVUtkY3Mzb3BKQ3IyM2F3dXJPTEhCVG9ldkplSE9rcXlsK0dtY2xhcDFlckhZR1lGYjFMN0c5Z1g5OHdMa29aWXE4PSIsIml2UGFyYW1ldGVyU3BlYyI6IkJaalJCTGZzeDNjTFFvZzQiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=main">
    </a>
    <a href="https://pypi.org/project/cfn-docgen/">
        <img alt="PyPI - Version" src="https://img.shields.io/pypi/v/cfn-docgen">
    </a>
    <a href="https://pypi.org/project/cfn-docgen/">
        <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/cfn-docgen">
    </a>
    <a href="https://pypi.org/project/cfn-docgen/">
        <img alt="PyPI - License" src="https://img.shields.io/pypi/l/cfn-docgen">
    </a>
</p>

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

The left cfn template file is source

![template-source-and-document-dest](./docs/images/source-template-and-dest-document.png)

