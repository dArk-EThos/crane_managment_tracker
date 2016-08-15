from flask_sqlalchemy import SQLAlchemy
import os

from flask import Flask
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/scottdb'
db = SQLAlchemy(app)