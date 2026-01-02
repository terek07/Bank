from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class User:
    user_id: int
    full_name: str
    created_at: datetime

@dataclass
class UserCredentials:
    user_id: int
    password_hash: str
    password_changed_at: datetime

@dataclass
class UserProfile:
    user_id: int
    email: str
    phone: str | None
    address: str | None