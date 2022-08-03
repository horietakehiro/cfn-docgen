import glob
import os
import random
import shutil
import unittest
import random
import pandas as pd
import json


from . import test_util
from cfn_docgen import main
import pandas as pd
from cfn_docgen import util
from click.testing import CliRunner
from parameterized import parameterized

TEST_DIR=os.path.dirname(__file__)



def random_sampling(l:list, n:int=50):
    new_list = []
    for _ in range(n):
        i = random.randint(0, len(l)-1)
        try:
            new_list.append(l.pop(i))
        except IndexError:
            break
    return new_list

class MainTestCase(unittest.TestCase):

    cfn_filepaths = test_util.create_template_per_resources(
        os.path.join(TEST_DIR, "resources"),
    )
    n = int(os.environ.get("SAMPLING", 0))
    if n:
        cfn_filepaths = random_sampling(cfn_filepaths, n)


    sample_filepath = os.path.join(TEST_DIR, "resources", "AWSEC2Instance.json")

    
    regions=[
        ('eu-north-1',),
        ('ap-south-1',),
        ('eu-west-3',),
        ('eu-west-2',),
        ('eu-west-1',),
        ('ap-northeast-3',),
        ('ap-northeast-2',),
        ('ap-northeast-1',),
        ('sa-east-1',),
        ('ca-central-1',),
        ('ap-southeast-1',),
        ('ap-southeast-2',),
        ('eu-central-1',),
        ('us-east-1',),
        ('us-east-2',),
        ('us-west-1',),
        ('us-west-2',),
    ]


    @classmethod
    def remove_files(cls):
        remove_filepath = glob.glob(os.path.join(TEST_DIR, "resources", "*"))
        remove_filepath = [f for f in remove_filepath if not f.endswith("json")]
        for f in remove_filepath:
            try:
                os.remove(f)
            except FileNotFoundError:
                pass

    @classmethod
    def setUpClass(cls) -> None:
        if not len(cls.cfn_filepaths):
            test_util.create_template_per_resources(os.path.join(TEST_DIR, "resources"))


        cls.remove_files()
        return super().setUpClass()

    def setUp(self) -> None:
        try:
            del os.environ["CFN_DOCGEN_AWS_REGION"]
        except KeyError:
            pass
        return super().setUp()

    def load_excel_sheet(self, filepath:str, sheet_name:str) -> pd.DataFrame:
        print(filepath, sheet_name)
        return pd.read_excel(
            filepath, sheet_name=sheet_name,
            header=1, index_col=1, 
        )

    @parameterized.expand(cfn_filepaths)
    def test_main(self, filepath:str):
        expected_filepath = os.path.splitext(filepath)[0] + ".xlsx"
        runner = CliRunner()
        result = runner.invoke(
            main.main, f"--in {filepath}"
        )
        self.assertTrue(os.path.exists(expected_filepath), result.exc_info)


    @parameterized.expand(["xlsx", "md", "csv", "html"])
    def test_main_arg_fmt(self, fmt):
        in_filepath = self.cfn_filepaths[0]
        # expected_filepath_pattern = f"{in_filepath.split('.')[0]}*.{fmt}"
        expected_filepath_pattern = os.path.splitext(in_filepath)[0] + f"*.{fmt}"


        paths = glob.glob(expected_filepath_pattern)
        for p in paths:
            try:
                os.remove(p)
            except FileNotFoundError:
                pass

        runner = CliRunner()
        result = runner.invoke(
            main.main, f"--in {in_filepath} --fmt {fmt}"
        )
        paths = glob.glob(expected_filepath_pattern)
        self.assertGreater(len(paths), 0, result.exception)


    def test_main_arg_omit(self):
        in_filepath = self.sample_filepath
        expected_filepath = os.path.splitext(in_filepath)[0] + ".xlsx"
        runner = CliRunner()
        result = runner.invoke(
            # main.main, ["--in", in_filepath]
            main.main, f"--in {in_filepath}"
        )
        full_data = self.load_excel_sheet(expected_filepath, "Resources_Property_Detail")

        result = runner.invoke(
            main.main, f"--in {in_filepath} --omit"
        )
        omitted_data = self.load_excel_sheet(expected_filepath, "Resources_Property_Detail")

        self.assertEqual(full_data.shape[1], omitted_data.shape[1])
        self.assertGreater(full_data.shape[0], omitted_data.shape[0])


    @parameterized.expand(regions)
    def test_main_arg_region(self, region):

        in_filepath = self.sample_filepath

        specs_by_region = glob.glob(os.path.join(util.CACHE_BASE_DIR, "*", "CloudFormationResourceSpecification.json"))
        for spec in specs_by_region:
            try:
                os.remove(spec)
            except FileNotFoundError as ex:
                raise ex

        runner = CliRunner()
        result = runner.invoke(
            main.main, f"--in {in_filepath} --region {region}", color=True,
        )

        specs_by_region = glob.glob(os.path.join(util.CACHE_BASE_DIR, "*", "CloudFormationResourceSpecification.json"))


        self.assertEqual(result.exit_code, 0, result.exc_info)
        self.assertEqual(len(specs_by_region), 1, result.exc_info)
        self.assertEqual(
            specs_by_region[0],
            os.path.join(util.CACHE_BASE_DIR, region, "CloudFormationResourceSpecification.json"),
            result.exc_info,
        )
    
    def test_main_arg_refresh(self):
        region = "ap-northeast-1"
        in_filepath = self.sample_filepath
        runner = CliRunner()
        result = runner.invoke(
            main.main, f"--in {in_filepath} --region {region}"
        )
        cache_filepath = os.path.join(util.CACHE_BASE_DIR, region, "CloudFormationResourceSpecification.json")
        prev_timestamp = os.path.getatime(cache_filepath)

        try:
            shutil.rmtree(os.path.join(TEST_DIR, "cache"))
        except FileNotFoundError:
            pass
        shutil.copytree(util.CACHE_BASE_DIR, os.path.join(TEST_DIR, "cache"))

        result = runner.invoke(
            main.main, f"--in {in_filepath} --region {region} --refresh"
        )
        refreshed_timestamp = os.path.getatime(cache_filepath)

        self.assertGreater(refreshed_timestamp, prev_timestamp)

        shutil.rmtree(util.CACHE_BASE_DIR)
        shutil.copytree(os.path.join(TEST_DIR, "cache"), util.CACHE_BASE_DIR, )


    def test_main_custom_resource(self):
        filepath = os.path.join(TEST_DIR, "resources", "CustomResource.json")
        with open(filepath, "w") as fp:
            fp.write(json.dumps(
                {
                    "AWSTemplateFormatVersion": "2010-09-09",
                    "Description": "Sample template using Custom Resource",
                    "Resources": {
                        "SomeCustomResource1": {
                            "Type": "Custom::SomeCustomResource",
                            "Properties": {
                                "ServiceToken": "some-token1",
                                "Region": {"Ref": "AWS::Region"},
                                "Prop1": "some-prop1",
                                "Prop2": {"KEY2": "VAL2"}
                            }
                        },
                        "SomeCustomResource2": {
                            "Type": "AWS::CloudFormation::CustomResource",
                            "Version": 1.0,
                            "Properties": {
                                "ServiceToken": "some-token2",
                                "Region": {"Ref": "AWS::Region"},
                                "Prop3": "some-prop3",
                                "Prop4": {"KEY4": "VAL4"}
                            }
                        }        
                    }
                }
            ))
        expected_props = {
            "Prop1": "some-prop1",
            "Prop2": {"KEY2": "VAL2"},
            "Prop3": "some-prop3",
            "Prop4": {"KEY4": "VAL4"}
        }
        runner = CliRunner()
        result = runner.invoke(
            main.main, f"--in {filepath} --fmt csv"
        )
        df = pd.read_csv(filepath.replace(".json", "_Resources_Property_Summary.csv"))
        self.assertEqual(df.shape[0], 2)
        df = pd.read_csv(filepath.replace(".json", "_Resources_Property_Detail.csv"))
        for k, v in expected_props.items():
            self.assertTrue(k in df["Property"].values.tolist())
            self.assertTrue(str(v) in df["Value"].values.tolist(), f"{v, df['Value'].values.tolist()}")