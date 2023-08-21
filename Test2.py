import os


generator_script_path = "/home/pi/patientenakte/patienten_datagenerator.py"

# Extrahiere den Skriptnamen ohne Pfad und Erweiterung
script_name = os.path.basename(generator_script_path)
script_name_without_extension = os.path.splitext(script_name)[0]

print(script_name)