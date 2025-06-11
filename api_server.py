import connexion
import os
from config import CONFIG

def create_app():
    # Create a Connexion app instance
    app = connexion.App(__name__, specification_dir='./')
    
    # Add the API using the OpenAPI specification
    app.add_api('hotel_api.yml', 
                base_path='/api',
                arguments={'title': 'Hotel Booking API'},
                options={"swagger_ui": True, "serve_spec": True})
    
    return app

if __name__ == '__main__':
    # Create the application
    app = create_app()
    
    # Start the server
    app.run(
        host=CONFIG['api']['listen_ip'],
        port=int(CONFIG['api']['port']),
        debug=CONFIG['api'].getboolean('debug')
    )