"""
Веб-интерфейс для авторизации через Госуслуги.
Предоставляет HTML страницы с кнопкой авторизации.
"""

import logging
from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from app.core.database import get_db
from app.core.config import settings
from app.services.oauth import OAuth2Service
from app.services.user import UserService
from app.services.esia import ESIAService

router = APIRouter(tags=["Веб-интерфейс"])
templates = Jinja2Templates(directory="templates")
logger = logging.getLogger(__name__)


@router.get("/", response_class=HTMLResponse, summary="Главная страница")
async def home(request: Request):
    """
    Главная страница с кнопкой авторизации через Госуслуги.
    
    Args:
        request: HTTP запрос
        
    Returns:
        HTML страница с интерфейсом авторизации
    """
    oauth_service = OAuth2Service()
    recommended_scopes = oauth_service.get_recommended_scopes()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "Авторизация через Госуслуги",
        "scopes": recommended_scopes,
        "esia_debug": settings.esia_debug
    })


@router.get("/login", summary="Инициация авторизации через веб-интерфейс")
async def web_login(
    scopes: str = Query("openid fullname email", description="Области доступа"),
    db: Session = Depends(get_db)
):
    """
    Инициация авторизации через веб-интерфейс.
    Перенаправляет пользователя на страницу авторизации ЕСИА.
    
    Args:
        scopes: Области доступа
        db: Сессия базы данных
        
    Returns:
        Перенаправление на страницу авторизации ЕСИА
    """
    logger.info(f"Веб-авторизация с областями доступа: {scopes}")
    
    try:
        oauth_service = OAuth2Service()
        
        # Построение URL авторизации
        auth_data = oauth_service.build_authorization_url(
            scopes=scopes,
            provider="esia_oauth"
        )
        
        # Сохранение запроса в базе данных
        user_service = UserService(db)
        request_data = {
            "client_id": settings.esia_client_id,
            "response_type": "code",
            "provider": "esia_oauth",
            "scope": scopes,
            "redirect_uri": auth_data["redirect_uri"],
            "state": auth_data["state"],
            "nonce": auth_data["nonce"]
        }
        user_service.auth_repo.create(request_data)
        
        logger.info(f"Перенаправление на авторизацию ЕСИА: {auth_data['state']}")
        
        # Перенаправление на страницу авторизации ЕСИА
        return RedirectResponse(url=auth_data["authorization_url"])
        
    except Exception as e:
        logger.error(f"Ошибка веб-авторизации: {str(e)}")
        raise HTTPException(status_code=400, detail={
            "error": "Ошибка авторизации",
            "message": "Не удалось инициировать авторизацию через Госуслуги"
        })


@router.get("/callback", response_class=HTMLResponse, summary="Обработка callback после авторизации")
async def web_callback(
    request: Request,
    code: Optional[str] = None,
    state: str = "",
    error: Optional[str] = None,
    error_description: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Обработка callback после авторизации в ЕСИА.
    Отображает результат авторизации и данные пользователя.
    
    Args:
        request: HTTP запрос
        code: Авторизационный код (при успешной авторизации)
        state: Состояние запроса
        error: Код ошибки (при неуспешной авторизации)
        error_description: Описание ошибки
        db: Сессия базы данных
        
    Returns:
        HTML страница с результатом авторизации
    """
    logger.info(f"Веб-callback авторизации: state={state}")
    
    try:
        user_service = UserService(db)
        
        # Поиск запроса авторизации по состоянию
        auth_request = user_service.auth_repo.get_by_state(state)
        if not auth_request:
            logger.warning(f"Запрос авторизации с состоянием {state} не найден")
            return templates.TemplateResponse("error.html", {
                "request": request,
                "title": "Ошибка авторизации",
                "error": "Запрос не найден",
                "message": "Запрос авторизации не найден в системе"
            })
        
        if error:
            # Обработка ошибки авторизации
            logger.warning(f"Ошибка авторизации: {error} - {error_description}")
            user_service.auth_repo.update_with_error(state, error, error_description or "")
            
            return templates.TemplateResponse("error.html", {
                "request": request,
                "title": "Ошибка авторизации",
                "error": error,
                "message": error_description or "Произошла ошибка при авторизации"
            })
        
        elif code:
            # Успешная авторизация - получение токена и данных пользователя
            logger.info(f"Успешная авторизация с кодом для состояния: {state}")
            user_service.auth_repo.update_with_code(state, code)
            
            try:
                # Обмен кода на токен
                async with ESIAService() as esia_service:
                    token_data = await esia_service.exchange_code_for_token({
                        "grant_type": "authorization_code",
                        "client_id": settings.esia_client_id,
                        "client_secret": settings.esia_client_secret,
                        "redirect_uri": auth_request.redirect_uri,
                        "code": code
                    })
                
                # Получение данных пользователя
                user_data = await esia_service.get_user_info(token_data["access_token"])
                
                # Создание или обновление пользователя в базе данных
                from app.schemas.user import ESIAUserInfo
                esia_user_info = ESIAUserInfo(**user_data)
                user = user_service.create_or_update_user_from_esia(esia_user_info)
                
                # Сохранение токена
                user_service.save_user_token(user.id, token_data)
                
                logger.info(f"Пользователь успешно авторизован: {user.esia_uid}")
                
                return templates.TemplateResponse("success.html", {
                    "request": request,
                    "title": "Успешная авторизация",
                    "user": user,
                    "user_info": esia_user_info.info,
                    "token_expires_in": token_data.get("expires_in", 0)
                })
                
            except Exception as e:
                logger.error(f"Ошибка получения данных пользователя: {str(e)}")
                return templates.TemplateResponse("error.html", {
                    "request": request,
                    "title": "Ошибка получения данных",
                    "error": "Ошибка API",
                    "message": "Не удалось получить данные пользователя из ЕСИА"
                })
        
        else:
            logger.error("Callback не содержит ни кода, ни ошибки")
            return templates.TemplateResponse("error.html", {
                "request": request,
                "title": "Неверный callback",
                "error": "Неверные параметры",
                "message": "Callback должен содержать либо код авторизации, либо информацию об ошибке"
            })
            
    except Exception as e:
        logger.error(f"Неожиданная ошибка при обработке callback: {str(e)}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "title": "Системная ошибка",
            "error": "Внутренняя ошибка",
            "message": "Произошла системная ошибка при обработке авторизации"
        })


@router.get("/profile", response_class=HTMLResponse, summary="Профиль пользователя")
async def profile(
    request: Request,
    user_id: Optional[int] = Query(None, description="ID пользователя"),
    db: Session = Depends(get_db)
):
    """
    Страница профиля пользователя с данными из ЕСИА.
    
    Args:
        request: HTTP запрос
        user_id: ID пользователя
        db: Сессия базы данных
        
    Returns:
        HTML страница профиля пользователя
    """
    if not user_id:
        return templates.TemplateResponse("error.html", {
            "request": request,
            "title": "Пользователь не найден",
            "error": "Отсутствует ID",
            "message": "Необходимо указать ID пользователя"
        })
    
    try:
        user_service = UserService(db)
        user = user_service.get_user_by_id(user_id)
        
        # Получение активного токена
        active_token = user_service.get_user_active_token(user_id)
        
        return templates.TemplateResponse("profile.html", {
            "request": request,
            "title": f"Профиль {user.first_name} {user.last_name}",
            "user": user,
            "has_active_token": active_token is not None,
            "token_expires_in": active_token.expires_in if active_token else 0
        })
        
    except Exception as e:
        logger.error(f"Ошибка получения профиля пользователя {user_id}: {str(e)}")
        return templates.TemplateResponse("error.html", {
            "request": request,
            "title": "Ошибка профиля",
            "error": "Пользователь не найден",
            "message": "Не удалось найти пользователя с указанным ID"
        })


@router.get("/scopes", response_class=HTMLResponse, summary="Информация об областях доступа")
async def scopes_info(request: Request):
    """
    Страница с информацией о доступных областях доступа ЕСИА.
    
    Args:
        request: HTTP запрос
        
    Returns:
        HTML страница с описанием областей доступа
    """
    oauth_service = OAuth2Service()
    scopes = oauth_service.get_recommended_scopes()
    
    return templates.TemplateResponse("scopes.html", {
        "request": request,
        "title": "Области доступа ЕСИА",
        "scopes": scopes,
        "allowed_scopes": settings.allowed_scopes
    })