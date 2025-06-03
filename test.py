from typing import List
from fastapi import FastAPI, Request, WebSocketDisconnect, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates") # som jeg lagde i stad

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, websocket: WebSocket):
        for connections in self.active_connections:
            if(connections == websocket):
                continue
            await websocket.send_text(message)

connectionmanager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
def read_index(request: Request):
    return templates.TemplateResponse("index.html", {"request" : Request})

@app.websocket("/ws/{clien_id}")
def websocket_endpoint(websocket: WebSocket, client_id: int):