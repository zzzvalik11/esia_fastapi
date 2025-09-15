"""
Тесты для API организаций.
"""

import pytest
from fastapi.testclient import TestClient
from app.models.organization import Organization
from app.models.user import User


class TestOrganizationsAPI:
    """Тесты для API организаций."""
    
    def test_get_organizations_empty(self, client: TestClient):
        """Тест получения пустого списка организаций."""
        response = client.get("/api/v1/organizations/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_organization(self, client: TestClient, sample_organization_data):
        """Тест создания организации."""
        response = client.post("/api/v1/organizations/", json=sample_organization_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["esia_oid"] == sample_organization_data["esia_oid"]
        assert data["full_name"] == sample_organization_data["full_name"]
        assert data["short_name"] == sample_organization_data["short_name"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_organization_duplicate_esia_oid(self, client: TestClient, sample_organization_data, db_session):
        """Тест создания организации с дублирующимся ЕСИА OID."""
        # Создание первой организации
        org = Organization(**sample_organization_data)
        db_session.add(org)
        db_session.commit()
        
        # Попытка создания второй организации с тем же ЕСИА OID
        response = client.post("/api/v1/organizations/", json=sample_organization_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "уже существует" in data["detail"]
    
    def test_get_organization_by_id(self, client: TestClient, sample_organization_data, db_session):
        """Тест получения организации по ID."""
        # Создание организации
        org = Organization(**sample_organization_data)
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
        
        response = client.get(f"/api/v1/organizations/{org.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == org.id
        assert data["esia_oid"] == sample_organization_data["esia_oid"]
    
    def test_get_organization_by_id_not_found(self, client: TestClient):
        """Тест получения несуществующей организации по ID."""
        response = client.get("/api/v1/organizations/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "не найдена" in data["detail"]
    
    def test_get_organization_by_esia_oid(self, client: TestClient, sample_organization_data, db_session):
        """Тест получения организации по ЕСИА OID."""
        # Создание организации
        org = Organization(**sample_organization_data)
        db_session.add(org)
        db_session.commit()
        
        response = client.get(f"/api/v1/organizations/esia/{sample_organization_data['esia_oid']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["esia_oid"] == sample_organization_data["esia_oid"]
    
    def test_get_organization_by_esia_oid_not_found(self, client: TestClient):
        """Тест получения несуществующей организации по ЕСИА OID."""
        response = client.get("/api/v1/organizations/esia/999999999")
        
        assert response.status_code == 404
        data = response.json()
        assert "не найдена" in data["detail"]
    
    def test_update_organization(self, client: TestClient, sample_organization_data, db_session):
        """Тест обновления организации."""
        # Создание организации
        org = Organization(**sample_organization_data)
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
        
        update_data = {
            "full_name": "Обновленная организация ООО",
            "short_name": "Обновленная ООО",
            "staff_count": 100
        }
        
        response = client.put(f"/api/v1/organizations/{org.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Обновленная организация ООО"
        assert data["short_name"] == "Обновленная ООО"
        assert data["staff_count"] == 100
        assert data["esia_oid"] == sample_organization_data["esia_oid"]  # Не изменился
    
    def test_update_organization_not_found(self, client: TestClient):
        """Тест обновления несуществующей организации."""
        update_data = {"full_name": "Новое название"}
        
        response = client.put("/api/v1/organizations/999", json=update_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "не найдена" in data["detail"]
    
    def test_delete_organization(self, client: TestClient, sample_organization_data, db_session):
        """Тест удаления организации."""
        # Создание организации
        org = Organization(**sample_organization_data)
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
        
        response = client.delete(f"/api/v1/organizations/{org.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "успешно удалена" in data["message"]
        
        # Проверка, что организация действительно удалена
        get_response = client.get(f"/api/v1/organizations/{org.id}")
        assert get_response.status_code == 404
    
    def test_delete_organization_not_found(self, client: TestClient):
        """Тест удаления несуществующей организации."""
        response = client.delete("/api/v1/organizations/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "не найдена" in data["detail"]
    
    def test_get_user_organizations(self, client: TestClient, sample_user_data, sample_organization_data, db_session):
        """Тест получения организаций пользователя."""
        # Создание пользователя
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Создание организации
        org = Organization(**sample_organization_data)
        db_session.add(org)
        db_session.commit()
        db_session.refresh(org)
        
        # Создание связи пользователя с организацией
        from app.models.organization import UserOrganization
        user_org = UserOrganization(
            user_id=user.id,
            organization_id=org.id,
            is_chief=True,
            is_admin=False,
            is_active=True
        )
        db_session.add(user_org)
        db_session.commit()
        
        response = client.get(f"/api/v1/organizations/users/{user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == org.id
        assert data[0]["esia_oid"] == sample_organization_data["esia_oid"]
    
    def test_get_user_organizations_empty(self, client: TestClient, sample_user_data, db_session):
        """Тест получения пустого списка организаций пользователя."""
        # Создание пользователя без организаций
        user = User(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        response = client.get(f"/api/v1/organizations/users/{user.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_get_organizations_with_pagination(self, client: TestClient, db_session):
        """Тест получения организаций с пагинацией."""
        # Создание нескольких организаций
        for i in range(5):
            org_data = {
                "esia_oid": 1000123456 + i,
                "full_name": f"Тестовая организация {i}",
                "short_name": f"Тест {i}",
                "inn": f"123456789{i}",
                "is_active": True
            }
            org = Organization(**org_data)
            db_session.add(org)
        
        db_session.commit()
        
        # Тест первой страницы
        response = client.get("/api/v1/organizations/?skip=0&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Тест второй страницы
        response = client.get("/api/v1/organizations/?skip=3&limit=3")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_create_organization_invalid_data(self, client: TestClient):
        """Тест создания организации с невалидными данными."""
        invalid_data = {
            "full_name": "Тестовая организация",
            # Отсутствует обязательное поле esia_oid
        }
        
        response = client.post("/api/v1/organizations/", json=invalid_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data