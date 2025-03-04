from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

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
    print(payload, payload.get("is_admin"))
    if not payload.get("is_admin"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="У вас недостаточно прав для выполнения действия"
        )
    return payload