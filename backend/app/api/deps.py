from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from ..core.database import get_db
from ..core.settings import settings
from ..models.models import Developer
from ..utils.auth import SECRET_KEY, ALGORITHM
from ..schemas.schemas import TokenData

security = HTTPBearer()


def get_current_developer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Developer:
    """
    获取当前登录的开发者

    :param credentials: Bearer token
    :param db: 数据库会话
    :return: 开发者对象
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭证",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        developer_id: int = payload.get("developer_id")
        if developer_id is None:
            raise credentials_exception
        token_data = TokenData(developer_id=developer_id)
    except JWTError:
        raise credentials_exception

    developer = db.query(Developer).filter(Developer.id == token_data.developer_id).first()
    if developer is None:
        raise credentials_exception

    if developer.status == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    return developer


def verify_admin_access(x_admin_key: str | None = Header(default=None)) -> None:
    if not settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="管理员功能未配置"
        )

    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无管理员权限"
        )
