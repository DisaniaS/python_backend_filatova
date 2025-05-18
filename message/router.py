from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, UploadFile, File, HTTPException, Request
from starlette import status
from typing import List
from .service import MessageService
from .schema import MessageResponse, MessageUpdate
from user.service import UserService
from user.repository import UserRepository
from fastapi.responses import FileResponse
import os
from utils.authenticate import get_current_user_ws, check_authenticate
from pydantic import BaseModel

router = APIRouter(prefix="/api/messages", tags=["messages"])
active_connections = []


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


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    message_service: MessageService = Depends(),
    user_repo: UserRepository = Depends()
):
    try:
        user = await get_current_user_ws(websocket, user_repo)
        if not user:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        await websocket.accept()
        active_connections.append(websocket)
        
        # Отправляем историю сообщений при подключении
        messages = message_service.get_all_messages()
        await websocket.send_json({
            "type": "history", 
            "messages": [msg.dict() for msg in messages]
        })
        
        while True:
            data = await websocket.receive_text()
            message = await message_service.send_message(data, user.id)
            
            # Отправляем сообщение всем подключенным клиентам
            for connection in active_connections:
                await connection.send_json({
                    "type": "message", 
                    "message": message.dict()
                })
                
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        if websocket in active_connections:
            active_connections.remove(websocket)
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)

@router.post("/upload", response_model=MessageResponse)
async def upload_file(
    file: UploadFile = File(...),
    message_service: MessageService = Depends(),
    token: dict = Depends(check_authenticate)
):
    return await message_service.send_message("", token, file)

@router.get("/file/{filename}")
async def get_file(filename: str):
    file_path = os.path.join("uploads", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(file_path)

@router.put("/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: int,
    update_data: MessageUpdate,
    message_service: MessageService = Depends(),
    token: dict = Depends(check_authenticate)
):
    return await message_service.update_message(message_id, token, update_data)

@router.delete("/{message_id}", response_model=MessageResponse)
async def delete_message(
    message_id: int,
    message_service: MessageService = Depends(),
    token: dict = Depends(check_authenticate)
):
    return await message_service.delete_message(message_id, token)