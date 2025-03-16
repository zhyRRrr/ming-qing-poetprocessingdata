#!/usr/bin/env python3
# python_socket_server.py
# 一个简单的WebSocket服务器，用于执行Python命令

import asyncio
import websockets
import json
import subprocess
import sys
import os
import signal
import threading

print("启动Python脚本运行服务器...")

# 处理命令执行
async def run_command(websocket, command):
    process = None
    try:
        # 在子进程中执行命令
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # 实时发送输出
        for line in process.stdout:
            await websocket.send(json.dumps({
                'type': 'output',
                'content': line.strip()
            }))
        
        # 等待进程完成
        process.wait()
        
        # 发送完成状态
        await websocket.send(json.dumps({
            'type': 'status',
            'status': 'completed',
            'exit_code': process.returncode
        }))
    except Exception as e:
        if process:
            try:
                process.terminate()
            except:
                pass
        await websocket.send(json.dumps({
            'type': 'output',
            'content': f"错误: {str(e)}"
        }))
        await websocket.send(json.dumps({
            'type': 'status',
            'status': 'error'
        }))

# 处理WebSocket连接
async def handle_connection(websocket):
    print(f"客户端已连接: {websocket.remote_address}")
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                if data['action'] == 'run':
                    await websocket.send(json.dumps({
                        'type': 'output',
                        'content': f"运行命令: {data['command']}"
                    }))
                    # 异步运行命令
                    await run_command(websocket, data['command'])
            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    'type': 'output',
                    'content': "错误: 收到无效的JSON数据"
                }))
    except websockets.exceptions.ConnectionClosed:
        print("客户端断开连接")

# 启动WebSocket服务器
async def main():
    # 在localhost的6789端口上启动WebSocket服务器
    server = await websockets.serve(handle_connection, "localhost", 6789)
    print("服务器已启动在 ws://localhost:6789")
    print("现在可以从网页中运行Python脚本了")
    await server.wait_closed()

# 处理信号以优雅退出
def signal_handler(sig, frame):
    print("\n正在关闭服务器...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# 启动服务器
if __name__ == "__main__":
    asyncio.run(main())