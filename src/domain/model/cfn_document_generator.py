from abc import ABC, abstractmethod
import json
import re
from typing import Any, List, cast

from domain.model.cfn_template import CfnTemplateParameterDefinition, CfnTemplateTree


class IDocumentGenerator(ABC):

    @abstractmethod
    def generate(self, tree:CfnTemplateTree) -> bytes:
        pass

class MarkdownDocumentGenerator(IDocumentGenerator):
    lfc = "\n"

    def generate(self, tree: CfnTemplateTree) -> bytes:
        return b""

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
        
    def title(self, tree:CfnTemplateTree) -> str:
        return f"# {tree.template_source.basename}"

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
    
    def description(self, tree:CfnTemplateTree) -> str:
        description:List[str] = []

        cfn_docgen_description = ""
        if tree.cfn_docgen_description is not None:
            cfn_docgen_description = tree.cfn_docgen_description
        
        description.append("## Description")
        description.append("")
        description.append(cfn_docgen_description)

        return self.lfc.join(description)
    
    def parameters(self, tree:CfnTemplateTree) -> str:
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
        independent_node = tree.parameters_node.group_nodes.get(
            tree.parameters_node.group_name_for_independent_parameters,
        )
        if independent_node is not None:
            for param_name, param in sorted(
                independent_node.leaves.items(), key=lambda p: p[0],
            ):
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

        if parameters[-1] == "":
            parameters = parameters[:-1]

        return self.lfc.join(parameters)
    
    def mappings(self, tree:CfnTemplateTree) -> str:
        mappings:List[str] = []
        
        mappings.append("## Mappings")
        mappings.append("")
        for map_name, map_leaf in sorted(tree.mappings_node.mapping_leaves.items(), key=lambda m: m[0]):
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

        if mappings[-1] == "":
            mappings = mappings[:-1]

        return self.lfc.join(mappings)
    
    def _dump_json(self, j:Any) -> str:
        if not isinstance(j, dict) and not isinstance(j, list):
            return str(j) # type: ignore
        dumped = json.dumps(j, indent=2, )
        dumped = dumped.replace("\n", "<br/>").replace(" ", "&nbsp;")
        return dumped

        

    def conditions(self, tree:CfnTemplateTree) -> str:
        conditions:List[str] = []

        conditions.append("## Conditions")
        conditions.append("")
        for cond_name, cond_leaf in sorted(tree.conditions_node.condition_leaves.items(), key=lambda c: c[0]):
            conditions.append(f"### {cond_name}")
            conditions.append("")
            conditions.append(cond_leaf.descirption if cond_leaf.descirption is not None else "")
            conditions.append("")
            conditions.append("|Conditions|")
            conditions.append("|-|")
            conditions.append(f"|{self._dump_json(cond_leaf.definition)}|")
            conditions.append("")

        if conditions[-1] == "":
            conditions = conditions[:-1]

        return self.lfc.join(conditions)
    

    def rules(self, tree:CfnTemplateTree) -> str:
        rules:List[str] = []

        rules.append("## Rules")
        rules.append("")
        for rule_name, rule_leaf in sorted(tree.rules_node.rule_leaves.items(), key=lambda r: r[0]):
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

        if rules[-1] == "":
            rules = rules[:-1]

        return self.lfc.join(rules)