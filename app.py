# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, flash, session, url_for, redirect, g, abort
from forms import ContactForm, SignupForm, SigninForm, ModificaForm, FormCita
from flask.ext.mail import Message, Mail
from functools import wraps
from models import Base, User, Cita
from flask.ext.sqlalchemy import SQLAlchemy
 

 
app = Flask(__name__)

app.secret_key = '\x84\xed\xca\xe36\x8d\x17\xd4\xb3X\xfd1\xdfJx\xc6\xe9\xcf\x00\xdf\x9e \xa9l'
 
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465
app.config["MAIL_USE_SSL"] = True
app.config["MAIL_USERNAME"] = 'dragost11@gmail.com'
app.config["MAIL_PASSWORD"] = '' #password

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://flasky:flasky123@127.0.0.1/contactosflask'

app.config["RECAPTCHA_PUBLIC_KEY"] = '6LeJmeoSAAAAAGAv9mSzRk-mKEE3I8i1LoqjClcA'
app.config["RECAPTCHA_PRIVATE_KEY"] = '6LeJmeoSAAAAAG38d7TBJqN5TPumnh80pVYwORL3'

#configuramos la app para mail 
mail = Mail()
mail.init_app(app)

# Configuración SQL Alchemy
db = SQLAlchemy(app)
db.Model = Base
    

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contacto', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
 
    if request.method == 'POST':
        if form.validate() == False:
            flash('Todos los campos son obligatorios')
            return render_template('contact.html', form=form)
        else:
            msg = Message(form.subject.data, sender='castilla.idoia@gmail.com', recipients=['castilla.idoia@gmail.com'])
            msg.body = """
              Mensaje de: %s <%s>
              %s
              """ % (form.name.data, form.email.data, form.message.data)
            #esta linea hay que comentarla en el instituto (puerto bloqueado)
            mail.send(msg)
            
            return render_template('contact.html', nombre=form.name.data, success=True)
    else:
        return render_template('contact.html', form=form)
    
@app.route('/alta', methods=['GET', 'POST'])
def signup():
    form = SignupForm(db=db)
    
    if 'email' in session:
        return redirect(url_for('perfil'))
   
    if request.method == 'POST':
        if form.validate(db) == False:
            return render_template('signup.html', form=form)
        else: 
            newuser = User(form.firstname.data, form.lastname.data, form.email.data, form.password.data)
            db.session.add(newuser)
            db.session.commit() 
            session['email'] = newuser.email
            return redirect(url_for('perfil'))
   
    elif request.method == 'GET':
        return render_template('signup.html', form=form)
         

    
@app.route('/perfil')
@login_required
def perfil():
    user = db.session.query(User).filter_by(email = session['email']).first()
    
    if user is None:
        return redirect(url_for('login'))
    else:
        return render_template('profile.html', user=user)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = SigninForm(db=db)
    if 'email' in session:
        return redirect(url_for('perfil'))
   
    if request.method == 'POST':
        if form.validate(db) == False:
            return render_template('signin.html', form=form)
        else:
            session['email'] = form.email.data
            user = db.session.query(User).filter_by(email = session['email']).first()
            session['uid']=user.uid #guardo el id en la sesion para luego usarlo en las relaciones BD
            return redirect(request.args.get("next") or url_for("perfil"))
    else:
        return render_template('signin.html', form=form) 
    
    
    
@app.route('/logout')
@login_required
def signout():
    session.pop('email', None)
    return redirect(url_for('home'))
    
@app.errorhandler(404)
def error_not_found(error):
    return render_template('error/not_found.html'), 404

@app.route('/modificar', methods=['GET', 'POST'])
@login_required
def modificar():
    form = ModificaForm()
    user = db.session.query(User).filter_by(email = session['email']).first()
   
    if request.method == 'POST':
        if form.validate() == False:
            return render_template('modifica.html', form=form)
        else: 
            user.firstname=form.firstname.data
            user.lastname= form.lastname.data
            user.set_password(form.password.data)
            db.session.commit() 
            return redirect(url_for('perfil'))
   
    elif request.method == 'GET':
        return render_template('modifica.html', form=form)
    
@app.route('/baja')
@login_required
def baja():
    user = db.session.query(User).filter_by(email = session['email']).first()
    return render_template('baja.html',user=user)

@app.route('/bajadefinitiva')

def baja_definitiva():
    user = db.session.query(User).filter_by(email = session['email']).first()
    
    #para eliminar citas si existen
    citas = (db.session.query(Cita).filter_by(user_id=session['uid']).all())
    for cita in citas:
        db.session.delete(cita)
        db.session.commit()
        
    db.session.delete(user)
    db.session.commit()
    session.pop('email', None)
    return redirect(url_for('home'))

@app.route('/lista_usuarios')
def lista_usuarios():
    usuarios = db.session.query(User).all()
    if 'email' in session:
        sesion = True
    else:
        sesion = False
        
    return render_template('usuarios.html',usuarios=usuarios, sesion = sesion)
    
   
@app.route('/testdb')
def testdb():
    if db.session.query("1").from_statement("SELECT 1").all():
        return 'It works.'
    else:
        return 'Something is broken.'

#CITAS

@app.route('/citas')
@login_required
def lista_citas():
    user = db.session.query(User).filter_by(email = session['email']).first()
    citas = db.session.query(Cita).filter_by(user_id = user.uid).order_by(Cita.inicio.asc()).all()
    return render_template('cita/index.html', citas = citas)



@app.route('/cita/crear/', methods=['GET', 'POST'])
@login_required
def crear_cita():
    """Muestra el formulario para crear una cita"""
    form = FormCita(request.form)
 
    if request.method == 'POST' and form.validate():
        cita = Cita(user_id=session['uid'])
        form.populate_obj(cita)
        db.session.add(cita)
        db.session.commit()
        # Exito: devuelve al usuario a la lista de citas
        return redirect(url_for('lista_citas'))
    # Error o GET.
    return render_template('cita/crear.html', form=form)
   
@app.route('/cita/<int:cita_id>/')
@login_required
def detalle_cita(cita_id):
    """Detalle de una cita dada."""
    # Query: obtiene el objeto por ID 
    cita = db.session.query(Cita).get(cita_id)
    if cita is None:
        abort(404)
    return render_template('cita/detalle.html', cita=cita)


@app.route('/cita/<int:cita_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_cita(cita_id):
    """Prepara el formulario HTML para editar una cita."""
    cita = db.session.query(Cita).filter_by(id=cita_id).first()
    if cita is None:
        abort(404)
    form = FormCita(request.form)
    if request.method == 'POST': 
        if  form.validate():
            return render_template('cita/editar.html', form=form, cita=cita )
        else:
            cita.evento=form.evento.data
            cita.inicio = form.inicio.data
            cita.fin = form.fin.data
            cita.todoeldia = form.todoeldia.data
            cita.lugar = form.lugar.data
            cita.descripcion = form.descripcion.data
            db.session.commit()
            # Si hay éxito, vuelve a la vista de detalle de la cita
            return redirect(url_for('detalle_cita', cita_id=cita.id))
    else:
        return render_template('cita/editar.html', form=form, cita=cita )

@app.route('/cita/<int:cita_id>/eliminar', methods=['GET', 'POST'])
@login_required
def eliminar_cita(cita_id):
    cita = db.session.query(Cita).filter_by(id = cita_id).first()
    db.session.delete(cita)
    db.session.commit()
    return redirect(url_for('lista_citas'))
    
    

    

if __name__ == '__main__':
    app.run(debug=True)
