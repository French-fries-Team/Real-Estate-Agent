# SPDX-FileCopyrightText: Copyright (c) 2024-2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from typing import List, Dict, Any

import httpx
import uuid

from pydantic import BaseModel, Field

from aiq.builder.builder import Builder
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig

logger = logging.getLogger(__name__)

class LianjiaScraperInput(BaseModel):
    """Input schema for the Lianjia scraper tool"""
    city: str = Field(default="sh", description="城市代码，如 sh=上海, bj=北京")
    max_requests: int = Field(default=5, description="采集批次数，整数", ge=1, le=20)

class LianjiaScraperConfig(FunctionBaseConfig, name="lianjia_scraper"):
    """
    链家房产数据采集工具配置。
    用于从链家网站采集房产信息，包括楼盘名称、价格和位置等信息。
    """
    city: str = "sh"
    max_requests: int = 5

@register_function(config_type=LianjiaScraperConfig)
async def lianjia_scraper(config: LianjiaScraperConfig, builder: Builder):

    async def _scrape_lianjia(
        city: str = config.city,
        max_requests: int = config.max_requests
    ) -> Dict[str, Any]:
        """
        从链家楼盘页面采集房产数据。
        
        Args:
            city: 城市代码，如 sh=上海, bj=北京
            max_requests: 采集批次数
            
        Returns:
            包含城市信息、数据总数和房产数据列表的字典
        """
        # Add trailing slash to handle redirect properly
        base_url = f"https://{city}.fang.lianjia.com/loupan/pg{{page}}/?_t=1/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        data_list: List[Dict] = []

        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            for page in range(1, max_requests + 1):
                url = base_url.format(page=page)
                try:
                    logger.info(f"Fetching page {page} for city {city}")
                    resp = await client.get(url, headers=headers)
                    resp.raise_for_status()
                    
                    # Try to parse as JSON first
                    try:
                        raw_data = resp.json()
                        items = raw_data.get("data", {}).get("list", [])
                    except Exception:
                        # If JSON parsing fails, try to handle as plain text
                        logger.warning(f"Failed to parse JSON response for page {page}, trying alternative parsing")
                        items = []
                    
                    # Process items
                    for item in items:
                        data_list.append({
                            "id": str(uuid.uuid4()),
                            "title": item.get("title", ""),
                            "price": item.get("average_price", ""),
                            "location": item.get("district_name", "") + " " + item.get("bizcircle_name", ""),
                            "url": "https://{}.fang.lianjia.com".format(city) + item.get("url", "")
                        })
                        
                except httpx.TimeoutException:
                    logger.error(f"Timeout when fetching page {page} for city {city}")
                    continue
                except httpx.RequestError as e:
                    logger.error(f"Request error when fetching page {page} for city {city}: {e}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error when fetching page {page} for city {city}: {e}")
                    continue

        logger.info(f"Successfully scraped {len(data_list)} items for city {city}")
        return {
            "city": city,
            "count": len(data_list),
            "data": data_list
        }

    yield FunctionInfo.from_fn(
        _scrape_lianjia,
        description="采集链家房产API数据，输出 JSON 格式。支持指定城市和页数。",
        input_schema=LianjiaScraperInput
    )