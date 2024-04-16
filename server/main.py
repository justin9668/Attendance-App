from flask import Flask, send_file
from flask_cors import CORS
from io import BytesIO
import random
import requests

app = Flask(__name__)
cors = CORS(app, origins='*')

code = None

@app.route("/")
def home():
    return "Here"

@app.route("/api/code", methods=['GET'])
def code():
    global code
    code = random.randint(1000, 9999)
    return str(code)

@app.route("/api/qrcode", methods=['GET'])
def qrcode():
    global code
    if code is None:
        return "No code generated yet.", 400

    size = "200x200"
    api_url = f"https://api.qrserver.com/v1/create-qr-code/?data={code}&size={size}"
    response = requests.get(api_url)
    if response.status_code == 200:
        img = BytesIO(response.content)
        img.seek(0)
        code = None
        return send_file(img, mimetype='image/png', as_attachment=False, download_name=f"qr_{code}.png")
    else:
        return "Failed to generate QR Code."
    
if __name__ == "__main__": 
    app.run(debug=True, port=5000)