"""
Тесты для API пользователей.
"""

import pytest
from fastapi.testclient import TestClient
from app.models.user import User
from app.schemas.user import UserCreate


class TestUsersAPI:
    """Тесты для API пользователей."""
    
    def test_get_users_empty(self, client: TestClient):
        """Тест получения пустого списка пользователей."""
        response = client.get("/api/v1/users/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_user(self, client: TestClient, sample_user_data):
        """Тест создания пользователя."""
        response = client.post("/api/v1/users/", json=sample_user_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["esia_uid"] == sample_user_data["esia_uid"]
        assert data["first_name"] == sample_user_data["first_name"]
        assert data["last_name"] == sample_user_data["last_name"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_user_duplicate_esia_uid(self, client: TestClient, sample_user_data, db_session):
        """Тест создания пользователя с дублирующимся ЕСИА UID."""
        # Создание первого пользователя
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        # Попытка создания второго пользователя с тем же ЕСИА UID
        response = client.post("/api/v1/users/", json=sample_user_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "уже существует" in data["detail"]
    
    def test_get_user_by_id(self, client: TestClient, sample_user_data, db_session):
        """Тест получения пользователя по ID."""
        # Создание пользователя
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        response = client.get(f"/api/v1/users/{user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user.id
        assert data["esia_uid"] == sample_user_data["esia_uid"]
    
    def test_get_user_by_id_not_found(self, client: TestClient):
        """Тест получения несуществующего пользователя по ID."""
        response = client.get("/api/v1/users/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "не найден" in data["detail"]
    
    def test_get_user_by_esia_uid(self, client: TestClient, sample_user_data, db_session):
        """Тест получения пользователя по ЕСИА UID."""
        # Создание пользователя
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        
        response = client.get(f"/api/v1/users/esia/{sample_user_data['esia_uid']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["esia_uid"] == sample_user_data["esia_uid"]
    
    def test_get_user_by_esia_uid_not_found(self, client: TestClient):
        """Тест получения несуществующего пользователя по ЕСИА UID."""
        response = client.get("/api/v1/users/esia/nonexistent_uid")
        
        assert response.status_code == 404
        data = response.json()
        assert "не найден" in data["detail"]
    
    def test_update_user(self, client: TestClient, sample_user_data, db_session):
        """Тест обновления пользователя."""
        # Создание пользователя
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        update_data = {
            "first_name": "Петр",
            "last_name": "Петров",
            "trusted": False
        }
        
        response = client.put(f"/api/v1/users/{user.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Петр"
        assert data["last_name"] == "Петров"
        assert data["trusted"] == False
        assert data["esia_uid"] == sample_user_data["esia_uid"]  # Не изменился
    
    def test_update_user_not_found(self, client: TestClient):
        """Тест обновления несуществующего пользователя."""
        update_data = {"first_name": "Новое имя"}
        
        response = client.put("/api/v1/users/999", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "не найден" in data["detail"]
    
    def test_delete_user(self, client: TestClient, sample_user_data, db_session):
        """Тест удаления пользователя."""
        # Создание пользователя
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        response = client.delete(f"/api/v1/users/{user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "успешно удален" in data["message"]
        
        # Проверка, что пользователь действительно удален
        get_response = client.get(f"/api/v1/users/{user.id}")
        assert get_response.status_code == 404
    
    def test_delete_user_not_found(self, client: TestClient):
        """Тест удаления несуществующего пользователя."""
        response = client.delete("/api/v1/users/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "не найден" in data["detail"]
    
    def test_get_users_with_pagination(self, client: TestClient, db_session):
        """Тест получения пользователей с пагинацией."""
        # Создание нескольких пользователей
        users_data = []
        for i in range(5):
            user_data = {
                "esia_uid": f"100012345{i}",
                "first_name": f"Пользователь{i}",
                "last_name": "Тестовый",
                "trusted": True,
                "status": "REGISTERED"
            }
            user = User(**user_data)
            db_session.add(user)
            users_data.append(user_data)
        
        db_session.commit()
        
        # Тест первой страницы
        response = client.get("/api/v1/users/?skip=0&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Тест второй страницы
        response = client.get("/api/v1/users/?skip=3&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_create_user_invalid_data(self, client: TestClient):
        """Тест создания пользователя с невалидными данными."""
        invalid_data = {
            "first_name": "Тест",
            # Отсутствует обязательное поле esia_uid
        }
        
        response = client.post("/api/v1/users/", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data