import unittest

import os
from cfn_docgen import cfn_spec

class CfnSpecTestCase(unittest.TestCase):

    base_spec_filename = "CloudFormationResourceSpecification.json"
    default_region = "ap-northeast-1"

    def setUp(self) -> None:
        os.environ["CFN_DOCGEN_AWS_REGION"] = self.default_region
        return super().setUp()

    def test_load_file_no_cache(self):
        """
        if spec file does not locally exsits, download it.
        """
        filepath = os.path.join(os.path.dirname(__file__), self.base_spec_filename)
        try:
            os.remove(filepath)
        except FileNotFoundError:
            pass

        spec = cfn_spec.CfnSpecification(
            filepath=filepath
        )

        expected_keys = set(["PropertyTypes", "ResourceSpecificationVersion", "ResourceTypes"])
        self.assertSetEqual(
            expected_keys, set(spec.spec.keys())
        )

        try:
            os.remove(filepath)
        except FileNotFoundError:
            pass

    def test_get_resource_spec(self):
        """
        get resource spec from spec
        """
        resource_name = "AWS::S3::Bucket"
        spec = cfn_spec.CfnSpecification()

        resource_spec = spec.get_resource_spec(resource_name)
        self.assertEqual(type(resource_spec), dict)
        print(resource_spec.keys())

    def test_get_property_spec(self):
        """
        get property spec of a specific resource from spec
        """
        resource_name = "AWS::S3::Bucket"
        spec = cfn_spec.CfnSpecification()

        property_spec = spec.get_property_spec(resource_name)

        self.assertEqual(56, len(property_spec))

