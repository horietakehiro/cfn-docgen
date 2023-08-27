Feature: cfn-docgen as serverless application
  @fixture.serverless.markdown.s3_single_source_s3_single_dest
  Scenario: Generate a markdown document file when a CloudFormation template file is uploaded to S3 bucket
    Given cfn-docgen serverless application is deployed
    When CloudFormation template file is uploaded to S3 bucket
    Then markdown document files are created and uploaded to S3 bucket