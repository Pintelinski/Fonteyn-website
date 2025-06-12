import connexion 
from flask import send_from_directory, Flask, render_template, request, redirect
import os 
from config import CONFIG 
import requests
from api import create_booking

# Create a Connexion app instance with the api
app = connexion.App(__name__, specification_dir='./')
app.add_api('hotel_api.yml')

# Define route for home page
@app.app.route('/')
def home():
    # Render the index.html template
    return render_template('index.html')

# Define route for rooms page
@app.app.route('/rooms')
def rooms():
    # Render the rooms.html template
    return render_template('rooms.html')

# Define route for login/register page
@app.app.route('/login')
def login_page():
    # Render the login.html template
    return render_template('login.html')

# Define route for checkout page
@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # Render the checkout.html template
    if request.method == 'POST':
        booking = create_booking()
        if booking[1] == 400:
            return redirect('/checkout')
        else:
            return redirect('/rooms')
    return render_template('checkout.html')

# Define route for curl request
@app.app.route('/curl/<path:url>', methods=['GET'])
def curl_request(url):
    try:
        response = requests.get(url)
        return {
            'status_code': response.status_code,
            'content': response.text,
            'headers': dict(response.headers)
        }
    except requests.exceptions.RequestException as e:
        return {
            'error': str(e)
        }, 400

# Main entry point of the application
if __name__ == '__main__':
    # Create static directory if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # Start the Flask application with configuration from CONFIG
    app.run(
        host=CONFIG['server']['listen_ip'],      # IP address to listen on
        port=int(CONFIG['server']['port']),      # Port number to use
        debug=CONFIG['server'].getboolean('debug')  # Debug mode setting
    )