from services.buscador_faq import buscar_faqs_relevantes, obtener_contexto_local
from app import construir_mensaje_bienvenida, enriquecer_con_contexto_conversacion, generar_respuesta


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
    assert "Impuesto predial" in respuesta
    assert "Citas del Sisben" in respuesta


def test_mensaje_bienvenida_muestra_menu_inicial():
    mensaje = construir_mensaje_bienvenida()

    assert "Bienvenido" in mensaje
    assert "1. Impuesto predial" in mensaje
    assert "4. Citas del Sisben" in mensaje
    assert "salir" in mensaje


def test_respuesta_general_en_singular_muestra_temas_disponibles():
    respuesta = generar_respuesta("que servicio presta la alcaldia")

    assert "Puedo orientarte" in respuesta
    assert "Recoleccion de aseo" in respuesta


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
        assert "Impuesto predial" in respuesta


def test_consulta_generica_muestra_temas_disponibles():
    respuesta = generar_respuesta("tengo una consulta")

    assert "Puedo orientarte" in respuesta
    assert "Impuesto predial" in respuesta


def test_palabras_generales_cortas_muestran_temas_disponibles():
    for consulta in ["ayuda", "informacion", "servicios"]:
        respuesta = generar_respuesta(consulta)

        assert "Puedo orientarte" in respuesta
        assert "Recoleccion de aseo" in respuesta


def test_consulta_de_salud_tiene_fallback_prudente():
    respuesta = generar_respuesta("me duele el cuerpo como me pueden ayudar")

    assert "Por ahora no cuento con informacion especifica de servicios de salud" in respuesta
    assert "centro de salud" in respuesta


def test_consulta_medica_tiene_fallback_prudente():
    respuesta = generar_respuesta("necesito un medico")

    assert "Por ahora no cuento con informacion especifica de servicios de salud" in respuesta
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

    assert "Por ahora no cuento con informacion especifica" in respuesta
    assert "Recoleccion de aseo" in respuesta


def test_saludo_responde_con_amabilidad_y_servicios():
    respuesta = generar_respuesta("buenas noches")

    assert "Es un gusto saludarte" in respuesta
    assert "servicios disponibles" in respuesta
    assert "Impuesto predial" in respuesta


def test_valida_dia_fuera_de_ruta_del_camion():
    respuesta = generar_respuesta("El camion pasa el domingo")

    assert "No, el camion no pasa el domingo" in respuesta
    assert "martes" in respuesta
    assert "jueves" in respuesta


def test_valida_hora_fuera_de_rango_del_camion():
    respuesta = generar_respuesta("El camion pasa a las 2pm")

    assert "No, en ese horario no pasa" in respuesta
    assert "6:00 AM a 10:00 AM" in respuesta


def test_consulta_general_aseo_entrega_dias_y_horario():
    respuesta = generar_respuesta("Recoleccion de aseo")

    assert "dias martes, jueves y sábado" in respuesta
    assert "6:00 AM a 10:00 AM" in respuesta


def test_valida_formato_predial_no_permite_word_ni_excel():
    respuesta = generar_respuesta("Puedo descargar el impuesto predial en word o excel?")

    assert "unico formato disponible es PDF" in respuesta


def test_valida_formato_predial_confirma_pdf():
    respuesta = generar_respuesta("El impuesto predial se descarga en PDF?")

    assert "formato disponible es PDF" in respuesta


def test_follow_up_corto_usa_contexto_previo():
    respuesta = generar_respuesta("Los lunes", ultima_pregunta_usuario="Recoleccion de aseo")

    assert "No, el camion no pasa el lunes" in respuesta


def test_validacion_aseo_no_se_confunde_con_lunes_de_sisben():
    respuesta = generar_respuesta("Recoleccion de aseo. Los lunes")

    assert "No, el camion no pasa el lunes" in respuesta


def test_enriquecimiento_mantiene_contexto_para_hora_corta():
    pregunta = enriquecer_con_contexto_conversacion("A las 1 pm", "Recoleccion de aseo")

    assert pregunta.startswith("Recoleccion de aseo.")


def test_enriquecimiento_no_mezcla_tema_explicito_sisben():
    pregunta = enriquecer_con_contexto_conversacion("Sisben", "Recoleccion de aseo")

    assert pregunta == "Sisben"
