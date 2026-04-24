import configparser
import re

# Crear el parser y leer el archivo .ini
config = configparser.ConfigParser()
config.read('twstft.ini')

patron = re.compile(r'^Lab [A-Z0-9]{1,5}$')

for seccion in config.sections():
    if patron.match(seccion):
        print(f"Procesando sección: {seccion}")
