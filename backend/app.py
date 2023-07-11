from flask import Flask, jsonify, request
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins='http://localhost:3000', supports_credentials=True, allow_headers=[
    'Content-Type', 'Authorization'], methods=['GET', 'POST', 'PUT', 'DELETE'])


@app.route('/feed', methods=['POST'])
def get_images():
    try:
        response = requests.get('https://api.data.gov.sg/v1/transport/traffic-images')
        data = response.json()
        print(data)
        cameras = data['items'][0]['cameras']

        images = []
        for index, camera in enumerate(cameras):
            camera_id = camera['camera_id']
            image_url = camera['image']
            image = {'camera_id': camera_id, 'image': image_url}
            images.append(image)

        return jsonify({'images': images})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


    

if __name__ == '__main__':
    app.run(debug=True)
