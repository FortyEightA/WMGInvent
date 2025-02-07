from flask import Flask
from app import templates, static
from app.views import views

app = Flask(__name__)
app.register_blueprint(views, url_prefix='')

if __name__ == '__main__':
    app.run(debug=True)
