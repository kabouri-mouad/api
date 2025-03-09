from flask import Flask, request, jsonify, send_file, abort
import subprocess
import os
import boto3
from PIL import Image

app = Flask(__name__)

# Configuration du stockage objet (OpenStack Swift ou S3)
storage_client = boto3.client(
    's3',
    endpoint_url='https://10.20.22.18:8080/',
    aws_access_key_id='votre-access-key',
    aws_secret_access_key='votre-secret-key',
    config=Config(signature_version='s3v4'),
    region='RegionZZ'
)
BUCKET_NAME = 'mon-conteneur'

@app.route('/generate-image/<int:image_id>', methods=['POST'])
def generate_image(image_id):
    # Générer l'image avec PovRay
    povray_command = f"povray +Iscene_{image_id}.pov +Oimage_{image_id}.png"
    subprocess.run(povray_command, shell=True, check=True)

    # Uploader l'image sur le stockage objet
    image_path = f"image_{image_id}.png"
    storage_client.upload_file(image_path, BUCKET_NAME, image_path)

    return jsonify({"message": f"Image {image_id} générée et uploadée."}), 200

@app.route('/get-image/<int:image_id>', methods=['GET'])
def get_image(image_id):
    image_path = f"image_{image_id}.png"
    try:
        storage_client.download_file(BUCKET_NAME, image_path, image_path)
        return send_file(image_path, mimetype='image/png')
    except Exception as e:
        abort(404, description="Image non trouvée.")

@app.route('/generate-gif', methods=['POST'])
def generate_gif():
    # Vérifier si toutes les images sont disponibles
    images = []
    for image_id in range(1, 11):  # Supposons 10 images
        image_path = f"image_{image_id}.png"
        try:
            storage_client.download_file(BUCKET_NAME, image_path, image_path)
            images.append(Image.open(image_path))
        except:
            abort(400, description=f"Image {image_id} manquante.")

    # Créer la vidéo GIF
    gif_path = "animation.gif"
    images[0].save(gif_path, save_all=True, append_images=images[1:], loop=0, duration=500)

    # Uploader la vidéo sur le stockage objet
    storage_client.upload_file(gif_path, BUCKET_NAME, gif_path)

    return jsonify({"message": "GIF généré et uploadé."}), 200

@app.route('/get-gif', methods=['GET'])
def get_gif():
    gif_path = "animation.gif"
    try:
        storage_client.download_file(BUCKET_NAME, gif_path, gif_path)
        return send_file(gif_path, mimetype='image/gif')
    except Exception as e:
        abort(404, description="GIF non trouvé.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)