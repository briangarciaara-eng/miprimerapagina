from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import NOMBRE_ASISTENTE, TEMAS_DISPONIBLES, construir_mensaje_bienvenida, generar_respuesta

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

api = FastAPI(
    title="Chatbot Alcaldia API",
    description="API para un asistente ciudadano basado en FAQs y Groq.",
    version="1.0.0",
)

api.mount("/web", StaticFiles(directory=WEB_DIR), name="web")


class ChatRequest(BaseModel):
    pregunta: str = Field(..., min_length=1, max_length=500)


class ChatResponse(BaseModel):
    respuesta: str


class MenuResponse(BaseModel):
    asistente: str
    bienvenida: str
    temas: list[str]


@api.get("/", include_in_schema=False)
def home():
    return FileResponse(WEB_DIR / "index.html")


@api.get("/api/menu", response_model=MenuResponse)
def obtener_menu():
    return {
        "asistente": NOMBRE_ASISTENTE,
        "bienvenida": construir_mensaje_bienvenida(),
        "temas": TEMAS_DISPONIBLES,
    }


@api.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    return {"respuesta": generar_respuesta(payload.pregunta)}
