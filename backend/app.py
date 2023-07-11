from flask import Flask, jsonify, request
import requests
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
scheduler = BackgroundScheduler()

@app.route('/camera-feed', methods=['POST'])
def get_images():
    try:
        # Fetch the updated feed
        response = requests.get('https://api.data.gov.sg/v1/transport/traffic-images')
        data = response.json()
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
    
@app.route('/camera/<camera_id>')
def get_camera(camera_id):
    try:
        response = requests.get('https://api.data.gov.sg/v1/transport/traffic-images')
        data = response.json()
        cameras = data['items'][0]['cameras']
        
        camera_info = next((camera for camera in cameras if camera['camera_id'] == camera_id), None)
        
        if camera_info:
            return jsonify({'camera': camera_info})
        else:
            return jsonify({'error': f'Camera ID {camera_id} not found.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def update_feed():
    with app.app_context():
        get_images()

if __name__ == '__main__':
    scheduler.add_job(update_feed, 'interval', seconds=20)
    scheduler.start()

    app.run(debug=True)
