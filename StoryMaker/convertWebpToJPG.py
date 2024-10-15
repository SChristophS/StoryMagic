from PIL import Image
import os

# Verzeichnis mit den .webp-Dateien
input_directory = r"path_to_webp_files"  # Verwende das r vor dem Pfad
# Verzeichnis für die .jpg-Dateien
output_directory = r"path_to_output_files"  # Verwende auch hier das r

# Stelle sicher, dass das Ausgabeverzeichnis existiert
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Durchlaufe alle Dateien im Eingangsverzeichnis
for filename in os.listdir(input_directory):
    if filename.endswith(".webp"):
        webp_path = os.path.join(input_directory, filename)
        # Öffne das .webp-Bild
        with Image.open(webp_path) as img:
            # Entferne die Dateiendung für den neuen Namen
            jpg_filename = os.path.splitext(filename)[0] + ".jpg"
            jpg_path = os.path.join(output_directory, jpg_filename)
            # Speichere das Bild als .jpg
            img = img.convert("RGB")  # Konvertiere das Bild in RGB
            img.save(jpg_path, "JPEG")

print("Konvertierung abgeschlossen!")
