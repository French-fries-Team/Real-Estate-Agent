#!/bin/bash

echo "🛑 停止 NVIDIA NeMo Agent Toolkit AI对话机器人"
echo "=============================================="

# 停止 MCP 服务
if [ -f .mcp.pid ]; then
    MCP_PID=$(cat .mcp.pid)
    if ps -p $MCP_PID > /dev/null; then
        echo "停止 MCP 服务 (PID: $MCP_PID)..."
        kill $MCP_PID
    fi
    rm -f .mcp.pid
fi

# 停止后端服务
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        echo "停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
    fi
    rm -f .backend.pid
fi

# 停止前端服务
if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        echo "停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    fi
    rm -f .frontend.pid
fi

# 清理其他相关进程
pkill -f "mcp-server-chart" 2>/dev/null || true
pkill -f "aiq serve" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true

echo "✅ 所有服务已停止"
