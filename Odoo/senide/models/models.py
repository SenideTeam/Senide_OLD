# -*- coding: utf-8 -*-

from odoo import models, fields, api


class usuario(models.Model):
    _name = 'senide.usuario'
    _description = 'Registro y gestión de los usuarios - de aqui sale los cuidadores y asociados.'

    name = fields.Char(string = 'DNI', required = True, size = 9, unique=True, index = True)
    nombre = fields.Char(string = 'Nombre', required = True)
    primer_apellido = fields.Char(string = 'Primer apellido', required = True)
    segundo_apellido = fields.Char(string = 'segundo apellido')
    nacimiento = fields.Date(String = 'Fecha de nacimientos', required = True )
    direccion = fields.Char(string = 'Dirección', required = True)
    pobalcion = fields.Char(string = 'Población', required = True)
    cp = fields.Char(string = 'Direccion', required = True, size = 5)
    movil = fields.Char(string = 'Direccion', required = True, size = 9)
    password = fields.Char(String = 'Contraseña') 

    dni_cuidador_ids = fields.Many2many('senide.cuidador')
    dni_asociado_ids = fields.Many2many('senide.asociado') 
    credecniales_id = fields.Many2one('senide.credenciales', string='Credenciales', inverse_name='usuario_id')  

class cuidador(models.Model):
    _name = 'senide.cuidador'
    _decription = 'Registro y gestión de los cuidadores'

    name = fields.Char(string = 'DNI', required = True, size = 9, unique=True, index = True)
    nombre = fields.Char(string = 'Nombre', required = True)
    primer_apellido = fields.Char(string = 'Primer apellido', required = True)
    segundo_apellido = fields.Char(string = 'segundo apellido')
    nacimiento = fields.Date(String = 'Fecha de nacimientos', required = True )
    direccion = fields.Char(string = 'Dirección', required = True)
    pobalcion = fields.Char(string = 'Población', required = True)
    cp = fields.Char(string = 'Direccion', required = True, size = 5)
    movil = fields.Char(string = 'Direccion', required = True, size = 9) 
    email = fields.Char(string = 'Nombre', required = True) 
    imagen = fields.Image(string = 'Imagen', required = True)
    primario = fields.Boolean(string = '¿Es cuidadore primario?', required = True)
    password = fields.Char(String = 'Contraseña')

    dni_usuario_ids = fields.Many2many('senide.usuario')
    credecniales_id = fields.Many2one('senide.credenciales', string='Credenciales', inverse_name='cuidador_id')

class asociado(models.Model):
    _name = 'senide.asociado'
    _decription = 'Registro y gestión de los cuidadores'

    name = fields.Char(string = 'DNI', required = True, size = 9, unique=True, index = True)
    nombre = fields.Char(string = 'Nombre', required = True)
    primer_apellido = fields.Char(string = 'Primer apellido', required = True)
    segundo_apellido = fields.Char(string = 'segundo apellido')
    nacimiento = fields.Date(String = 'Fecha de nacimientos', required = True )
    direccion = fields.Char(string = 'Dirección', required = True)
    pobalcion = fields.Char(string = 'Población', required = True)
    cp = fields.Char(string = 'Direccion', required = True, size = 5)
    movil = fields.Char(string = 'Direccion', required = True, size = 9) 
    email = fields.Char(string = 'Nombre', required = True) 
    imagen = fields.Image(string = 'Imagen', required = True)
    estadisticas = fields.Boolean(string = '¿Quieres dar acceso a la estadisticas del usuario?', required = True)
    password = fields.Char(String = 'Contraseña')


    dni_usuario_ids = fields.Many2many('senide.usuario')
    credecniales_id = fields.Many2one('senide.credenciales', string='Credenciales', inverse_name='asociado_id')

class usuario_cuidador_rel(models.Model):
    _name = 'senide.usuario_cuidador_rel'
    _description = 'tabla relacional usuario cuidador'

    dni_usuario = fields.Many2one('senide.usuario')
    dni_cuidador = fields.Many2one('senide.cuidador')

class llamadas(models.Model):
    _name = 'senide.llamadas'
    _description = 'registro y gestion de las llamadas relaizadas entre cuidadores y usuarios'

    fecha_hora_inicio = fields.Datetime(string='Fecha y hora de inicio', required=True, default=lambda self: fields.Datetime.now())
    fecha_horafin = fields.Datetime(string='Fecha y hora de hora', required=True, default=lambda self: fields.Datetime.now())
    respuesta = fields.Boolean(string = '¿Ha respondido el cuidador?', required = True)

    rel_id = fields.Many2one('senide.usuario_cuidador_rel')
    transcripcion_id = fields.Many2one('senide.transcripcion', string='Transcripción', inverse_name='llamada_id')


class transcripcion(models.Model):
    _name = 'senide.transcripcion'
    _description = 'registro y gestion de las llamadas relaizadas entre cuidadores y usuarios'

    name = fields.Text(string = "Transcripción de la llamada", required= True)

    llamada_id = fields.Many2one('senide.llamadas', string='Llamada', inverse_name='transcripcion_id')

class credenciales(models.Model):
    _name = 'senide.credenciales'
    _description = 'aqui se guardan las credenciales para acceder a la página web.'

    name = fields.Char(string = 'usuario', required = True)
    pwd = fields.Char(String = 'contraseña', required = True)

    usuario_id = fields.Many2one('senide.usuario', string='Usuario', inverse_name='credecniales_id')
    cuidador_id = fields.Many2one('senide.cuidador', string='Cuidador', inverse_name='credecniales_id')
    asociado_id = fields.Many2one('senide.usuario', string='Asociado', inverse_name='credecniales_id')




#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
