Feature: cfn-docgen as command line tool

  @fixture.command_line_tool.markdown.single_file
  Scenario: Generate a markdown document file from a CloudFormation template file
    Given that cfn-docgen command line tool is locally installed 
    And CloudFormation template yaml file is locally saved
    When cfn-docgen is invoked, with specifying input file, output file, and output file format as markdown
    Then a single markdown document file is locally created
    And all of the definitions of CloudFormation template are written as a form of markdown in it.
  