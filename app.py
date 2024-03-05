from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from bing_image_downloader import downloader
import pandas as pd
import os
import shutil

app = Flask(__name__)
CORS(app)

# Ruta de la carpeta de descargas
DOWNLOADS_FOLDER = "downloads"

@app.route('/buscar_imagenes', methods=['POST'])
def buscar_imagenes():
    try:
        # Obtener el archivo Excel y el nombre de la columna del formulario
        archivo_excel = request.files['archivo_excel']
        nombre_columna = request.form['nombre_columna']

        # Guardar el archivo Excel temporalmente
        archivo_excel.save(archivo_excel.filename)

        # Leer el archivo Excel y obtener la lista de nombres de modelos
        df = pd.read_excel(archivo_excel.filename)
        nombres_modelos = df[nombre_columna].tolist()

        # Eliminar el archivo Excel temporal
        os.remove(archivo_excel.filename)

        # Definir la carpeta base de destino para guardar las imágenes descargadas
        base_output_folder = "downloads"
        images_downloaded = 0  # Inicializar la variable fuera del bucle

        for nombre in nombres_modelos:
            # Eliminar espacios en blanco adicionales al principio y al final del nombre del modelo
            nombre = nombre.strip()

            # Definir la carpeta de destino para guardar las imágenes de este modelo
            output_folder = os.path.join(base_output_folder, nombre)
            images_downloaded = 0  # Reiniciar el contador para cada modelo

            # Descargar las imágenes con Bing Image Downloader
            while images_downloaded < 3:
                try:
                    downloader.download(nombre, limit=3 - images_downloaded, output_dir=output_folder, adult_filter_off=True, force_replace=False)
                    images_downloaded += 3 - images_downloaded
                    print(f"Se descargaron imágenes para '{nombre}' en la carpeta '{output_folder}'.")
                except Exception as e:
                    print(f"No se pudieron descargar imágenes para '{nombre}': {str(e)}")
                    break  # Salir del bucle en caso de error

        return jsonify({'message': 'Imágenes listas para descargar.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/descargar_zip')
def descargar_zip():
    try:

        # Comprimir el contenido de la carpeta downloads en un archivo ZIP
        shutil.make_archive(DOWNLOADS_FOLDER, 'zip', DOWNLOADS_FOLDER)
        
        return send_file('downloads.zip', as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/verificar_zip')
def verificar_zip():
    try:
        zip_file_path = os.path.join(DOWNLOADS_FOLDER, 'downloads.zip')
        if os.path.exists(zip_file_path):
            return jsonify({'message': 'El archivo ZIP existe.'}), 200
        else:
            return jsonify({'message': 'El archivo ZIP no existe.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/eliminar_zip')
def eliminar_zip():
    try:
        zip_file_path = os.path.join(os.getcwd(), 'downloads.zip')
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)
            return jsonify({'message': 'El archivo ZIP fue eliminado correctamente.'}), 200
        else:
            return jsonify({'error': 'El archivo ZIP no existe.'}), 404
    except Exception as e:
        print(f"Error al eliminar el archivo ZIP: {e}")
        return jsonify({'error': str(e)}), 500
@app.route('/limpiar_downloads', methods=['GET'])
def limpiar_downloads():
    try:
        limpiar_downloads()
        return jsonify({'message': 'Contenido de la carpeta "downloads" eliminado correctamente.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
def limpiar_downloads():
    try:
        # Borrar el contenido de la carpeta downloads
        for filename in os.listdir(DOWNLOADS_FOLDER):
            file_path = os.path.join(DOWNLOADS_FOLDER, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"No se pudo eliminar {file_path}: {e}")
    except Exception as e:
        print(f"Error al limpiar la carpeta downloads: {e}")

if __name__ == '__main__':
    app.run(debug=True)
