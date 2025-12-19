from app.main import app

def test_github_login_route_registered():
    paths = {getattr(r, "path", "") for r in app.routes}
    assert "/auth/github/login" in paths
