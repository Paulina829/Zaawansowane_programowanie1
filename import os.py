import os

model_path = "C:/Users/pauli/Desktop/Zaawansowane_programowanie-1/Projekt/models/frozen_inference_graph.pb"

if os.path.exists(model_path):
    print("✅ Plik modelu istnieje!")
else:
    print("❌ Plik modelu NIE ISTNIEJE! Sprawdź ścieżkę.")