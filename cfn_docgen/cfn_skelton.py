from cfn_docgen import cfn_spec, cfn_def
import json
import yaml
import re

class CfnSkelton(object):

    def __init__(self, resource_type:str, recursive:bool=False, fmt:str="yaml") -> None:
        self.resource_type = resource_type
        self.recursive = recursive
        self.fmt = fmt

    def main(self, ) -> str:

        skelton = {
            "Metadata": {
                "UserNotes": {
                    "ResourceNote": "",
                    "PropNotes": {}
                }
            }
        }

        resource = cfn_def.CfnResource("Skelton", {"Type": self.resource_type, "Properties": {}})
        prop_df = resource.prop_to_df("Detail")

        leaves = {}
        keys = sorted(prop_df["Property"].values.tolist())
        next_keys = keys[1:] + [None]
        for key, next_key in zip(keys, next_keys):
            if next_key is None:
                leaves[key] = ""
                break
            if not next_key.startswith(key):
                leaves[key] = ""

        d = {}
        for key, value in leaves.items():
            s = d
            tokens = re.findall(r'\w+', key)
            for count, (index, next_token) in enumerate(zip(tokens, tokens[1:] + [value]), 1):
                value = next_token if count == len(tokens) else [] if next_token.isdigit() else {}
                if isinstance(s, list):
                    index = int(index)
                    while index >= len(s):
                        s.append(value)
                elif index not in s:
                    s[index] = value
                s = s[index]


        prop_notes = {}
        if self.recursive:
            prop_notes = d
        else:
            prop_notes = {key: val for key, val in d.items() if isinstance(val, str)}

        skelton["Metadata"]["UserNotes"]["PropNotes"] = prop_notes


        # dump by format
        if self.fmt == "yaml":
            skelton = yaml.dump(skelton)
        else:
            skelton = json.dumps(skelton, indent=2)

        return skelton