import json
import uuid
from typing import Dict

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="MCP Service (WebSocket Demo)")
sessions: Dict[str, WebSocket] = {}          # 简易会话表

@app.websocket("/mcp")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    session_id = str(uuid.uuid4())
    sessions[session_id] = ws
    await ws.send_json({"session_id": session_id})  # 首帧回 sessionId

    try:
        while True:
            message = json.loads(await ws.receive_text())
            resp = {"jsonrpc": "2.0", "id": message.get("id")}

            if message.get("method") == "echo":
                resp["result"] = message.get("params", {})
            else:
                resp["error"] = {"code": -32601, "message": "method not found"}

            await ws.send_json(resp)
    except WebSocketDisconnect:
        sessions.pop(session_id, None)

def main():
    uvicorn.run("mcp_service.server:app", host="0.0.0.0", port=8012, reload=True)

if __name__ == "__main__":
    main()
