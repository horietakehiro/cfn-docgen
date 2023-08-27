Feature: cfn-docgen as docker image
  @fixture.docker.markdown.local_single_file_local_single_dest
  Scenario: Generate a markdown document file via docker image
    Given cfn-docgen docker image is installed locally
    When Invoke cfn-docgen as docker container
    Then markdown document files are created and saved locally
