# from sqlalchemy.exc import IntegrityError

# from modelos import \
#     db, \
#     Ejercicio, \
#     Entrenamiento

# class UtilidadReporte:
#     def calcular_imc(self, talla, peso):
#         return peso / (talla*talla)

#     def dar_clasificacion_imc(self, imc):
#         if imc<18.5:
#             return "Bajo peso"
#         elif imc<25:
#             return "Peso saludable"
#         elif imc<30:
#             return "Sobrepeso"
#         else:
#             return "Obesidad"

#     def dar_resultados(self, entrenamientos):
#         calorias = {}
#         repeticiones = {}
#         resultados = []

#         calorias_total = 0
#         repeticiones_total = 0

#         for entrenamiento in entrenamientos:
#             repeticiones_temp = entrenamiento.repeticiones
#             calorias_temp = self.calcular_calorias(entrenamiento)

#             if str(entrenamiento.fecha) in repeticiones:
#                 repeticiones[str(entrenamiento.fecha)] = repeticiones [str(entrenamiento.fecha)] + repeticiones_temp
#             else:
#                 repeticiones[str(entrenamiento.fecha)] = repeticiones_temp

#             if str(entrenamiento.fecha) in calorias:
#                 calorias[str(entrenamiento.fecha)] = calorias [str(entrenamiento.fecha)] + calorias_temp
#             else:
#                 calorias[str(entrenamiento.fecha)] =  calorias_temp

#             calorias_total = calorias_total + calorias_temp
#             repeticiones_total = repeticiones_total + repeticiones_temp

#         for fecha_resultados in list(repeticiones.keys()):
#             fila = dict(fecha=fecha_resultados, repeticiones=str(repeticiones[str(fecha_resultados)]), calorias=str(calorias[str(fecha_resultados)]))
#             resultados.append(fila)

#         resultados.append(dict(fecha='Total', repeticiones=str(repeticiones_total), calorias=str(calorias_total)))
#         return resultados

#     def calcular_calorias(self, entrenamiento):
#         ejercicio = Ejercicio.query.get_or_404(entrenamiento.ejercicio)
#         tiempo_segundos = (entrenamiento.tiempo.hour*60*60) + (entrenamiento.tiempo.minute*60) + entrenamiento.tiempo.second
#         return((4*entrenamiento.repeticiones*entrenamiento.repeticiones*ejercicio.calorias)/tiempo_segundos)
