# import json
# import hashlib
# from unittest import TestCase

# from faker import Faker
# from faker.generator import random
# from modelos import db, Usuario, Ejercicio

# from main import app


# class TestEjercicio:

#   def setUp(self):
#     self.data_factory = Faker()
#     self.client = app.test_client()

#     nombre_usuario = 'test_' + self.data_factory.name()
#     contrasena = 'T1$' + self.data_factory.word()
#     contrasena_encriptada = hashlib.md5(contrasena.encode('utf-8')).hexdigest()

#     # Se crea el usuario para identificarse en la aplicación
#     usuario_nuevo = Usuario(usuario=nombre_usuario, contrasena=contrasena_encriptada)
#     db.session.add(usuario_nuevo)
#     db.session.commit()

#     usuario_login = {
#         "usuario": nombre_usuario,
#         "contrasena": contrasena
#     }

#     solicitud_login = self.client.post("/login",
#                                        data=json.dumps(usuario_login),
#                                        headers={'Content-Type': 'application/json'})

#     respuesta_login = json.loads(solicitud_login.get_data())

#     self.token = respuesta_login["token"]
#     self.usuario_id = respuesta_login["id"]

#     self.ejercicios_creados = []

#   def tearDown(self):
#     for ejercicio_creado in self.ejercicios_creados:
#       ejercicio = Ejercicio.query.get(ejercicio_creado.id)
#       db.session.delete(ejercicio)
#       db.session.commit()

#     usuario_login = Usuario.query.get(self.usuario_id)
#     db.session.delete(usuario_login)
#     db.session.commit()

#   def test_crear_ejercicio(self):
#     # Crear los datos del ejercicio
#     nombre_nuevo_ejercicio = self.data_factory.sentence()
#     descripcion_nuevo_ejercicio = self.data_factory.sentence()
#     video_nuevo_ejercicio = self.data_factory.sentence()
#     calorias_nuevo_ejercicio = round(random.uniform(0.1, 0.99), 2)

#     # Crear el json con el ejercicio a crear
#     nuevo_ejercicio = {
#         "nombre": nombre_nuevo_ejercicio,
#         "descripcion": descripcion_nuevo_ejercicio,
#         "video": video_nuevo_ejercicio,
#         "calorias": calorias_nuevo_ejercicio
#     }

#     # Definir endpoint, encabezados y hacer el llamado
#     endpoint_ejercicios = "/ejercicios"
#     headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

#     resultado_nuevo_ejercicio = self.client.post(endpoint_ejercicios,
#                                                  data=json.dumps(nuevo_ejercicio),
#                                                  headers=headers)

#     # Obtener los datos de respuesta y dejarlos un objeto json y en el objeto a comparar
#     datos_respuesta = json.loads(resultado_nuevo_ejercicio.get_data())
#     ejercicio = Ejercicio.query.get(datos_respuesta['id'])
#     self.ejercicios_creados.append(ejercicio)

#     # Verificar que el llamado fue exitoso y que el objeto recibido tiene los datos iguales a los creados
#     self.assertEqual(resultado_nuevo_ejercicio.status_code, 200)
#     self.assertEqual(datos_respuesta['nombre'], ejercicio.nombre)
#     self.assertEqual(datos_respuesta['descripcion'], ejercicio.descripcion)
#     self.assertEqual(datos_respuesta['video'], ejercicio.video)
#     self.assertEqual(float(datos_respuesta['calorias']), float(ejercicio.calorias))
#     self.assertIsNotNone(datos_respuesta['id'])

#   def test_editar_ejercicio(self):
#     # Crear los datos del ejercicio
#     nombre_nuevo_ejercicio = self.data_factory.sentence()
#     descripcion_nuevo_ejercicio = self.data_factory.sentence()
#     video_nuevo_ejercicio = self.data_factory.sentence()
#     calorias_nuevo_ejercicio = round(random.uniform(0.1, 0.99), 2)

#     # Crear los datos que quedarán luego de la edición
#     nombre_ejercicio_editado = self.data_factory.sentence()
#     descripcion_ejercicio_editado = self.data_factory.sentence()
#     video_ejercicio_editado = self.data_factory.sentence()
#     calorias_ejercicio_editado = round(random.uniform(0.1, 0.99), 2)

#     # Crear el ejercicio con los datos originales para obtener su id
#     ejercicio = Ejercicio(nombre=nombre_nuevo_ejercicio,
#                           descripcion=descripcion_nuevo_ejercicio,
#                           video=video_nuevo_ejercicio,
#                           calorias=calorias_nuevo_ejercicio)
#     db.session.add(ejercicio)
#     db.session.commit()
#     self.ejercicios_creados.append(ejercicio)

#     # Crear el json con el ejercicio a editar
#     ejercicio_editado = {
#         "nombre": nombre_ejercicio_editado,
#         "descripcion": descripcion_ejercicio_editado,
#         "video": video_ejercicio_editado,
#         "calorias": calorias_ejercicio_editado
#     }

#     # Definir endpoint, encabezados y hacer el llamado
#     endpoint_ejercicios = "/ejercicio/" + str(ejercicio.id)
#     headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

#     resultado_edicion_ejercicio = self.client.put(endpoint_ejercicios,
#                                                   data=json.dumps(ejercicio_editado),
#                                                   headers=headers)

#     # Obtener los datos de respuesta y dejarlos un objeto json
#     datos_respuesta = json.loads(resultado_edicion_ejercicio.get_data())

#     # Verificar que el llamado fue exitoso y que el objeto recibido no tiene los datos originales
#     self.assertEqual(resultado_edicion_ejercicio.status_code, 200)
#     self.assertNotEqual(datos_respuesta['nombre'], nombre_nuevo_ejercicio)
#     self.assertNotEqual(datos_respuesta['descripcion'], descripcion_nuevo_ejercicio)
#     self.assertNotEqual(datos_respuesta['video'], video_nuevo_ejercicio)
#     self.assertNotEqual(float(datos_respuesta['calorias']), calorias_nuevo_ejercicio)

#     # Verificar que el llamado retornó los datos cambiados según el id enviado
#     self.assertEqual(datos_respuesta['id'], str(ejercicio.id))
#     self.assertEqual(datos_respuesta['nombre'], nombre_ejercicio_editado)
#     self.assertEqual(datos_respuesta['descripcion'], descripcion_ejercicio_editado)
#     self.assertEqual(datos_respuesta['video'], video_ejercicio_editado)
#     self.assertEqual(float(datos_respuesta['calorias']), calorias_ejercicio_editado)

#   def test_borrar_ejercicio(self):
#     # Prueba del endpoint para crear ejercicios
#     nombre_nuevo_ejercicio = self.data_factory.sentence()
#     descripcion_nuevo_ejercicio = self.data_factory.sentence()
#     video_nuevo_ejercicio = self.data_factory.sentence()
#     calorias_nuevo_ejercicio = round(random.uniform(0.1, 0.99), 2)

#     # Crear el ejercicio directamente con los datos originales para obtener su id
#     ejercicio = Ejercicio(nombre=nombre_nuevo_ejercicio,
#                           descripcion=descripcion_nuevo_ejercicio,
#                           video=video_nuevo_ejercicio,
#                           calorias=calorias_nuevo_ejercicio)
#     db.session.add(ejercicio)
#     db.session.commit()

#     # Definir endpoint, encabezados y hacer el llamado
#     endpoint_ejercicios = "/ejercicio/" + str(ejercicio.id)
#     headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}
#     resultado_borrado_ejercicio = self.client.delete(endpoint_ejercicios,
#                                                      headers=headers)

#     # Verificar que el llamado retornó los datos cambiados según el id enviado
#     self.assertEqual(resultado_borrado_ejercicio.status_code, 204)

#     # Busco el ejercicio y verfico que ya no exista
#     ejercicio_borrado = Ejercicio.query.get(ejercicio.id)
#     self.assertIsNone(ejercicio_borrado)

#   def test_dar_ejercicio(self):
#     # Crear los datos del ejercicio
#     nombre_nuevo_ejercicio = self.data_factory.sentence()
#     descripcion_nuevo_ejercicio = self.data_factory.sentence()
#     video_nuevo_ejercicio = self.data_factory.sentence()
#     calorias_nuevo_ejercicio = round(random.uniform(0.1, 0.99), 2)

#     # Crear el ejercicio con los datos originales para obtener su id
#     ejercicio = Ejercicio(nombre=nombre_nuevo_ejercicio,
#                           descripcion=descripcion_nuevo_ejercicio,
#                           video=video_nuevo_ejercicio,
#                           calorias=calorias_nuevo_ejercicio)
#     db.session.add(ejercicio)
#     db.session.commit()
#     self.ejercicios_creados.append(ejercicio)

#     # Definir endpoint, encabezados y hacer el llamado
#     endpoint_ejercicios = "/ejercicio/" + str(ejercicio.id)
#     headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

#     resultado_consulta_ejercicio = self.client.get(endpoint_ejercicios,
#                                                    headers=headers)

#     # Obtener los datos de respuesta y dejarlos un objeto json
#     datos_respuesta = json.loads(resultado_consulta_ejercicio.get_data())

#     # Verificar que el llamado fue exitoso y que el objeto recibido tiene los datos iguales a los creados
#     self.assertEqual(resultado_consulta_ejercicio.status_code, 200)
#     self.assertEqual(datos_respuesta['nombre'], nombre_nuevo_ejercicio)
#     self.assertEqual(datos_respuesta['descripcion'], descripcion_nuevo_ejercicio)
#     self.assertEqual(datos_respuesta['video'], video_nuevo_ejercicio)
#     self.assertEqual(float(datos_respuesta['calorias']), float(calorias_nuevo_ejercicio))
#     self.assertIsNotNone(datos_respuesta['id'])

#   def test_listar_ejercicios(self):
#     # Generar 10 ejercicios con datos aleatorios
#     for i in range(0, 10):
#       # Crear los datos del ejercicio
#       nombre_nuevo_ejercicio = self.data_factory.sentence()
#       descripcion_nuevo_ejercicio = self.data_factory.sentence()
#       video_nuevo_ejercicio = self.data_factory.sentence()
#       calorias_nuevo_ejercicio = round(random.uniform(0.1, 0.99), 2)

#       # Crear el ejercicio con los datos originales para obtener su id
#       ejercicio = Ejercicio(nombre=nombre_nuevo_ejercicio,
#                             descripcion=descripcion_nuevo_ejercicio,
#                             video=video_nuevo_ejercicio,
#                             calorias=calorias_nuevo_ejercicio)
#       db.session.add(ejercicio)
#       db.session.commit()
#       self.ejercicios_creados.append(ejercicio)

#     # Definir endpoint, encabezados y hacer el llamado
#     endpoint_ejercicios = "/ejercicios"
#     headers = {'Content-Type': 'application/json', "Authorization": "Bearer {}".format(self.token)}

#     resultado_consulta_ejercicio = self.client.get(endpoint_ejercicios,
#                                                    headers=headers)

#     # Obtener los datos de respuesta y dejarlos un objeto json
#     datos_respuesta = json.loads(resultado_consulta_ejercicio.get_data())

#     # Verificar que el llamado fue exitoso
#     self.assertEqual(resultado_consulta_ejercicio.status_code, 200)

#     # Verificar los ejercicios creados con sus datos
#     for ejercicio in datos_respuesta:
#       for ejercicio_creado in self.ejercicios_creados:
#         if ejercicio['id'] == str(ejercicio_creado.id):
#           self.assertEqual(ejercicio['nombre'], ejercicio_creado.nombre)
#           self.assertEqual(ejercicio['descripcion'], ejercicio_creado.descripcion)
#           self.assertEqual(ejercicio['video'], ejercicio_creado.video)
#           self.assertEqual(float(ejercicio['calorias']), float(ejercicio_creado.calorias))
#           self.assertEqual(ejercicio['id'], str(ejercicio_creado.id))
