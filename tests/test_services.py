"""
Тесты для сервисов приложения.
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.esia import ESIAService
from app.services.user import UserService
from app.services.organization import OrganizationService
from app.schemas.auth import AuthorizeRequest, TokenRequest
from app.schemas.user import ESIAUserInfo


class TestESIAService:
    """Тесты для сервиса ЕСИА."""
    
    def test_build_authorization_url(self):
        """Тест построения URL авторизации."""
        esia_service = ESIAService()
        
        request = AuthorizeRequest(
            client_id="test_client_id",
            response_type="code",
            provider="esia_oauth",
            scope="openid fullname",
            redirect_uri="https://example.com/callback",
            state="test_state",
            nonce="test_nonce"
        )
        
        url = esia_service.build_authorization_url(request)
        
        assert "demo.gate.esia.pro/auth/authorize" in url
        assert "client_id=test_client_id" in url
        assert "response_type=code" in url
        assert "provider=esia_oauth" in url
        assert "scope=openid%20fullname" in url
        assert "state=test_state" in url
        assert "nonce=test_nonce" in url
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_exchange_code_for_token_success(self, mock_post):
        """Тест успешного обмена кода на токен."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "access_token": "test_access_token",
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": "test_refresh_token",
            "scope": "openid fullname",
            "created_at": 1640995200
        }
        mock_post.return_value = mock_response
        
        esia_service = ESIAService()
        
        request = TokenRequest(
            grant_type="authorization_code",
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://example.com/callback",
            code="test_code"
        )
        
        result = await esia_service.exchange_code_for_token(request)
        
        assert result["access_token"] == "test_access_token"
        assert result["token_type"] == "Bearer"
        assert result["expires_in"] == 3600
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_exchange_code_for_token_error(self, mock_post):
        """Тест ошибки при обмене кода на токен."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        esia_service = ESIAService()
        
        request = TokenRequest(
            grant_type="authorization_code",
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://example.com/callback",
            code="invalid_code"
        )
        
        with pytest.raises(Exception):  # ESIAServiceError
            await esia_service.exchange_code_for_token(request)
    
    @pytest.mark.asyncio
    @patch('httpx.AsyncClient.post')
    async def test_get_user_info_success(self, mock_post):
        """Тест успешного получения информации о пользователе."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "sub": "3",
            "info": {
                "uid": "1000123456",
                "firstName": "Иван",
                "lastName": "Иванов",
                "trusted": True,
                "status": "REGISTERED"
            }
        }
        mock_post.return_value = mock_response
        
        esia_service = ESIAService()
        
        result = await esia_service.get_user_info("test_access_token")
        
        assert result["sub"] == "3"
        assert result["info"]["uid"] == "1000123456"
        assert result["info"]["firstName"] == "Иван"
    
    def test_build_logout_url(self):
        """Тест построения URL выхода."""
        from app.schemas.auth import LogoutRequest
        
        esia_service = ESIAService()
        
        request = LogoutRequest(
            client_id="test_client_id",
            redirect_uri="https://example.com/logout",
            state="test_logout_state"
        )
        
        url = esia_service.build_logout_url(request)
        
        assert "demo.gate.esia.pro/auth/logout" in url
        assert "client_id=test_client_id" in url
        assert "redirect_uri=https%3A//example.com/logout" in url
        assert "state=test_logout_state" in url


class TestUserService:
    """Тесты для сервиса пользователей."""
    
    def test_create_or_update_user_from_esia_new_user(self, db_session):
        """Тест создания нового пользователя из данных ЕСИА."""
        user_service = UserService(db_session)
        
        esia_data = ESIAUserInfo(
            sub="3",
            info={
                "uid": "1000123456",
                "firstName": "Иван",
                "lastName": "Иванов",
                "middleName": "Иванович",
                "trusted": True,
                "status": "REGISTERED"
            }
        )
        
        user = user_service.create_or_update_user_from_esia(esia_data)
        
        assert user.esia_uid == "1000123456"
        assert user.first_name == "Иван"
        assert user.last_name == "Иванов"
        assert user.trusted == True
        assert user.status == "REGISTERED"
    
    def test_create_or_update_user_from_esia_existing_user(self, db_session, sample_user_data):
        """Тест обновления существующего пользователя из данных ЕСИА."""
        from app.models.user import User
        
        # Создание существующего пользователя
        existing_user = User(**sample_user_data)
        db_session.add(existing_user)
        db_session.commit()
        
        user_service = UserService(db_session)
        
        esia_data = ESIAUserInfo(
            sub="3",
            info={
                "uid": sample_user_data["esia_uid"],
                "firstName": "Петр",  # Изменено имя
                "lastName": "Петров",  # Изменена фамилия
                "middleName": "Петрович",
                "trusted": False,  # Изменен статус
                "status": "VERIFIED"  # Изменен статус
            }
        )
        
        user = user_service.create_or_update_user_from_esia(esia_data)
        
        assert user.id == existing_user.id  # Тот же пользователь
        assert user.first_name == "Петр"  # Обновлено
        assert user.last_name == "Петров"  # Обновлено
        assert user.trusted == False  # Обновлено
        assert user.status == "VERIFIED"  # Обновлено
    
    def test_save_user_token(self, db_session, sample_user_data, sample_token_data):
        """Тест сохранения токена пользователя."""
        from app.models.user import User
        
        # Создание пользователя
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        user_service = UserService(db_session)
        
        token = user_service.save_user_token(user.id, sample_token_data)
        
        assert token.user_id == user.id
        assert token.access_token == sample_token_data["access_token"]
        assert token.token_type == sample_token_data["token_type"]
        assert token.expires_in == sample_token_data["expires_in"]
        assert token.is_active == True
    
    def test_get_user_active_token(self, db_session, sample_user_data, sample_token_data):
        """Тест получения активного токена пользователя."""
        from app.models.user import User, UserToken
        
        # Создание пользователя
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Создание токена
        token_data = {
            "user_id": user.id,
            "access_token": sample_token_data["access_token"],
            "token_type": sample_token_data["token_type"],
            "expires_in": sample_token_data["expires_in"],
            "is_active": True
        }
        token = UserToken(**token_data)
        db_session.add(token)
        db_session.commit()
        
        user_service = UserService(db_session)
        
        active_token = user_service.get_user_active_token(user.id)
        
        assert active_token is not None
        assert active_token.user_id == user.id
        assert active_token.access_token == sample_token_data["access_token"]
        assert active_token.is_active == True


class TestOrganizationService:
    """Тесты для сервиса организаций."""
    
    def test_create_or_update_organization_from_esia_new_org(self, db_session, sample_user_data):
        """Тест создания новой организации из данных ЕСИА."""
        from app.models.user import User
        from app.schemas.organization import ESIAOrganizationInfo
        
        # Создание пользователя
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        org_service = OrganizationService(db_session)
        
        esia_data = ESIAOrganizationInfo(
            sub=str(user.id),
            info={
                "oid": 1000123456,
                "fullName": "Тестовая организация ООО",
                "shortName": "Тест ООО",
                "inn": "1234567890",
                "ogrn": "1234567890123",
                "type": "LEGAL",
                "active": True,
                "chief": True,
                "admin": False
            }
        )
        
        org = org_service.create_or_update_organization_from_esia(esia_data, user.id)
        
        assert org.esia_oid == 1000123456
        assert org.full_name == "Тестовая организация ООО"
        assert org.short_name == "Тест ООО"
        assert org.inn == "1234567890"
        assert org.is_active == True
    
    def test_process_organizations_from_esia(self, db_session, sample_user_data):
        """Тест обработки списка организаций из ЕСИА."""
        from app.models.user import User
        
        # Создание пользователя
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        org_service = OrganizationService(db_session)
        
        user_info = {
            "orgs": [
                {
                    "oid": 1000123456,
                    "fullName": "Организация 1",
                    "shortName": "Орг 1",
                    "inn": "1111111111",
                    "active": True,
                    "chief": True
                },
                {
                    "oid": 1000123457,
                    "fullName": "Организация 2",
                    "shortName": "Орг 2",
                    "inn": "2222222222",
                    "active": True,
                    "chief": False
                }
            ]
        }
        
        organizations = org_service.process_organizations_from_esia(user_info, user.id)
        
        assert len(organizations) == 2
        assert organizations[0].esia_oid == 1000123456
        assert organizations[1].esia_oid == 1000123457
        assert organizations[0].full_name == "Организация 1"
        assert organizations[1].full_name == "Организация 2"