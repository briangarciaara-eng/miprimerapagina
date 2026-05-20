import re

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

SALUDOS = [
    "hola",
    "buenos dias",
    "buenas tardes",
    "buenas noches",
    "saludos",
    "hola como estas",
    "como estas",
    "que tal",
]

DIAS_SEMANA = {
    "lunes",
    "martes",
    "miercoles",
    "jueves",
    "viernes",
    "sabado",
    "domingo",
}

PALABRAS_ASEO = {"aseo", "basura", "camion", "recoleccion", "residuos"}
PALABRAS_PREDIAL = {"predial", "impuesto", "recibo", "factura"}
PALABRAS_TEMA_EXPLICITO = {
    "aseo",
    "basura",
    "camion",
    "recoleccion",
    "predial",
    "impuesto",
    "sisben",
    "hueco",
    "huecos",
    "luminaria",
    "luminarias",
}

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


def capitalizar_inicial(texto):
    contenido = str(texto or "").strip()
    if not contenido:
        return ""
    return contenido[0].upper() + contenido[1:]


def construir_lista_temas():
    return "\n".join(f"- {capitalizar_inicial(tema)}" for tema in TEMAS_DISPONIBLES)


def construir_menu_temas():
    temas = construir_lista_temas()
    return (
        "Puedo orientarte sobre la informacion que tengo cargada actualmente:\n"
        f"{temas}\n\n"
        "Sobre cual tema necesitas ayuda?"
    )


def construir_mensaje_bienvenida():
    temas_enumerados = "\n".join(
        f"{indice}. {capitalizar_inicial(tema)}"
        for indice, tema in enumerate(TEMAS_DISPONIBLES, start=1)
    )
    return (
        f"Bienvenido al {NOMBRE_ASISTENTE}.\n"
        "Estoy entrenado para orientarte sobre estos temas:\n"
        f"{temas_enumerados}\n\n"
        "Escribe tu pregunta o el tema sobre el que necesitas ayuda. "
        "Para terminar, escribe 'salir'."
    )


def construir_respuesta_sin_contexto():
    temas = construir_lista_temas()
    return (
        "Por ahora no cuento con informacion especifica para esa solicitud. "
        "Actualmente puedo orientarte sobre:\n"
        f"{temas}"
    )


def construir_respuesta_salud():
    return (
        "Por ahora no cuento con informacion especifica de servicios de salud para esa solicitud. "
        "Si tienes sintomas fuertes, una urgencia o te sientes en riesgo, comunicate con los "
        "servicios de emergencia o acude al centro de salud mas cercano. "
        "Actualmente puedo orientarte sobre:\n"
        f"{construir_lista_temas()}"
    )


def es_saludo(pregunta):
    pregunta_normalizada = normalizar_texto(pregunta)
    return any(saludo in pregunta_normalizada for saludo in SALUDOS)


def construir_respuesta_saludo():
    return (
        "Hola, gracias por escribir. Es un gusto saludarte.\n"
        "Te puedo orientar sobre estos servicios disponibles:\n"
        f"{construir_lista_temas()}\n\n"
        "Si deseas, escribe directamente el tema o tu consulta."
    )


def extraer_dias_contexto(contexto):
    contexto_normalizado = normalizar_texto(contexto)
    return {dia for dia in DIAS_SEMANA if dia in contexto_normalizado}


def normalizar_dia_para_salida(dia):
    reemplazos = {"miercoles": "miércoles", "sabado": "sábado"}
    return reemplazos.get(dia, dia)


def construir_texto_dias(dias):
    orden = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    dias_ordenados = [normalizar_dia_para_salida(dia) for dia in orden if dia in dias]
    if not dias_ordenados:
        return ""
    if len(dias_ordenados) == 1:
        return dias_ordenados[0]
    if len(dias_ordenados) == 2:
        return f"{dias_ordenados[0]} y {dias_ordenados[1]}"
    return f"{', '.join(dias_ordenados[:-1])} y {dias_ordenados[-1]}"


def extraer_rango_horario_contexto(contexto):
    patron = re.search(
        r"de\s+(\d{1,2}:\d{2})\s*([APap]\.?[Mm]\.?)\s+a\s+(\d{1,2}:\d{2})\s*([APap]\.?[Mm]\.?)",
        contexto,
    )
    if not patron:
        return None

    inicio = convertir_a_minutos(patron.group(1), patron.group(2))
    fin = convertir_a_minutos(patron.group(3), patron.group(4))
    if inicio is None or fin is None:
        return None
    return inicio, fin


def convertir_a_minutos(hora, meridiano):
    partes = hora.split(":")
    if len(partes) != 2:
        return None

    horas = int(partes[0])
    minutos = int(partes[1])
    meridiano_normalizado = meridiano.lower().replace(".", "")

    if meridiano_normalizado == "pm" and horas != 12:
        horas += 12
    if meridiano_normalizado == "am" and horas == 12:
        horas = 0

    return (horas * 60) + minutos


def extraer_horas_pregunta(pregunta):
    coincidencias = re.findall(r"(\d{1,2})(?::(\d{2}))?\s*([ap]\.?m\.?)", pregunta, flags=re.IGNORECASE)
    horas = []
    for hora, minutos, meridiano in coincidencias:
        hora_texto = f"{hora}:{minutos or '00'}"
        valor = convertir_a_minutos(hora_texto, meridiano)
        if valor is not None:
            horas.append(valor)
    return horas


def es_consulta_aseo(pregunta):
    pregunta_normalizada = normalizar_texto(pregunta)
    return any(palabra in pregunta_normalizada for palabra in PALABRAS_ASEO)


def construir_respuesta_validacion_formato(pregunta, contexto):
    pregunta_normalizada = normalizar_texto(pregunta)
    contexto_normalizado = normalizar_texto(contexto)
    if not any(palabra in pregunta_normalizada for palabra in PALABRAS_PREDIAL):
        return None

    consulta_sobre_formato = any(
        termino in pregunta_normalizada
        for termino in ["formato", "pdf", "word", "excel", "doc", "docx", "xlsx"]
    )
    if not consulta_sobre_formato:
        return None

    if "formato pdf" in contexto_normalizado:
        if any(termino in pregunta_normalizada for termino in ["word", "excel", "doc", "docx", "xlsx"]):
            return "No, para impuesto predial el unico formato disponible es PDF."
        if "pdf" in pregunta_normalizada:
            return "Si, para impuesto predial el formato disponible es PDF."
        return "Para impuesto predial, el formato de descarga disponible es PDF."

    return None


def extraer_contexto_aseo(contexto):
    bloques = [bloque.strip() for bloque in contexto.split("\n\n") if bloque.strip()]
    bloques_aseo = []
    for bloque in bloques:
        bloque_normalizado = normalizar_texto(bloque)
        if any(palabra in bloque_normalizado for palabra in PALABRAS_ASEO):
            bloques_aseo.append(bloque)
    if not bloques_aseo:
        return contexto
    return "\n\n".join(bloques_aseo)


def construir_respuesta_validacion_aseo(pregunta, contexto):
    if not es_consulta_aseo(pregunta):
        return None

    contexto_aseo = extraer_contexto_aseo(contexto)
    pregunta_normalizada = normalizar_texto(pregunta)
    dias_contexto = extraer_dias_contexto(contexto_aseo)
    dia_consultado = next((dia for dia in DIAS_SEMANA if dia in pregunta_normalizada), None)
    if dia_consultado and dias_contexto:
        dias_texto = construir_texto_dias(dias_contexto)
        dia_salida = normalizar_dia_para_salida(dia_consultado)
        if dia_consultado in dias_contexto:
            return (
                f"Si, el camion si pasa el {dia_salida}. "
                f"Pasa los dias {dias_texto}."
            )
        return (
            f"No, el camion no pasa el {dia_salida}. "
            f"Pasa solo los dias {dias_texto}."
        )

    horas_consultadas = extraer_horas_pregunta(pregunta)
    rango = extraer_rango_horario_contexto(contexto_aseo)
    if horas_consultadas and rango:
        inicio, fin = rango
        if all(inicio <= hora <= fin for hora in horas_consultadas):
            return "Si, ese horario esta dentro del rango de atencion del camion de recoleccion."
        return "No, en ese horario no pasa. El camion pasa en la jornada de la manana, de 6:00 AM a 10:00 AM."

    return None


def construir_respuesta_resumen_aseo(contexto):
    contexto_aseo = extraer_contexto_aseo(contexto)
    dias = extraer_dias_contexto(contexto_aseo)
    rango = extraer_rango_horario_contexto(contexto_aseo)
    if not dias and not rango:
        return None

    partes = []
    if dias:
        partes.append(f"El camion de recoleccion pasa los dias {construir_texto_dias(dias)}.")
    if rango:
        partes.append("El horario de paso es en la manana, de 6:00 AM a 10:00 AM.")
    return " ".join(partes)


def necesita_contexto_previo(entrada):
    texto = normalizar_texto(entrada)
    tokens = texto.split()
    if len(tokens) <= 3:
        return True
    if texto.startswith("a las ") or texto.startswith("y a las "):
        return True
    if re.search(r"\b\d{1,2}\s*(am|pm)\b", texto):
        return True
    disparadores = {"si", "no", "entonces", "y", "ok", "vale"}
    if any(token in disparadores for token in tokens):
        return True
    return False


def es_consulta_tema_explicito(entrada):
    texto = normalizar_texto(entrada)
    return any(palabra in texto for palabra in PALABRAS_TEMA_EXPLICITO)


def enriquecer_con_contexto_conversacion(entrada, ultima_pregunta_usuario=None):
    if not ultima_pregunta_usuario:
        return entrada
    if es_consulta_tema_explicito(entrada):
        return entrada
    if not necesita_contexto_previo(entrada):
        return entrada
    return f"{ultima_pregunta_usuario}. {entrada}"


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


def generar_respuesta(entrada, ultima_pregunta_usuario=None):
    entrada_procesada = enriquecer_con_contexto_conversacion(entrada, ultima_pregunta_usuario)

    if es_saludo(entrada_procesada):
        return construir_respuesta_saludo()

    if parece_consulta_salud(entrada_procesada):
        return construir_respuesta_salud()

    if es_pregunta_general(entrada_procesada):
        return construir_menu_temas()

    if pide_dato_institucional(entrada_procesada):
        return construir_respuesta_sin_contexto()

    contexto_encontrado = obtener_contexto_local(entrada_procesada)
    if not hay_contexto_disponible(contexto_encontrado):
        return construir_respuesta_sin_contexto()

    respuesta_validacion_aseo = construir_respuesta_validacion_aseo(entrada_procesada, contexto_encontrado)
    if respuesta_validacion_aseo:
        return respuesta_validacion_aseo

    respuesta_validacion_formato = construir_respuesta_validacion_formato(entrada_procesada, contexto_encontrado)
    if respuesta_validacion_formato:
        return respuesta_validacion_formato

    if es_consulta_aseo(entrada_procesada):
        resumen_aseo = construir_respuesta_resumen_aseo(contexto_encontrado)
        if resumen_aseo:
            return resumen_aseo

    return preguntar_a_llama(entrada_procesada, contexto_encontrado)


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
