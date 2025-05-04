import json
import os 
import requests 
import aiohttp 
import asyncio 
from datetime import datetime
from dotenv import load_dotenv 


load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
MY_NUMBER = os.getenv("MY_NUMBER")
TEST_NUMBER_ID = os.getenv("TEST_NUMBER_ID")
VERSION = os.getenv("VERSION")
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")


async def send_message(data):
    headers = {
        "Content-type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}",
    }

    async with aiohttp.ClientSession() as session:
        url = "https://graph.facebook.com" + f"/{VERSION}/{TEST_NUMBER_ID}/messages" #Para enviar mensajes desde el servidor a Whatsapp usando la versión 22.0 de la API de WhatsApp Business.
        try:
            async with session.post(url, data=data, headers=headers) as response:
                if response.status == 200:
                    print("Status:", response.status)
                    print("Content-type:", response.headers["content-type"])

                    html = await response.text()
                    print("Body:", html)
                else:
                    print(response.status)
                    print(response)
        except aiohttp.ClientConnectorError as e:
            print("Error de conexión", str(e))

# Te lo proporciona la API de WhatsApp Business
# La función prepara el mensaje en el formato requerido por la API de WhatsApp Business   
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


# Esto es de prueba
data = get_text_message_input(
    recipient=MY_NUMBER, 
    text="Hola Steven soy tu asistente de ventas personal en que puedo ayudarte hoy??"
)

def get_image_message_input(recipient, image_url):
    return json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "image",
        "image": {"link": image_url}
    })

imagen = get_image_message_input(
    recipient=MY_NUMBER,  
    image_url="https://i.postimg.cc/sfSJSKgg/qr.jpg"  # URL imagen (solo soporta imagenes de tipo .png y .jpg)
)

async def main():
    await send_message(data)    # Enviar texto
    await send_message(imagen)  # Enviar imagen

asyncio.run(main())

