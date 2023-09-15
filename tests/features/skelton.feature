Feature: cfn-docgen skelton

  @fixture.command_line_tool.skelton.cunstom_resource_specification
  Scenario: show sample skelton for custom resource specification
    Given cfn-docgen command line tool is locally installed 
    When cfn-docgen skelton subcommand is invoked, with specifying skelton type as custom-resource-specification
    Then sample skelton for custom resource specification is show in stdout
