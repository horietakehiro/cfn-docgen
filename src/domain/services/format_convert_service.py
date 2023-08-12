
from abc import ABC, abstractmethod
import json
import os
from re import escape
from typing import Any, List, Mapping

from src.domain.model.cfn_template import CfnTemplate, CfnTemplateParameterLeaf

class IFormatConvertService(ABC):

    @abstractmethod
    def convert(self, cfn_template:CfnTemplate) -> str:
        pass

class MarkdownConvertService(IFormatConvertService):

    def convert(self, cfn_template: CfnTemplate) -> str:
        markdown_str = "\n---\n".join([
            self.table_of_contents(cfn_template),
            self.overview(cfn_template),
            self.description(cfn_template),
            self.parameters(cfn_template),
            self.mappings(cfn_template),
            self.conditions(cfn_template),
            self.rules(cfn_template),

            self.resources(cfn_template),

            self.outputs(cfn_template),

        ])

        return markdown_str

    def escape_str(self, string:str) -> str:
        return string.lower().replace(" ", "-").replace(":", "")
    
    def escase_json(self, j:Mapping[Any, Any] | str) -> str:
        if isinstance(j, str):
            return j
        s = json.dumps(j, indent=2)
        return s.replace("\n", "<br/>").replace(" ", "&nbsp;")
    
    def overview(self, cfn_template:CfnTemplate) -> str:
        overview:List[str] = []
        overview.append(f"# {os.path.basename(cfn_template.filepath)}")
        overview.append(f"")
        overview.append("| | |")
        overview.append("|-|-|")
        v = cfn_template.definition.AWSTemplateFormatVersion
        overview.append(f"|AWSTemplateFormatVersion|{v if v is not None else '-'}|")
        d = cfn_template.definition.Description
        overview.append(f"|Description|{d if d is not None else '-'}|")
        t = cfn_template.definition.Transform
        transform = ""
        if isinstance(t, str):
            transform = t
        elif len(t) == 0:
            transform = "-"
        else:
            # transform = "<ul>" + "".join([f"<li>{_t}</li>" for _t in t]) + "</ul>"
            transform = self.list_item(t)
        overview.append(f"|Transform|{transform}|")

        return "\n".join(overview)

    def description(self, cfn_template:CfnTemplate) -> str:
        description:List[str] = []
        metadata = cfn_template.definition.Metadata
        if metadata is None:
            description.append("")
        else:
            c = metadata.CfnDocgen
            if c is None:
                description.append("")
            else:
                d = c.Description
                if d is not None:
                    description.append(d)
        return "\n".join(description)

    def table_of_contents(self, cfn_template:CfnTemplate) -> str:
        toc:List[str] = []
        toc.append(f"- [{cfn_template.filepath}](#{self.escape_str(cfn_template.filepath)})")
        toc.append("  - [Description](#description)")

        toc.append("  - [Parameters](#parameters)")
        parameters_by_group, ungrouped_parameter = cfn_template.get_parameters_by_group()
        for group in sorted([group for group in parameters_by_group.keys()]):
            toc.append(f"    - [{group}](#{escape(group)})")
            for parameter in parameters_by_group[group]:
                toc.append(f"      - [{parameter.name}](#{escape(parameter.name)})")
        for parameter in ungrouped_parameter:
            toc.append(f"      - [{parameter.name}](#{escape(parameter.name)})")

        toc.append("  - [Mappings](#mappings)")
        for map_name in sorted([name for name in cfn_template.definition.Mappings.keys()]):
            toc.append(f"    - [{map_name}](#{self.escape_str(map_name)})")
        
        toc.append("  - [Conditions](#conditions)")
        for cond_name in sorted([name for name in cfn_template.definition.Conditions.keys()]):
            toc.append(f"    - [{cond_name}](#{self.escape_str(cond_name)})")
        
        toc.append("  - [Rules](#rules)")
        for rule_name in sorted([name for name in cfn_template.definition.Rules.keys()]):
            toc.append(f"    - [{rule_name}](#{self.escape_str(rule_name)})")
        
        toc.append("  - [Resources](#resources)")
        resource_names_and_types = sorted(
            [[name, cfn_template.definition.Resources[name].Type] for name in cfn_template.definition.Resources.keys()]
        )
        for resource_name, resource_type in resource_names_and_types:
            toc.append(f"    - [{resource_name} ({resource_type})](#{self.escape_str(resource_name)}-{self.escape_str(resource_type)})")

        toc.append("  - [Outputs](#outputs)")
        for output_name in sorted([name for name in cfn_template.definition.Outputs.keys()]):
            toc.append(f"    - [{output_name}](#{self.escape_str(output_name)})")

        return "\n".join(toc)

    def parameters(self, cfn_template:CfnTemplate) -> str:
        doc:List[str] = []

        doc.append("## Parameters")
        doc.append("\n---\n")

        parameters_by_group, ungrouped_parameters = cfn_template.get_parameters_by_group()
        for group in sorted([group for group in parameters_by_group.keys()]):
            doc.append(f"### {group}")
            doc.append("\n---\n")
            for parameter in parameters_by_group[group]:
                doc.append(self.parameter(parameter))

        for parameter in ungrouped_parameters:
            doc.append(self.parameter(parameter))

        return "\n".join(doc)
    
    def parameter(self, parameter:CfnTemplateParameterLeaf) -> str:
        d = parameter.definition
        p:List[str] = []
        p.append(f"#### {parameter.name}")
        p.append("")
        p.append(d.Description if d.Description is not None else "")
        p.append("")
        p.append("|Type|Default|AllowedValues|AllowedPattern|NoEcho|MinValue|MaxValue|MinLength|MaxLength|ConstraintDescription|")
        p.append("|-|-|-|-|-|-|-|-|-|-|")
        
        default = "-"
        if d.Default is not None:
            if isinstance(d.Default, list):
                # default = "<ul>" + "".join([f"<li>{str(_d)}</li>" for _d in d.Default]) + "</ul>"
                default = self.list_item(d.Default)
            else:
                default = str(d.Default)
        allowed_values = "-"
        if d.AllowedValues is not None:
            # allowed_values = "<ul>" + "".join([f"<li>{str(v)}</li>" for v in d.AllowedValues]) + "</ul>"
            allowed_values = self.list_item(d.AllowedValues)
        p.append(
            "|{Type}|{Default}|{AllowedValues}|{AllowedPattern}|{NoEcho}|{MinValue}|{MaxValue}|{MinLength}|{MaxLength}|{ConstraintDescription}|".format(
                Type=d.Type,
                Default=default, 
                AllowedValues=allowed_values,
                AllowedPattern=d.AllowedPattern if d.AllowedPattern is not None else "-",
                NoEcho=str(d.NoEcho).lower(),
                MinValue=str(d.MinValue) if d.MinValue is not None else "-",
                MaxValue=str(d.MaxValue) if d.MaxValue is not None else "-",
                MinLength=str(d.MinLength) if d.MinLength is not None else "-",
                MaxLength=str(d.MaxLength) if d.MaxLength is not None else "-",
                ConstraintDescription=d.ConstraintDescription if d.ConstraintDescription is not None else "-",
            )
        )
        p.append("\n---\n")

        return "\n".join(p)

    def mappings(self, cfn_template:CfnTemplate) -> str:
        doc:List[str] = []

        doc.append("## Mappings")

        mappings = cfn_template.mappings
        for mapping in sorted(mappings, key=lambda m: m.name):
            doc.append("\n---\n")
            doc.append(f"### {mapping.name}")
            doc.append("")
            doc.append(mapping.description if mapping.description is not None else "")
            doc.append("")
            doc.append("|Map|Key|Value|")
            doc.append("|-|-|-|")
            for key in sorted([key for key in mapping.definition.keys()]):
                doc.append(f"|{mapping.name}|{key}|{mapping.definition[key]}|")
        return "\n".join(doc)


    def conditions(self, cfn_template:CfnTemplate) -> str:
        doc:List[str] = []

        doc.append("## Conditions")
        
        conditions = cfn_template.conditions
        for condition in sorted(conditions, key=lambda c: c.name):
            doc.append("\n---\n")
            doc.append(f"### {condition.name}")
            doc.append("")
            doc.append(condition.description if condition.description is not None else "")
            doc.append("")
            doc.append("|Condition|")
            doc.append("|-|")
            if condition.definition is None:
                continue
            doc.append(f"|{self.escase_json(condition.definition)}|")

        return "\n".join(doc)

    def rules(self, cfn_template:CfnTemplate) -> str:
        doc:List[str] = []

        doc.append("## Rules")

        rules = cfn_template.rules
        for rule in sorted(rules, key=lambda r: r.name):
            doc.append("\n---\n")
            doc.append(f"### {rule}")
            doc.append("")
            doc.append(rule.description if rule.description is not None else "")
            doc.append("")
            doc.append("|RuleCondition|")
            doc.append("|-|")
            if rule.definition.RuleCondition is not None:
                doc.append(f"|{self.escase_json(rule.definition.RuleCondition)}|")
            else:
                doc.append("|-|")
            doc.append("")
            doc.append("|Assert|AssertDescription|")
            doc.append("|-|-|")
            if len(rule.definition.Assertions) > 0:
                for assertion in rule.definition.Assertions:
                    doc.append(f"|{self.escase_json(assertion.Assert)}|{assertion.AssertDescription}|")
            else:
                doc.append("|-|-|")
        
        return "\n".join(doc)


    def outputs(self, cfn_template:CfnTemplate) -> str:

        doc:List[str] = []

        doc.append("## Outputs")
        outputs = cfn_template.outputs
        for output in sorted(outputs, key=lambda o: o.name):
            doc.append("\n---\n")
            doc.append(f"### {output.name}")
            doc.append("")
            definition = output.definition
            doc.append(definition.Description if definition.Description is not None else "")
            
            doc.append("")
            doc.append("|Value|ExportName|Condition|")
            doc.append("|-|-|-|")
            value = definition.Value
            export = definition.Export
            export_name = export.Name if export is not None else "-"
            condition = definition.Condition if definition.Condition is not None else "-"            
            doc.append(f"|{self.escase_json(value)}|{self.escase_json(export_name)}|{condition}|")

        return "\n".join(doc)

    def resources(self, cfn_template:CfnTemplate) -> str:
        doc:List[str] = []

        doc.append("## Resources")
        resources = cfn_template.resources
        for resource in sorted(resources, key=lambda r: (r.definition.Type, r.name)):
            doc.append("\n---\n")
            doc.append(f"### {resource.name} ({resource.definition.Type})")
            doc.append("")
            doc.append(resource.description if resource.description is not None else "")
            doc.append("")

            spec = resource.spec

            doc.append(spec.Documentation if spec is not None and spec.Documentation is not None else "")
            doc.append("")
            doc.append("|DependsOn|Condition|CreationPolicy|UpdatePolicy|UpdateReplacePolicy|DeletionPolicy|")
            doc.append("|-|-|-|-|-|-|")
            doc.append("|{DependsOn}|{Condition}|{CreationPolicy}|{UpdatePolicy}|{UpdateReplacePolicy}|{DeletionPolicy}|".format(
                DependsOn=self.list_item(resource.definition.DependsOn) if resource.definition.DependsOn is not None else "-",
                Condition=resource.definition.Condition if resource.definition.Condition is not None else "-",
                CreationPolicy=self.escase_json(resource.definition.CreationPolicy) if resource.definition.CreationPolicy is not None else "-",
                UpdatePolicy=self.escase_json(resource.definition.UpdatePolicy) if resource.definition.UpdatePolicy is not None else "-",
                UpdateReplacePolicy=resource.definition.UpdateReplacePolicy,
                DeletionPolicy=resource.definition.DeletionPolicy,
            ))
            doc.append("")

            doc.append("|Property|Value|Description|Type|Required|UpdateType|")
            doc.append("|-|-|-|-|-|-|")
            doc.append()

        return "\n".join(doc)

    def list_item(self, l:List[Any]) -> str:
        return "<ul>" + "".join([f"<li>{str(i)}</li>" for i in l]) + "</ul>"


