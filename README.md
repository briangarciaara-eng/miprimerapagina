# Chatbot Alcaldia

Laboratorio practico de un asistente virtual para atencion ciudadana en alcaldias y municipios.

El proyecto usa Python, un archivo de preguntas frecuentes en CSV y Groq para generar respuestas con un modelo de lenguaje. Antes de llamar al modelo, el sistema busca FAQs relevantes con una capa local de recuperacion flexible para entender preguntas no literales.

## Estructura

```text
app.py
api.py
data/
  faqs.csv
  README.md
services/
  buscador_faq.py
  groq_service.py
tests/
  test_api.py
  test_buscador_faq.py
web/
  index.html
  styles.css
  app.js
.env.example
.gitignore
README.md
```

## Configuracion

Crea un archivo `.env` en la raiz del proyecto:

```env
GROQ_API_KEY=gsk_tu_clave_real
```

El archivo `.env` no se debe subir a GitHub. Para eso esta incluido en `.gitignore`.

## Ejecutar

Instala dependencias:

```powershell
pip install -r requirements.txt
```

Consola:

```powershell
.venv\Scripts\activate
python app.py
```

API y frontend web:

```powershell
uvicorn api:api --reload
```

Luego abre:

```text
http://127.0.0.1:8000
```

Documentacion automatica de la API:

```text
http://127.0.0.1:8000/docs
```

## Adaptar A Otro Cliente

Este proyecto esta armado como plantilla. Para usarlo con otro tipo de cliente:

1. Edita `data/faqs.csv` con preguntas y respuestas oficiales del cliente.
2. Ajusta `NOMBRE_ASISTENTE` en `app.py`.
3. Ajusta `TEMAS_DISPONIBLES` en `app.py`.
4. Agrega sinonimos importantes en `services/buscador_faq.py`.
5. Crea pruebas nuevas en `tests/test_buscador_faq.py`.

Ejemplos:

- Consultorio odontologico: citas, limpieza dental, urgencias, horarios, direccion, medios de pago.
- Institucion educativa: matriculas, pensiones, horarios, certificados, calendario academico.
- Alcaldia: impuestos, aseo, Sisbén, infraestructura, PQRS, canales oficiales.

Si el bot no encuentra contexto confiable, responde con una salida controlada en vez de inventar informacion.

## Probar Busqueda Local

Las pruebas validan que el buscador encuentre la FAQ correcta aunque el ciudadano pregunte con otras palabras:

```powershell
pytest
```

Ejemplos que debe entender:

- `a que hora pasa el auto del aseo`
- `cuando recogen los residuos`
- `necesito bajar la factura predial`
- `como aviso que hay una lampara rota`

## Objetivo De Aprendizaje

Este laboratorio simula una necesidad real de un AI Engineer Junior: construir un chatbot que no dependa de coincidencias literales, separe responsabilidades del codigo y pueda crecer hacia FastAPI, Streamlit y RAG.
"# miprimerapagina" 
