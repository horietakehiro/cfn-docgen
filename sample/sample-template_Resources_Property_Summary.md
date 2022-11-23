| ResourceType                              | ResourceId                            | ResourceNote           |
|:------------------------------------------|:--------------------------------------|:-----------------------|
| AWS::EC2::EIP                             | BastionIPAddress                      |                        |
| AWS::EC2::EIP                             | NATIPAddress                          |                        |
| AWS::EC2::Instance                        | BastionHost                           |                        |
| AWS::EC2::Instance                        | NATDevice                             | This is a ec2 instance |
| AWS::EC2::InternetGateway                 | InternetGateway                       |                        |
| AWS::EC2::NetworkAcl                      | PrivateNetworkAcl                     |                        |
| AWS::EC2::NetworkAcl                      | PublicNetworkAcl                      |                        |
| AWS::EC2::NetworkAclEntry                 | InboundEphemeralPublicNetworkAclEntry |                        |
| AWS::EC2::NetworkAclEntry                 | InboundHTTPPublicNetworkAclEntry      |                        |
| AWS::EC2::NetworkAclEntry                 | InboundHTTPSPublicNetworkAclEntry     |                        |
| AWS::EC2::NetworkAclEntry                 | InboundPrivateNetworkAclEntry         |                        |
| AWS::EC2::NetworkAclEntry                 | InboundSSHPublicNetworkAclEntry       |                        |
| AWS::EC2::NetworkAclEntry                 | OutBoundPrivateNetworkAclEntry        |                        |
| AWS::EC2::NetworkAclEntry                 | OutboundPublicNetworkAclEntry         |                        |
| AWS::EC2::Route                           | PrivateRoute                          |                        |
| AWS::EC2::Route                           | PublicRoute                           |                        |
| AWS::EC2::RouteTable                      | PrivateRouteTable                     |                        |
| AWS::EC2::RouteTable                      | PublicRouteTable                      |                        |
| AWS::EC2::SecurityGroup                   | BastionSecurityGroup                  |                        |
| AWS::EC2::SecurityGroup                   | BeanstalkSecurityGroup                |                        |
| AWS::EC2::SecurityGroup                   | NATSecurityGroup                      |                        |
| AWS::EC2::Subnet                          | PrivateSubnet                         |                        |
| AWS::EC2::Subnet                          | PublicSubnet                          |                        |
| AWS::EC2::SubnetNetworkAclAssociation     | PrivateSubnetNetworkAclAssociation    |                        |
| AWS::EC2::SubnetNetworkAclAssociation     | PublicSubnetNetworkAclAssociation     |                        |
| AWS::EC2::SubnetRouteTableAssociation     | PrivateSubnetRouteTableAssociation    |                        |
| AWS::EC2::SubnetRouteTableAssociation     | PublicSubnetRouteTableAssociation     |                        |
| AWS::EC2::VPC                             | VPC                                   | VPCリソースに対するコメント.       |
| AWS::EC2::VPCGatewayAttachment            | GatewayToInternet                     |                        |
| AWS::ElasticBeanstalk::Application        | SampleApplication                     |                        |
| AWS::ElasticBeanstalk::ApplicationVersion | SampleApplicationVersion              |                        |
| AWS::ElasticBeanstalk::Environment        | SampleEnvironment                     |                        |
| AWS::IAM::InstanceProfile                 | WebServerInstanceProfile              |                        |
| AWS::IAM::Policy                          | WebServerRolePolicy                   |                        |
| AWS::IAM::Role                            | WebServerRole                         |                        |