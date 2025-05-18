from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from starlette.websockets import WebSocket
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

from core.config.config import settings
from user.model import UserRole
from user.repository import UserRepository
from .jwt_auth import decode_token
from user.service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()

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

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends()
) -> dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=401,
                detail="Неверные учетные данные"
            )
            
        user = user_service.get_user_by_username(username)
        if user is None:
            raise HTTPException(
                status_code=401,
                detail="Пользователь не найден"
            )
            
        return user
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Неверные учетные данные"
        )

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt