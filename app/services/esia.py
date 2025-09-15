"""
Сервис для работы с ЕСИА шлюзом.
Обеспечивает интеграцию с внешним API ЕСИА.
"""

import httpx
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlencode
from app.core.config import settings
from app.core.exceptions import ESIAServiceError, ExternalServiceError
from app.schemas.auth import AuthorizeRequest, TokenRequest, UserInfoRequest, LogoutRequest

logger = logging.getLogger("esia")


class ESIAService:
    """
    Сервис для взаимодействия с ЕСИА шлюзом.
    Предоставляет методы для авторизации, получения токенов и данных пользователей.
    """
    
    def __init__(self):
        """Инициализация сервиса ЕСИА."""
        self.base_url = settings.esia_demo_url
        self.client_id = settings.esia_client_id
        self.client_secret = settings.esia_client_secret
        self.redirect_uri = settings.esia_redirect_uri
        
        # Настройка HTTP клиента
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "ESIA-Gateway-FastAPI/1.0.0"
            }
        )
        
        logger.info("ЕСИА сервис инициализирован")
    
    async def __aenter__(self):
        """Асинхронный контекст менеджер - вход."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекст менеджер - выход."""
        await self.http_client.aclose()
    
    def build_authorization_url(self, request: AuthorizeRequest) -> str:
        """
        Построение URL для авторизации в ЕСИА.
        
        Args:
            request: Параметры запроса авторизации
            
        Returns:
            URL для перенаправления на авторизацию
        """
        logger.info(f"Построение URL авторизации для клиента: {request.client_id}")
        
        params = {
            "client_id": request.client_id,
            "response_type": request.response_type.value,
            "provider": request.provider.value,
            "scope": request.scope,
            "redirect_uri": str(request.redirect_uri),
            "state": request.state,
        }
        
        if request.nonce:
            params["nonce"] = request.nonce
        
        authorization_url = f"{self.base_url}/auth/authorize?{urlencode(params)}"
        
        logger.info(f"URL авторизации построен: {authorization_url}")
        return authorization_url
    
    async def exchange_code_for_token(self, request: TokenRequest) -> Dict[str, Any]:
        """
        Обмен авторизационного кода на токен доступа.
        
        Args:
            request: Параметры запроса токена
            
        Returns:
            Данные токена от ЕСИА
            
        Raises:
            ESIAServiceError: При ошибке получения токена
        """
        logger.info(f"Обмен кода авторизации на токен для клиента: {request.client_id}")
        
        data = {
            "grant_type": request.grant_type.value,
            "client_id": request.client_id,
            "client_secret": request.client_secret,
            "redirect_uri": str(request.redirect_uri),
        }
        
        if request.code:
            data["code"] = request.code
        elif request.refresh_token:
            data["refresh_token"] = request.refresh_token
        
        try:
            response = await self.http_client.post(
                f"{self.base_url}/auth/token",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            logger.debug(f"Ответ ЕСИА на запрос токена: {response.status_code}")
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Ошибка получения токена: {response.status_code} - {error_text}")
                raise ESIAServiceError(
                    f"Ошибка получения токена: {response.status_code}",
                    details={"response": error_text, "status_code": response.status_code}
                )
            
            token_data = response.json()
            logger.info("Токен успешно получен от ЕСИА")
            
            return token_data
            
        except httpx.RequestError as e:
            logger.error(f"Ошибка сети при запросе токена: {str(e)}")
            raise ExternalServiceError(
                "Ошибка соединения с ЕСИА",
                details={"error": str(e)}
            )
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении токена: {str(e)}")
            raise ESIAServiceError(
                "Неожиданная ошибка при получении токена",
                details={"error": str(e)}
            )
    
    async def get_user_info(self, access_token: str, scope: Optional[str] = None) -> Dict[str, Any]:
        """
        Получение информации о пользователе из ЕСИА.
        
        Args:
            access_token: Токен доступа
            scope: Конкретные области доступа (опционально)
            
        Returns:
            Информация о пользователе
            
        Raises:
            ESIAServiceError: При ошибке получения данных
        """
        logger.info("Получение информации о пользователе из ЕСИА")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {}
        if scope:
            data["scope"] = scope
        
        try:
            response = await self.http_client.post(
                f"{self.base_url}/auth/userinfo",
                headers=headers,
                data=data if data else None
            )
            
            logger.debug(f"Ответ ЕСИА на запрос данных пользователя: {response.status_code}")
            
            if response.status_code != 200:
                error_text = response.text
                logger.error(f"Ошибка получения данных пользователя: {response.status_code} - {error_text}")
                raise ESIAServiceError(
                    f"Ошибка получения данных пользователя: {response.status_code}",
                    details={"response": error_text, "status_code": response.status_code}
                )
            
            user_data = response.json()
            logger.info("Данные пользователя успешно получены из ЕСИА")
            
            return user_data
            
        except httpx.RequestError as e:
            logger.error(f"Ошибка сети при запросе данных пользователя: {str(e)}")
            raise ExternalServiceError(
                "Ошибка соединения с ЕСИА",
                details={"error": str(e)}
            )
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении данных пользователя: {str(e)}")
            raise ESIAServiceError(
                "Неожиданная ошибка при получении данных пользователя",
                details={"error": str(e)}
            )
    
    def build_logout_url(self, request: LogoutRequest) -> str:
        """
        Построение URL для выхода из ЕСИА.
        
        Args:
            request: Параметры запроса выхода
            
        Returns:
            URL для выхода из системы
        """
        logger.info(f"Построение URL выхода для клиента: {request.client_id}")
        
        params = {
            "client_id": request.client_id,
            "redirect_uri": str(request.redirect_uri),
        }
        
        if request.state:
            params["state"] = request.state
        
        logout_url = f"{self.base_url}/auth/logout?{urlencode(params)}"
        
        logger.info(f"URL выхода построен: {logout_url}")
        return logout_url
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Обновление токена доступа с помощью refresh token.
        
        Args:
            refresh_token: Токен обновления
            
        Returns:
            Новые данные токена
            
        Raises:
            ESIAServiceError: При ошибке обновления токена
        """
        logger.info("Обновление токена доступа")
        
        request = TokenRequest(
            grant_type="refresh_token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            refresh_token=refresh_token
        )
        
        return await self.exchange_code_for_token(request)
    
    async def get_organization_info(self, access_token: str, org_oid: int, scopes: list) -> Dict[str, Any]:
        """
        Получение информации об организации из ЕСИА.
        
        Args:
            access_token: Токен доступа
            org_oid: OID организации
            scopes: Список запрашиваемых областей доступа
            
        Returns:
            Информация об организации
        """
        logger.info(f"Получение информации об организации {org_oid} из ЕСИА")
        
        # Формирование scope для организации
        org_scopes = []
        for scope in scopes:
            org_scopes.append(f"http://esia.gosuslugi.ru/{scope}?org_oid={org_oid}")
        
        scope_string = " ".join(org_scopes)
        
        return await self.get_user_info(access_token, scope_string)
    
    async def get_groups_info(self, access_token: str, org_oid: int) -> Dict[str, Any]:
        """
        Получение информации о группах доступа организации.
        
        Args:
            access_token: Токен доступа
            org_oid: OID организации
            
        Returns:
            Информация о группах доступа
        """
        logger.info(f"Получение информации о группах доступа организации {org_oid}")
        
        scopes = [
            f"http://esia.gosuslugi.ru/org_grps?org_oid={org_oid}",
            f"http://esia.gosuslugi.ru/org_emps?org_oid={org_oid}"
        ]
        
        scope_string = " ".join(scopes)
        
        return await self.get_user_info(access_token, scope_string)