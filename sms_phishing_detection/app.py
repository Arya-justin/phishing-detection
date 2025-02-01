from flask import Flask, render_template, request, jsonify
import re
from twilio.rest import Client
from flask_socketio import SocketIO, emit

app = Flask(__name__,template_folder='templates')
socketio = SocketIO(app)

# Twilio credentials (use your own credentials here)
account_sid = 'your_account_sid'
auth_token = 'your_auth_token'
twilio_phone_number = 'your_twilio_phone_number'

# India-specific phishing keywords (add more as needed)
india_phishing_keywords = [
    "जीतें", "फ्री", "लॉटरी", "ऑनलाइन", "बैंक", "ओटीपी", "कूपन", "पैसा", 
    "आधार", "सुरक्षित", "बैंक खाता", "विकसित", "धन", "राशि", "प्रीमियम", 
    "जवाब", "हैक", "पीएनआर", "स्मार्टफोन"
]

# Function to detect phishing URLs in a message
def is_phishing(url):
    for keyword in india_phishing_keywords:
        if keyword in url.lower():
            return True
    return False

# Function to process the SMS message
def process_sms(sms_text):
    urls_in_message = re.findall(r'(https?://[^\s]+)', sms_text)
    phishing_urls = []
    
    for url in urls_in_message:
        if is_phishing(url):
            phishing_urls.append(url)
    
    return phishing_urls

@app.route('/')
def home():
    return render_template('index.html')

# Twilio webhook to receive SMS messages
@app.route("/sms", methods=['POST'])
def sms_reply():
    sms_text = request.form['Body']
    from_number = request.form['From']

    phishing_urls = process_sms(sms_text)

    # Emit the result to the frontend (via WebSocket)
    socketio.emit('sms_received', {'from': from_number, 'sms_text': sms_text, 'phishing_urls': phishing_urls})

    return jsonify({"message": "success"}), 200

# SocketIO event to handle real-time updates on frontend
@socketio.on('connect')
def handle_connect():
    print("Client connected!")

if __name__ == '__main__':
    socketio.run(app, debug=True)
