import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import UserAnswer, UserAsk
from app.ml_services import agrupar_textos, analizar_texto_completo, parsear_ubicacion_canonica
from app.geo_peru import PROVINCIAS_PERU, PROVINCIAS_VALIDAS
from app.supabase_repository import (
    fetch_pending_answers,
    fetch_pending_asks,
    insert_answers_raw,
    insert_asks_raw,
    mark_answers_processing,
    mark_answers_processed,
    mark_answers_error,
    mark_asks_processing,
    mark_asks_processed,
    mark_asks_error,
    upsert_answer_analysis_results,
    upsert_dashboard_cache,
    create_analysis_run,
    finish_analysis_run,
)

load_dotenv()

app = FastAPI(
    title="API de Mapeo Social - Buen Gobierno",
    version="5.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def healthcheck():
    return {
        "status": "ok",
        "service": "API de Mapeo Social - Buen Gobierno",
        "version": "5.1.0"
    }


@app.get("/api/geo/provincias", tags=["Geografía"])
def listar_provincias():
    return {
        "total": len(PROVINCIAS_PERU),
        "items": PROVINCIAS_PERU
    }


# =========================================================
# ENDPOINTS DE INGESTA
# FastAPI guarda en Supabase.
# =========================================================

@app.post("/api/answers/lote", tags=["Recolección"])
def registrar_dolencias_lote(answers: List[UserAnswer]):
    rows = []

    for ans in answers:
        data = ans.model_dump()

        if data["ubicacion"] not in PROVINCIAS_VALIDAS:
            raise HTTPException(
                status_code=422,
                detail="Ubicación no válida. Debe ser una provincia oficial en formato PROVINCIA-DEPARTAMENTO."
            )

        rows.append({
            "nombre": data["nombre"],
            "ubicacion": data["ubicacion"],
            "dolencia": data["dolencia"],
            "status": "pending",
            "source": "fastapi"
        })

    insert_answers_raw(rows)

    return {
        "mensaje": "Dolencias registradas correctamente en Supabase",
        "registradas": len(rows),
    }


@app.post("/api/asks/lote", tags=["Recolección"])
def registrar_preguntas_lote(asks: List[UserAsk]):
    rows = []

    for ask in asks:
        data = ask.model_dump()

        if data["ubicacion"] not in PROVINCIAS_VALIDAS:
            raise HTTPException(
                status_code=422,
                detail="Ubicación no válida. Debe ser una provincia oficial en formato PROVINCIA-DEPARTAMENTO."
            )

        rows.append({
            "nombre": data["nombre"],
            "ubicacion": data["ubicacion"],
            "pregunta": data["pregunta"],
            "status": "pending",
            "source": "fastapi"
        })

    insert_asks_raw(rows)

    return {
        "mensaje": "Preguntas registradas correctamente en Supabase",
        "registradas": len(rows),
    }


# =========================================================
# ENDPOINTS INTERNOS DE LECTURA DESDE SUPABASE
# =========================================================

@app.get("/internal/pending-answers", tags=["Interno"])
def get_pending_answers(limit: int = 100):
    items = fetch_pending_answers(limit=limit)
    return {
        "total": len(items),
        "items": items
    }


@app.get("/internal/pending-asks", tags=["Interno"])
def get_pending_asks(limit: int = 100):
    items = fetch_pending_asks(limit=limit)
    return {
        "total": len(items),
        "items": items
    }


# =========================================================
# ANÁLISIS INDIVIDUAL
# =========================================================

@app.post("/api/analizar-texto", tags=["Análisis de Campaña"])
def analizar_texto(payload: UserAnswer):
    if payload.ubicacion not in PROVINCIAS_VALIDAS:
        raise HTTPException(
            status_code=422,
            detail="Ubicación no válida. Debe ser una provincia oficial en formato PROVINCIA-DEPARTAMENTO."
        )

    analisis = analizar_texto_completo(payload.dolencia)
    geo = parsear_ubicacion_canonica(payload.ubicacion)

    return {
        "nombre": payload.nombre,
        "ubicacion": payload.ubicacion,
        "geo": geo,
        "analisis": analisis
    }


# =========================================================
# PROCESAMIENTO DE PENDIENTES DESDE SUPABASE
# SIN VALIDACIÓN DE CRON_SECRET PARA PRUEBAS LOCALES
# =========================================================

@app.post("/internal/process-pending", tags=["Interno"])
def process_pending_jobs():
    run_id = create_analysis_run()

    pending_answers = fetch_pending_answers(limit=200)
    pending_asks = fetch_pending_asks(limit=200)

    total_answers_read = len(pending_answers)
    total_asks_read = len(pending_asks)

    if not pending_answers and not pending_asks:
        finish_analysis_run(
            run_id=run_id,
            status="success",
            total_answers_read=0,
            total_answers_processed=0,
            total_asks_read=0,
            total_asks_processed=0,
            message="No había registros pendientes",
            payload_summary={}
        )
        return {
            "message": "No había registros pendientes",
            "processed_answers": 0,
            "processed_asks": 0
        }

    answer_ids = [item["id"] for item in pending_answers]
    ask_ids = [item["id"] for item in pending_asks]

    mark_answers_processing(answer_ids)
    mark_asks_processing(ask_ids)

    try:
        analysis_rows: List[Dict[str, Any]] = []

        textos = []
        ubicaciones = []
        nombres = []

        for item in pending_answers:
            geo = parsear_ubicacion_canonica(item["ubicacion"])
            analisis = analizar_texto_completo(item["dolencia"])

            textos.append(item["dolencia"])
            ubicaciones.append(item["ubicacion"])
            nombres.append(item["nombre"])

            analysis_rows.append({
                "answer_id": item["id"],
                "ubicacion_canonica": item["ubicacion"],
                "provincia": geo["provincia"],
                "departamento": geo["departamento"],
                "provincia_legible": geo["provincia_legible"],
                "departamento_legible": geo["departamento_legible"],
                "categoria_id": analisis["categoria_id"],
                "categoria": analisis["categoria"],
                "confianza": analisis["confianza"],
                "frases_dolencia": analisis["frases_dolencia"],
                "terminos_relevantes": list(analisis["terminos_matcheados"].keys())[:8],
                "puntajes_sector": analisis["puntajes_sector"],
                "detalles_sector": analisis["detalles_sector"],
                "texto_normalizado": analisis["texto_normalizado"],
            })

        upsert_answer_analysis_results(analysis_rows)

        if pending_answers:
            dashboard_payload = {
                "mapeo_geografico": agrupar_textos(
                    textos=textos,
                    ubicaciones=ubicaciones,
                    nombres=nombres
                )
            }
            upsert_dashboard_cache(dashboard_payload)

        mark_answers_processed(answer_ids)
        mark_asks_processed(ask_ids)

        finish_analysis_run(
            run_id=run_id,
            status="success",
            total_answers_read=total_answers_read,
            total_answers_processed=len(answer_ids),
            total_asks_read=total_asks_read,
            total_asks_processed=len(ask_ids),
            message="Procesamiento exitoso",
            payload_summary={
                "dashboard_cache_key": "latest",
                "processed_answer_ids": answer_ids,
                "processed_ask_ids": ask_ids,
            }
        )

        return {
            "message": "Procesamiento exitoso",
            "processed_answers": len(answer_ids),
            "processed_asks": len(ask_ids),
            "dashboard_cache_key": "latest"
        }

    except Exception as exc:
        mark_answers_error(answer_ids, str(exc))
        mark_asks_error(ask_ids, str(exc))

        finish_analysis_run(
            run_id=run_id,
            status="error",
            total_answers_read=total_answers_read,
            total_answers_processed=0,
            total_asks_read=total_asks_read,
            total_asks_processed=0,
            message=str(exc),
            payload_summary={}
        )

        raise HTTPException(status_code=500, detail=str(exc))