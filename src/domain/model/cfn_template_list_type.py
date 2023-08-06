
from typing import List, TypeAlias, Union, TYPE_CHECKING

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
