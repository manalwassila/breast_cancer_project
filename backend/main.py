import os
import glob
import numpy as np
import tensorflow as tf
from PIL import Image
from io import BytesIO
import uuid

# Set encoding to avoid emoji errors if possible, or just don't use them
import sys
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from fastapi import FastAPI, Depends, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_, text

import models, schemas, auth, database
from database import engine

from tensorflow.keras.applications.densenet import preprocess_input

# ---------------- DB INIT ----------------
models.Base.metadata.create_all(bind=engine)

def run_migrations():
    with engine.connect() as conn:
        try:
            conn.execute(text("SELECT role FROM users LIMIT 1"))
        except Exception:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'staff'"))
            conn.commit()

run_migrations()

# ---------------- APP ----------------
app = FastAPI(title="MammoScan AI API")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
UPLOAD_DIR = os.path.join(STATIC_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- MODEL LOAD ----------------
MODEL_PATH = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models")),
    "best_model.keras"
)

model = None
model_loaded = False

def load_model():
    global model, model_loaded
    if os.path.exists(MODEL_PATH):
        try:
            model = tf.keras.models.load_model(MODEL_PATH)
            model_loaded = True
            print("INFO: Model loaded successfully")
        except Exception as e:
            print(f"ERROR: Error loading model: {e}")
    else:
        print(f"ERROR: No model found at {MODEL_PATH}")

load_model()

# ---------------- LOGIN ----------------
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

# ---------------- USERS ----------------
@app.get("/users/me")
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }

@app.get("/users")
def list_users(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin only")
    return db.query(models.User).all()

@app.post("/users")
def create_user(user_in: schemas.UserCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin only")
    
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = models.User(
        email=user_in.email,
        hashed_password=auth.get_password_hash(user_in.password),
        role=getattr(user_in, 'role', 'staff')
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.patch("/users/{user_id}")
def update_user(user_id: int, user_in: dict, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin only")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if "email" in user_in: user.email = user_in["email"]
    if "role" in user_in: user.role = user_in["role"]
    if "password" in user_in and user_in["password"]:
        user.hashed_password = auth.get_password_hash(user_in["password"])
    
    db.commit()
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin only")
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    return {"detail": "User deleted"}

# ---------------- PREDICT ----------------
@app.post("/predict")
async def predict(
    first_name: str = Form(...),
    last_name: str = Form(...),
    date_of_birth: str = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):

    if not model_loaded:
        raise HTTPException(status_code=503, detail="Model not loaded")

    try:
        # -------- VALIDATION --------
        from datetime import datetime
        if date_of_birth > datetime.now().strftime("%Y-%m-%d"):
            raise HTTPException(status_code=400, detail="Birth date cannot be in the future")

        # -------- IMAGE PROCESS --------
        image_bytes = await file.read()

        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        image = image.resize((224, 224))

        img_array = np.array(image, dtype=np.float32)
        img_array = preprocess_input(img_array)
        img_array = np.expand_dims(img_array, axis=0)

        # -------- PREDICTION --------
        pred = float(model.predict(img_array, verbose=0)[0][0])

        THRESHOLD = 0.5

        if pred >= THRESHOLD:
            result = "High Risk"
            confidence = pred * 100
        else:
            result = "Low Risk"
            confidence = (1 - pred) * 100

        confidence = round(confidence, 2)

        # -------- SAVE IMAGE --------
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.png"
        path = os.path.join(UPLOAD_DIR, filename)

        with open(path, "wb") as f:
            f.write(image_bytes)

        # -------- PATIENT --------
        patient = db.query(models.Patient).filter(
            models.Patient.first_name == first_name,
            models.Patient.last_name == last_name,
            models.Patient.date_of_birth == date_of_birth
        ).first()

        if not patient:
            patient = models.Patient(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=date_of_birth
            )
            db.add(patient)
            db.commit()
            db.refresh(patient)

        # -------- SAVE ANALYSIS --------
        analysis = models.Analysis(
            user_id=current_user.id,
            patient_id=patient.id,
            image_path=f"http://localhost:8000/static/uploads/{filename}",
            ai_result=result,
            probability=confidence,
            status="Pending"
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        return {
            "prediction": result,
            "probability": confidence,
            "patient_info": f"{first_name} {last_name}",
            "image_url": analysis.image_path,
            "analysis_id": analysis.id,
            "disclaimer": "AI result must be confirmed by a doctor."
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ---------------- PATIENTS ----------------
@app.get("/patients")
def list_patients(search: str = "", db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    query = db.query(models.Patient)
    if search:
        query = query.filter(or_(
            models.Patient.first_name.ilike(f"%{search}%"),
            models.Patient.last_name.ilike(f"%{search}%")
        ))
    return query.all()

@app.get("/patients/{patient_id}")
def get_patient(patient_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return {
        "id": patient.id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "date_of_birth": patient.date_of_birth,
        "analyses": patient.analyses
    }

# ---------------- ANALYSES ----------------
@app.get("/analyses/pending")
def get_pending_analyses(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != 'doctor' and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Doctor access only")
    
    results = db.query(models.Analysis).filter(models.Analysis.status == "Pending").all()
    
    out = []
    for a in results:
        p = db.query(models.Patient).filter(models.Patient.id == a.patient_id).first()
        out.append({
            "id": a.id,
            "patient_name": f"{p.first_name} {p.last_name}" if p else "Unknown",
            "image_path": a.image_path,
            "ai_result": a.ai_result,
            "probability": a.probability,
            "created_at": a.created_at,
            "status": a.status
        })
    return out

@app.patch("/analyses/{analysis_id}")
def update_analysis(analysis_id: int, data: dict, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != 'doctor' and current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Operation not permitted")
    
    analysis = db.query(models.Analysis).filter(models.Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if "doctor_decision" in data: analysis.doctor_decision = data["doctor_decision"]
    if "doctor_notes" in data: analysis.doctor_notes = data["doctor_notes"]
    if "status" in data: analysis.status = data["status"]
    if "doctor_result" in data: analysis.doctor_result = data["doctor_result"]
    
    db.commit()
    return analysis

# ---------------- PATIENTS (ADMIN) ----------------
@app.patch("/patients/{patient_id}")
def update_patient(patient_id: int, data: dict, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin only")
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient: raise HTTPException(status_code=404, detail="Patient not found")
    if "first_name" in data: patient.first_name = data["first_name"]
    if "last_name" in data: patient.last_name = data["last_name"]
    if "date_of_birth" in data: patient.date_of_birth = data["date_of_birth"]
    db.commit()
    return patient

@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin only")
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient: raise HTTPException(status_code=404, detail="Patient not found")
    db.query(models.Analysis).filter(models.Analysis.patient_id == patient_id).delete()
    db.delete(patient)
    db.commit()
    return {"detail": "Patient deleted"}

# ---------------- SUPPORT ----------------
@app.post("/support")
def create_ticket(ticket_in: schemas.SupportTicketCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_ticket = models.SupportTicket(
        user_id=current_user.id,
        subject=ticket_in.subject,
        message=ticket_in.message
    )
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket

@app.get("/support")
def list_tickets(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role == 'admin':
        results = db.query(models.SupportTicket).all()
    else:
        results = db.query(models.SupportTicket).filter(models.SupportTicket.user_id == current_user.id).all()
    
    out = []
    for t in results:
        sender = db.query(models.User).filter(models.User.id == t.user_id).first()
        out.append({
            "id": t.id,
            "user_email": sender.email if sender else "Unknown",
            "subject": t.subject,
            "message": t.message,
            "admin_reply": t.admin_reply,
            "status": t.status,
            "created_at": t.created_at
        })
    return out

@app.patch("/support/{ticket_id}")
def reply_ticket(ticket_id: int, data: dict, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Admin only")
    
    ticket = db.query(models.SupportTicket).filter(models.SupportTicket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    if "admin_reply" in data: ticket.admin_reply = data["admin_reply"]
    if "status" in data: ticket.status = data["status"]
    
    db.commit()
    return ticket