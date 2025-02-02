import cv2
import pytesseract
import os
from PIL import Image

#
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def convert_to_jpg(image_path):
    """Konwertuje obraz na format JPG, jeśli nie jest w tym formacie."""
    if not os.path.exists(image_path):
        print(f"❌ Plik {image_path} nie istnieje!")
        exit()

    file_ext = os.path.splitext(image_path)[1].lower()
    if file_ext not in ['.jpg', '.jpeg']:
        img = Image.open(image_path)
        new_path = image_path.rsplit(".", 1)[0] + ".jpg"
        img.convert("RGB").save(new_path, "JPEG")
        print(f"🔄 Przekonwertowano {image_path} → {new_path}")
        return new_path
    return image_path

def read_text_from_image(image_path):
    """Odczytuje tekst ze zdjęcia za pomocą OCR (Tesseract)."""
    image_path = convert_to_jpg(image_path)

    # Wczytanie obrazu
    image = cv2.imread(image_path)
    
    if image is None:
        print(f"❌ Błąd: Nie udało się wczytać obrazu {image_path}. Sprawdź ścieżkę!")
        exit()

    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    
    extracted_text = pytesseract.image_to_string(gray, lang="eng")  
    return extracted_text

if __name__ == "__main__":
    image_path = input("Podaj ścieżkę do obrazu: ").strip('"')  
    text = read_text_from_image(image_path)
    print("\n📜 Rozpoznany tekst:")
    print(text)
