import logging
from flask import current_app, jsonify
import json
import os
import requests
from app.services.openai_services import generate_response
import re
# Para depuración 
def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")

# Construye el payload JSON para enviar mensajes de texto a través de la API de WhatsApp
def get_text_message_input(recipient, text):
    return json.dumps(
        {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": recipient,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
    )   

# Función de prueba para generar una respuesta (solo para pruebas; reemplazar con OpenAI en producción)
#def generate_response(response):
#    return response.upper()

# Puente entre el servidor y la API de WhatsApp Business para enviar mensajes
def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
    }

    url = f"https://graph.facebook.com/{current_app.config['VERSION']}/{current_app.config['TEST_NUMBER_ID']}/messages"

    try:
        print(current_app.config['ACCESS_TOKEN'])
        response = requests.post(url, data=data, headers=headers, timeout=10)
        response.raise_for_status()
        log_http_response(response)
        return response
    except requests.Timeout:
        logging.error("Se superó el tiempo de espera de la solicitud")
        return jsonify({"status": "error", "message": "solicitar tiempo de espera"}), 408
    except requests.RequestException as e:
        logging.error(f"La solicitud falló debido a: {e}")
        return jsonify({"status": "error", "message": "Fallo al enviar el mensaje"}), 500

# Procesar el texto para WhatsApp, eliminando caracteres especiales, emojis y formateando el texto
def process_text_for_whatsapp(text):
    text = re.sub(r"\【.*?\】", "", text).strip()
    text = re.sub(r"\*\*(.*?)\*\*", r"*\1*", text)
    return text

# Procesar el mensaje de WhatsApp entrante y generar una respuesta
def process_whatsapp_message(body):
    if not is_valid_whatsapp_message(body):
        return {"status": "error", "message": "Mensaje no válido"}, 400
    try:
        wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"].get("name", "")
        message = body["entry"][0]["changes"][0]["value"]["messages"][0]

        if message.get("type") != "text":
            return jsonify({"status": "ignored", "message": "Tipo de mensaje no soportado"}), 200

        message_body = message["text"]["body"]
        #response = generate_response(message_body)  # Solo para pruebas

        # OpenAI Integration
        response = generate_response(message_body, wa_id, name)
        response = process_text_for_whatsapp(response)
    
        data = get_text_message_input(wa_id, response)# Para pruebas, enviar la respuesta generada
        return send_message(data)
    
    except KeyError as e:
        logging.error(f"Error al procesar el mensaje de WhatsApp: {e}")
        return jsonify({"status": "error", "message": "Error al procesar el mensaje"}), 500

# Enviar una imagen cargada desde el servidor a la API de WhatsApp Business
def upload_media(filepath):
    url = f"https://graph.facebook.com/v{current_app.config['VERSION']}/{current_app.config['TEST_NUMBER_ID']}/media"
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}"
    }
    with open(filepath, "rb") as file:
        files = {
            "file": file,
            "type": (None, "image/jpeg")
        }
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        return response.json()["id"]

# Función para enviar un mensaje de imagen la API de WhatsApp Business
def send_image_message(recipient, image_url, caption=""):
    url = f"https://graph.facebook.com/v{current_app.config['VERSION']}/{current_app.config['TEST_NUMBER_ID']}/messages"
    headers = {
        "Authorization": f"Bearer {current_app.config['ACCESS_TOKEN']}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "image",
        "image": {
            "link": "https://i.postimg.cc/sfSJSKgg/qr.jpg", #Si se quiere usar id en lugar de url. Cargar la imagen a los servidores de la API de Whatsapp y luego con POST  pedirla
            "caption": caption
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# Verificar que el evento webhook entrante tiene una estructura válida
def is_valid_whatsapp_message(body):
    return (
        body.get("object")
        and body.get("entry")
        and body["entry"][0].get("changes")
        and body["entry"][0]["changes"][0].get("value")
        and body["entry"][0]["changes"][0]["value"].get("messages")
        and body["entry"][0]["changes"][0]["value"]["messages"][0]
    )
    
