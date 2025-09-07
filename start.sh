#!/bin/bash
echo "🚀 启动 NVIDIA NeMo Agent Toolkit AI对话机器人"
echo "=============================================="

# 设置环境变量
export TAVILY_API_KEY=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

# 启动 MCP 服务
npm install -g @antv/mcp-server-chart
mcp-server-chart --transport sse &
MCP_PID=$!

# 等待 MCP 服务启动
echo "⏳ 等待 MCP 服务启动..."
sleep 3

# 激活Python虚拟环境
source .venv/bin/activate

# 启动后端服务
echo "📡 启动后端服务..."
no_proxy="localhost,127.0.0.1" aiq serve --config_file configs/hackathon_config.yml --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 10

# 启动前端服务
echo "🎨 启动前端服务..."
cd external/aiqtoolkit-opensource-ui
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ 系统启动完成！"
echo ""
echo "🌐 访问地址:"
echo "   前端界面: http://localhost:3000"
echo "   API文档:  http://localhost:8001/docs"
echo ""
echo "📝 测试建议:"
echo "   1. 天气查询: '北京今天的天气怎么样，气温是多少？'"
echo "   2. 公司信息: '帮我介绍一下NVIDIA Agent Intelligence Toolkit'"
echo "   3. 时间查询: '现在几点了？'"
echo ""
echo "🛑 停止服务: 按 Ctrl+C 或运行 ./stop.sh"
echo ""

# 保存进程ID
echo $MCP_PID > .mcp.pid
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# 等待用户中断
wait
