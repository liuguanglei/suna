import json
import asyncio
from contextlib import AsyncExitStack
from mcp import ClientSession
from mcp.client.sse import sse_client

class Client:
    def __init__(self):
        self._exit_stack = None
        self.session = None
        self._lock = asyncio.Lock()
        self.is_connected = False

    async def connect_server(self, server_config):
        async with self._lock:
            url = server_config["mcpServers"]["amap-amap-sse"]["url"]
            print(f"尝试连接到: {url}")
            self._exit_stack = AsyncExitStack()
            sse_cm = sse_client(url)
            streams = await self._exit_stack.enter_async_context(sse_cm)
            print("SSE 流已获取。")
            session_cm = ClientSession(streams[0], streams[1])
            self.session = await self._exit_stack.enter_async_context(session_cm)
            print("ClientSession 已创建。")
            await self.session.initialize()
            print("Session 已初始化。")
            response = await self.session.list_tools()
            self.tools = {tool.name: tool for tool in response.tools}
            print(f"成功获取 {len(self.tools)} 个工具:")
            for name, tool in self.tools.items():
                print(f"  - {name}: {tool.description[:50]}...")
            print("连接成功并准备就绪。")

    async def disconnect(self):
        async with self._lock:
            await self._exit_stack.aclose()

async def main():
    server_config = {
        "mcpServers": {
            "amap-amap-sse": {
                "url": "https://mcp.amap.com/sse?key=ad0179431f686db5d937a3c7b8071c80"
            }
        }
    }
    client = Client()
    await client.connect_server(server_config)
    # 在此处可以使用 client.session 调用工具等
    await client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())