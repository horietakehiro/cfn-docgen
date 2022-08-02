| Name    | Description                                  | Value                                                                                 | ExportName   | Filename             |
|:--------|:---------------------------------------------|:--------------------------------------------------------------------------------------|:-------------|:---------------------|
| Bastion | IP Address of the Bastion host               | {'Ref': 'BastionIPAddress'}                                                           |              | sample-template.json |
| URL     | The URL of the Elastic Beanstalk environment | {'Fn::Join': ['', ['http://', {'Fn::GetAtt': ['SampleEnvironment', 'EndpointURL']}]]} |              | sample-template.json |