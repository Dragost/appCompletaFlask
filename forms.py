# -*- coding: utf-8 -*- 

from wtforms import TextField, TextAreaField, SubmitField, validators, ValidationError, PasswordField, DateTimeField, BooleanField, DateField
from models import User, Base, Cita
from flask_wtf import Form, RecaptchaField
 
class ContactForm(Form):
    name = TextField("Nombre",  [validators.Required("Introduzca su nombre")])
    email = TextField("Email",  [validators.Required("Introduzca su email"), validators.Email("Introduzca un mail correcto")])
    subject = TextField("Asunto",  [validators.Required("Indique un asunto")])
    message = TextAreaField("Mensaje",  [validators.Required("Escríbanos su mensaje")])
    submit = SubmitField("Enviar")
    
class SignupForm(Form):
    firstname = TextField("Nombre",  [validators.Required("Introduzca su nombre")])
    lastname = TextField("Apellido",  [validators.Required("Introduzca su apellido.")])
    email = TextField("Email",  [validators.Required("Ingrese email."), validators.Email("Ingrese un mail correcto")])
    password = PasswordField('Contrasena', [validators.Required("Introduzca contrasena.")])
    submit = SubmitField("Crear cuenta")
    recaptcha = RecaptchaField()
 
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
    
 
    def validate(self,db):
        if not Form.validate(self):
            return False
        user = db.session.query(User).filter_by(email = self.email.data.lower()).first()
        #busca si el mail que se ha introducido ya existe en la base de datos
        if user:
            self.email.errors.append("El email ya existe.")#le añanade al mensaje de error otro.
            return False
        else:
            return True
        

class SigninForm(Form):
    email = TextField("Email",  [validators.Required("Por favor ingrese su email"), validators.Email("Por favor ingrese su email.")])
    password = PasswordField('Password', [validators.Required("Introduca la contraseña.")])
    submit = SubmitField("Login")
   
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
 
    def validate(self,db):
        if not Form.validate(self):
            return False
        user = db.session.query(User).filter_by(email = self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            self.email.errors.append("Usuario o contraseña no encontrados")
            return False
    
       

class ModificaForm(Form):
    
    firstname = TextField("Nombre",  [validators.Required("Introduzca su nombre")])
    lastname = TextField("Apellido",  [validators.Required("Introduzca su apellido.")])
    password = PasswordField('Contraseña', [validators.Required("Introduzca contraseña.")])
    submit = SubmitField("Modificar")
    
    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
    
    def validate(self):
        if not Form.validate(self):
            return False

class FormCita(Form):
    """Formulario para el modelo Citas. Genera HTML y valida entradas 
    """
    evento = TextField('Título', [validators.Length(max=255)])
    #fecha = DateField('Fecha',[validators.Required()], format='%d-%m-%Y')
    inicio = DateTimeField('Hora de inicio', [validators.Required()],format='%H:%M')
    fin = DateTimeField('Hora de finalización',[validators.Required()],format='%H:%M')
    todoeldia = BooleanField('Todo el día')
    lugar = TextField('Lugar', [validators.Length(max=255)])
    descripcion = TextAreaField('Descripción')
    submit = SubmitField("Enviar")
