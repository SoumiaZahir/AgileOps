import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import duckdb
import joblib
from pydantic import BaseModel, Field
from typing import List
from contextlib import asynccontextmanager
import pandas as pd


CURRENT_VERSION = "V1.0.0"

MODEL_PATH = "./best_model.joblib"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("server begin running")

    if os.path.exists(MODEL_PATH):
        app.model = joblib.load(MODEL_PATH)
    else:
        app.model = None
        print(f"Attention : Modèle introuvable sur {MODEL_PATH}. Fonctionnement en mode test.")

    yield
    print("server stop running")


app = FastAPI(
    title="Smart Platform for University Success - Prediction API",
    description="FastAPI service for serving student success prediction models.",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Frontend setup (Jinja2 + static assets) ---------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# Shared DuckDB database path inside container mount
DATABASE_PATH = os.getenv("DATABASE_PATH", "/app/data/university.duckdb")


class StudentFeatures(BaseModel):
    # Nombre d'évaluations soumises : doit être un entier positif ou zéro
    n_assessments_submitted: int = Field(..., ge=0, description="Nombre d'évaluations soumises")

    # Nombre de jours actifs : doit être un entier supérieur ou égal à zéro
    n_active_days: int = Field(..., ge=0, description="Nombre de jours actifs sur la plateforme")

    # Nombre total de clics : un entier positif ou zéro
    total_clicks: int = Field(..., ge=0, description="Nombre total de clics/interactions")

    # Moyenne pondérée des scores : valeur décimale entre 0.0 et 100.0
    weighted_avg_score: float = Field(..., ge=0.0, le=100.0, description="Moyenne pondérée des scores (0-100)")

    # Moyenne standard des scores : valeur décimale entre 0.0 et 100.0
    avg_score: float = Field(..., ge=0.0, le=100.0, description="Moyenne générale des scores (0-100)")

    # Nombre de soumissions tardives : un entier positif ou zéro
    n_late_submissions: int = Field(..., ge=0, description="Nombre de soumissions en retard")


# Modèle pour recevoir une liste d'étudiants (Prédiction par lot / Batch)
class PredictionInput(BaseModel):
    students: List[StudentFeatures]


# --- Frontend page ------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def frontend_home(request: Request):
    """Tableau de bord HTML : statut du service + formulaire de prédiction."""
    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "version": CURRENT_VERSION,
            "model_loaded": app.model is not None,
            "db_path": DATABASE_PATH,
        },
    )


# --- JSON API (unchanged paths so Docker healthchecks / Dagster jobs keep working) --
@app.get("/api/info")
def read_root():
    return {
        "status": "online",
        "service": "Student Pass/Fail Prediction API",
        "database_configured_path": DATABASE_PATH,
    }


@app.get("/health")
def health_check():
    # Check if the DuckDB file is accessible or if we can establish a connection
    try:
        # Create parent directory if it does not exist (SQLite/DuckDB standard)
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        conn = duckdb.connect(database=DATABASE_PATH, read_only=False)
        conn.execute("SELECT 1")
        conn.close()
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy",
        "database": db_status,
    }


@app.get("/version")
def get_version_model():
    return CURRENT_VERSION


@app.post("/predict")
def predict_student_status(input_data: PredictionInput):
    # 1. Convertir les données validées en dictionnaire puis en DataFrame Pandas
    features_list = [student.dict() for student in input_data.students]
    df = pd.DataFrame(features_list)

    if app.model is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non chargé (mode test) : aucune prédiction disponible.",
        )

    try:
        # 2. Exécuter la prédiction avec le modèle chargé
        predictions = app.model.predict(df)

        # Convertir le résultat en liste pour la sérialisation JSON de FastAPI
        return {
            "status": "success",
            "predictions": predictions.tolist(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Échec de la prédiction : {str(e)}")