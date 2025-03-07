from flask import Flask
from app.views import views
from datetime import timedelta

# Create the Flask app
app = Flask(__name__, static_folder='app/static',
            template_folder='app/templates')
app.secret_key = "WMGInvent"
app.permanent_session_lifetime = timedelta(days=0.5)
app.register_blueprint(views, url_prefix='')


if __name__ == '__main__':
    app.run(debug=True)
