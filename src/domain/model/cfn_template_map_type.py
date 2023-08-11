from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, TypeAlias, Union

if TYPE_CHECKING:
    from src.domain.model.cfn_template_list_type import CfnTemplateResourcePropertyListTypeDefinition
    from src.domain.model.cfn_template_primitive_type import CfnTemplateResourcePropertyPrimitiveTypeDefinition


CfnTemplateResourcePropertyMapTypeDefinition:TypeAlias = Mapping[
    str, Union[
        'CfnTemplateResourcePropertyPrimitiveTypeDefinition',
        'CfnTemplateResourcePropertyListTypeDefinition',
        'CfnTemplateResourcePropertyMapTypeDefinition',
    ]
]
