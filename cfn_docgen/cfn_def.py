from copy import deepcopy
import os
from typing import List
import json
import pandas as pd
import re
from cfn_flip import to_json
import tqdm
from styleframe import StyleFrame, Styler, utils

from cfn_docgen import util

logger = util.get_module_logger(__name__, util.get_verbose())


def info_logging(name:str):
    def _info_logging(fn):
        def wrap(*args, **kwargs):
            logger.info(f"start process for {name}")
            ret = fn(*args, **kwargs)
            logger.info(f"end process for {name}")
            return ret
        return wrap
    return _info_logging


class CfnResource(object):
    def __init__(self, resource_id:str, resource_def:dict) -> None:

        self.id = resource_id
        self.definition = resource_def
        self.type = resource_def["Type"]

        
        self.creation_policy_def = resource_def.get("CreationPolicy", None)
        self.creation_policy_doc = CfnTemplate.get_spec("creation_policy").get_definition(self.type)
        self.deletion_policy_def = resource_def.get("DeletionPolicy", None)
        self.deletion_policy_doc = CfnTemplate.get_spec("deletion_policy").get_definition(self.type)
        self.update_policy_def = resource_def.get("UpdatePolicy", None)
        self.update_policy_doc = CfnTemplate.get_spec("update_policy").get_definition(self.type)
        self.update_replace_polocy_def = resource_def.get("UpdateReplacePolicy", None)
        self.update_replace_polocy_doc = CfnTemplate.get_spec("update_replace_policy").get_definition(self.type)
        self.depends_on_def = resource_def.get("DependsOn", [])

        self.user_notes = resource_def.get("Metadata", {}).get("UserNotes", {})
        self.note = self.user_notes.get("ResourceNote")

        self.resource_spec = CfnTemplate.get_spec("resource_spec").get_resource_spec(self.type, self.definition)
        self.property_spec = CfnTemplate.get_spec("resource_spec").get_property_spec(self.type)

        self.properties = dict()

        self.construct_root_props()

    def construct_root_props(self):
        """
        construct root properties in definition as property object
        """
        for root_prop_id, root_prop_spec in self.resource_spec["Properties"].items():
            try:
                root_prop_def = self.definition["Properties"][root_prop_id]
            except KeyError:
                root_prop_def = None
            self.properties[root_prop_id] = CfnProperty(
                self.id, self.type, root_prop_id, root_prop_def, root_prop_spec,
                self.user_notes.get("PropNotes", None),
            )


    def to_df(self, name:str):
        """
        convert resource and its property as dataframe
        """
        subcategory = name.split("_")[1]

        if subcategory == "Property":
            return self.prop_to_df(subcategory)
        if subcategory == "CreationPolicy":
            return self.creation_policy_to_df(subcategory)
        if subcategory == "DeletionPolicy":
            return self.deletion_policy_to_df(subcategory)
        if subcategory == "DependsOn":
            return self.depends_on_to_df(subcategory)
        if subcategory == "UpdatePolicy":
            return self.update_policy_to_df(subcategory)
        if subcategory == "UpdateReplacePolicy":
            return self.update_replace_policy_to_df(subcategory) 

    def add_resource_level_columns(self, df:pd.DataFrame) -> pd.DataFrame:
        df.insert(0, "ResourceNote", self.note)
        df.insert(0, "ResourceType", self.type)
        df.insert(0, "ResourceId", self.id)

        return df
    
    def prop_to_df(self, name:str) -> pd.DataFrame:
        df = pd.DataFrame(columns=[
            "Property", "Value", "UserNote", "Required", "Type", "UpdateType", "Description",
        ])

        for prop_id, prop in self.properties.items():
            df = prop.set_record(df)

        df = self.add_resource_level_columns(df)

        df = df.reset_index(drop=True)
        # df = df.sort_values(["ResourceType","ResourceId", "Property"], )
        df.index.name = name

        return df

    def creation_policy_to_df(self, name:str) -> pd.DataFrame:
        if self.creation_policy_doc is None:
            return None

        records = []
        for prop_id, prop_def in self.creation_policy_doc.items():
            record = {"Property": None, "Value": None, "Description": None, "Required": None, "Type": None}
            for key, val in prop_def.items():
                if key == "Description":
                    record["Property"] = prop_id
                    record["Description"] = val
                    records.append(deepcopy(record))
                    record = {k: None for k in record.keys()}
                else:
                    for k, v in val.items():
                        record["Property"] = f"{prop_id}.{key}"
                        record[k] = v
                        if self.creation_policy_def is not None:
                            record["Value"] = self.creation_policy_def.get(prop_id, {}).get(key, None)
                    records.append(deepcopy(record))
                    record = {k: None for k in record.keys()}


        df = pd.DataFrame(records).sort_values(["Property"])

        df = self.add_resource_level_columns(df)
        
        return df

    def deletion_policy_to_df(self, name:str) -> pd.DataFrame:
        if self.deletion_policy_doc is None:
            return None

        records = []
        record = {"Property": None, "Selected": None, "Description": None}
        for key, val in self.deletion_policy_doc.items():
            record["Property"] = key
            record["Description"] = val["Description"]
            record["Selected"] = self.deletion_policy_def == key

            records.append(deepcopy(record))
            record = {k: None for k in record.keys()}

        df = pd.DataFrame(records).sort_values(["Property"])

        df = self.add_resource_level_columns(df)

        return df

    def depends_on_to_df(self, name:str) -> pd.DataFrame:
        records = []
        record = {"DependsOn": None}
        if isinstance(self.depends_on_def, str):
            record["DependsOn"] = self.depends_on_def
            records.append(deepcopy(record))
        else:
            for val in self.depends_on_def:
                record["DependsOn"] = val
                records.append(deepcopy(record))
                record = {k: None for k in record.keys()}

        df = pd.DataFrame(records)
        df = self.add_resource_level_columns(df)

        return df
        

    def update_policy_to_df(self, name:str) -> pd.DataFrame:
        if self.update_policy_doc is None:
            return None

        records = []
        for prop_id, prop_def in self.update_policy_doc.items():
            record = {"Property": None, "Value": None, "Description": None, "Required": None, "Type": None}
            for key, val in prop_def.items():
                if key == "Description":
                    record["Property"] = prop_id
                    record["Description"] = val
                else:
                    record["Property"] = f"{prop_id}.{key}"
                    for k, v in val.items():
                        record[k] = v
                    if self.update_policy_def is not None:
                        record["Value"] = self.update_policy_def.get(prop_id, {}).get(key, None)
                records.append(deepcopy(record))
                record = {k: None for k in record.keys()}

        df = pd.DataFrame(records).sort_values(["Property"])

        df = self.add_resource_level_columns(df)
        
        return df

    def update_replace_policy_to_df(self, name:str) -> pd.DataFrame:
        if self.update_replace_polocy_doc is None:
            return None

        records = []
        record = {"Property": None, "Selected": None, "Description": None}
        for key, val in self.update_replace_polocy_doc.items():
            record["Property"] = key
            record["Description"] = val["Description"]
            record["Selected"] = self.update_replace_polocy_def == key

            records.append(deepcopy(record))
            record = {k: None for k in record.keys()}

        df = pd.DataFrame(records).sort_values(["Property"])

        df = self.add_resource_level_columns(df)
        
        return df

class CfnProperty(object):

    indent_unit = 2

    def __init__(
        self, resource_id:str, resource_type:str, prop_id:str, prop_def:dict, prop_spec:dict,
        prop_notes:dict=None, parent_prop_id:str=None ,level=0, index=None
    ) -> None:

        self.resource_id = resource_id
        self.resource_type = resource_type
        self.id = prop_id
        self.definition = prop_def
        self.spec = prop_spec

        self.prop_notes = prop_notes if prop_notes is not None else dict()

        self.duplication_allowed = prop_spec.get("DuplicatesAllowed", None)
        self.type = prop_spec.get("Type", None)
        self.required = prop_spec.get("Required", None)
        self.update_type = prop_spec.get("UpdateType", None)
        self.primitive_type = prop_spec.get("PrimitiveType", None)
        self.primitive_item_type = prop_spec.get("PrimitiveItemType", None)
        self.item_type = prop_spec.get("ItemType", None)

        self.doc_description = prop_spec.get("DocDescription", None)
        self.doc_required = prop_spec.get("DocRequired", None)
        self.doc_update = prop_spec.get("DocUpdate requires", None)
        self.doc_type = prop_spec.get("DocType", None)

        self.parent_prop_id = parent_prop_id
        self.level = level
        self.index = index

        self.fqid = self.get_fqid()
        self.note = self.prop_notes.get(self.fqid, None)

        self.omitable = None


        # if this prop is primitive, set value
        if self.definition is not None and (self.primitive_type is not None or self.primitive_item_type is not None):
            self.value = self.definition
        elif self.resource_type.startswith("Custom::") or self.resource_type == "AWS::CloudFormation::CustomResource":
            self.value = self.definition
        else:
            self.value = None
        self.child_props = dict()


        self.add_child_prop()


    def get_fqid(self) -> str:
        if self.level == 0:
            return self.id
        if self.index is None:
            return self.parent_prop_id + f".{self.id}"

        return self.parent_prop_id + f"[{self.index}].{self.id}"

    def should_stop(self, resource_type:str, fqid:str) -> bool:

        # logger.error(f"{resource_type}/{fqid}")
        if self.definition is not None:
            return False

        if resource_type == "AWS::EMR::InstanceGroupConfig" and fqid == "Configurations[0].Configurations":
            return True
        if resource_type == "AWS::EMR::InstanceFleetConfig" and fqid == "InstanceTypeConfigs[0].Configurations[0].Configurations":
            return True
        if resource_type == "AWS::EMR::Cluster" and fqid == "Configurations[0].Configurations":
            return True
        if resource_type == "AWS::EMR::Cluster" and fqid == "Instances.CoreInstanceFleet.InstanceTypeConfigs[0].Configurations[0].Configurations":
            return True
        if resource_type == "AWS::EMR::Cluster" and fqid == "Instances.CoreInstanceGroup.Configurations[0].Configurations":
            return True
        if resource_type == "AWS::EMR::Cluster" and fqid == "Instances.MasterInstanceFleet.InstanceTypeConfigs[0].Configurations[0].Configurations":
            return True
        if resource_type == "AWS::EMR::Cluster" and fqid == "Instances.TaskInstanceFleets[0].InstanceTypeConfigs[0].Configurations[0].Configurations":
            return True
        if resource_type == "AWS::EMR::Cluster" and fqid == "Instances.MasterInstanceGroup.Configurations[0].Configurations":
            return True
        if resource_type == "AWS::EMR::Cluster" and fqid == "Instances.TaskInstanceGroups[0].Configurations[0].Configurations":
            return True
        if resource_type == "AWS::WAFv2::WebACL" and re.match(r"^Rules\[0\]\.Statement\.[0-9a-zA-Z]+Statement\.[0-9a-zA-Z]*(Statements\[0\]|Statement)\.", fqid):
            return True
        if resource_type == "AWS::WAFv2::RuleGroup" and re.match(r"^Rules\[0\]\.Statement\.[0-9a-zA-Z]+Statement\.[0-9a-zA-Z]*(Statements\[0\]|Statement)\.", fqid):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid == "BindingProperties.BindingProperties.Predicates[0].Or[0].Or":
            logger.debug("match")
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid == "BindingProperties.BindingProperties.Predicates[0].Or[0].And":
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid == "BindingProperties.BindingProperties.Predicates[0].And[0].And":
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid == "BindingProperties.BindingProperties.Predicates[0].And[0].Or":
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid == "Children[0].Children":
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid == "CollectionProperties.Predicate.Or[0].Or":
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid == "CollectionProperties.Predicate.Or[0].And":
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid == "CollectionProperties.Predicate.And[0].And":
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid == "CollectionProperties.Predicate.And[0].Or":
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.Type.Concat[0]."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.Type.Condition."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.Url.Concat[0]."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.Url.Condition."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.Anchor.Concat[0]."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.Anchor.Condition."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.Target.Concat[0]."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.Target.Condition."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.Global.Concat[0]."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.Global.Condition."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.Fields.Concat[0]."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.Fields.Condition."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.Id.Concat[0]."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.Id.Condition."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.State.Set.Concat[0]."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Events.Parameters.State.Set.Condition."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Properties.Concat[0]."):
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Component" and fqid.startswith("Properties.Condition."):
            return True

        if resource_type == "AWS::AmplifyUIBuilder::Theme" and fqid == "Overrides[0].Value.Children[0].Value":
            return True
        if resource_type == "AWS::AmplifyUIBuilder::Theme" and fqid == "Values[0].Value.Children[0].Value":
            return True

        # if resource_type == "AWS::IoTWireless::TaskDefinition" and fqid == "LoRaWANUpdateGatewayTaskEntry":
        #     return True
        # if resource_type == "AWS::IoTWireless::TaskDefinition" and fqid == "LoRaWANUpdateGatewayTaskEntry":
        #     return True
        # if resource_type == "AWS::IoTWireless::TaskDefinition" and fqid == "LoRaWANUpdateGatewayTaskEntry":
        #     return True


        if resource_type == "AWS::Rekognition::StreamProcessor" and fqid == "List":
            return True

        return False

    def add_child_prop(self):
        """
        if this property has child property, set it to child attr
        child prop may be multiple(list of properties)
        """
        if self.primitive_type is not None or self.primitive_item_type is not None:
            return

        if self.should_stop(self.resource_type, self.fqid):
            return  


        prop_id = self.item_type if self.item_type is not None else self.type
        property_name = prop_id if prop_id == "Tag" else f"{self.resource_type}.{prop_id}"

        prop_spec = CfnTemplate.get_spec("resource_spec").get_property_spec(self.resource_type, property_name)


        for child_prop_id, child_prop_spec in prop_spec[property_name]["Properties"].items():
            unique_id = f"{self.resource_id}.{child_prop_id}"
        # for child_prop_id, child_prop_spec in prop_spec.items():
            if self.type is not None and self.type == "List":
                if isinstance(self.definition, list):
                    child_props = []
                    for i, prop_def in enumerate(self.definition):
                        try:
                            child_prop_def = prop_def[child_prop_id]
                        except (KeyError, TypeError):
                            child_prop_def = None

                        child_props.append(CfnProperty(
                            self.resource_id, self.resource_type, child_prop_id, child_prop_def, child_prop_spec,
                            prop_notes=self.prop_notes,
                            parent_prop_id=self.fqid,
                            level=self.level+1, index=i,
                        ))

                    self.child_props[unique_id] = deepcopy(child_props)
                else:
                    child_props = []
                    child_props.append(CfnProperty(
                        self.resource_id, self.resource_type, child_prop_id, None, child_prop_spec,
                        prop_notes=self.prop_notes,
                        parent_prop_id=self.fqid,
                        level=self.level+1, index=0,
                    ))
                    self.child_props[unique_id] = deepcopy(child_props)
            else:
                prop_def = self.definition

                try:
                    child_prop_def = prop_def[child_prop_id]
                except (KeyError, TypeError):
                    child_prop_def = None
                self.child_props[unique_id] = CfnProperty(
                    self.resource_id, self.resource_type, child_prop_id, child_prop_def, child_prop_spec,
                    prop_notes=self.prop_notes,
                    parent_prop_id=self.fqid,
                    level=self.level+1,
                )

    def repr(self) -> str:
        return self.fqid

    def is_omittable(self, is_parent_omittable:bool=False) -> bool:
        if self.omitable is not None:
            return self.omitable

        if self.value:
            self.omitable = False
            return self.omitable

        if not bool(self.child_props):
            if self.required == False:
                self.omitable = True
                return self.omitable
            else: # required = True
                self.omitable = is_parent_omittable == True
                return self.omitable

        else:
            is_current_omittable = self.required == False

        results = []
        for props in self.child_props.values():
            if isinstance(props, list):
                for prop in props:
                    results.append(prop.is_omittable(is_current_omittable))
            else:
                results.append(props.is_omittable(is_current_omittable))
        self.omitable = all(results)
        return self.omitable

    def set_record(self, df:pd.DataFrame) -> pd.DataFrame:
        tmp_df = pd.DataFrame({
            "Property": [self.repr()],
            "Value": [self.value],
            "UserNote": [self.note],
            "Required": [self.doc_required],
            "Type": [self.doc_type],
            "UpdateType": [self.doc_update],
            "IsOmittable": [self.is_omittable()],
            "Description": [self.doc_description],
            # "FQID": [self.fqid]
        })

        df = pd.concat([df, tmp_df])
        if self.value is None:
            for props in self.child_props.values():
                if isinstance(props, list):
                    for prop in props:
                        df = prop.set_record(df)
                else:
                    df = props.set_record(df)


        return df

class CfnParameter(object):

    def __init__(self, param_id:str, param_def:dict) -> None:
        self.id = param_id
        self.description = param_def.get("Description", None)
        self.allowed_pattern = param_def.get("AllowedPattern", None)
        self.allowed_values = param_def.get("AllowedValues", [])
        self.constraint_description = param_def.get("ConstraintDescription", None)
        self.default = param_def.get("Default", None)
        self.max_length = param_def.get("MaxLength", None)
        self.max_value = param_def.get("MaxValue", None)
        self.min_length = param_def.get("MinLength", None)
        self.min_value = param_def.get("MinValue", None)
        self.no_echo = param_def.get("NoEcho", False)
        self.type = param_def.get("Type", None)

    def to_df(self, name:str) -> pd.DataFrame:
        df = pd.DataFrame({
            "Name": [self.id],
            "Type": [self.type],
            "Description": [self.description],
            "Default": [self.default],
            "MaxLength": [self.max_length],
            "MinLength": [self.min_length],
            "MaxValue": [self.max_value],
            "MinValue": [self.min_value],
            "AllowedPattern": [self.allowed_pattern],
            "AllowedValues": [self.allowed_values],
            "ConstraintDescription": [self.constraint_description],
            "NoEcho": [self.no_echo],
        })

        df.index.name = name

        return df


class CfnOutput(object):

    def __init__(self, output_id:str, output_def:dict) -> None:
        self.id = output_id
        self.description = output_def.get("Description", None)
        self.value = output_def.get("Value", None)
        self.export_name = output_def.get("Export", {}).get("Name", None)

    def to_df(self, name:str) -> pd.DataFrame:
        df = pd.DataFrame({
            "Name": [self.id],
            "Description": [self.description],
            "Value": [self.value],
            "ExportName": [self.export_name],
        })
        df.index.name = name

        return df

class CfnMappings(object):

    def __init__(self, mapping_id:str, mapping_def:dict) -> None:
        self.id = mapping_id
        self.mapping_def = mapping_def

    def to_df(self, name:str) -> pd.DataFrame:
        columns = ["Name", "Item", "Key", "Value"]
        df = pd.DataFrame(columns=columns)
        for item, keyval in self.mapping_def.items():
            for key, val in keyval.items():
                df = pd.concat([
                    df, pd.DataFrame(
                        [[self.id, item, key, val]],
                        columns=columns,
                    )
                ])
        df.index.name = name
        return df


from cfn_docgen import cfn_spec



class CfnTemplate(object):

    cfn_specs = {
        "resource_spec": cfn_spec.CfnSpecification(),
        "creation_policy": cfn_spec.CfnCreationPolicy(),
        "deletion_policy": cfn_spec.CfnDeletionPolicy(),
        "update_policy": cfn_spec.CfnUpdatePolicy(),
        "update_replace_policy": cfn_spec.CfnUpdateReplacePolicy(),
    }

    @classmethod
    def reload_specs(cls):
        spec = cfn_spec.CfnSpecification()
        logger.info(spec.region_name)
        cls.cfn_specs = {
            "resource_spec": cfn_spec.CfnSpecification(),
            "creation_policy": cfn_spec.CfnCreationPolicy(),
            "deletion_policy": cfn_spec.CfnDeletionPolicy(),
            "update_policy": cfn_spec.CfnUpdatePolicy(),
            "update_replace_policy": cfn_spec.CfnUpdateReplacePolicy(),
        }
        logger.info(cls.cfn_specs["resource_spec"].region_name)


    @classmethod
    def get_spec(cls, spec_name:str):
        return cls.cfn_specs[spec_name]
        # return {
        #     "resource_spec": cfn_spec.CfnSpecification(),
        #     "creation_policy": cfn_spec.CfnCreationPolicy(),
        #     "deletion_policy": cfn_spec.CfnDeletionPolicy(),
        #     "update_policy": cfn_spec.CfnUpdatePolicy(),
        #     "update_replace_policy": cfn_spec.CfnUpdateReplacePolicy(),
        # }[spec_name]

    def __init__(self, filepath:str, omit:bool=False) -> None:

        self.reload_specs()
        self.filepath = filepath
        self.body = self.load_template()
        self.is_omit = omit


        self.parameters = self.parse_parameters()
        self.mappings = self.parse_mappings()
        self.resources = self.parse_resources()
        self.outputs = self.parse_outputs()

        # TODOs
        self.description = None
        self.rules = None
        self.conditions = None
        self.transform = None
        self.metadata = None


    @info_logging("parameters")
    def parse_parameters(self) -> List[CfnParameter]:
        logger.info("start process for parameter")
        parameters = []
        for param_id, param_def in tqdm.tqdm(self.body.get("Parameters", {}).items(), desc="parameters"):
            parameters.append(CfnParameter(
                param_id, param_def,
            ))
        logger.info("end process for parameter")
        return parameters

    @info_logging("mappings")
    def parse_mappings(self) -> List[CfnMappings]:
        mappings = []
        for mapping_id, mapping_def in tqdm.tqdm(self.body.get("Mappings", {}).items(), desc="mappings"):
            mappings.append(CfnMappings(
                mapping_id, mapping_def,
            ))
        return mappings


    @info_logging("resources")
    def parse_resources(self) -> List[CfnResource]:
        resources = []
        for resource_id, resource_def in tqdm.tqdm(self.body["Resources"].items(), desc="resources"):
            resource_type = resource_def["Type"]
            if resource_type == "AWS::CDK::Metadata":
                continue
            resources.append(CfnResource(
                resource_id, resource_def,
            ))
        return resources

    @info_logging("outputs")
    def parse_outputs(self) -> List[CfnOutput]:
        outputs = []
        for output_id, output_def in tqdm.tqdm(self.body.get("Outputs", {}).items(), desc="outputs"):
            outputs.append(CfnOutput(
                output_id, output_def,
            ))
        return outputs


    def to_df(self, items:list, name:str) -> pd.DataFrame:

        df = pd.DataFrame()
        all_df = [item.to_df(name) for item in items]

        all_df = [df for df in all_df if df is not None]

        df = pd.concat([df, *all_df])

        # set template level columns
        df["Filename"] = os.path.basename(self.filepath)

        df = df.reset_index(drop=True)
        return df

    def merge_df(self) -> dict:
        targets = {
            "Parameters": self.parameters,
            "Mappings": self.mappings,
            "Resources_Property_Summary": self.resources,
            "Resources_Property_Detail": self.resources,
            "Resources_CreationPolicy": self.resources,
            "Resources_DeletionPolicy": self.resources,
            "Resources_DependsOn": self.resources,
            "Resources_UpdatePolicy": self.resources,
            "Resources_UpdateReplacePolicy": self.resources,
            "Outputs": self.outputs,
        }
        dfs = dict()
        for name, items in targets.items():
            df = self.to_df(items=items, name=name)
            if name == "Resources_Property_Detail":
                df = df.sort_values(["ResourceType", "ResourceId", "Property"])
                if self.is_omit:
                    df = df[df["IsOmittable"] == False]
            dfs[name] = df

        # summarize properties
        target_cols = ["ResourceType", "ResourceId", "ResourceNote"]
        dfs["Resources_Property_Summary"] = (
            dfs["Resources_Property_Detail"].groupby(target_cols, dropna=False)
            .count().reset_index().sort_values(target_cols)
        )[target_cols]
        return dfs

    def load_template(self) -> dict:
        """
        load json or yaml cfn template as dict
        """
        with open(self.filepath, "r") as fp:
            raw = fp.read()
        logger.info(f"load template file from {self.filepath}")
        if self.filepath.split(".")[-1] != "json":
            logger.debug(f"convert template from yaml to json")
            return json.loads(to_json(raw))
        else:
            return json.loads(raw)
    
    def to_file(self, filepath:str=None, fmt:str="xlsx"):
        method_by_fmt = {
            "xlsx": self.to_excel,
            "md": self.to_md,
            "csv": self.to_csv,
            "html": self.to_html,
        }

        if filepath is None:
            filepath = f"{os.path.splitext(self.filepath)[0]}.{fmt}"
        else:
            if fmt != "xlsx":
                filepath = f"{os.path.splitext(self.filepath)[0]}.{fmt}"
            else:
                fmt = filepath.split(".")[-1]
        method_by_fmt[fmt](filepath)

        logger.info(f"save generated file as {fmt} at {filepath}")

    def to_md(self, filepath:str):
        dfs = self.merge_df()

        for name, df in dfs.items():
            path, ext = os.path.splitext(filepath)
            path = f"{path}_{name}{ext}"
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
            df.to_markdown(path, index=False)
        
    def to_csv(self, filepath:str):
        dfs = self.merge_df()
        for name, df in dfs.items():
            path, ext = os.path.splitext(filepath)
            path = f"{path}_{name}{ext}"
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
            df.to_csv(path, index=False)

    def to_html(self, filepath:str):
        dfs = self.merge_df()
        for name, df in dfs.items():
            path, ext = os.path.splitext(filepath)
            path = f"{path}_{name}{ext}"
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
            df.to_html(path, index=False)
        

    def to_excel(self, filepath:str):
        dfs = self.merge_df()
        try:
            os.remove(filepath)
        except FileNotFoundError:
            pass
        with pd.ExcelWriter(filepath, ) as writer:
            wb = writer.book
            for name, df in dfs.items():
                ws = wb.add_worksheet(name)
                # ws = wb.sheets[name]
                (max_row, max_col) = df.shape
                ws.autofilter(1, 1, max_row, max_col - 1)

        style = Styler(horizontal_alignment=utils.horizontal_alignments.left)
        with StyleFrame.ExcelWriter(filepath, mode="a", if_sheet_exists="overlay") as writer:
            for name, df in dfs.items():
                sf = StyleFrame(df)
                sf.set_column_width(columns=sf.columns, width=25)
                if "Description" in sf.columns.tolist():
                    sf.set_column_width(columns="Description", width=100)
                sf.apply_column_style(cols_to_style=sf.columns, styler_obj=style)

                sf.to_excel(
                    writer, index=False, sheet_name=name,
                    startcol=1, startrow=1,
                    freeze_panes=(2,2),
                )
