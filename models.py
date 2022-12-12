import datetime

import jwt

from app import db, bcrypt
from config import BaseConfig


class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)

    materias = db.relationship('Materia', backref='user')
    examenes = db.relationship('Examen', backref='user')

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, BaseConfig.BCRYPT_LOG_ROUNDS
        ).decode()

        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def encode_auth_token(self, user_id):
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                BaseConfig.SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        try:
            payload = jwt.decode(auth_token, BaseConfig.SECRET_KEY, algorithms=['HS256'])
            return payload['sub']
        except jwt.ExpiredSignatureError as e:
            print(e)
            return 'Inicio expirado. Por favor inicie sesión de nuevo.'
        except jwt.InvalidTokenError as e:
            print(e)
            return 'Token invalido. Por favor inicie sesión de nuevo.'

    def __str__(self):
        return f'ID: {self.id}, email: {self.email}, Admin: {self.admin}'


class Materia(db.Model):
    __tablename__ = "materia"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), unique=True, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    salon = db.Column(db.String(255), nullable=False)
    examenes = db.relationship('Examen', backref='materia')

    def __str__(self):
        return f'ID: {self.id}, Nombre: {self.nombre}, Salón:{self.salon}'


class Examen(db.Model):
    __tablename__ = "examen"
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    materia_id = db.Column(db.Integer, db.ForeignKey('materia.id'))
    fecha = db.Column(db.DateTime)
    status = db.Column(db.String(250))

    def __str__(self):
        return f'ID: {self.id}, Usuario: {self.usuario_id}, Materia:{self.materia_id}, Fecha: {self.fecha}, Status: {self.status} '
