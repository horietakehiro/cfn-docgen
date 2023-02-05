from cfn_docgen import cfn_spec, cfn_def
import json
import yaml
import re

class MyDumper(yaml.Dumper):

    def increase_indent(self, flow=False, indentless=False):
        return super(MyDumper, self).increase_indent(flow, False)


def unflatten_json(j:dict) -> dict:

    d = {}
    for key, value in j.items():
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
    return d

class CfnSkelton(object):

    def __init__(self, resource_type:str, recursive:bool=False, fmt:str="yaml", section:str="metadata") -> None:
        self.resource_type = resource_type
        self.recursive = recursive
        self.fmt = fmt
        self.section = section

    def main(self, ) -> str:

        skelton = {
            "Metadata": {
                "UserNotes": {
                    "ResourceNote": "",
                    "PropNotes": {}
                }
            },
            "Properties": {}
        }

        resource = cfn_def.CfnResource("Skelton", {"Type": self.resource_type, "Properties": {}})
        prop_df = resource.prop_to_df("Detail")

        metadata = {}
        recursive_properties = {}
        keys = sorted(prop_df["Property"].values.tolist())
        next_keys = keys[1:] + [None]
        for key, next_key in zip(keys, next_keys):
            if next_key is None:
                metadata[key] = ""
                recursive_properties[key] = prop_df[prop_df["Property"] == key]["Type"].values[0]
                break
            # if not next_key.startswith(f"{key}.") or not next_key.startswith(f"{key}["):
            if not next_key.startswith(f"{key}"):
                recursive_properties[key] = prop_df[prop_df["Property"] == key]["Type"].values[0]
                metadata[key] = ""

        properties = {key: prop_df[prop_df["Property"] == key]["Type"].values[0] for key in keys}
        metadata.keys

        unflatten_metadata = unflatten_json(metadata)

        prop_notes = {}
        prop_types = {}
        if self.recursive:
            prop_notes = unflatten_metadata
            prop_types = unflatten_json(recursive_properties)

        else:
            prop_notes = {key: "" for key in unflatten_metadata.keys()}
            prop_types = {key: properties[key] for key in unflatten_metadata.keys()}
            # prop_notes = {key: val for key, val in d.items() if isinstance(val, str)}

        skelton["Metadata"]["UserNotes"]["PropNotes"] = prop_notes
        skelton["Properties"] = prop_types

        # trim by section
        if self.section == "all":
            pass
        if self.section == "metadata":
            _ = skelton.pop("Properties")
        if self.section == "properties":
            _ = skelton.pop("Metadata")

        # dump by format
        if self.fmt == "yaml":
            skelton = yaml.dump(skelton, Dumper=MyDumper)
        else:
            skelton = json.dumps(skelton, indent=2)

        return skelton