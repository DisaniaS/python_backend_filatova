from typing import List

from fastapi import Depends
from .repository import MessageRepository
from .schema import MessageResponse
from user.repository import UserRepository
from datetime import datetime

class MessageService:
    def __init__(self,
                 message_repo: MessageRepository = Depends(),
                 user_repo: UserRepository = Depends()):
        self.message_repo = message_repo
        self.user_repo = user_repo

    async def send_message(self, content: str, user_id: int) -> MessageResponse:
        db_message = self.message_repo.create(content, user_id)
        return self._format_message_response(db_message)

    def get_all_messages(self) -> List[MessageResponse]:
        messages = self.message_repo.get_all_messages()
        return [self._format_message_response(msg) for msg in messages]

    def _format_message_response(self, db_message) -> MessageResponse:
        user = self.user_repo.find(db_message.user_id)
        return MessageResponse(
            id=db_message.id,
            content=db_message.content,
            user_id=db_message.user_id,
            ts=db_message.ts.isoformat(),
            user_name=f"{user.fname} {user.lname}",
            user_role=user.role.value,
        )