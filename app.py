from typing import List
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, WebSocket, Request, WebSocketDisconnect
from datetime import datetime, timedelta
import re

app = FastAPI()
templates = Jinja2Templates(directory="templates")

FORBUDTE_ORD = ["faen", "banneord2", "script", "<script>", "xss"]  # Legg til flere ved behov

def filtrer_melding(melding: str) -> tuple[str, bool]:
    original = melding
    # Enkel XSS-sikring
    melding = re.sub(r"<.*?script.*?>", "[sensurert]", melding, flags=re.IGNORECASE)
    # Skjellsord
    for ord in FORBUDTE_ORD:
        melding = re.sub(rf"\b{ord}\b", "[***]", melding, flags=re.IGNORECASE)
    endret = melding != original
    return melding, endret

def logg_mistenkelig_innhold(client_id: int, melding: str):
    tidspunkt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("sikkerhetslogg.txt", "a") as fil:
        fil.write(f"[{tidspunkt}] Klient {client_id} sendte mistenkelig melding: {melding}\n")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.last_message_time = {}

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.last_message_time[websocket] = datetime.min

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        self.last_message_time.pop(websocket, None)

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
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await connectionmanager.connect(websocket)
    try:
        while True:
            now = datetime.now()
            last_time = connectionmanager.last_message_time[websocket]
            if now - last_time < timedelta(seconds=5):
                continue

            data = await websocket.receive_text()
            filtrert_data, endret = filtrer_melding(data)

            if endret:
                logg_mistenkelig_innhold(client_id, data)

            await connectionmanager.send_personal_message(f"You: {filtrert_data}", websocket)
            await connectionmanager.broadcast(f"Client #{client_id}: {filtrert_data}", websocket)

            connectionmanager.last_message_time[websocket] = now

    except WebSocketDisconnect:
        connectionmanager.disconnect(websocket)
        await connectionmanager.broadcast(f"Client #{client_id} har forlatt chatten.")
