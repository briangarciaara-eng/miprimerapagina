from services.buscador_faq import hay_contexto_disponible, normalizar_texto, obtener_contexto_local
from services.groq_service import preguntar_a_llama

# Configuracion principal del asistente.
# Para adaptar este proyecto a otro cliente, cambia estos valores:
# - Consultorio odontologico: "Asistente Virtual Consultorio Dental"
# - Institucion educativa: "Asistente Virtual Colegio San Jose"
# - Alcaldia/municipio: "Asistente Virtual Alcaldia"
NOMBRE_ASISTENTE = "Asistente Virtual Alcaldia"

# Lista de temas que el bot puede mencionar cuando el ciudadano hace una
# pregunta muy general o cuando no hay informacion suficiente en las FAQs.
# Manten esta lista alineada con el contenido real de data/faqs.csv.
TEMAS_DISPONIBLES = [
    "impuesto predial",
    "recoleccion de aseo",
    "reporte de huecos o luminarias danadas",
    "citas del Sisben",
]

PREGUNTAS_GENERALES_EXACTAS = {
    "ayuda",
    "informacion",
    "servicio",
    "servicios",
}

PREGUNTAS_GENERALES = [
    "que servicio",
    "que servicios",
    "que hace la alcaldia",
    "que hace el municipio",
    "que hace esta entidad",
    "a que se dedica la alcaldia",
    "a que se dedica el municipio",
    "que puedo consultar",
    "como apoya la alcaldia",
    "como me apoya la alcaldia",
    "como apoya el municipio",
    "como me apoya el municipio",
    "como ayuda la alcaldia",
    "como ayuda el municipio",
    "como me puede ayudar",
    "en que me puedes ayudar",
    "en que me puede ayudar",
    "que haces",
    "que sabes",
    "tengo una consulta",
    "tengo una duda",
    "necesito ayuda",
]

DATOS_INSTITUCIONALES = [
    "direccion",
    "ubicacion",
    "ubicada",
    "ubicado",
    "telefono",
    "nit",
    "ciudad",
    "horario de atencion",
    "sede",
]

SINTOMAS_SALUD = [
    "enfermo",
    "enferma",
    "dolor",
    "duele",
    "cuerpo",
    "fiebre",
    "medico",
    "doctor",
    "urgencia medica",
    "salud",
]


def construir_menu_temas():
    temas = "\n".join(f"- {tema}" for tema in TEMAS_DISPONIBLES)
    return (
        "Puedo orientarte sobre la informacion que tengo cargada actualmente:\n"
        f"{temas}\n\n"
        "Sobre cual tema necesitas ayuda?"
    )


def construir_mensaje_bienvenida():
    return (
        f"Bienvenido al {NOMBRE_ASISTENTE}.\n"
        "Estoy entrenado para orientarte sobre estos temas:\n"
        f"{chr(10).join(f'{indice}. {tema}' for indice, tema in enumerate(TEMAS_DISPONIBLES, start=1))}\n\n"
        "Escribe tu pregunta o el tema sobre el que necesitas ayuda. "
        "Para terminar, escribe 'salir'."
    )


def construir_respuesta_sin_contexto():
    temas = "\n".join(f"- {tema}" for tema in TEMAS_DISPONIBLES)
    return (
        "No tengo esa informacion en la base de conocimiento disponible. "
        "Actualmente puedo orientarte sobre:\n"
        f"{temas}"
    )


def construir_respuesta_salud():
    return (
        "No tengo informacion de servicios de salud en la base de conocimiento disponible. "
        "Si tienes sintomas fuertes, una urgencia o te sientes en riesgo, comunicate con los "
        "servicios de emergencia o acude al centro de salud mas cercano. "
        "Actualmente puedo orientarte sobre:\n"
        f"{chr(10).join(f'- {tema}' for tema in TEMAS_DISPONIBLES)}"
    )


def es_pregunta_general(pregunta):
    pregunta_normalizada = normalizar_texto(pregunta)
    if pregunta_normalizada in PREGUNTAS_GENERALES_EXACTAS:
        return True

    return any(frase in pregunta_normalizada for frase in PREGUNTAS_GENERALES)


def pide_dato_institucional(pregunta):
    pregunta_normalizada = normalizar_texto(pregunta)
    return any(dato in pregunta_normalizada for dato in DATOS_INSTITUCIONALES)


def parece_consulta_salud(pregunta):
    pregunta_normalizada = normalizar_texto(pregunta)
    return any(sintoma in pregunta_normalizada for sintoma in SINTOMAS_SALUD)


def generar_respuesta(entrada):
    if parece_consulta_salud(entrada):
        return construir_respuesta_salud()

    if es_pregunta_general(entrada):
        return construir_menu_temas()

    if pide_dato_institucional(entrada):
        return construir_respuesta_sin_contexto()

    contexto_encontrado = obtener_contexto_local(entrada)
    if not hay_contexto_disponible(contexto_encontrado):
        return construir_respuesta_sin_contexto()

    return preguntar_a_llama(entrada, contexto_encontrado)


def iniciar_chat():
    print(f"[{NOMBRE_ASISTENTE}] En linea.\n")
    print(f"Bot: {construir_mensaje_bienvenida()}\n")

    while True:
        entrada = input("Ciudadano: ")
        if entrada.lower() == "salir":
            print("Bot: Que tenga un excelente dia. Hasta luego!")
            break

        respuesta_ia = generar_respuesta(entrada)
        print(f"Bot: {respuesta_ia}\n")


if __name__ == "__main__":
    iniciar_chat()
