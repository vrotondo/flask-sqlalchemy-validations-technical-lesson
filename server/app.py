from flask import Flask, make_response
from flask_migrate import Migrate

from models import db, EmailAddress

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return 'Validations Technical Lesson'

if __name__ == '__main__':
    app.run(port=5555, debug=True)