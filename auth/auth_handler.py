import shortuuid
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(user_id: str) -> str:
    return f"{user_id}|{shortuuid.uuid()}"

def extract_user_id(token: str) -> str:
    return token.split('|')[0]