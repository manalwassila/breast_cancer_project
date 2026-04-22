from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, auth

def seed():
    db = SessionLocal()
    try:
        # Create roles if they don't exist is handled by main.py migration
        # But we need basic users
        
        users = [
            {"email": "admin@mammoscan.ai", "password": "adminpassword", "role": "admin"},
            {"email": "doctor@mammoscan.ai", "password": "doctorpassword", "role": "doctor"},
            {"email": "staff@mammoscan.ai", "password": "staffpassword", "role": "staff"},
        ]
        
        for u in users:
            existing = db.query(models.User).filter(models.User.email == u["email"]).first()
            if not existing:
                print(f"Creating user: {u['email']}")
                new_user = models.User(
                    email=u["email"],
                    hashed_password=auth.get_password_hash(u["password"]),
                    role=u["role"]
                )
                db.add(new_user)
        
        db.commit()
        print("✅ Seeding complete!")
    except Exception as e:
        print(f"❌ Error seeding: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
