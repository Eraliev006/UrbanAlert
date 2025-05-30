from passlib.context import CryptContext

def hash_password(password: bytes) -> str:
    """Hash password"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    return pwd_context.hash(password)

def verify_password(plain_pass: bytes, hashed_password: bytes) -> bool:
    """Verify password"""
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    return pwd_context.verify(plain_pass, hashed_password)