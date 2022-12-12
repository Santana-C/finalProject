from flask import Blueprint, request,jsonify, render_template, url_for, redirect
from sqlalchemy import exc
from models import Usuario
from app import db,bcrypt
from auth import tokenCheck, obtenerInfo

appuser = Blueprint('appsuer', __name__, template_folder="templates")


# Vista de registrar usuarios
@appuser.route('/auth/registro')
def registro_view():
    return render_template('registro.html')


# Registra un nuevo usuario normal
@appuser.route('/auth/registro', methods =['POST'])
def registro():
    nombreUser = request.form['email']
    userPass = request.form['password']
    searchUser = Usuario.query.filter_by(email=nombreUser).first()
    if searchUser:
        mensaje = "Usuario existente"
    else:
        usuario = Usuario(email=nombreUser, password=userPass)
        try:
            db.session.add(usuario)
            db.session.commit()
            mensaje = "Usuario creado"
        except exc.SQLAlchemyError as e:
            mensaje = "Error"
    return render_template('msjLogin.html', mensaje=mensaje)


# vista de login
@appuser.route('/auth/login')
def login_view():
    return render_template('login.html')


# muestra el listado correspondiente para el usuario
# si es admin, el listado completo
# si es normal solo el de sus mascotas
@appuser.route('/auth/login', methods=['POST'])
def login():
    nombreUser = request.form['email']
    userPass = request.form['password']
    searchUser = Usuario.query.filter_by(email=nombreUser).first()
    if searchUser:
        validation = bcrypt.check_password_hash(searchUser.password,userPass)
        if validation:
            auth_token = searchUser.encode_auth_token(user_id=searchUser.id)
            print(auth_token)
            if searchUser.admin:
                print("El usuario es admin")
                return redirect(url_for('appsuer.func_admin_view', auth_token=auth_token))
            else:
                print("El usuario NO es admin")
                return redirect(url_for('appsuer.func_user_view', auth_token=auth_token))
    return render_template('401.html')


# vista de las funciones del usuario
@appuser.route('/funcionesUsuario')
def func_user_view():
    token = request.args['auth_token']
    return render_template('funcionesUsuario.html', token=token)


# vista de las funciones del admin
@appuser.route('/funcionesAdmin')
def func_admin_view():
    token = request.args['auth_token']
    print("recibiendo token para mandorlo al html")
    print(token)
    return render_template('funcionesAdmin.html', token=token)


# Muestra todos los usuarios si recibe un token de usuario admin
@appuser.route('/usuarios') #get
def obtenerUsuarios():
    token = request.args.get('token')
    usuario = obtenerInfo(token)
    info_user = usuario['data']
    if info_user['admin']:
        output = []
        usuarios = Usuario.query.all()
        for usuario in usuarios:
            usuarioData = {}
            usuarioData['id'] = usuario.id
            usuarioData['email'] = usuario.email
            usuarioData['password'] = usuario.password
            usuarioData['registered_on'] = usuario.registered_on
            usuarioData['admin'] = usuario.admin
            output.append(usuarioData)
    return render_template('ListUsuarios.html', usuarios = output, token = token)