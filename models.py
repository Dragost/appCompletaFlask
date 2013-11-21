#!/usr/bin/env python
# -*-coding: utf-8 -*-


from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
from werkzeug import generate_password_hash, check_password_hash
from sqlalchemy import Boolean, Column, String, DateTime, Integer, String, Text, ForeignKey
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship

Base=declarative_base()

class User(Base):
    __tablename__ = 'users'
    uid = Column(Integer, primary_key = True)
    firstname =Column(String(100))
    lastname = Column(String(100))
    email = Column(String(120), unique=True)
    pwdhash =Column(String(200))
   
    def __init__(self, firstname, lastname, email, password):
        self.firstname = firstname.title()
        self.lastname = lastname.title()
        self.email = email.lower()
        self.set_password(password)
     
    def set_password(self, password):
        self.pwdhash = generate_password_hash(password)#El password ya va cifrado.
   
    def check_password(self, password):
        return check_password_hash(self.pwdhash, password)
    
    def __str__(self):
        return "%s %s (%s)" %(self.firstname, self.lastname, self.email)

class Cita(Base):
    """Una cita en el calendario."""
    __tablename__ = 'citas'
 
    id = Column(Integer, primary_key=True)
    creada = Column(DateTime, default=datetime.now)
    modificada = Column(DateTime, default=datetime.now,
                      onupdate=datetime.now)
    evento = Column(String(255))
    inicio = Column(DateTime, nullable=False)
    fin = Column(DateTime, nullable=False)
    todoeldia = Column(Boolean, default=False)
    lugar = Column(String(255))
    descripcion = Column(Text)
    user_id = Column(Integer, ForeignKey('users.uid'), nullable=False)
    usuario = relationship(User, lazy='joined', join_depth=1, viewonly=True)
    
    def duracion(self):
        tiempo = self.fin - self.inicio
        return tiempo.seconds / 60
 
    def __str__(self):
        return "{evento} [{fecha}}".format(evento=self.evento,
            fecha=self.fecha)#o .inicio
        
if __name__ == '__main__':
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('mysql://flasky:flasky123@localhost/contactosflask', echo=True)

   	# Crea tablas si no existen
    Base.metadata.create_all(engine)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    usuario=User('Pepe', 'Ramos', 'pepe@1.org', 'secret')
    session.add(usuario)
    session.commit()
    
    ahora=datetime.now()
    
    cita1 =Cita(user_id=usuario.uid, evento='Conferencia', inicio=ahora-timedelta(days=5),fin= ahora-timedelta(days=5), 
                todoeldia=False, lugar="Instituto")
    session.add(cita1)
    cita2 =Cita(user_id=usuario.uid, evento='Quedada', inicio=ahora+timedelta(days=1),fin= ahora+timedelta(days=5), 
                todoeldia=False, lugar="En el bar")
    session.add(cita2)
    session.commit()
    