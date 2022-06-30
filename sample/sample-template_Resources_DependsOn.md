| ResourceId       | ResourceType    | ResourceNote   | DependsOn         | Filename             |
|:-----------------|:----------------|:---------------|:------------------|:---------------------|
| PublicRoute      | AWS::EC2::Route |                | GatewayToInternet | sample-template.json |
| NATIPAddress     | AWS::EC2::EIP   |                | GatewayToInternet | sample-template.json |
| BastionIPAddress | AWS::EC2::EIP   |                | GatewayToInternet | sample-template.json |