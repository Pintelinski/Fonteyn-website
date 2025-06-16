import connexion
import os
from config import CONFIG

app = connexion.FlaskApp(__name__, specification_dir='./')
    
app.add_api('hotel_api.yml', 
            base_path='/api',
            arguments={'title': 'Hotel Booking API'},
            options={"swagger_ui": True, "serve_spec": True})

"""app.run(
    host=CONFIG['api']['listen_ip'],
    port=int(CONFIG['api']['port']),
    debug=CONFIG['api'].getboolean('debug')
)
"""