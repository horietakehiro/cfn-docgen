from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
import datetime
import json
import re
from typing import Any, List, Literal, Mapping, cast
from cfn_docgen.config import AppContext
from cfn_docgen.domain.model.cfn_specification import CfnSpecificationProperty

from cfn_docgen.domain.model.cfn_template import CfnTemplateParameterDefinition, CfnTemplateResourcePropertiesNode, CfnTemplateResourcePropertyNode, CfnTemplateTree

SupportedFormat = Literal["markdown"]


def document_generator_factory(fmt:SupportedFormat, context:AppContext) -> ICfnDocumentGenerator:
    match fmt:
        case "markdown":
            context.log_debug(f"format is [{fmt}]. return {CfnMarkdownDocumentGenerator.__name__}")
            return CfnMarkdownDocumentGenerator(context=context)
        case _: # type: ignore
            raise NotImplementedError

class CfnDocumentDestination:
    type: Literal["LocalFilePath", "S3BucketKey", "HttpUrl"]
    dest: str

    def __init__(self, dest:str, context:AppContext) -> None:
        if dest.startswith("s3://"):
            self.type = "S3BucketKey"
        elif dest.startswith("http://") or dest.startswith("https://"):
            self.type = "HttpUrl"
        else:
            self.type = "LocalFilePath"
        self.dest = dest

        context.log_debug(f"type of dest [{dest}] is [{self.type}]")


@dataclass
class PropertyField:
    Property: str
    Value: str
    Description: str
    Required: str
    UpdateType: str
    Type: str
    def as_table_row(self) -> str:
        return "|{Property}|{Value}|{Description}|{Type}|{Required}|{UpdateType}|".format(
            **self.__dict__
        )

class ICfnDocumentGenerator(ABC):

    def __init__(self, context:AppContext) -> None:
        self.context = context

    @abstractmethod
    def generate(self, cfn_template_tree:CfnTemplateTree) -> str:
        pass

class CfnMarkdownDocumentGenerator(ICfnDocumentGenerator):
    lfc = "\n"
    failed_message = "**[cfn-docgen] FAILED TO GENERATE {section}**"

    def generate(self, cfn_template_tree: CfnTemplateTree) -> str:
        start = datetime.datetime.now()
        doc = self.lfc.join([
            self.table_of_contents(cfn_template_tree),
            "",
            "---",
            "",
            self.overview(cfn_template_tree),
            "",
            "---",
            "",
            self.description(cfn_template_tree),
            "",
            "---",
            "",
            self.parameters(cfn_template_tree),
            "",
            "---",
            "",
            self.mappings(cfn_template_tree),
            "",
            "---",
            "",
            self.conditions(cfn_template_tree),
            "",
            "---",
            "",
            self.rules(cfn_template_tree),
            "",
            "---",
            "",
            self.resources(cfn_template_tree),
            "",
            "---",
            "",
            self.outputs(cfn_template_tree),
        ])

        end = datetime.datetime.now()
        self.context.log_debug(f"elapsed time to generate document for [{cfn_template_tree.template_source.source}] is [{(end - start).total_seconds()}s]")
        return doc

    def _toc_escape(self, s:str) -> str:
        """
        - replace ' ' with '-'
        - truncate symbols(except '_' and '-')
        - convert Upper to lower
        """
        return re.sub(
            r"[^\w_-]", "",
            s.lower().replace(" ", "-"),
        )

    def table_of_contents(self, tree:CfnTemplateTree) -> str:
        try:
            toc:List[str] = []
            def line(name:str, indent:int) -> str:
                return f"{' '*indent}- [{name}](#{self._toc_escape(name)})"

            toc.append(line(name=tree.template_source.basename, indent=0))
            toc.append(line(name="Description", indent=2))
            
            toc.append(line(name="Parameters", indent=2))
            for group_name in sorted(
                tree.parameters_node.group_nodes.keys()
            ):
                # list parameters in independ node at the tail of list
                if group_name == tree.parameters_node.group_name_for_independent_parameters:
                    continue
                toc.append(line(name=group_name, indent=4))
                for param_name in sorted(
                    tree.parameters_node.group_nodes[group_name].leaves.keys()
                ):
                    toc.append(line(name=param_name, indent=6))
            independent_nodes = tree.parameters_node.group_nodes.get(
                tree.parameters_node.group_name_for_independent_parameters,
            )
            if independent_nodes is not None:
                for param_name in sorted(independent_nodes.leaves.keys()):
                    toc.append(line(name=param_name, indent=6))
            
            toc.append(line(name="Mappings", indent=2))
            for map_name in sorted(tree.mappings_node.mapping_leaves.keys()):
                toc.append(line(name=map_name, indent=4))
            
            toc.append(line(name="Conditions", indent=2))
            for cond_name in sorted(tree.conditions_node.condition_leaves.keys()):
                toc.append(line(name=cond_name, indent=4))
            
            toc.append(line(name="Rules", indent=2))
            for rule_name in sorted(tree.rules_node.rule_leaves.keys()):
                toc.append(line(name=rule_name, indent=4))
            
            toc.append(line(name="Resources", indent=2))
            for resource_name, resource_node in sorted(
                tree.resources_node.resource_nodes.items(),
                key=lambda item: (item[1].type, item[0])
            ):
                toc.append(line(name=f"{resource_name} ({resource_node.type})", indent=4))
            
            toc.append(line(name="Outputs", indent=2))
            for out_name in sorted(tree.outputs_node.output_leaves.keys()):
                toc.append(line(name=out_name, indent=4))

            return self.lfc.join(toc)
        except Exception:
            self.context.log_warning(
                f"failed to build table_of_contents for [{tree.template_source.source}]"
            )
            return self.failed_message.format(section="Table of Contents")


    def _unordered_list(self, l:Any) -> str:
        if not isinstance(l, list):
            return str(l)
        
        l = cast(List[Any], l)
        if len(l) == 0:
            return "-"
        unorderd_list =  "<ul>"
        for elem in l:
            unorderd_list += f"<li>{str(elem)}</li>"
        unorderd_list += "</ul>"
        return unorderd_list

    def overview(self, tree:CfnTemplateTree) -> str:
        try:
            overview:List[str] = []

            version = "-"
            description = "-"
            transform = "-"
            if tree.aws_template_format_version is not None:
                version = tree.aws_template_format_version
            if tree.description is not None:
                description = tree.description
            if isinstance(tree.transform, str):
                transform = tree.transform
            else:
                transform = self._unordered_list(tree.transform)

            overview.append(f"# {tree.template_source.basename}")
            overview.append("")
            overview.append("| | |")
            overview.append("|-|-|")
            overview.append(f"|AWSTemplateFormatVersion|{version}|")
            overview.append(f"|Description|{description}|")
            overview.append(f"|Transform|{transform}|")

            return self.lfc.join(overview)
        except Exception:
            self.context.log_warning(
                f"failed to build overview for [{tree.template_source.source}]"
            )
            return self.failed_message.format(section="Overview")
    
    def description(self, tree:CfnTemplateTree) -> str:
        try:
            description:List[str] = []

            cfn_docgen_description = ""
            if tree.cfn_docgen_description is not None:
                cfn_docgen_description = tree.cfn_docgen_description
            
            description.append("## Description")
            description.append("")
            description.append(cfn_docgen_description)

            if description[-1] == "":
                description = description[:-1]

            return self.lfc.join(description)
        except Exception:
            self.context.log_warning(
                f"failed to build description for [{tree.template_source.source}]"
            )
            return self.failed_message.format(section="Description")
    
    def parameters(self, tree:CfnTemplateTree) -> str:
        try:
            parameters:List[str] = []
            headers = "|Type|Default|AllowedValues|AllowedPattern|NoEcho|MinValue|MaxValue|MinLength|MaxLength|ConstraintDescription|"
            separators = "|-|-|-|-|-|-|-|-|-|-|"

            def row(d:CfnTemplateParameterDefinition) -> str:
                return "|{Type}|{Default}|{AllowedValues}|{AllowedPattern}|{NoEcho}|{MinValue}|{MaxValue}|{MinLength}|{MaxLength}|{ConstraintDescription}|".format(
                    Type=d.Type,
                    Default=self._unordered_list(d.Default) if d.Default is not None else "-",
                    AllowedValues=self._unordered_list(d.AllowedValues) if d.AllowedValues is not None else "-",
                    AllowedPattern=d.AllowedPattern if d.AllowedPattern is not None else "-",
                    NoEcho=str(d.NoEcho).lower(),
                    MinValue=str(d.MinValue) if d.MinValue is not None else "-",
                    MaxValue=str(d.MaxValue) if d.MaxValue is not None else "-",
                    MinLength=str(d.MinLength) if d.MinLength is not None else "-",
                    MaxLength=str(d.MaxLength) if d.MaxLength is not None else "-",
                    ConstraintDescription=d.ConstraintDescription if d.ConstraintDescription is not None else "-",
                )

            parameters.append("## Parameters")
            parameters.append("")

            for group_name, group_node in sorted(tree.parameters_node.group_nodes.items(), key=lambda g: g[0]):
                if group_name == tree.parameters_node.group_name_for_independent_parameters:
                    continue
                parameters.append(f"### {group_name}")
                parameters.append("")
                for param_name, param in sorted(group_node.leaves.items(), key=lambda p: p[0]):
                    try:
                        d = param.definition
                        parameters.append(f"#### {param_name}")
                        parameters.append("")
                        parameters.append(
                            d.Description if d.Description is not None else ""
                        )
                        parameters.append("")
                        parameters.append(headers)
                        parameters.append(separators)
                        parameters.append(row(param.definition))
                        parameters.append("")
                    except Exception:
                        self.context.log_warning(f"failed to build parameter [{param_name}]")
                        continue

            independent_node = tree.parameters_node.group_nodes.get(
                tree.parameters_node.group_name_for_independent_parameters,
            )
            if independent_node is not None:
                for param_name, param in sorted(
                    independent_node.leaves.items(), key=lambda p: p[0],
                ):
                    try:
                        d = param.definition
                        parameters.append(f"#### {param_name}")
                        parameters.append("")
                        parameters.append(
                            d.Description if d.Description is not None else ""
                        )
                        parameters.append("")
                        parameters.append(headers)
                        parameters.append(separators)
                        parameters.append(row(param.definition))
                        parameters.append("")
                    except Exception:
                        self.context.log_warning(f"failed to build parameter [{param_name}]")
                        continue

            if parameters[-1] == "":
                parameters = parameters[:-1]

            return self.lfc.join(parameters)
        except Exception:
            self.context.log_warning(
                f"failed to build parameters for [{tree.template_source.source}]"
            )
            return self.failed_message.format(section="Parameters")
    
    def mappings(self, tree:CfnTemplateTree) -> str:
        try:
            mappings:List[str] = []
            
            mappings.append("## Mappings")
            mappings.append("")
            for map_name, map_leaf in sorted(tree.mappings_node.mapping_leaves.items(), key=lambda m: m[0]):
                try:
                    mappings.append(f"### {map_name}")
                    mappings.append("")
                    mappings.append(map_leaf.description if map_leaf.description is not None else "")
                    mappings.append("")
                    mappings.append("|Map|Key|Value|")
                    mappings.append("|-|-|-|")
                    for name, body in sorted(map_leaf.definition.items(), key=lambda i: i[0]):
                        for key, val in sorted(body.items(), key=lambda _i: _i[0]):
                            mappings.append(f"|{name}|{key}|{str(val)}|")
                    mappings.append("")
                except Exception:
                    self.context.log_warning(f"failed to build mapping [{map_name}]")
                    continue

            if mappings[-1] == "":
                mappings = mappings[:-1]

            return self.lfc.join(mappings)
        except Exception:
            self.context.log_warning(
                f"failed to build mappings for [{tree.template_source.source}]"
            )
            return self.failed_message.format(section="Mappings")
        
    def _dump_json(self, j:Any) -> str:
        if not isinstance(j, dict) and not isinstance(j, list):
            if isinstance(j, bool):
                self.context.log_error(str(j).lower())
                return str(j).lower()
            # in pydantic v1, bool value will be trated as string
            if isinstance(j, str) and (j == "True" or j == "False"):
                return str(j).lower()
            return str(j) # type: ignore
        dumped = json.dumps(j, indent=2, )
        dumped = dumped.replace("\n", "<br/>").replace(" ", "&nbsp;")
        return dumped

        

    def conditions(self, tree:CfnTemplateTree) -> str:
        try:
            conditions:List[str] = []

            conditions.append("## Conditions")
            conditions.append("")
            for cond_name, cond_leaf in sorted(tree.conditions_node.condition_leaves.items(), key=lambda c: c[0]):
                try:
                    conditions.append(f"### {cond_name}")
                    conditions.append("")
                    conditions.append(cond_leaf.descirption if cond_leaf.descirption is not None else "")
                    conditions.append("")
                    conditions.append("|Condition|")
                    conditions.append("|-|")
                    conditions.append(f"|{self._dump_json(cond_leaf.definition)}|")
                    conditions.append("")
                except Exception:
                    self.context.log_warning(f"failed to build condition [{cond_name}]")

            if conditions[-1] == "":
                conditions = conditions[:-1]

            return self.lfc.join(conditions)
        except Exception:
            self.context.log_warning(
                f"failed to build conditions for [{tree.template_source.source}]"
            )
            return self.failed_message.format(section="Conditions")
    

    def rules(self, tree:CfnTemplateTree) -> str:
        try:
            rules:List[str] = []

            rules.append("## Rules")
            rules.append("")
            for rule_name, rule_leaf in sorted(tree.rules_node.rule_leaves.items(), key=lambda r: r[0]):
                try:
                    rules.append(f"### {rule_name}")
                    rules.append("")
                    rules.append(rule_leaf.description if rule_leaf.description is not None else "")
                    rules.append("")
                    rules.append("|RuleCondition|")
                    rules.append("|-|")
                    rules.append("|{RuleCondition}|".format(
                        RuleCondition=self._dump_json(
                            rule_leaf.definition.RuleCondition
                        ) if rule_leaf.definition.RuleCondition is not None else '-'
                    ))
                    rules.append("")
                    rules.append("|Assert|AssertDescription|")
                    rules.append("|-|-|")
                    for assertion in rule_leaf.definition.Assertions:
                        rules.append("|{Assert}|{AssertDescription}|".format(
                            Assert=self._dump_json(assertion.Assert),
                            AssertDescription=self._dump_json(assertion.AssertDescription)
                        ))
                    rules.append("")
                except Exception:
                    self.context.log_warning(f"failed to build rule [{rule_name}]")
                    continue

            if rules[-1] == "":
                rules = rules[:-1]

            return self.lfc.join(rules)
        except Exception:
            self.context.log_warning(
                f"failed to build rules for [{tree.template_source.source}]"
            )
            return self.failed_message.format(section="Rules")

    def _prop_type_rep(self, p:CfnSpecificationProperty) -> str:
        if p.PrimitiveType is not None:
            return p.PrimitiveType
        if p.PrimitiveItemType is not None and p.Type is not None:
            return f"{p.Type} of {p.PrimitiveItemType}"
        if p.ItemType is not None and p.Type is not None:
            return f"{p.Type} of {p.ItemType}"
        if p.Type is not None:
            return p.Type
        
        return "-"

    def _simplify_jsonpath(self, json_path:str) -> str:
        *rest, tail = json_path.split(".")
        if len(rest) == 1: # ["$"]
            return tail
        
        spaces = "&nbsp;" * 2 * (len(rest)-1)
        # index = re.search(r"\[\d\]$", rest[-1])
        # if index is not None:
        #     return f"{spaces}{index.group()}.{tail}"
        
        return f"{spaces}{tail}"

    def _flatten_property_node(self, property_node:CfnTemplateResourcePropertyNode) -> Mapping[str, PropertyField]:
        property_fields:Mapping[str, PropertyField] = {}

        for leaf in property_node.property_leaves.values():
            if leaf.definition is None:
                continue
            property_fields[leaf.json_path] = PropertyField(
                Property=self._simplify_jsonpath(leaf.json_path),
                Value=self._dump_json(leaf.definition),
                Description=leaf.description if leaf.description is not None else "-",
                Required=str(leaf.spec.Required).lower() if leaf.spec.Required is not None else "-",
                UpdateType=leaf.spec.UpdateType if leaf.spec.UpdateType is not None else "-",
                Type=self._prop_type_rep(leaf.spec)
            )
        for node in property_node.property_nodes.values():
            if not node.has_leaves:
                continue
            property_fields[node.json_path] = PropertyField(
                Property=self._simplify_jsonpath(node.json_path),
                Value="-",
                Description=node.description if node.description is not None else "-",
                Required=str(node.spec.Required).lower() if node.spec is not None and node.spec.Required is not None else "-",
                UpdateType=node.spec.UpdateType if node.spec is not None and node.spec.UpdateType is not None else "-",
                Type=self._prop_type_rep(node.spec) if node.spec is not None else "-"
            )
            property_fields.update(self._flatten_property_node(node))
        for nodes in property_node.property_nodes_list.values():
            for node in nodes:
                if not node.has_leaves:
                    continue
                property_fields[node.json_path] = PropertyField(
                    Property=self._simplify_jsonpath(node.json_path),
                    Value="-",
                    Description=node.description if node.description is not None else "-",
                    Required=str(node.spec.Required).lower() if node.spec is not None and node.spec.Required is not None else "-",
                    UpdateType=node.spec.UpdateType if node.spec is not None and node.spec.UpdateType is not None else "-",
                    Type=self._prop_type_rep(node.spec) if node.spec is not None else "-"
                )
                property_fields.update(self._flatten_property_node(node))
        for nodes in property_node.property_nodes_map.values():
            for node in nodes.values():
                if not node.has_leaves:
                    continue
                property_fields[node.json_path] = PropertyField(
                    Property=self._simplify_jsonpath(node.json_path),
                    Value="-",
                    Description=node.description if node.description is not None else "-",
                    Required=str(node.spec.Required).lower() if node.spec is not None and node.spec.Required is not None else "-",
                    UpdateType=node.spec.UpdateType if node.spec is not None and node.spec.UpdateType is not None else "-",
                    Type=self._prop_type_rep(node.spec) if node.spec is not None else "-"
                )
                property_fields.update(self._flatten_property_node(node))

        return property_fields

    def _flatten_properties_node(self, properties_node:CfnTemplateResourcePropertiesNode) -> List[PropertyField]:
        property_fields:Mapping[str, PropertyField] = {}

        # leaves
        for leaf in properties_node.property_leaves.values():
            if leaf.definition is None:
                continue
            property_fields[leaf.json_path] = PropertyField(
                Property=self._simplify_jsonpath(leaf.json_path),
                Value=self._dump_json(leaf.definition),
                Description=leaf.description if leaf.description is not None else "-",
                Required=str(leaf.spec.Required).lower() if leaf.spec.Required is not None else "-",
                UpdateType=leaf.spec.UpdateType if leaf.spec.UpdateType is not None else "-",
                Type=self._prop_type_rep(leaf.spec)
            )
        for node in properties_node.property_nodes.values():
            if not node.has_leaves:
                continue
            property_fields[node.json_path] = PropertyField(
                Property=self._simplify_jsonpath(node.json_path),
                Value="-",
                Description=node.description if node.description is not None else "-",
                Required=str(node.spec.Required).lower() if node.spec is not None and node.spec.Required is not None else "-",
                UpdateType=node.spec.UpdateType if node.spec is not None and node.spec.UpdateType is not None else "-",
                Type=self._prop_type_rep(node.spec) if node.spec is not None else "-"
            )
            property_fields.update(self._flatten_property_node(node))
        for nodes in properties_node.property_nodes_list.values():
            for node in nodes:
                if not node.has_leaves:
                    continue
                property_fields[node.json_path] = PropertyField(
                    Property=self._simplify_jsonpath(node.json_path),
                    Value="-",
                    Description=node.description if node.description is not None else "-",
                    Required=str(node.spec.Required).lower() if node.spec is not None and node.spec.Required is not None else "-",
                    UpdateType=node.spec.UpdateType if node.spec is not None and node.spec.UpdateType is not None else "-",
                    Type=self._prop_type_rep(node.spec) if node.spec is not None else "-"
                )
                property_fields.update(self._flatten_property_node(node))
        for nodes in properties_node.property_nodes_map.values():
            for node in nodes.values():
                if not node.has_leaves:
                    continue
                property_fields[node.json_path] = PropertyField(
                    Property=self._simplify_jsonpath(node.json_path),
                    Value="-",
                    Description=node.description if node.description is not None else "-",
                    Required=str(node.spec.Required).lower() if node.spec is not None and node.spec.Required is not None else "-",
                    UpdateType=node.spec.UpdateType if node.spec is not None and node.spec.UpdateType is not None else "-",
                    Type=self._prop_type_rep(node.spec) if node.spec is not None else "-"
                )
                property_fields.update(self._flatten_property_node(node))

        property_fields_tuple = sorted(
            [(k, v) for k, v in property_fields.items()],
            key=lambda t: t[0]
        )
        property_fields_list = [t[1] for t in property_fields_tuple]
        return property_fields_list

    def resources(self, tree:CfnTemplateTree) -> str:
        try:
            resources:List[str] = []


            resources.append("## Resources")
            resources.append("")
            for resource_name, resource_node in sorted(
                tree.resources_node.resource_nodes.items(), key=lambda r: (r[1].type, r[0])
            ):
                try:
                    
                    resources.append("### [{Name} ({Type})]({Url})".format(
                        Name=resource_name,
                        Type=resource_node.type,
                        Url=resource_node.spec.Documentation,
                    ))
                    resources.append("")
                    resources.append(
                        resource_node.description if resource_node.description is not None else ""
                    )
                    resources.append("")
                    resources.append("|DependsOn|Condition|CreationPolicy|UpdatePolicy|UpdateReplacePolicy|DeletionPolicy|")
                    resources.append("|-|-|-|-|-|-|")
                    resources.append("|{DependsOn}|{Condition}|{CreationPolicy}|{UpdatePolicy}|{UpdateReplacePolicy}|{DeletionPolicy}|".format(
                        DependsOn=self._dump_json(resource_node.depends_on) if len(resource_node.depends_on) > 0 else "-",
                        Condition=resource_node.condition if resource_node.condition is not None else "-",
                        CreationPolicy=self._dump_json(resource_node.creation_policy) if resource_node.creation_policy is not None else "-",
                        UpdatePolicy=self._dump_json(resource_node.update_policy) if resource_node.update_policy is not None else "-",
                        UpdateReplacePolicy=resource_node.update_replace_policy,
                        DeletionPolicy=resource_node.deletion_policy,
                    ))
                    resources.append("")

                    resources.append("|Property|Value|Description|Type|Required|UpdateType|")
                    resources.append("|-|-|-|-|-|-|")
                    property_fields = self._flatten_properties_node(resource_node.properties_node)
                    for property_field in property_fields:
                        resources.append(property_field.as_table_row())
                    resources.append("")
                except Exception:
                    self.context.log_warning(f"failed to build resource [{resource_name}]")

            if resources[-1] == "":
                resources = resources[:-1]

            return self.lfc.join(resources)
        except Exception:
            self.context.log_warning(
                f"failed to build resources for [{tree.template_source.source}]"
            )
            return self.failed_message.format(section="Resources")
    
    def outputs(self, tree:CfnTemplateTree) -> str:
        try:
            outputs:List[str] = []

            outputs.append("## Outputs")
            outputs.append("")
            for output_name, output_leaf in sorted(
                tree.outputs_node.output_leaves.items(), key=lambda o: o[0],
            ):
                try:
                    outputs.append(f"### {output_name}")
                    outputs.append("")
                    outputs.append(
                        output_leaf.definition.Description if output_leaf.definition.Description is not None else ""
                    )
                    outputs.append("")
                    outputs.append("|Value|ExportName|Condition|")
                    outputs.append("|-|-|-|")
                    outputs.append("|{Value}|{ExportName}|{Condition}|".format(
                        Value=self._dump_json(output_leaf.definition.Value),
                        ExportName=self._dump_json(output_leaf.definition.Export.Name) if output_leaf.definition.Export is not None else  "-",
                        Condition=output_leaf.definition.Condition if output_leaf.definition.Condition is not None else "-",
                    ))
                    outputs.append("")
                except Exception:
                    self.context.log_warning(f"failed to build output [{output_name}]")
            
            if outputs[-1] == "":
                outputs = outputs[:-1]

            return self.lfc.join(outputs)

        except Exception:
            self.context.log_warning(
                f"failed to build outputs for [{tree.template_source.source}]"
            )
            return self.failed_message.format(section="Outputs")
        