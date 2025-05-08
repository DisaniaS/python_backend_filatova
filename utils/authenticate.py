from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from starlette.websockets import WebSocket

from user.model import UserRole
from user.repository import UserRepository
from .jwt_auth import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def check_authenticate(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен или срок действия истёк"
        )
    return payload

def check_admin(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен или срок действия истёк"
        )
    print(payload, payload.get("role"))
    if payload.get("role")!=UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="У вас недостаточно прав для выполнения действия"
        )
    return payload


async def get_current_user_ws(websocket: WebSocket, user_repo: UserRepository = Depends()):
    token = websocket.query_params.get("token")
    if not token:
        return None

    try:
        payload = decode_token(token)
        if payload is None:
            return None

        login = payload.get("sub")
        return user_repo.find_by_login(login)
    except Exception:
        return None