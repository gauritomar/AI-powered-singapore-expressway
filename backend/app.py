from flask import Flask, jsonify, request
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask_cors import CORS
import redis
import json
from car_detection import CarDetection

r = redis.Redis(host='localhost', port=6379, db=0)
detector = CarDetection('cars.xml')

app = Flask(__name__)
CORS(app, origins='http://localhost:3000', supports_credentials=True, allow_headers=[
    'Content-Type', 'Authorization'], methods=['GET', 'POST', 'PUT', 'DELETE'])

def make_api_request_and_store_to_redis():
    try:
        response = requests.get('https://api.data.gov.sg/v1/transport/traffic-images')
        data = response.json()
        cameras = data['items'][0]['cameras']

        # Store each camera in Redis
        for camera in cameras:
            camera_id = camera['camera_id']
            json_data = json.dumps(camera)
            r.set(camera_id, json_data)

        print("Data stored in Redis successfully!")
    except Exception as e:
        print(f"Error occurred while making API request and storing to Redis: {str(e)}")

@app.route('/feed', methods=['POST'])
def get_images():
    try:
        camera_ids = r.keys("*")
        images = []
        for camera_id in camera_ids:
            stored_data = r.get(camera_id)
            if stored_data is not None:
                camera_data = json.loads(stored_data)
                image = {'camera_id': camera_data['camera_id'], 'image': camera_data['image']}
                images.append(image)

        return jsonify({'images': images})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/feed/<camera_id>', methods=['GET'])
def get_camera(camera_id):
    try:
        stored_data = r.get(camera_id)
        if stored_data is not None:
            camera_data = json.loads(stored_data)
            added_bounding_box = detector.detect_car(camera_data)
            print(added_bounding_box)
            return jsonify({'camera': added_bounding_box})
        

        return jsonify({'error': 'Camera data not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


    

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(make_api_request_and_store_to_redis, 'interval', seconds=20)
    scheduler.start()

    app.run(debug=True)
