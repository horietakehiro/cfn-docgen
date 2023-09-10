Feature: cfn-docgen integration with AWS CDK
  @fixture.cdk.markdown
  Scenario: Generate a markdown document file from AWS-CDK-generated template json file.
    Given cfn-docgen command line tool is locally installed
    And AWS-CDK-generated template json file is saved locally
    When Invoke cfn-docgen to generate document from AWS-CDK-generated template json file
    Then markdown document file is locally created and embeded metadatas are written in it