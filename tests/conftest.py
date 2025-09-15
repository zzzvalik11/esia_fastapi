"""
Конфигурация pytest для тестов.
Содержит фикстуры и настройки для тестирования.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

# Создание тестовой базы данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Переопределение зависимости базы данных для тестов."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def db_engine():
    """Фикстура движка базы данных для тестов."""
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Фикстура сессии базы данных для каждого теста."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """Фикстура тестового клиента FastAPI."""
    app.dependency_overrides[get_db] = lambda: db_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data():
    """Фикстура с примером данных пользователя."""
    return {
        "esia_uid": "1000123456",
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "trusted": True,
        "status": "REGISTERED",
        "verifying": False,
        "r_id_doc": 123456,
        "contains_up_cfm_code": False,
        "e_tag": "test_etag_123",
        "updated_on": 1640995200,
        "state_facts": ["EntityRoot"]
    }


@pytest.fixture
def sample_organization_data():
    """Фикстура с примером данных организации."""
    return {
        "esia_oid": 1000123456,
        "prn_oid": 1000123455,
        "full_name": "Тестовая организация ООО",
        "short_name": "Тест ООО",
        "ogrn": "1234567890123",
        "inn": "1234567890",
        "kpp": "123456789",
        "org_type": "LEGAL",
        "leg": "ООО",
        "phone": "+7 (495) 123-45-67",
        "email": "test@example.com",
        "is_chief": True,
        "is_admin": False,
        "is_active": True,
        "has_right_of_substitution": False,
        "has_approval_tab_access": True,
        "is_liquidated": False,
        "staff_count": 50,
        "e_tag": "org_etag_123"
    }


@pytest.fixture
def sample_token_data():
    """Фикстура с примером данных токена."""
    return {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.test_token",
        "token_type": "Bearer",
        "expires_in": 3600,
        "refresh_token": "refresh_token_example",
        "scope": "openid fullname",
        "id_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.id_token",
        "created_at": 1640995200
    }


@pytest.fixture
def sample_auth_request_data():
    """Фикстура с примером данных запроса авторизации."""
    return {
        "client_id": "test_client_id",
        "response_type": "code",
        "provider": "esia_oauth",
        "scope": "openid fullname",
        "redirect_uri": "https://example.com/callback",
        "state": "test_state_12345",
        "nonce": "test_nonce_67890"
    }