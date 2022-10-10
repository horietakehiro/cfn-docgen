import os
import subprocess
import boto3
import tempfile
import glob
import json
import traceback
from click.testing import CliRunner
from cfn_docgen import main

s3 = boto3.client("s3")

# {
#   "Records": [
#     {
#       "eventVersion": "2.1",
#       "eventSource": "aws:s3",
#       "awsRegion": "us-east-2",
#       "eventTime": "2019-09-03T19:37:27.192Z",
#       "eventName": "ObjectCreated:Put",
#       "userIdentity": {
#         "principalId": "AWS:AIDAINPONIXQXHT3IKHL2"
#       },
#       "requestParameters": {
#         "sourceIPAddress": "205.255.255.255"
#       },
#       "responseElements": {
#         "x-amz-request-id": "D82B88E5F771F645",
#         "x-amz-id-2": "vlR7PnpV2Ce81l0PRw6jlUpck7Jo5ZsQjryTjKlc5aLWGVHPZLj5NeC6qMa0emYBDXOo6QBU0Wo="
#       },
#       "s3": {
#         "s3SchemaVersion": "1.0",
#         "configurationId": "828aa6fc-f7b5-4305-8584-487c791949c1",
#         "bucket": {
#           "name": "DOC-EXAMPLE-BUCKET",
#           "ownerIdentity": {
#             "principalId": "A3I5XTEXAMAI3E"
#           },
#           "arn": "arn:aws:s3:::lambda-artifacts-deafc19498e3f2df"
#         },
#         "object": {
#           "key": "b21b84d653bb07b05b1e6b33684dc11b",
#           "size": 1305107,
#           "eTag": "b21b84d653bb07b05b1e6b33684dc11b",
#           "sequencer": "0C0F6F405D6ED209E1"
#         }
#       }
#     }
#   ]
# }

def lambda_handler(event:dict, context:dict):

    print(f"{event=}")
    print(f"{context=}")

    args = os.environ.get("CFN_DOCGEN_ARGS", "")
    args = args.split(",") if args != "" else []

    try:
        
        for record in event["Records"]:
            bucket = record["s3"]["bucket"]["name"]
            key = record["s3"]["object"]["key"]

            with tempfile.TemporaryDirectory() as tmpdir:
                # download file from s3
                local_input_file = os.path.join(tmpdir, key)
                local_input_dir = os.path.dirname(local_input_file)
                os.makedirs(local_input_dir, exist_ok=True)
                download_result = s3.download_file(
                    Bucket=bucket, Key=key,
                    Filename=local_input_file,
                )
                print(f"{download_result=}")


                # exec cfn-docgen command
                args = ["--in", local_input_file] + args
                print(f"{args=}")
                runner = CliRunner()
                command_result = runner.invoke(
                    main.main, args
                )
                print(f"{command_result.stdout=}")

                upload_files = glob.glob(os.path.join(local_input_dir, "*"))
                upload_files = list(filter(
                    lambda file: not file.endswith(".json") and not file.endswith(".yaml"),
                    upload_files,
                ))
                upload_keys = []
                for file in upload_files:
                    upload_key = os.path.join(os.path.dirname(key), os.path.basename(file))
                    upload_result = s3.upload_file(
                        Bucket=bucket, Key=upload_key,
                        Filename=file,
                    )
                    print(f"{upload_result=}")
                    upload_keys.append(f"s3://{upload_key}")
                print(f"{upload_keys=}")
                
    except Exception as ex:
        error = traceback.format_exception(type(ex), ex, ex.__traceback__)
        print(f"{error=}")
