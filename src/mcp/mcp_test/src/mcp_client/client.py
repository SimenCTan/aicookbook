import asyncio, json, uuid, websockets

URL = "ws://127.0.0.1:8012/mcp"

async def run():
    async with websockets.connect(URL) as ws:
        print("Handshake:", await ws.recv())             # session_id
        req = {"jsonrpc": "2.0", "id": str(uuid.uuid4()),
               "method": "echo", "params": {"msg": "Hello, MCP!"}}
        await ws.send(json.dumps(req))
        print("Response :", await ws.recv())

def main():
    asyncio.run(run())

if __name__ == "__main__":
    main()
