Feature: cfn-docgen as python package
  @fixture.package.markdown.local_single_file_local_single_dest
  Scenario: Generate a markdown document file via python code
    Given cfn-docgen package is installed locally
    When Invoke cfn-docgen from python code
    Then markdown document files are created