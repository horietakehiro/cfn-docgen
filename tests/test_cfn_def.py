import json
import unittest

import os
from cfn_docgen import cfn_def

class CfnDefTestCase(unittest.TestCase):

    default_region = "ap-northeast-1"

    def setUp(self) -> None:
        os.environ["CFN_DOCGEN_AWS_REGION"] = self.default_region
        return super().setUp()

    def test_from_json(self):

        resource_id = "VPC"
        resource_def = {
            'Type': 'AWS::EC2::VPC',
            'Metadata': {
                'UserNotes': {
                    'ResourceNote': 'これはVPCリソースに対するユーザ独自のコメントです',
                    'PropNotes': {
                        'CidrBlock': 'これはCidrBlockプロパティに対するユーザ独自のコメントです',
                        'Tags[1].Key': 'これはTagsプロパティ配列の2番目のKeyプロパティに対するユーザ独自のコメントです'
                    }
                }
            },
            'Properties': {
                'CidrBlock': '10.0.0.0/16',
                'Tags': [
                    {'Key': 'ENV', 'Value': 'DEV'},
                    {'Key': 'DEPARTMENT', 'Value': 'SOMU'}
                ]
            }
        }

        resource = cfn_def.CfnResource(resource_id, resource_def)

        resource_json = resource.to_df("Resource_Property_Detail").to_dict(orient="records")
        expected_resource = {
            resource_id: resource_def
        }
        ret_resource = cfn_def.CfnResource.from_json_def(resource_json)
        print(json.dumps(ret_resource, indent=2))
        self.assertDictEqual(ret_resource, expected_resource)
