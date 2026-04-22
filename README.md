# 🧬 MammoScan AI: Clinical Grade Breast Cancer Detection

MammoScan AI is a state-of-the-art medical application designed to assist pathologists and radiologists in classifying breast cancer from histopathological images. By leveraging Deep Learning architectures, the system provides high-accuracy predictions to support clinical decision-making.

## 🚀 Key Features

- **Advanced AI Diagnostics**: Utilizes fine-tuned **ResNet50/DenseNet121** architectures for binary classification of tumor tissues.
- **Clinical Workflow**: Implements a structured review process where AI results are validated by specialized doctors.
- **Role-Based Access Control (RBAC)**:
  - **Staff**: Manage patient data and upload scans for AI analysis.
  - **Doctor**: Review AI findings, add clinical notes, and provide final confirmation.
  - **Admin**: System configuration, user management, and performance monitoring.
- **Real-time Patient Management**: Complete database integration for tracking patient history and longitudinal analysis.
- **Support System**: Integrated ticketing for system support and technical assistance.

## 🛠️ Technology Stack

- **Frontend**: React 19, Vite, TailwindCSS, Lucide React.
- **Backend**: Python 3, FastAPI, SQLAlchemy (SQLite), Uvicorn.
- **AI/ML**: TensorFlow, Keras, NumPy, OpenCV, Scikit-learn.
- **Data**: PCam Dataset (over 277,000 histopathological images).

## 📈 Performance
- **Target Accuracy**: 98%
- **Architecture**: Transfer Learning with Fine-Tuning.
- **Pre-processing**: Dynamic data augmentation (rotation, zoom, horizontal flip) and normalization.

## 📦 Installation & Setup

### Prerequisites
- Python 3.10+
- Node.js & npm

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## 🛡️ Disclaimer
*This tool is intended for research and educational purposes. All AI-generated diagnoses must be verified by a qualified medical professional before any clinical action is taken.*

---
Created as part of a PFA (Projet de Fin d'Études) focusing on AI in Healthcare.
