# Como Armar Las FAQs

El archivo `faqs.csv` es la base de conocimiento del chatbot. Debe conservar dos columnas:

```csv
pregunta,respuesta
```

Cada fila representa una pregunta frecuente y su respuesta oficial. Si una respuesta tiene comas, escribe el valor entre comillas dobles.

Ejemplo para una alcaldia:

```csv
"Como descargo el recibo del impuesto predial?","Ingrese al portal web oficial y seleccione Impuestos Virtuales."
```

Ejemplo para un consultorio odontologico:

```csv
"Como agendo una cita odontologica?","Puede agendar su cita por WhatsApp o llamando a la recepcion."
```

Ejemplo para una institucion educativa:

```csv
"Cuando son las matriculas?","Las matriculas se realizan del 10 al 20 de enero en secretaria academica."
```

Buenas practicas:

- Usa respuestas oficiales, claras y verificadas.
- No incluyas informacion que el cliente no haya autorizado.
- Agrega varias FAQs para temas importantes como direccion, horarios, telefonos y canales oficiales si quieres que el bot responda eso.
- Actualiza `TEMAS_DISPONIBLES` en `app.py` para que coincida con los temas reales del CSV.
