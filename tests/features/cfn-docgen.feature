@fixture.command_line_tool.markdown.local_single_file_local_single_dest
Feature: cfn-docgen as command line tool

  Scenario: Generate a markdown document file from a CloudFormation template file
    Given cfn-docgen command line tool is locally installed 
    And CloudFormation template file is locally saved
    When cfn-docgen is invoked, with specifying source and dest, and format as markdown
    Then a single markdown document file is locally created
    And all of the definitions of CloudFormation template are written as a form of markdown in it.
