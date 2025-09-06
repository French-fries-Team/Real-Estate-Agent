#!/bin/bash
npm install -g @antv/mcp-server-chart
# 使用 nohup 和 & 将进程放到后台运行
nohup mcp-server-chart --transport sse > mcp.log 2>&1 &
# 保存进程ID
echo $! > .mcp.pid
