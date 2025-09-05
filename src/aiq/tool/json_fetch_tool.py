# SPDX-FileCopyrightText: Copyright (c) 2024-2025, NVIDIA CORPORATION & AFFILIATES.
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

import aiohttp
import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict

from aiq.builder.builder import Builder
from aiq.builder.function_info import FunctionInfo
from aiq.cli.register_workflow import register_function
from aiq.data_models.function import FunctionBaseConfig


class JsonFetchToolConfig(FunctionBaseConfig, name="json_fetch_tool"):
    """
    链家新房采集工具：支持分页采集，并导出为 JSON 文件
    """
    base_url: str = "https://sh.fang.lianjia.com/loupan/pg{page}/?_t=1/"
    max_pages: int = 5               # 最大采集页数
    delay_seconds: float = 1.0       # 每页采集间隔（秒）
    export_dir: str = "./data"       # 导出 JSON 文件目录


@register_function(config_type=JsonFetchToolConfig)
async def json_fetch_tool(config: JsonFetchToolConfig, builder: Builder):
    """
    采集链家新房数据并导出为 JSON 文件
    """

    async def _fetch_and_export(unused: str) -> Dict:
        all_data: List[Dict] = []
        os.makedirs(config.export_dir, exist_ok=True)

        timeout = aiohttp.ClientTimeout(total=15)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for page in range(1, config.max_pages + 1):
                url = config.base_url.format(page=page)
                try:
                    async with session.get(url) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        # Fixed data parsing - the correct path is data["data"]["list"]
                        if "data" in data and "list" in data["data"]:
                            all_data.extend(data["data"]["list"])
                except Exception as e:
                    print(f"[ERROR] Failed to fetch page {page}: {e}")
                await asyncio.sleep(config.delay_seconds)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(config.export_dir, f"lianjia_data_{timestamp}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        return {
            "status": "success",
            "file_path": file_path,
            "total_items": len(all_data),
            "preview": all_data[:2]  # 返回部分数据预览
        }

    yield FunctionInfo.from_fn(
        _fetch_and_export,
        description="采集链家新房数据并导出为 JSON 文件，可配置页数和频次"
    )