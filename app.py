from flask import Flask, jsonify, send_file
import os
import subprocess
from swiftclient.client import Connection
import tempfile

app = Flask(__name__)

# Configuration Swift
swift_conn = Connection(
    authurl='http://10.20.22.18:5000',
    user='7035f6f73248406aab2d7ab392c9736a',
    key='AZYszujA_A$a*&amp;djz',
    auth_version='3',
    os_options={
        'region_name': 'RegionZZ'
    }
)

@app.route('/image/<image_id>', methods=['POST'])
def generate_image(image_id):
    # Génération de l'image avec POV-Ray
    try:
        subprocess.run(['povray', f'scene{image_id}.pov'], check=True)
        
        # Upload vers Swift
        with open(f'scene{image_id}.png', 'rb') as img:
            swift_conn.put_object('renders', f'image_{image_id}.png', img)
            
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/image/<image_id>', methods=['GET'])
def get_image(image_id):
    try:
        # Téléchargement depuis Swift
        _, obj = swift_conn.get_object('renders', f'image_{image_id}.png')
        
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(obj)
            return send_file(tmp.name, mimetype='image/png')
    except:
        return jsonify({'error': 'Image not found'}), 404

@app.route('/video', methods=['POST'])
def generate_video():
    try:
        # Vérification que toutes les images sont présentes
        _, objects = swift_conn.get_container('renders')
        if len(objects) < expected_image_count:
            return jsonify({'error': 'Not all images generated yet'}), 400
            
        # Génération du GIF
        subprocess.run(['convert', 'scene*.png', 'animation.gif'], check=True)
        
        # Upload vers Swift
        with open('animation.gif', 'rb') as gif:
            swift_conn.put_object('renders', 'animation.gif', gif)
            
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/video', methods=['GET'])
def get_video():
    try:
        # Téléchargement depuis Swift
        _, obj = swift_conn.get_object('renders', 'animation.gif')
        
        with tempfile.NamedTemporaryFile() as tmp:
            tmp.write(obj)
            return send_file(tmp.name, mimetype='image/gif')
    except:
        return jsonify({'error': 'Video not found'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)