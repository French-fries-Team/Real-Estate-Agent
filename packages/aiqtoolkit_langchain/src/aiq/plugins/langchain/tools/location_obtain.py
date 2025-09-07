from aiq.builder.builder import Builder
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

class LocationToolConfig(FunctionBaseConfig, name="current_location"):
    max_results: int = 1
    api_key: str = ""
    

@register_function(config_type=LocationToolConfig)
async def location_obtain(tool_config: LocationToolConfig, builder: Builder):
    import os 
    import requests
    
    async def get_ip_location(ip_address: str) -> str:
        # 使用 ip-api.com 的免费 API
        url = f"http://ip-api.com/json/{ip_address}?lang=zh-CN"
        response = requests.get(url)
        data = response.json()

        if data['status'] == 'success':
            # 格式化输出，使其更具可读性
            location_info = (
                f"IP 地址: {data['query']}\n"
                f"国家: {data['country']} ({data['countryCode']})\n"
                f"地区: {data['regionName']} ({data['region']})\n"
                f"城市: {data['city']}\n"
                f"经度: {data['lon']}\n"
                f"纬度: {data['lat']}\n"
                f"ISP: {data['isp']}\n"
                f"组织: {data['org']}"
            )
            return location_info
    
    yield FunctionInfo.from_fn(
        get_ip_location,
        description=("""This tool retrieves relevant location from IP.

                        Args:
                            question (str): The question to be answered.
                    """),
    )