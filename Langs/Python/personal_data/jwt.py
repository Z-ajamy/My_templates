import jwt
import datetime
from typing import Dict, Any

class JWTAuthenticator:
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.issuer = "api.mycompany.com"

    def create_access_token(self, user_id: int, role: str) -> str:
        now = datetime.datetime.now(datetime.timezone.utc)
        expires = now + datetime.timedelta(minutes=15)

        payload = {
            "sub": str(user_id),      # Subject: ID
            "exp": expires,           # Expiration Time
            "iat": now,               # Issued At
            "iss": self.issuer,       # Issuer
            
            # 2. (Private Claims)
            "role": role              # (admin, user, ...)
        }

        # تشفير القاموس وتحويله إلى JWT String
        token = jwt.encode(
            payload=payload,
            key=self.secret_key,
            algorithm=self.algorithm
        )
        return token

    def verify_access_token(self, token: str) -> Dict[str, Any]:
        try:
            decoded_payload = jwt.decode(
                jwt=token,
                key=self.secret_key,
                algorithms=[self.algorithm],
                issuer=self.issuer,
                options={"require": ["exp", "iss", "sub"]} 
            )
            return decoded_payload
            
        except jwt.ExpiredSignatureError:
            # ثغرة شائعة: عدم التقاط هذا الخطأ بشكل مستقل
            # يجب أن يعرف العميل أن الخطأ بسبب الانتهاء ليقوم بطلب Refresh Token
            raise ValueError("Token has expired. Please authenticate again.")
            
        except jwt.InvalidIssuerError:
            raise ValueError("Token was issued by an untrusted server.")
            
        except jwt.InvalidTokenError:
            # التقاط أي خطأ آخر (مثل تلاعب الهاكر بالتوقيع أو تلف الـ Base64)
            raise ValueError("Invalid Token structure or signature mismatch.")


if __name__ == "__main__":
    SECRET = "super_secret_key_that_must_be_long_and_random_12345!"
    
    auth_service = JWTAuthenticator(secret_key=SECRET)
    
    print("--- Issuing Token ---")
    access_token = auth_service.create_access_token(user_id=105, role="admin")
    print(f"Generated JWT: {access_token}\n")
    
    print("--- Verifying Valid Token ---")
    try:
        user_data = auth_service.verify_access_token(token=access_token)
        print("Success! User Data extracted from Token:")
        print(f"User ID: {user_data['sub']} | Role: {user_data['role']}\n")
    except ValueError as e:
        print(f"Auth Failed: {e}\n")
        
    print("--- Verifying Tampered Token ---")
    tampered_token = access_token[:-1] + "A" 
    try:
        auth_service.verify_access_token(token=tampered_token)
    except ValueError as e:
        print(f"Auth Failed (Tampered): {e}")
