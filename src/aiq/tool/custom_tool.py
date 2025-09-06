'''
Author: Westen
Date: 2025-09-04 20:31:04
LastEditors: your Name
LastEditTime: 2025-09-04 21:02:48
Description: 
'''
import logging

from pydantic import BaseModel
from pydantic import Field
from pydantic import HttpUrl

from aiq.builder.builder import Builder
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)


class CustomToolConfig(FunctionBaseConfig, name="custom_tool"):
    """ 测试自定义工具调用 """
@register_function(config_type=CustomToolConfig)
async def custom_tool(config: CustomToolConfig, builder: Builder):

    async def _custom_tool_test(text: str) -> str:
        return '这是一个自定义工具调用测试${text}'

    yield FunctionInfo.from_fn(
        _custom_tool_test,
        description="这是一个自定义工具调用测试",
    )