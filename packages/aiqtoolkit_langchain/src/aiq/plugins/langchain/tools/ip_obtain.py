from aiq.builder.builder import Builder
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

class IPObtainToolConfig(FunctionBaseConfig, name="ip_obtain"):
    """
    Tool that retrieves the public IP address of the machine where the code is running.
    """
    max_results: int = 1
    api_key: str = ""
    
@register_function(config_type=IPObtainToolConfig)
async def ip_obtain(tool_config: IPObtainToolConfig, builder: Builder):
    import os 
    import requests
    
    async def get_public_ip(question: str) -> str:
        return requests.get("https://ifconfig.me").text.strip()
    
    yield FunctionInfo.from_fn(
        get_public_ip,
        description=("""This tool retrieves relevant IP from public.

                        Args:
                            question (str): The question to be answered.
                    """),
    )