from fastapi.testclient import TestClient
from app.core.database import get_session
from app.core.security import hash_password
from app.domain.enums import UserRole
from app.infrastructure.orm.user_model import UserModel
from app.main import app


def test_login_sets_signed_cookie_and_client_role_is_enforced(session):
    session.add(UserModel(name="Web Client", email="web-client@example.test",
        password_hash=hash_password("Password123!"), role=UserRole.CLIENT))
    session.commit()

    def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    try:
        with TestClient(app) as client:
            login = client.post("/auth/login", data={"email": "web-client@example.test",
                "password": "Password123!"}, follow_redirects=False)
            assert login.status_code == 303
            assert login.headers["location"] == "/appointments/"
            cookie = login.headers["set-cookie"].lower()
            assert "styleagenda_session=" in cookie
            assert "httponly" in cookie and "samesite=lax" in cookie
            assert client.get("/appointments/").status_code == 200
            assert client.get("/admin/").status_code == 403
            assert client.post("/auth/logout", follow_redirects=False).status_code == 303
            assert client.get("/appointments/").status_code == 401
    finally:
        app.dependency_overrides.pop(get_session, None)
