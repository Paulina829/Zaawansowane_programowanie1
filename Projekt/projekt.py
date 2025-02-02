import os
import json
import uuid
import threading
import requests
import imghdr
import cv2 as cv
import pika
from PIL import Image
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('image_analysis_ui.html')

#  Konfiguracja RabbitMQ
RABBITMQ_HOST = 'localhost'
QUEUE_NAME = 'image_tasks'

def get_rabbitmq_channel():
    """Tworzy połączenie z RabbitMQ i zwraca kanał."""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    return connection, channel

#  Statusy zadań
task_status = {}

#  Konwersja obrazu do JPEG
def convert_to_jpeg(image_path):
    """Konwertuje obraz do JPEG, jeśli jest w innym formacie."""
    file_type = imghdr.what(image_path)
    if file_type == 'jpeg':
        return image_path, None

    try:
        img = Image.open(image_path)
        new_path = image_path + ".jpg"
        img.convert("RGB").save(new_path, "JPEG")
        os.remove(image_path)
        return new_path, None
    except Exception as e:
        return None, f"Błąd konwersji: {str(e)}"

#  Pobieranie modelu AI
def process_image_with_model(image_path):
    """Analizuje obraz i zwraca liczbę wykrytych osób."""
    model_path = 'C:/Users/pauli/Desktop/Zaawansowane_programowanie1/Projekt/models/frozen_inference_graph.pb'
    config_path = 'C:/Users/pauli/Desktop/Zaawansowane_programowanie1/Projekt/models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt'

    if not os.path.exists(model_path) or not os.path.exists(config_path):
        return "Błąd: Model nie został znaleziony"

    cvNet = cv.dnn.readNetFromTensorflow(model_path, config_path)
    image_path, error = convert_to_jpeg(image_path)
    if error:
        return error

    img = cv.imread(image_path)
    if img is None:
        return "Błąd: Nie można wczytać obrazu"

    cvNet.setInput(cv.dnn.blobFromImage(img, size=(300, 300), swapRB=True, crop=False))
    cvOut = cvNet.forward()

    detected_people = sum(1 for detection in cvOut[0, 0, :, :] if float(detection[2]) > 0.3 and int(detection[1]) == 1)

    return detected_people

# Przetwarzanie zadania w RabbitMQ
def process_image(ch, method, properties, body):
    """Przetwarza zadanie i wykonuje analizę obrazu."""
    try:
        task = json.loads(body)
        task_id = task['task_id']
        image_source = task['image_source']

        print(f"🔄 Przetwarzanie zadania {task_id}")

        detected_people = process_image_with_model(image_source)
        task_status[task_id] = {"status": "completed", "result": detected_people}

        print(f"✅ Zadanie {task_id} zakończone: {detected_people} osób.")
        del task_status[task_id]  # Usuwamy po zakończeniu, aby nie zaśmiecać pamięci

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        task_status[task_id] = {"status": "failed", "result": str(e)}
        print(f"❌ Błąd w zadaniu {task_id}: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

@app.route('/upload', methods=['POST'])
def upload_image():
    """Dodaje zdjęcie do kolejki RabbitMQ 1000 razy."""
    if 'image' not in request.files:
        return jsonify({"error": "Brak pliku w żądaniu."}), 400

    image = request.files['image']
    image_uuid = str(uuid.uuid4())
    image_path = f"uploads/{image_uuid}.jpg"
    os.makedirs('uploads', exist_ok=True)
    image.save(image_path)

    _, channel = get_rabbitmq_channel()

    for _ in range(1000):
        task_id = str(uuid.uuid4())
        task_status[task_id] = {"status": "pending", "result": None}
        task = {"task_id": task_id, "image_source": image_path}
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=json.dumps(task))

    channel.close()

    return jsonify({"message": "Zadanie zakolejkowane 1000 razy"}), 202

#  Endpoint do analizy zdjęcia z URL (GET)
@app.route('/analyze', methods=['GET'])
def analyze_image():
    """Dodaje zadanie analizy obrazu z URL do kolejki RabbitMQ 1000 razy."""
    image_url = request.args.get('url')
    if not image_url:
        return jsonify({"error": "Brak URL w żądaniu."}), 400

    _, channel = get_rabbitmq_channel()

    for _ in range(1000):
        task_id = str(uuid.uuid4())
        task_status[task_id] = {"status": "pending", "result": None}
        task = {"task_id": task_id, "image_source": image_url}
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=json.dumps(task))

    channel.close()

    return jsonify({"message": "Zadanie zakolejkowane 1000 razy"}), 202

#  Endpoint do analizy lokalnego zdjęcia
@app.route('/local-analyze', methods=['GET'])
def local_analyze():
    """Dodaje zadanie analizy lokalnego zdjęcia do kolejki RabbitMQ 1000 razy."""
    image_path = request.args.get('path')

    if not image_path or not os.path.exists(image_path):
        return jsonify({"error": "Nie znaleziono pliku"}), 400  #  JSON zamiast HTML!

    _, channel = get_rabbitmq_channel()

    for _ in range(1000):  #  Każde zadanie dostaje unikalne ID
        task_id = str(uuid.uuid4())
        task_status[task_id] = {"status": "pending", "result": None}
        task = {"task_id": task_id, "image_source": image_path}
        channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=json.dumps(task))

    channel.close()

    return jsonify({"message": "Zadanie zakolejkowane 1000 razy"}), 202


#  Uruchamianie konsumentów RabbitMQ
def start_consumer():
    """Uruchamia konsumenta RabbitMQ do przetwarzania zadań."""
    while True:
        try:
            connection, channel = get_rabbitmq_channel()
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_image)
            print("🟢 Konsument uruchomiony i oczekuje na zadania...")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print("🔴 Utracono połączenie z RabbitMQ. Ponowne łączenie...")
            continue

if __name__ == '__main__':
    for _ in range(10):  
        threading.Thread(target=start_consumer, daemon=True).start()

    print("🚀 Serwer działa na http://127.0.0.1:5000")
    app.run(debug=True)