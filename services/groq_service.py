import os

client = None


def cargar_variables_env(ruta_env=".env"):
    """Carga variables simples CLAVE=valor desde .env si aun no existen."""
    if not os.path.exists(ruta_env):
        return

    with open(ruta_env, mode="r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue

            clave, valor = linea.split("=", 1)
            clave = clave.strip()
            valor = valor.strip().strip('"').strip("'")
            os.environ.setdefault(clave, valor)


def preguntar_a_llama(pregunta, contexto):
    """Envia la pregunta y el contexto de la alcaldia al modelo Llama 3 en la nube."""
    prompt_sistema = (
        "Eres un chatbot de atencion al ciudadano para una alcaldia en Colombia. "
        "Tu unica fuente de verdad es el 'Contexto de la alcaldia' provisto abajo. "
        "No uses conocimiento general, definiciones externas ni supuestos institucionales. "
        "No expliques que es un impuesto, que es el Sisben, ni detalles de un tramite si no aparecen "
        "literalmente en el contexto. "
        "El contexto ya fue recuperado con busqueda flexible, asi que puedes interpretar sinonimos, "
        "pero la respuesta final debe limitarse a los datos presentes en el contexto. "
        "Si el ciudadano pide informacion general sobre un tema y el contexto solo contiene un tramite "
        "puntual, responde solo con ese tramite puntual. "
        "Si falta el dato especifico solicitado, di: 'No tengo esa informacion en la base de conocimiento disponible.' "
        "y, si aplica, menciona brevemente que informacion relacionada si aparece en el contexto. "
        "Responde de forma amable, clara y breve, sin inventar pasos, canales, ubicaciones, telefonos, "
        "definiciones, recomendaciones ni explicaciones adicionales."
    )

    prompt_usuario = f"Contexto de la alcaldia:\n{contexto}\n\nPregunta del ciudadano: {pregunta}"

    try:
        global client
        if client is None:
            cargar_variables_env()
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                return (
                    "Falta configurar GROQ_API_KEY. Agrega tu clave en el archivo .env "
                    "asi: GROQ_API_KEY=gsk_tu_clave"
                )

            from groq import Groq

            client = Groq(api_key=api_key)

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario},
            ],
            temperature=0.0,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error de conexion con el motor de IA: {e}"
