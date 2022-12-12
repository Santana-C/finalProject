from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_migrate import Migrate

from config import BaseConfig
from database import db
from encriptador import bcrypt
from routes.examen.examen import appexamenes
from routes.materia.materia import appmateria
from routes.user.user import appuser

app = Flask(__name__)

app.register_blueprint(appuser)
app.register_blueprint(appexamenes)
app.register_blueprint(appmateria)


app.config.from_object(BaseConfig)

db.init_app(app)

CORS(app)

bcrypt.init_app(app)
migrate = Migrate()
migrate.init_app(app, db)


@app.route('/')
def inicio():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def iniciar_sesion():
    return render_template('login.html')


def pagina_no_encontrada(error):
    return render_template('404.html')


app.register_error_handler(404, pagina_no_encontrada)


def peticion_incorrecta(error):
    return render_template('400.html')


app.register_error_handler(400, peticion_incorrecta)
