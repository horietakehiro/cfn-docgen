Feature: cfn-docgen skeleton

  @fixture.command_line_tool.skeleton.resource_type
  Scenario: show skeleton for specified resource type
    Given cfn-docgen command line tool is locally installed 
    When cfn-docgen skeleton subcommand is invoked, with specifying resource type
    Then skeleton for the resource type is show in stdout
