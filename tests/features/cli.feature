Feature: cfn-docgen as command line tool

  @fixture.command_line_tool.markdown.local_single_file_local_single_dest
  Scenario: Generate a markdown document file from a local CloudFormation template file
    Given cfn-docgen command line tool is locally installed 
    And CloudFormation template files are locally saved
    When cfn-docgen is invoked, with specifying source and dest, and format as markdown
    Then markdown document files are locally created
    And all of the definitions of CloudFormation template are written as a form of markdown in it.

  @fixture.command_line_tool.markdown.local_multiple_source_local_multiple_dest
  Scenario: Generate multiple markdown document files from multiple local CloudFormation template files
    Given cfn-docgen command line tool is locally installed 
    And CloudFormation template files are locally saved
    When cfn-docgen is invoked, with specifying source and dest, and format as markdown
    Then markdown document files are locally created

  @fixture.command_line_tool.markdown.s3_single_file_s3_single_dest
  Scenario: Generate a markdown document file from a CloudFormation template file at S3 bucket
    Given cfn-docgen command line tool is locally installed 
    And CloudFormation template files are saved at S3 bucket
    When cfn-docgen is invoked, with specifying source and dest, and format as markdown
    Then markdown document files are created at S3 bucket

  @fixture.command_line_tool.markdown.s3_multiple_source_s3_multiple_dest
  Scenario: Generate multiple markdown document files from multiple CloudFormation template files at S3 bucket
    Given cfn-docgen command line tool is locally installed 
    And CloudFormation template files are saved at S3 bucket
    When cfn-docgen is invoked, with specifying source and dest, and format as markdown
    Then markdown document files are created at S3 bucket

