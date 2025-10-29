import pytest
from app import create_app, db
from app.services.auth_service import AuthService


@pytest.fixture()
def app_ctx():
    app = create_app()
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_signup_and_login(app_ctx):
    svc = AuthService(db.session)
    user = svc.signup("Alice", "alice@example.com", "password", "teacher")
    assert user.id is not None

    # Duplicate email should raise
    with pytest.raises(ValueError):
        svc.signup("Alice2", "alice@example.com", "password", "teacher")

    login = svc.login("alice@example.com", "password")
    assert login is not None

    bad = svc.login("alice@example.com", "wrong")
    assert bad is None
