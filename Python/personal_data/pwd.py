import hashlib
import bcrypt

class PasswordHasher:

    def __init__(self, rounds: int = 12) -> None:
        self.rounds = rounds

    def _pre_hash(self, password: str) -> bytes:
        return hashlib.sha256(password.encode('utf-8')).hexdigest().encode('utf-8')

    def hash_password(self, plain_password: str) -> str:
        pre_hashed: bytes = self._pre_hash(plain_password)
        salt: bytes = bcrypt.gensalt(rounds=self.rounds)
        
        hashed_bytes: bytes = bcrypt.hashpw(pre_hashed, salt)
        
        return hashed_bytes.decode('utf-8')

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            pre_hashed: bytes = self._pre_hash(plain_password)
            stored_hash_bytes: bytes = hashed_password.encode('utf-8')
            
            return bcrypt.checkpw(pre_hashed, stored_hash_bytes)
        except ValueError:
            return False


if __name__ == "__main__":
    hasher = PasswordHasher(rounds=12)
    
    password = "SuperSecretPassword123!"
    
    # 1. (Registration)
    hashed = hasher.hash_password(password)
    print(f"Stored in DB (CHAR 60): {hashed}")
    
    # 2. (Login)
    is_valid = hasher.verify_password(password, hashed)
    print(f"Password Valid: {is_valid}")
