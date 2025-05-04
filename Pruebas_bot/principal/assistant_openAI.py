from openai import OpenAI
import shelve
from dotenv import load_dotenv
import os
import time

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

#Cargar el archivo de prompts para el asistente
def promps_file(path):
    try:
        with open (path,'rb') as f:
            
            file = client.files.create(file=f,purpose="assistants") #En posbile caso de que el archivo deje de funcionar
        return file
    except FileNotFoundError:
        print("Archivo no encontrado")
        return None

file = promps_file("/promps/promps_assistant.pdf")

def create_assistant(file):
    
    assistant = client.beta.assistants.create(
        name="Assistant_FOBO",
        instructions="Eres un asistente de WhatsApp que ayuda guiando a los clientes a comprar productos. Usa tu base de conocimientos para responder mejor a las consultas de los clientes. Se amable y útil en tus respuestas.",
        tools=[{"type": "retrieval"}],
        model="gpt-4o-turbo",
        file_ids=[file.id],
    )
    return assistant

#Se crea el asistente al iniciar el programa. Solo usar para testeo, hay que modificar luego
assistant = create_assistant(file)

#Verificar si el hilo de conversascion existe
def check_if_thread_exists(wpp_id_conversation):
    with shelve.open("threads_db") as threads_shelf:
        return threads_shelf.get(wpp_id_conversation, None)

#Almacenar el hilo de conversación
def store_thread(wpp_id_conversation, thread_id):
    with shelve.open("threads_db", writeback=True) as threads_shelf:
        threads_shelf[wpp_id_conversation] = thread_id

def generate_response(message_body, wpp_id_conversation, name):
    thread_id = check_if_thread_exists(wpp_id_conversation)

    #Existe el hilo de conversación?
    if thread_id is None:
        print(f"Creating new thread for {name} with wpp_id_conversation {wpp_id_conversation}")
        thread = client.beta.threads.create()
        store_thread(wpp_id_conversation, thread.id)
        thread_id = thread.id

    #Si no, recuperar el hilo de conversación
    else:
        print(f"Retrieving existing thread for {name} with wpp_id_conversation {wpp_id_conversation}")
        thread = client.beta.threads.retrieve(thread_id)

    # Añadir el mensaje del usuario
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=message_body,
    )

    # Obtener la respuesta del asistente
    new_message = run_assistant(thread)
    print(f"To {name}:", new_message)
    return new_message

def run_assistant(thread):
    #Recuperar el asistente
    assistant = client.beta.assistants.retrieve("asst_7Wx2nQwoPWSf710jrdWTDlfE")# Hardcodeado por ahora

    # Correr el asistente
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    # Esperar a que el asistente termine la tarea
    while run.status != "completed":
        # Be nice to the API
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Recuperar el mensaje generado
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    print(f"Generated message: {new_message}")
    return new_message
