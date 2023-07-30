
from abc import ABC, abstractmethod
import json
import os
from re import escape
from typing import Any, List, Mapping

from src.domain.model.cfn_template import CfnTemplate, CfnTemplateParameter

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
            transform = "<ul>" + "".join([f"<li>{_t}</li>" for _t in t]) + "</ul>"
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
        parameters:List[str] = []

        parameters.append("## Parameters")
        parameters.append("\n---\n")

        parameters_by_group, ungrouped_parameters = cfn_template.get_parameters_by_group()
        for group in sorted([group for group in parameters_by_group.keys()]):
            parameters.append(f"### {group}")
            parameters.append("\n---\n")
            for parameter in parameters_by_group[group]:
                parameters.append(self.parameter(parameter))

        for parameter in ungrouped_parameters:
            parameters.append(self.parameter(parameter))

        return "\n".join(parameters)
    
    def parameter(self, parameter:CfnTemplateParameter) -> str:
        d = parameter.definition
        if d is None:
            return ""
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
                default = "<ul>" + "".join([f"<li>{str(_d)}</li>" for _d in d.Default]) + "</ul>"
            else:
                default = str(d.Default)
        allowed_values = "-"
        if d.AllowedValues is not None:
            allowed_values = "<ul>" + "".join([f"<li>{str(v)}</li>" for v in d.AllowedValues]) + "</ul>"
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
        mappings:List[str] = []

        mappings.append("## Mappings")

        m = cfn_template.definition.Mappings
        for map_name in sorted([map_name for map_name in m.keys()]):
            mappings.append("\n---\n")
            mappings.append(f"### {map_name}")
            mappings.append("")
            d = cfn_template.get_mapping_description(map_name)
            mappings.append(d if d is not None else "")
            mappings.append("")
            mappings.append("|Map|Key|Value|")
            mappings.append("|-|-|-|")
            for key in sorted([key for key in m[map_name].keys()]):
                mappings.append(f"|{map_name}|{key}|{m[map_name][key]}|")
            
        return "\n".join(mappings)


    def conditions(self, cfn_template:CfnTemplate) -> str:
        conditions:List[str] = []

        conditions.append("## Conditions")
        
        c = cfn_template.definition.Conditions
        for cond_name in sorted([cond_name for cond_name in c.keys()]):
            conditions.append("\n---\n")
            conditions.append(f"### {cond_name}")
            conditions.append("")
            d = cfn_template.get_condition_description(cond_name)
            conditions.append(d if d is not None else "")
            conditions.append("")
            conditions.append("|Condition|")
            conditions.append("|-|")
            conditions.append(f"|{self.escase_json(c[cond_name])}|")

        return "\n".join(conditions)

    def rules(self, cfn_template:CfnTemplate) -> str:
        rules:List[str] = []

        rules.append("## Rules")

        r = cfn_template.definition.Rules
        for rule_name in sorted([rule_name for rule_name in r.keys()]):
            rules.append("\n---\n")
            rules.append(f"### {rule_name}")
            rules.append("")
            d = cfn_template.get_rule_description(rule_name)
            rules.append(d if d is not None else "")
            rules.append("")
            rules.append("|RuleCondition|")
            rules.append("|-|")
            rule_condition = r[rule_name].RuleCondition
            rules.append(f"|{self.escase_json(rule_condition) if rule_condition is not None else '-'}|")
            rules.append("")
            rules.append("|Assert|AssertDescription|")
            rules.append("|-|-|")
            assertions = r[rule_name].Assertions
            if len(assertions) == 0:
                rules.append("|-|-|")
            else:
                for assertion in assertions:
                    rules.append(f"|{self.escase_json(assertion.Assert)}|{assertion.AssertDescription}|")
        
        return "\n".join(rules)


    def outputs(self, cfn_template:CfnTemplate) -> str:

        outputs:List[str] = []

        outputs.append("## Outputs")
        o = cfn_template.definition.Outputs
        for output_name in sorted([output_name for output_name in o.keys()]):
            outputs.append("\n---\n")
            outputs.append(f"### {output_name}")
            outputs.append("")
            d = o[output_name].Description
            outputs.append(d if d is not None else "")
            outputs.append("")
            outputs.append("|Value|ExportName|Condition|")
            outputs.append("|-|-|-|")
            value = o[output_name].Value
            export = o[output_name].Export
            export_name = export.Name if export is not None else "-"
            condition = o[output_name].Condition if o[output_name].Condition is not None else "-"
            outputs.append(f"|{self.escase_json(value)}|{self.escase_json(export_name)}|{condition}|")

        return "\n".join(outputs)

    def resources(self, cfn_template:CfnTemplate) -> str:
        resource:List[str] = []

        resource.append("## Resources")
        r = cfn_template.definition.Resources
        for r_name, r_type in sorted([(r_name, r[r_name].Type) for r_name in r.keys()], key=lambda r: (r[1], r[0])):
            