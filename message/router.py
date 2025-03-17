from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from starlette import status

from user.repository import UserRepository
from .service import MessageService
from utils.authenticate import get_current_user_ws
from typing import List

router = APIRouter(prefix="/ws/messages", tags=["messages"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("")
async def websocket_endpoint(
        websocket: WebSocket,
        message_service: MessageService = Depends(),
        user_repo: UserRepository = Depends()
):
    user = await get_current_user_ws(websocket, user_repo)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = await message_service.send_message(data, user.id)
            await manager.broadcast(message.dict())
    except WebSocketDisconnect:
        manager.disconnect(websocket)