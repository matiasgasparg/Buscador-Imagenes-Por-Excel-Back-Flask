from bing_image_downloader import downloader
import pandas as pd
import os

# Leer el archivo Excel y obtener la lista de nombres de modelos
archivo_excel = 'ventas.xlsx'
df = pd.read_excel(archivo_excel)
nombres_modelos = df['MODELO'].tolist()

# Definir la carpeta base de destino para guardar las imágenes descargadas
base_output_folder = "downloads"

for nombre in nombres_modelos:
    # Eliminar espacios en blanco adicionales al principio y al final del nombre del modelo
    nombre = nombre.strip()

    # Definir la carpeta de destino para guardar las imágenes de este modelo
    output_folder = os.path.join(base_output_folder, nombre)

    # Inicializar el contador de imágenes descargadas
    images_downloaded = 0

    # Descargar las imágenes con Bing Image Downloader
    while images_downloaded < 3:
        try:
            downloader.download(nombre, limit=3 - images_downloaded, output_dir=output_folder, adult_filter_off=True, force_replace=False)
            images_downloaded += 3 - images_downloaded
            print(f"Se descargaron imágenes para '{nombre}' en la carpeta '{output_folder}'.")
        except Exception as e:
            print(f"No se pudieron descargar imágenes para '{nombre}': {str(e)}")
            break  # Salir del bucle en caso de error
