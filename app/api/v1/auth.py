"""
API роуты для авторизации и аутентификации через ЕСИА.
"""

import logging
import uuid
from fastapi import APIRouter, Depends, HTTPException, Header, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.config import settings
from app.core.exceptions import ESIAGatewayException, AuthenticationError, ValidationError
from app.schemas.auth import (
    AuthorizeResponse, TokenResponse, LogoutResponse
)
from app.schemas.user import ESIAUserInfo
from app.services.esia import ESIAService
from app.services.oauth import OAuth2Service
from app.services.user import UserService
from app.services.organization import OrganizationService

router = APIRouter(prefix="/auth", tags=["Авторизация"])
logger = logging.getLogger("esia")


@router.get("/authorize", response_model=AuthorizeResponse, summary="Инициация авторизации")
async def authorize(
    response_type: str = "code",
    provider: str = "esia_oauth",
    scope: str = "openid fullname",
    redirect_uri: Optional[str] = None,
    state: Optional[str] = None,
    nonce: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Инициация процесса авторизации через ЕСИА.
    
    Создает запрос авторизации и возвращает URL для перенаправления пользователя.
    
    Args:
        response_type: Тип ответа (code)
        provider: Провайдер данных (esia_oauth, ebs_oauth, cpg_oauth)
        scope: Области доступа (разрешены: openid, fullname, birthdate, gender, citizenship, id_doc, email, mobile, addresses)
        redirect_uri: URI возврата (если не указан, берется из настроек)
        state: Состояние запроса (UUID, генерируется автоматически если не указан)
        nonce: Nonce для предотвращения подделки (UUID, генерируется автоматически если не указан)
        db: Сессия базы данных
        
    Returns:
        URL для авторизации и состояние запроса
        
    Raises:
        HTTPException: При ошибке валидации или создания запроса
    """
    logger.info(f"OAuth 2.0 запрос авторизации с областями доступа: {scope}")
    
    try:
        # Инициализация OAuth 2.0 сервиса
        oauth_service = OAuth2Service()
        
        # Построение URL авторизации
        auth_data = oauth_service.build_authorization_url(
            scopes=scope,
            state=state,
            nonce=nonce,
            redirect_uri=redirect_uri,
            provider=provider
        )
        
        # Сохранение запроса в базе данных
        user_service = UserService(db)
        request_data = {
            "client_id": settings.esia_client_id,
            "response_type": response_type,
            "provider": provider,
            "scope": scope,
            "redirect_uri": auth_data["redirect_uri"],
            "state": auth_data["state"],
            "nonce": auth_data["nonce"]
        }
        user_service.auth_repo.create(request_data)
        
        logger.info(f"OAuth 2.0 URL авторизации создан для состояния: {auth_data['state']}")
        
        return AuthorizeResponse(
            authorization_url=auth_data["authorization_url"],
            state=auth_data["state"]
        )
        
    except ValidationError as e:
        logger.error(f"Ошибка валидации запроса авторизации: {str(e)}")
        raise HTTPException(status_code=422, detail={
            "error": "Ошибка валидации данных",
            "message": str(e),
            "details": e.details
        })
    except ESIAGatewayException as e:
        logger.error(f"Ошибка ЕСИА при создании запроса авторизации: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail={
            "error": "Ошибка сервиса ЕСИА",
            "message": str(e),
            "details": e.details
        })
    except Exception as e:
        logger.error(f"Неожиданная ошибка при создании запроса авторизации: {str(e)}")
        raise HTTPException(status_code=400, detail={
            "error": "Ошибка создания запроса авторизации",
            "message": "Не удалось создать запрос авторизации. Проверьте корректность переданных параметров."
        })


@router.post("/token", response_model=TokenResponse, summary="Получение токена доступа")
async def get_token(
    grant_type: str = Form(..., description="Тип разрешения: authorization_code или refresh_token"),
    redirect_uri: str = Form(...),
    code: Optional[str] = Form(None),
    refresh_token: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    OAuth 2.0 обмен авторизационного кода на токен доступа или обновление токена.
    
    Args:
        grant_type: Тип разрешения (authorization_code или refresh_token)
        redirect_uri: URI возврата
        code: Авторизационный код (для authorization_code)
        refresh_token: Токен обновления (для refresh_token)
        db: Сессия базы данных
        
    Returns:
        Данные токена доступа
        
    Raises:
        HTTPException: При ошибке получения токена
    """
    logger.info(f"OAuth 2.0 запрос токена, тип разрешения: {grant_type}")
    
    # Валидация grant_type
    if grant_type not in ["authorization_code", "refresh_token"]:
        raise HTTPException(status_code=422, detail={
            "error": "Неверный тип разрешения",
            "message": "grant_type должен быть 'authorization_code' или 'refresh_token'",
            "details": {"grant_type": grant_type}
        })
    
    # Валидация параметров в зависимости от типа разрешения
    if grant_type == "authorization_code" and not code:
        raise HTTPException(status_code=422, detail={
            "error": "Отсутствует код авторизации",
            "message": "Для grant_type='authorization_code' требуется параметр 'code'",
            "details": {"grant_type": grant_type}
        })
    
    if grant_type == "refresh_token" and not refresh_token:
        raise HTTPException(status_code=422, detail={
            "error": "Отсутствует токен обновления",
            "message": "Для grant_type='refresh_token' требуется параметр 'refresh_token'",
            "details": {"grant_type": grant_type}
        })
    
    try:
        # Создание запроса токена с параметрами из настроек
        token_request_data = {
            grant_type=grant_type,
            "client_id": settings.esia_client_id,
            "client_secret": settings.esia_client_secret,
            redirect_uri=redirect_uri,
        }
        
        if code:
            token_request_data["code"] = code
        if refresh_token:
            token_request_data["refresh_token"] = refresh_token
        
        # Получение токена от ЕСИА
        async with ESIAService() as esia_service:
            token_data = await esia_service.exchange_code_for_token(token_request_data)
        
        logger.info(f"OAuth 2.0 токен успешно получен")
        
        return TokenResponse(**token_data)
        
    except ESIAGatewayException as e:
        logger.error(f"Ошибка ЕСИА при получении токена: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail={
            "error": "Ошибка получения токена",
            "message": str(e),
            "details": e.details
        })
    except ValidationError as e:
        logger.error(f"Ошибка валидации запроса токена: {str(e)}")
        raise HTTPException(status_code=422, detail={
            "error": "Ошибка валидации данных",
            "message": str(e),
            "details": e.details
        })
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении токена: {str(e)}")
        raise HTTPException(status_code=400, detail={
            "error": "Ошибка получения токена",
            "message": "Не удалось получить токен доступа. Проверьте корректность переданных параметров."
        })


@router.post("/userinfo", response_model=ESIAUserInfo, summary="Получение данных пользователя")
async def get_user_info(
    authorization: str = Header(..., description="Bearer токен"),
    scope: Optional[str] = Form(None, description="Конкретные области доступа"),
    db: Session = Depends(get_db)
):
    """
    Получение информации о пользователе из ЕСИА.
    
    Args:
        authorization: Заголовок авторизации с Bearer токеном
        scope: Конкретные области доступа (опционально)
        db: Сессия базы данных
        
    Returns:
        Информация о пользователе из ЕСИА
        
    Raises:
        HTTPException: При ошибке получения данных
    """
    logger.info("Запрос данных пользователя из ЕСИА")
    
    try:
        # Извлечение токена из заголовка
        if not authorization.startswith("Bearer "):
            raise AuthenticationError(
                "Неверный формат токена авторизации. Ожидается 'Bearer <token>'",
                details={"header": "Authorization"}
            )
        
        access_token = authorization.replace("Bearer ", "")
        
        # Получение данных пользователя от ЕСИА
        async with ESIAService() as esia_service:
            user_data = await esia_service.get_user_info(access_token, scope)
        
        # Создание или обновление пользователя в базе данных
        user_service = UserService(db)
        org_service = OrganizationService(db)
        
        esia_user_info = ESIAUserInfo(**user_data)
        user = user_service.create_or_update_user_from_esia(esia_user_info)
        
        # Обработка организаций пользователя (если есть)
        if "orgs" in esia_user_info.info:
            org_service.process_organizations_from_esia(esia_user_info.info, user.id)
        
        logger.info(f"Данные пользователя успешно получены: {user.esia_uid}")
        
        return esia_user_info
        
    except AuthenticationError as e:
        logger.error(f"Ошибка аутентификации: {str(e)}")
        raise HTTPException(status_code=401, detail={
            "error": "Ошибка аутентификации",
            "message": str(e),
            "details": e.details
        })
    except ESIAGatewayException as e:
        logger.error(f"Ошибка ЕСИА при получении данных пользователя: {str(e)}")
        raise HTTPException(status_code=e.status_code, detail={
            "error": "Ошибка получения данных пользователя",
            "message": str(e),
            "details": e.details
        })
    except Exception as e:
        logger.error(f"Неожиданная ошибка при получении данных пользователя: {str(e)}")
        raise HTTPException(status_code=400, detail={
            "error": "Ошибка получения данных пользователя",
            "message": "Не удалось получить данные пользователя. Проверьте корректность токена доступа."
        })


@router.get("/logout", response_model=LogoutResponse, summary="Выход из системы ЕСИА")
async def logout(
    redirect_uri: Optional[str] = None,
    state: Optional[str] = None
):
    """
    OAuth 2.0 инициация выхода из системы ЕСИА.
    
    Args:
        redirect_uri: URI возврата после выхода (если не указан, берется из настроек)
        state: Состояние запроса (UUID, генерируется автоматически если не указан)
        
    Returns:
        URL для выхода из системы
        
    Raises:
        HTTPException: При ошибке создания запроса выхода
    """
    logger.info("OAuth 2.0 запрос выхода из системы")
    
    try:
        # Инициализация OAuth 2.0 сервиса
        oauth_service = OAuth2Service()
        
        # Построение URL выхода
        logout_url = oauth_service.build_logout_url(redirect_uri, state)
        
        logger.info("OAuth 2.0 URL выхода создан")
        
        return LogoutResponse(
            logout_url=logout_url,
            redirect_uri=redirect_uri or settings.esia_redirect_uri
        )
        
    except ValidationError as e:
        logger.error(f"Ошибка валидации запроса выхода: {str(e)}")
        raise HTTPException(status_code=422, detail={
            "error": "Ошибка валидации данных",
            "message": str(e),
            "details": e.details
        })
    except Exception as e:
        logger.error(f"Неожиданная ошибка при создании запроса выхода: {str(e)}")
        raise HTTPException(status_code=400, detail={
            "error": "Ошибка создания запроса выхода",
            "message": "Не удалось создать запрос выхода. Проверьте корректность переданных параметров."
        })


@router.get("/callback", summary="Обработка callback после авторизации")
async def auth_callback(
    code: Optional[str] = None,
    state: str = "",
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Обработка callback после авторизации в ЕСИА.
    
    Args:
        code: Авторизационный код (при успешной авторизации)
        state: Состояние запроса
        error: Код ошибки (при неуспешной авторизации)
        error_description: Описание ошибки
        db: Сессия базы данных
        
    Returns:
        Перенаправление на соответствующую страницу
    """
    logger.info(f"Callback авторизации получен: state={state}")
    
    try:
        user_service = UserService(db)
        
        # Поиск запроса авторизации по состоянию
        auth_request = user_service.auth_repo.get_by_state(state)
        if not auth_request:
            logger.warning(f"Запрос авторизации с состоянием {state} не найден")
            raise HTTPException(status_code=404, detail={
                "error": "Запрос авторизации не найден",
                "message": f"Запрос авторизации с состоянием {state} не найден в системе"
            })
        
        if error:
            # Обработка ошибки авторизации
            logger.warning(f"Ошибка авторизации: {error} - {error_description}")
            user_service.auth_repo.update_with_error(state, error, error_description or "")
            
            # Перенаправление на страницу ошибки
            error_url = f"{auth_request.redirect_uri}?error={error}&error_description={error_description or ''}&state={state}"
            return RedirectResponse(url=error_url)
        
        elif code:
            # Успешная авторизация
            logger.info(f"Успешная авторизация с кодом для состояния: {state}")
            user_service.auth_repo.update_with_code(state, code)
            
            # Перенаправление на страницу успеха
            success_url = f"{auth_request.redirect_uri}?code={code}&state={state}"
            return RedirectResponse(url=success_url)
        
        else:
            logger.error("Callback не содержит ни кода, ни ошибки")
            raise HTTPException(status_code=400, detail={
                "error": "Неверный callback",
                "message": "Callback должен содержать либо код авторизации, либо информацию об ошибке"
            })
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке callback: {str(e)}")
        raise HTTPException(status_code=400, detail={
            "error": "Ошибка обработки callback",
            "message": "Не удалось обработать callback от ЕСИА"
        })