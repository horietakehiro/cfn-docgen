import os
import boto3
import json
import unittest
import datetime as dt

from serverless.lambda_function import lambda_handler

s3 = boto3.client("s3")

class LambdaFunctionTestCase(unittest.TestCase):

    bucket_name = f"cfn-docgen-test-{str(int(dt.datetime.now().timestamp()))}"
    upload_filepath = os.path.join(os.path.dirname(__file__), "..", "sample", "sample-template.json")
    s3_filepath = os.path.basename(upload_filepath)

    @classmethod
    def setUpClass(cls) -> None:
        s3.create_bucket(
            Bucket=cls.bucket_name,
            CreateBucketConfiguration={
                "LocationConstraint": s3.meta.config.region_name,
            }
        )
        return super().setUpClass()

    def setUp(self) -> None:
        s3.upload_file(
            Filename=self.upload_filepath,
            Bucket=self.bucket_name,
            Key=self.s3_filepath,
        )
        return super().setUp()

    def tearDown(self) -> None:
        objects = s3.list_objects(Bucket=self.bucket_name)
        keys = [{"Key": obj["Key"]} for obj in objects["Contents"]]
        s3.delete_objects(
            Bucket=self.bucket_name,
            Delete={"Objects": keys},
        )

        return super().tearDown()

    @classmethod
    def tearDownClass(cls) -> None:
        s3.delete_bucket(Bucket=cls.bucket_name)
        return super().tearDownClass()

    def test_lambda_handler_default(self):
        event = {
            "Records": [{
                "s3": {
                    "bucket" : {
                        "name": self.bucket_name,
                    },
                    "object": {
                        "key": self.s3_filepath
                    }
                }
            }]
        }

        lambda_handler(event, None)

        objects = s3.list_objects(Bucket=self.bucket_name)
        self.assertEqual(len(objects["Contents"]), 2, objects)

    def test_lambda_handler_with_args(self):
        os.environ["CFN_DOCGEN_ARGS"] = "--fmt,csv"
        event = {
            "Records": [{
                "s3": {
                    "bucket" : {
                        "name": self.bucket_name,
                    },
                    "object": {
                        "key": self.s3_filepath
                    }
                }
            }]
        }

        lambda_handler(event, None)

        objects = s3.list_objects(Bucket=self.bucket_name)
        self.assertGreater(len(objects["Contents"]), 2, objects)

        
