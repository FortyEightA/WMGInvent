from flask import Flask
from app.views import views

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = "WMGInvent"
app.register_blueprint(views, url_prefix='')

if __name__ == '__main__':
    app.run(debug=True)
