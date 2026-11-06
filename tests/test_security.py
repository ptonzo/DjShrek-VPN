from app.security import issue_access_token, password_hash, password_verify, verify_access_token

def test_password_hash_round_trip():
    stored = password_hash("correct-horse-battery-staple")
    assert password_verify("correct-horse-battery-staple", stored)
    assert not password_verify("wrong-password", stored)

def test_access_token_round_trip():
    token = issue_access_token(42)
    assert verify_access_token(token) == 42
