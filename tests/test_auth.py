"""
Тесты для API авторизации и аутентификации.
"""

import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient


class TestAuthAPI:
    """Тесты для API авторизации."""
    
    def test_authorize_endpoint(self, client: TestClient, sample_auth_request_data):
        """Тест эндпоинта авторизации."""
        response = client.get("/api/v1/auth/authorize", params=sample_auth_request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "authorization_url" in data
        assert "state" in data
        assert data["state"] == sample_auth_request_data["state"]
        assert "demo.gate.esia.pro" in data["authorization_url"]
    
    def test_authorize_missing_required_params(self, client: TestClient):
        """Тест авторизации с отсутствующими обязательными параметрами."""
        response = client.get("/api/v1/auth/authorize", params={
            "client_id": "test_client"
        })
        
        assert response.status_code == 422
    
    @patch('app.services.esia.ESIAService.exchange_code_for_token')
    def test_token_endpoint_authorization_code(self, mock_exchange, client: TestClient, sample_token_data):
        """Тест получения токена по коду авторизации."""
        mock_exchange.return_value = AsyncMock(return_value=sample_token_data)
        
        token_request_data = {
            "grant_type": "authorization_code",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "redirect_uri": "https://example.com/callback",
            "code": "test_authorization_code"
        }
        
        response = client.post("/api/v1/auth/token", data=token_request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == sample_token_data["access_token"]
        assert data["token_type"] == sample_token_data["token_type"]
    
    @patch('app.services.esia.ESIAService.exchange_code_for_token')
    def test_token_endpoint_refresh_token(self, mock_exchange, client: TestClient, sample_token_data):
        """Тест обновления токена."""
        mock_exchange.return_value = AsyncMock(return_value=sample_token_data)
        
        token_request_data = {
            "grant_type": "refresh_token",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "redirect_uri": "https://example.com/callback",
            "refresh_token": "test_refresh_token"
        }
        
        response = client.post("/api/v1/auth/token", data=token_request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["access_token"] == sample_token_data["access_token"]
    
    def test_token_endpoint_missing_params(self, client: TestClient):
        """Тест получения токена с отсутствующими параметрами."""
        response = client.post("/api/v1/auth/token", data={
            "grant_type": "authorization_code",
            "client_id": "test_client"
        })
        
        assert response.status_code == 422
    
    @patch('app.services.esia.ESIAService.get_user_info')
    def test_userinfo_endpoint(self, mock_get_user_info, client: TestClient):
        """Тест получения информации о пользователе."""
        mock_user_data = {
            "sub": "3",
            "info": {
                "uid": "1000123456",
                "firstName": "Иван",
                "lastName": "Иванов",
                "middleName": "Иванович",
                "trusted": True,
                "status": "REGISTERED"
            }
        }
        mock_get_user_info.return_value = AsyncMock(return_value=mock_user_data)
        
        headers = {"Authorization": "Bearer test_access_token"}
        response = client.post("/api/v1/auth/userinfo", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["sub"] == "3"
        assert "info" in data
    
    def test_userinfo_endpoint_no_token(self, client: TestClient):
        """Тест получения информации о пользователе без токена."""
        response = client.post("/api/v1/auth/userinfo")
        
        assert response.status_code == 422
    
    def test_userinfo_endpoint_invalid_token_format(self, client: TestClient):
        """Тест получения информации о пользователе с неверным форматом токена."""
        headers = {"Authorization": "InvalidToken"}
        response = client.post("/api/v1/auth/userinfo", headers=headers)
        
        assert response.status_code == 401
    
    def test_logout_endpoint(self, client: TestClient):
        """Тест эндпоинта выхода из системы."""
        logout_params = {
            "client_id": "test_client_id",
            "redirect_uri": "https://example.com/logout",
            "state": "test_logout_state"
        }
        
        response = client.get("/api/v1/auth/logout", params=logout_params)
        
        assert response.status_code == 200
        data = response.json()
        assert "logout_url" in data
        assert "redirect_uri" in data
        assert data["redirect_uri"] == logout_params["redirect_uri"]
    
    def test_logout_endpoint_missing_params(self, client: TestClient):
        """Тест выхода из системы с отсутствующими параметрами."""
        response = client.get("/api/v1/auth/logout", params={
            "client_id": "test_client"
        })
        
        assert response.status_code == 422
    
    def test_callback_endpoint_success(self, client: TestClient, db_session):
        """Тест успешного callback после авторизации."""
        # Создание запроса авторизации в базе данных
        from app.models.user import AuthorizationRequest
        
        auth_request = AuthorizationRequest(
            client_id="test_client_id",
            response_type="code",
            provider="esia_oauth",
            scope="openid fullname",
            redirect_uri="https://example.com/callback",
            state="test_callback_state",
            nonce="test_nonce"
        )
        db_session.add(auth_request)
        db_session.commit()
        
        callback_params = {
            "code": "test_authorization_code",
            "state": "test_callback_state"
        }
        
        response = client.get("/api/v1/auth/callback", params=callback_params)
        
        # Проверяем редирект
        assert response.status_code == 307  # Temporary Redirect
        assert "test_authorization_code" in response.headers["location"]
    
    def test_callback_endpoint_error(self, client: TestClient, db_session):
        """Тест callback с ошибкой авторизации."""
        # Создание запроса авторизации в базе данных
        from app.models.user import AuthorizationRequest
        
        auth_request = AuthorizationRequest(
            client_id="test_client_id",
            response_type="code",
            provider="esia_oauth",
            scope="openid fullname",
            redirect_uri="https://example.com/callback",
            state="test_error_state",
            nonce="test_nonce"
        )
        db_session.add(auth_request)
        db_session.commit()
        
        callback_params = {
            "error": "access_denied",
            "error_description": "User denied access",
            "state": "test_error_state"
        }
        
        response = client.get("/api/v1/auth/callback", params=callback_params)
        
        # Проверяем редирект с ошибкой
        assert response.status_code == 307  # Temporary Redirect
        assert "error=access_denied" in response.headers["location"]
    
    def test_callback_endpoint_invalid_state(self, client: TestClient):
        """Тест callback с неверным состоянием."""
        callback_params = {
            "code": "test_authorization_code",
            "state": "invalid_state"
        }
        
        response = client.get("/api/v1/auth/callback", params=callback_params)
        
        assert response.status_code == 404