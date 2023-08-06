
from typing import Mapping, TypeAlias, Union, TYPE_CHECKING

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
