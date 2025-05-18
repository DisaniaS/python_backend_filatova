from typing import List, Optional, Union
from fastapi import Depends, HTTPException
from .repository import MessageRepository
from .schema import MessageResponse, MessageUpdate
from user.repository import UserRepository
from datetime import datetime
import os
from fastapi import UploadFile
import aiofiles
import uuid

class MessageService:
    def __init__(self,
                 message_repo: MessageRepository = Depends(),
                 user_repo: UserRepository = Depends()):
        self.message_repo = message_repo
        self.user_repo = user_repo
        self.upload_dir = "uploads"

    def _get_user_id(self, token: dict) -> int:
        username = token.get("sub")
        user = self.user_repo.find_by_login(username)
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return user.id

    async def send_message(self, content: str, token_or_id: Union[dict, int], file: Optional[UploadFile] = None) -> MessageResponse:
        user_id = self._get_user_id(token_or_id) if isinstance(token_or_id, dict) else token_or_id
        file_url = None
        file_name = None
        
        if file:
            file_name = f"{uuid.uuid4()}_{file.filename}"
            file_path = os.path.join(self.upload_dir, file_name)
            os.makedirs(self.upload_dir, exist_ok=True)

            async with aiofiles.open(file_path, 'wb') as out_file:
                content = await file.read()
                await out_file.write(content)
            
            file_url = f"/uploads/{file_name}"
            file_name = file.filename

        db_message = self.message_repo.create("", user_id, file_url, file_name)
        return self._format_message_response(db_message)

    def get_all_messages(self) -> List[MessageResponse]:
        messages = self.message_repo.get_all_messages()
        return [self._format_message_response(msg) for msg in messages]

    async def update_message(self, message_id: int, token: dict, update_data: MessageUpdate) -> MessageResponse:
        user_id = self._get_user_id(token)
        message = self.message_repo.get_message(message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Сообщение не найдено")
        if message.user_id != user_id:
            raise HTTPException(status_code=403, detail="Нет прав на редактирование этого сообщения")
        
        updated_message = self.message_repo.update_message(
            message_id=message_id,
            content=update_data.content,
            is_edited=True,
            edited_at=datetime.now()
        )
        return self._format_message_response(updated_message)

    async def delete_message(self, message_id: int, token: dict) -> MessageResponse:
        user_id = self._get_user_id(token)
        message = self.message_repo.get_message(message_id)
        if not message:
            raise HTTPException(status_code=404, detail="Сообщение не найдено")
        if message.user_id != user_id:
            raise HTTPException(status_code=403, detail="Нет прав на удаление этого сообщения")
        
        deleted_message = self.message_repo.delete_message(message_id)
        return self._format_message_response(deleted_message)

    def _format_message_response(self, db_message) -> MessageResponse:
        user = self.user_repo.find(db_message.user_id)
        return MessageResponse(
            id=db_message.id,
            content=db_message.content,
            user_id=db_message.user_id,
            ts=db_message.ts.isoformat(),
            user_name=f"{user.fname} {user.lname}",
            user_role=user.role.value,
            is_edited=db_message.is_edited,
            edited_at=db_message.edited_at.isoformat() if db_message.edited_at else None,
            file_url=db_message.file_url,
            file_name=db_message.file_name,
            is_deleted=db_message.is_deleted
        )