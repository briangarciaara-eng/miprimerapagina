from services.buscador_faq import buscar_faqs_relevantes, obtener_contexto_local
from app import construir_mensaje_bienvenida, generar_respuesta


def primera_pregunta_encontrada(consulta):
    resultados = buscar_faqs_relevantes(consulta, max_resultados=1)
    assert resultados, f"No se encontraron FAQs para: {consulta}"
    return resultados[0]["pregunta"]


def test_encuentra_horario_del_aseo_con_sinonimos():
    pregunta = primera_pregunta_encontrada("a que hora pasa el auto del aseo")

    assert "Hora de pasada" in pregunta


def test_encuentra_dias_de_recoleccion_con_pregunta_no_literal():
    pregunta = primera_pregunta_encontrada("cuando recogen los residuos")

    assert "Dias en que pasa" in pregunta


def test_encuentra_predial_con_factura():
    pregunta = primera_pregunta_encontrada("necesito bajar la factura predial")

    assert "impuesto predial" in pregunta


def test_encuentra_reporte_de_luminaria():
    pregunta = primera_pregunta_encontrada("como aviso que hay una lampara rota")

    assert "luminaria" in pregunta


def test_contexto_indica_sin_informacion_si_no_hay_coincidencia():
    contexto = obtener_contexto_local("quiero renovar mi pasaporte")

    assert "No hay informacion especifica" in contexto


def test_respuesta_general_muestra_temas_disponibles():
    respuesta = generar_respuesta("que servicios presta la alcaldia")

    assert "Puedo orientarte" in respuesta
    assert "impuesto predial" in respuesta
    assert "citas del Sisben" in respuesta


def test_mensaje_bienvenida_muestra_menu_inicial():
    mensaje = construir_mensaje_bienvenida()

    assert "Bienvenido" in mensaje
    assert "1. impuesto predial" in mensaje
    assert "4. citas del Sisben" in mensaje
    assert "salir" in mensaje


def test_respuesta_general_en_singular_muestra_temas_disponibles():
    respuesta = generar_respuesta("que servicio presta la alcaldia")

    assert "Puedo orientarte" in respuesta
    assert "recoleccion de aseo" in respuesta


def test_preguntas_sobre_funcion_o_apoyo_muestran_temas_disponibles():
    consultas = [
        "que hace la alcaldia",
        "a que se dedica la alcaldia",
        "como ayuda la alcaldia",
        "como apoya la alcaldia al ciudadano",
        "como me apoya la alcaldia",
    ]

    for consulta in consultas:
        respuesta = generar_respuesta(consulta)

        assert "Puedo orientarte" in respuesta
        assert "impuesto predial" in respuesta


def test_consulta_generica_muestra_temas_disponibles():
    respuesta = generar_respuesta("tengo una consulta")

    assert "Puedo orientarte" in respuesta
    assert "impuesto predial" in respuesta


def test_palabras_generales_cortas_muestran_temas_disponibles():
    for consulta in ["ayuda", "informacion", "servicios"]:
        respuesta = generar_respuesta(consulta)

        assert "Puedo orientarte" in respuesta
        assert "recoleccion de aseo" in respuesta


def test_consulta_de_salud_tiene_fallback_prudente():
    respuesta = generar_respuesta("me duele el cuerpo como me pueden ayudar")

    assert "No tengo informacion de servicios de salud" in respuesta
    assert "centro de salud" in respuesta


def test_consulta_medica_tiene_fallback_prudente():
    respuesta = generar_respuesta("necesito un medico")

    assert "No tengo informacion de servicios de salud" in respuesta
    assert "centro de salud" in respuesta


def test_ayuda_con_tema_concreto_no_muestra_menu_generico():
    contexto = obtener_contexto_local("ayuda con el sisben")

    assert "citas se agendan" in contexto


def test_consulta_amplia_sobre_aseo_encuentra_contexto():
    contexto = obtener_contexto_local("quiero saber toda la informacion disponible sobre aseo")

    assert "camion de recoleccion de aseo" in contexto
    assert "6:00 AM a 10:00 AM" in contexto


def test_respuesta_sin_contexto_no_llama_al_modelo():
    respuesta = generar_respuesta("donde esta ubicada la alcaldia")

    assert "No tengo esa informacion" in respuesta
    assert "recoleccion de aseo" in respuesta
