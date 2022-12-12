from flask import Blueprint, request, jsonify, render_template, url_for, redirect
from sqlalchemy import exc
from models import Materia
from app import db, bcrypt
from auth import tokenCheck, obtenerInfo
from models import Usuario
from flask_login import login_required

appmateria = Blueprint('appmateria', __name__, template_folder="templates")


@appmateria.route('/materia/registrar')
def formulario_registrar():
    token = request.args.get('token')
    return render_template('AgregarMateria.html', token=token)


@appmateria.route('/materia/registro', methods=['POST'])
def registro():
    token = request.form['token']
    nombreMateria = request.form['nombre']
    salon = request.form['salon']
    usuario = obtenerInfo(token)
    info_user = usuario['data']

    if nombreMateria == '' or salon == '':
        mensaje = "Datos Incompletos"
        return render_template('AgregarMateria.html', token=token, mensaje=mensaje)
    if info_user:
        materia = Materia(nombre=nombreMateria, usuario_id=info_user['user_id'], salon=salon)
        try:
            db.session.add(materia)
            db.session.commit()
            mensaje = "Materia creada"
        except exc.SQLAlchemyError as e:
            mensaje = "Error"
    else:
        mensaje = "Datos Erróneos"
    return render_template('AgregarMateria.html', token=token, mensaje=mensaje)


@appmateria.route('/materias')
def getMaterias():
    token = request.args.get('token')
    usuario = obtenerInfo(token)
    info_user = usuario['data']
    output = []
    if info_user['admin']:
        materias = Materia.query.all()
        for materia in materias:
            materiaData = {}
            materiaData['id'] = materia.id
            materiaData['nombre'] = materia.nombre
            materiaData['id_usuario'] = materia.usuario_id
            materiaData['salon'] = materia.salon
            usuario = db.engine.execute('select email from public.usuario where id = ' + str(materia.usuario_id) + ';').first()
            materiaData['Usuario'] = usuario[0]
            output.append(materiaData)
    else:
        output.append('El usuario no es administrador')
    return render_template('ListMaterias.html', materias=output, token=token)


@appmateria.route('/materias-user')
def getMateriasUsuario():
    token = request.args.get('token')
    usuario = obtenerInfo(token)
    info_user = usuario['data']
    materias = Materia.query.filter_by(usuario_id=info_user['user_id'])
    email_user = db.engine.execute('select email from public.usuario where id = ' + str(info_user['user_id']) + ';').first()
    output = []
    if materias is not None:
        for materia in materias:
            materiaData = {}
            materiaData['id'] = materia.id
            materiaData['nombre'] = materia.nombre
            materiaData['email'] = email_user
            materiaData['salon'] = materia.salon
            output.append(materia)
    else:
        output.append('El usuario no tiene materias')
    return render_template('ListUsuarioMaterias.html', materias=output, token=token)
