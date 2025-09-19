"""
Сервис OAuth 2.0 для работы с ЕСИА.
Реализует модель контроля доступа на основе OAuth 2.0.
"""

import logging
import secrets
import hashlib
import base64
from typing import Dict, Any, Optional, List
from urllib.parse import urlencode, parse_qs, urlparse
from app.core.config import settings
from app.core.exceptions import ValidationError, AuthenticationError

logger = logging.getLogger("esia")


class OAuth2Service:
    """
    Сервис OAuth 2.0 для интеграции с ЕСИА.
    Реализует стандартный flow авторизации OAuth 2.0.
    """
    
    def __init__(self):
        """Инициализация OAuth 2.0 сервиса."""
        self.client_id = settings.esia_client_id
        self.client_secret = settings.esia_client_secret
        self.redirect_uri = settings.esia_redirect_uri
        self.base_url = settings.esia_base_url
        
        if not all([self.client_id, self.client_secret, self.redirect_uri]):
            raise ValidationError(
                "Не настроены обязательные параметры OAuth 2.0",
                details={
                    "client_id": bool(self.client_id),
                    "client_secret": bool(self.client_secret),
                    "redirect_uri": bool(self.redirect_uri)
                }
            )
    
    def validate_scopes(self, scopes: str) -> List[str]:
        """
        Валидация запрашиваемых областей доступа.
        
        Args:
            scopes: Строка с областями доступа через пробел
            
        Returns:
            Список валидных областей доступа
            
        Raises:
            ValidationError: При наличии недопустимых областей доступа
        """
        scope_list = scopes.split()
        invalid_scopes = [scope for scope in scope_list if scope not in settings.allowed_scopes]
        
        if invalid_scopes:
            raise ValidationError(
                f"Недопустимые области доступа: {', '.join(invalid_scopes)}",
                details={
                    "invalid_scopes": invalid_scopes,
                    "allowed_scopes": settings.allowed_scopes
                }
            )
        
        return scope_list
    
    def generate_state(self) -> str:
        """
        Генерация случайного состояния для предотвращения CSRF атак.
        
        Returns:
            UUID строка состояния
        """
        import uuid
        return str(uuid.uuid4())
    
    def generate_nonce(self) -> str:
        """
        Генерация nonce для предотвращения подделки токена.
        
        Returns:
            UUID строка nonce
        """
        import uuid
        return str(uuid.uuid4())
    
    def generate_code_verifier(self) -> str:
        """
        Генерация code_verifier для PKCE (Proof Key for Code Exchange).
        
        Returns:
            Случайная строка code_verifier
        """
        return base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    
    def generate_code_challenge(self, code_verifier: str) -> str:
        """
        Генерация code_challenge из code_verifier для PKCE.
        
        Args:
            code_verifier: Строка code_verifier
            
        Returns:
            SHA256 хеш code_verifier в base64url формате
        """
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    
    def build_authorization_url(
        self,
        scopes: str,
        state: Optional[str] = None,
        nonce: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        provider: str = "esia_oauth"
    ) -> Dict[str, str]:
        """
        Построение URL авторизации OAuth 2.0.
        
        Args:
            scopes: Области доступа
            state: Состояние запроса (генерируется если не указано)
            nonce: Nonce (генерируется если не указано)
            redirect_uri: URI возврата (из настроек если не указано)
            provider: Провайдер данных
            
        Returns:
            Словарь с URL авторизации и параметрами
        """
        logger.info(f"Построение OAuth 2.0 URL авторизации для scopes: {scopes}")
        
        # Валидация областей доступа
        self.validate_scopes(scopes)
        
        # Генерация параметров если не переданы
        if not state:
            state = self.generate_state()
        if not nonce:
            nonce = self.generate_nonce()
        if not redirect_uri:
            redirect_uri = self.redirect_uri
        
        # Генерация PKCE параметров
        code_verifier = self.generate_code_verifier()
        code_challenge = self.generate_code_challenge(code_verifier)
        
        # Параметры авторизации
        auth_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "scope": scopes,
            "redirect_uri": redirect_uri,
            "state": state,
            "nonce": nonce,
            "provider": provider,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }
        
        authorization_url = f"{self.base_url}/auth/authorize?{urlencode(auth_params)}"
        
        logger.info(f"OAuth 2.0 URL авторизации создан для состояния: {state}")
        
        return {
            "authorization_url": authorization_url,
            "state": state,
            "nonce": nonce,
            "code_verifier": code_verifier,
            "redirect_uri": redirect_uri
        }
    
    def validate_callback(self, callback_url: str, expected_state: str) -> Dict[str, Any]:
        """
        Валидация callback URL после авторизации.
        
        Args:
            callback_url: URL callback с параметрами
            expected_state: Ожидаемое состояние
            
        Returns:
            Словарь с параметрами callback
            
        Raises:
            AuthenticationError: При ошибке валидации
        """
        logger.info("Валидация OAuth 2.0 callback")
        
        parsed_url = urlparse(callback_url)
        params = parse_qs(parsed_url.query)
        
        # Извлечение параметров
        code = params.get('code', [None])[0]
        state = params.get('state', [None])[0]
        error = params.get('error', [None])[0]
        error_description = params.get('error_description', [None])[0]
        
        # Проверка состояния
        if state != expected_state:
            raise AuthenticationError(
                "Неверное состояние в callback",
                details={"expected": expected_state, "received": state}
            )
        
        # Проверка на ошибки
        if error:
            raise AuthenticationError(
                f"Ошибка авторизации: {error}",
                details={"error": error, "description": error_description}
            )
        
        # Проверка наличия кода
        if not code:
            raise AuthenticationError(
                "Отсутствует код авторизации в callback",
                details={"callback_url": callback_url}
            )
        
        logger.info(f"OAuth 2.0 callback успешно валидирован для состояния: {state}")
        
        return {
            "code": code,
            "state": state
        }
    
    def build_logout_url(self, redirect_uri: Optional[str] = None, state: Optional[str] = None) -> str:
        """
        Построение URL выхода из системы.
        
        Args:
            redirect_uri: URI возврата после выхода
            state: Состояние запроса
            
        Returns:
            URL для выхода из системы
        """
        logger.info("Построение OAuth 2.0 URL выхода")
        
        if not redirect_uri:
            redirect_uri = self.redirect_uri
        if not state:
            state = self.generate_state()
        
        logout_params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "state": state
        }
        
        logout_url = f"{self.base_url}/auth/logout?{urlencode(logout_params)}"
        
        logger.info(f"OAuth 2.0 URL выхода создан: {logout_url}")
        
        return logout_url
    
    def get_recommended_scopes(self) -> Dict[str, str]:
        """
        Получение рекомендуемых областей доступа с описанием.
        
        Returns:
            Словарь с областями доступа и их описанием
        """
        return {
            "openid": "Базовая идентификация пользователя",
            "fullname": "ФИО пользователя",
            "birthdate": "Дата рождения",
            "gender": "Пол",
            "citizenship": "Гражданство",
            "id_doc": "Документ, удостоверяющий личность",
            "email": "Адрес электронной почты",
            "mobile": "Номер мобильного телефона",
            "addresses": "Адреса регистрации и проживания"
        }