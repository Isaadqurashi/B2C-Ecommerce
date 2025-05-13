# main.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# Flask-Uploads & SQLAlchemy config
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'jpg','jpeg','png','gif'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:pgadmin4@localhost:5432/ecomproject'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Firebase backup config
app.config['FIREBASE_SERVICE_ACCOUNT'] = 'serviceAccountKey.json'
app.config['FIREBASE_BUCKET']          = 'kuchu-muchu.appspot.com'

db = SQLAlchemy(app)

# register your backup CLI command
from backup import backup_db_command
app.cli.add_command(backup_db_command)

# import your views
from views import *
from admin import *

if __name__ == '__main__':
    app.run(debug=True)
