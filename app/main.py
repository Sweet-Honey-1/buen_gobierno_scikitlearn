from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import UserAnswer, UserAsk
from app.ml_services import agrupar_textos

app = FastAPI(title="API de Mapeo Social - Buen Gobierno")

# CORS vital para que Vercel se pueda conectar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cambiaremos esto por tu dominio de Vercel en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bases de datos temporales (en memoria)
answers_db = []
asks_db = []

@app.post("/api/answers", tags=["Recolección"])
def registrar_dolencia(answer: UserAnswer):
    answers_db.append(answer.model_dump())
    return {"mensaje": "Dolencia registrada con éxito", "data": answer}

@app.post("/api/asks", tags=["Recolección"])
def registrar_pregunta(ask: UserAsk):
    asks_db.append(ask.model_dump())
    return {"mensaje": "Pregunta registrada con éxito", "data": ask}

@app.get("/api/mapeo-dolencias", tags=["Análisis de Campaña"])
def mapear_dolencias():
    if len(answers_db) < 3:
        return {"mensaje": "Faltan datos para agrupar.", "total": len(answers_db)}

    textos = [item["dolencia"] for item in answers_db]
    ubicaciones = [item["ubicacion"] for item in answers_db]
    nombres = [item["nombre"] for item in answers_db]

    resultados = agrupar_textos(textos, ubicaciones, nombres)
    return {"mapeo_geografico": resultados}