from __future__ import annotations
from typing import TYPE_CHECKING, List, TypeAlias, Union

if TYPE_CHECKING:
    from src.domain.model.cfn_template_map_type import CfnTemplateResourcePropertyMapTypeDefinition
    from src.domain.model.cfn_template_primitive_type import CfnTemplateResourcePropertyPrimitiveTypeDefinition


CfnTemplateResourcePropertyListTypeDefinition:TypeAlias = List[
    Union[
        'CfnTemplateResourcePropertyPrimitiveTypeDefinition', 
        'CfnTemplateResourcePropertyMapTypeDefinition',
        'CfnTemplateResourcePropertyListTypeDefinition',
    ]
]
