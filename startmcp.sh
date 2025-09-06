#!/bin/bash
npm install -g @antv/mcp-server-chart
no_proxy="localhost,127.0.0.1" mcp-server-chart --transport sse
