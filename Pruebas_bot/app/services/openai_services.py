from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time
import logging
import sys

# Configuración básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class AssistantManager:
    def __init__(self):
        # Configuración inicial para Windows
        if sys.platform == "win32":
            os.system('chcp 65001')

        # Carga de configuración
        load_dotenv()
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
        self.client = OpenAI(api_key=self.OPENAI_API_KEY)

    def load_prompts_file(self):
        """Carga el archivo PDF con los prompts del asistente"""
        try:
            BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            pdf_path = os.path.join(BASE_DIR, "resources", "prompts", "prompts_assistant.pdf")

            if not os.path.exists(pdf_path):
                logging.error(f"Archivo no encontrado en {pdf_path}")
                return None

            with open(pdf_path, 'rb') as f:
                file = self.client.files.create(file=f, purpose="assistants")
                return file

        except Exception as e:
            logging.error(f"Error al cargar el archivo: {str(e)}", exc_info=True)
            return None

    def create_assistant(self, file):
        """Crea un nuevo asistente con el archivo cargado"""
        assistant = self.client.beta.assistants.create(
            name="ASISTENTE FOBO",
            instructions="Eres un asistente de WhatsApp que ayuda guiando a los clientes a comprar productos.",
            tools=[{"type": "retrieval"}],
            model="gpt-4-turbo",
            file_ids=[file.id],
        )
        return assistant

    def _get_thread_db(self):
        """Maneja la conexión con la base de datos de threads"""
        return shelve.open("threads_db", writeback=True)

    def check_if_thread_exists(self, wa_id):
        """Verifica si existe un thread para el usuario"""
        with self._get_thread_db() as threads_shelf:
            return threads_shelf.get(wa_id, None)

    def store_thread(self, wa_id, thread_id):
        """Almacena un nuevo thread para el usuario"""
        with self._get_thread_db() as threads_shelf:
            threads_shelf[wa_id] = thread_id

    def run_assistant(self, thread, name):
        """Ejecuta el asistente para un thread específico"""
        assistant = self.client.beta.assistants.retrieve(self.OPENAI_ASSISTANT_ID)
        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions=f"Estás teniendo una conversación con {name}"
        )
        
        while run.status != "completed":
            time.sleep(0.5)
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id, 
                run_id=run.id
            )

        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        return messages.data[0].content[0].text.value

    def generate_response(self, message_body, wa_id, name):
        """Genera una respuesta para el mensaje del usuario"""
        thread_id = self.check_if_thread_exists(wa_id)

        if thread_id is None:
            thread = self.client.beta.threads.create()
            self.store_thread(wa_id, thread.id)
            thread_id = thread.id
        else:
            thread = self.client.beta.threads.retrieve(thread_id)

        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message_body,
        )

        return self.run_assistant(thread, name)