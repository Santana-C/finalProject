from flask import Blueprint, request, jsonify, render_template, url_for, redirect
from sqlalchemy import exc
from models import Materia
from app import db, bcrypt
from auth import tokenCheck, obtenerInfo
from models import Usuario
from models import Examen
from flask_login import login_required
from json2excel import Json2Excel

appexamenes = Blueprint('appexamenes', __name__, template_folder="templates")


@appexamenes.route('/examen/registrar')
def formulario_registrar():
    token = request.args.get('token')
    usuario = obtenerInfo(token)
    info_user = usuario['data']
    output = []
    mensaje = ''
    materias = Materia.query.filter_by(usuario_id=info_user['user_id'])
    if materias is not None:
        for materia in materias:
            materiaData = {}
            materiaData['nombre'] = materia.nombre
            output.append(materiaData)
    else:
        mensaje = 'El usuario no tiene materias'
        return render_template('AgendarExamen.html', token=token, mensaje=mensaje)
    return render_template('AgendarExamen.html', token=token, mensaje=mensaje, json=output)


@appexamenes.route('/examen/registro', methods=['POST'])
def registro():
    token = request.form['token']
    nombreMateria = request.form['nombre']
    json = request.form['json']
    fecha = request.form['date']
    hora = request.form['time']
    listaHorarios = ['19:00', '18:00', '17:00', '16:00', '15:00', '14:00', '13:00', '12:00', '11:00', '10:00', '09:00']
    if hora not in listaHorarios:
        mensaje = "Horario no disponible"
        return render_template('AgendarExamen.html', token=token, mensaje=mensaje, json=json)

    fechaExamen = fecha + ' ' + hora
    if nombreMateria == '':
        mensaje = "Datos invalidos"
        return render_template('AgendarExamen.html', token=token, mensaje=mensaje, json=json)

    usuario = obtenerInfo(token)
    info_user = usuario['data']
    idUsuario = info_user['user_id']
    IdMateriadb = db.engine.execute('select id from public.materia where usuario_id = ' +
                                    str(idUsuario) + ' and nombre = \'' + nombreMateria + '\';').first()
    searchDate = Examen.query.filter_by(fecha=fechaExamen).first()
    if searchDate:
        mensaje = "Horario no disponible"
        return render_template('AgendarExamen.html', token=token, mensaje=mensaje, json=json)

    if IdMateriadb is not None:
        materiaId = IdMateriadb[0]
        examen = Examen(usuario_id=idUsuario, fecha=fechaExamen, status='Agendado', materia_id=materiaId)
        try:
            db.session.add(examen)
            db.session.commit()
            mensaje = "Examen agendado"
        except exc.SQLAlchemyError as e:
            mensaje = "Error"
    else:
        mensaje = "Datos Incompletos"
    return render_template('AgendarExamen.html', token=token, mensaje=mensaje, json=json)


@appexamenes.route('/examenes')
def getExamenes():
    token = request.args.get('token')
    usuario = obtenerInfo(token)
    info_user = usuario['data']
    output = []
    if info_user['admin']:
        examenes = Examen.query.all()
        for examen in examenes:
            examenData = {}
            examenData['id'] = examen.id
            examenData['fecha'] = examen.fecha
            examenData['status'] = examen.status
            usuario = db.engine.execute(
                'select email from public."usuario" where id = ' + str(examen.usuario_id) + ';').first()
            print('select email from public."usuario" where id = ' + str(examen.usuario_id) + ';')
            examenData['usuario'] = usuario[0]
            materiaName = db.engine.execute(
                'select nombre from public."materia" where id = ' + str(examen.materia_id) + ';').first()
            examenData['materia'] = materiaName[0]
            output.append(examenData)
    else:
        output.append('El usuario no es administrador')
    return render_template('ListExamenes.html', examenes=output, token=token)


@appexamenes.route('/examenes-excel')
def GenerarExcel():
    token = request.args.get('token')
    usuario = obtenerInfo(token)
    info_user = usuario['data']
    output = []
    if info_user['admin']:
        examenes = Examen.query.all()
        for examen in examenes:
            examenData = {}
            examenData['id'] = examen.id
            examenData['id_usuario'] = examen.usuario_id
            examenData['fecha'] = examen.fecha
            examenData['status'] = examen.status
            usuario = db.engine.execute('select email from public.usuario where id = '+str(examen.usuario_id) + ';').first()
            examenData['usuario'] = usuario[0]
            materiaName = db.engine.execute(
                'select nombre from public.materia where id = ' + str(examen.materia_id) + ';').first()
            examenData['nombre_materia'] = materiaName[0]
            output.append(examenData)
        json2excel = Json2Excel(head_name_cols=["id", "nombre_materia", "usuario", "id_usuario", "fecha", "status"])
        ruta = json2excel.run(output)
    else:
        output.append('El usuario no es administrador')
    return render_template('GeneracionExcel.html', ruta=ruta, token=token)


@appexamenes.route('/examen-user')
def getMateriaUsuario():
    token = request.args.get('token')
    usuario = obtenerInfo(token)
    info_user = usuario['data']
    examenes = Examen.query.filter_by(usuario_id=info_user['user_id'])
    output = []
    if examenes is not None:
        for examen in examenes:
            examenData = {}
            examenData['id'] = examen.id
            examenData['id_usuario'] = examen.usuario_id
            examenData['fecha'] = examen.fecha
            examenData['status'] = examen.status
            materiaName = db.engine.execute(
                'select nombre from public."materia" where id = ' + str(examen.materia_id) + ';').first()
            examenData['nombre_materia'] = materiaName[0]
            output.append(examenData)
    else:
        output.append('El usuario no tiene exámenes para ninguna de sus materias')
    return render_template('ListUsuarioExamenes.html', examenes=output, token=token)