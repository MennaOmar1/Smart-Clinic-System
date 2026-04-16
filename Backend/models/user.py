from core.security import hash_password

users = [
    {
        "id": 1,
        "email": "drmagdyfahmi9@gmail.com",
        "password": hash_password("Magdy@1950"),
        "role": "doctor",
        "is_active": True
    },
    {
        "id": 2,
        "email": "receptionist@gmail.com",
        "password": hash_password("1234"),
        "role": "receptionist",
        "is_active": True
    },
    {
    "id": 3,
    "email": "admin@gmail.com",
    "password": hash_password("1234"),
    "role": "admin",
    "is_active": True
    }  
]