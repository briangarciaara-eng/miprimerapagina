import csv
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

RUTA_FAQS = Path(__file__).resolve().parent.parent / "data" / "faqs.csv"
MENSAJE_SIN_INFORMACION = "No hay informacion especifica en el manual de procesos locales."

PALABRAS_VACIAS = {
    "a",
    "al",
    "ante",
    "como",
    "con",
    "cual",
    "cuando",
    "de",
    "del",
    "donde",
    "e",
    "el",
    "en",
    "es",
    "la",
    "las",
    "lo",
    "los",
    "me",
    "mi",
    "o",
    "para",
    "por",
    "quiero",
    "quiereo",
    "que",
    "se",
    "si",
    "sobre",
    "su",
    "toda",
    "todo",
    "un",
    "una",
    "y",
    "informacion",
    "disponible",
}

SINONIMOS = {
    "agendar": {"cita", "programar", "reservar", "sacar"},
    "aseo": {"basura", "camion", "carro", "auto", "recoleccion", "residuos"},
    "basura": {"aseo", "recoleccion", "residuos", "camion", "carro", "auto", "recogen", "recoger"},
    "camion": {"basura", "aseo", "auto", "carro", "recoleccion", "residuos"},
    "carro": {"aseo", "basura", "camion", "recoleccion", "residuos"},
    "auto": {"aseo", "basura", "camion", "recoleccion", "residuos"},
    "cita": {"agendar", "programar", "reservar", "sacar", "turno"},
    "descargar": {"bajar", "obtener", "sacar", "imprimir"},
    "hueco": {"bache", "via", "calle", "reporte", "reportar"},
    "hora": {"horario", "jornada", "cuando"},
    "impuesto": {"predial", "recibo", "pago", "factura"},
    "aviso": {"reportar", "radicar", "informar"},
    "danada": {"rota", "mala", "averiada"},
    "lampara": {"luminaria", "alumbrado", "poste", "luz"},
    "luminaria": {"lampara", "alumbrado", "poste", "luz"},
    "predial": {"impuesto", "recibo", "pago", "factura"},
    "recibo": {"factura", "impuesto", "predial", "pago"},
    "reportar": {"radicar", "avisar", "denunciar", "informar"},
    "rota": {"danada", "luminaria", "lampara"},
    "sisben": {"encuesta", "puntaje", "cita", "planeacion"},
}


def normalizar_texto(texto):
    """Convierte texto a una forma comparable: minusculas, sin tildes ni signos."""
    texto = str(texto or "").lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(caracter for caracter in texto if unicodedata.category(caracter) != "Mn")
    texto = re.sub(r"[^a-z0-9\s]", " ", texto)
    return re.sub(r"\s+", " ", texto).strip()


def tokenizar(texto):
    tokens = {
        palabra
        for palabra in normalizar_texto(texto).split()
        if len(palabra) > 2 and palabra not in PALABRAS_VACIAS
    }

    expandidos = set(tokens)
    for token in tokens:
        expandidos.update(SINONIMOS.get(token, set()))

    return expandidos


def cargar_faqs(ruta_csv=RUTA_FAQS):
    faqs = []
    with open(ruta_csv, mode="r", encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            pregunta = (fila.get("pregunta") or "").strip()
            respuesta = (fila.get("respuesta") or "").strip()
            if pregunta and respuesta:
                faqs.append({"pregunta": pregunta, "respuesta": respuesta})
    return faqs


def puntuar_coincidencia(pregunta_usuario, faq):
    texto_usuario = normalizar_texto(pregunta_usuario)
    texto_faq = normalizar_texto(f"{faq['pregunta']} {faq['respuesta']}")

    tokens_usuario = tokenizar(pregunta_usuario)
    tokens_faq = tokenizar(texto_faq)

    if not tokens_usuario or not tokens_faq:
        return 0

    coincidencias = tokens_usuario.intersection(tokens_faq)
    cobertura = len(coincidencias) / len(tokens_usuario)
    afinidad = len(coincidencias) / len(tokens_faq)
    similitud_frase = SequenceMatcher(None, texto_usuario, texto_faq).ratio()

    return (cobertura * 0.65) + (afinidad * 0.20) + (similitud_frase * 0.15)


def buscar_faqs_relevantes(pregunta_usuario, ruta_csv=RUTA_FAQS, max_resultados=3, puntaje_minimo=0.18):
    faqs = cargar_faqs(ruta_csv)
    resultados = []

    for faq in faqs:
        puntaje = puntuar_coincidencia(pregunta_usuario, faq)
        if puntaje >= puntaje_minimo:
            resultados.append((puntaje, faq))

    resultados.sort(key=lambda item: item[0], reverse=True)
    return [faq for _, faq in resultados[:max_resultados]]


def construir_contexto(faqs):
    if not faqs:
        return MENSAJE_SIN_INFORMACION

    bloques = []
    for faq in faqs:
        bloques.append(
            f"Pregunta frecuente: {faq['pregunta']}\n"
            f"Respuesta oficial: {faq['respuesta']}"
        )

    return "\n\n".join(bloques)


def obtener_contexto_local(pregunta_usuario, ruta_csv=RUTA_FAQS, max_resultados=3):
    """Busca FAQs relevantes aunque el ciudadano no pregunte con palabras literales."""
    try:
        faqs = buscar_faqs_relevantes(pregunta_usuario, ruta_csv, max_resultados)
    except FileNotFoundError:
        print("Nota: Archivo faqs.csv no encontrado. Continuando sin contexto local.")
        return MENSAJE_SIN_INFORMACION

    return construir_contexto(faqs)


def hay_contexto_disponible(contexto):
    return contexto != MENSAJE_SIN_INFORMACION
