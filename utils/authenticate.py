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