Feature: cfn-docgen skelton

  @fixture.command_line_tool.skelton.resource_type
  Scenario: show skelton for specified resource type
    Given cfn-docgen command line tool is locally installed 
    When cfn-docgen skelton subcommand is invoked, with specifying resource type
    Then skelton for the resource type is show in stdout
