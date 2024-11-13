#!/usr/bin/python3

archivo = 'telefonos.dat'

class Registro:
    # Estructura de cada registro:
    # - Nombre: 30
    # - Apellido: 30
    # - Correo: 50
    # - Teléfono: 10
    # - Otros: 50
    # →TOTAL: 170 caracteres por registro.
    def __init__(self, nombre:bytes =b'', apellido:bytes =b'',
                 correo:bytes =b'', telefono:bytes =b'', otros:bytes =b''):
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.telefono = telefono
        self.otros = otros

    def to_record(self):
        return '%-30s%-30s%-50s%-10s%-50s' % (self.nombre, self.apellido,
                                              self.correo, self.telefono,
                                              self.otros)
    @classmethod
    def longitud(cls):
        return 170

    @classmethod
    def from_data(cls, data:bytes = b''):
        # De algún modo, obtiene la información recibida en data y la acomoda en
        # un Registro
        # return Registro()# ...
        return data


class BaseDatos:
    def __init__(self, archivo):
        self.archivo = open(archivo, 'r+')

    def guarda(self, pos : int, registro : Registro):
        self.archivo.seek(Registro.longitud() * pos)
        self.archivo.write(registro.to_record())

    def registros_validos(self):
        lista=[]
        registro = 0

        self.archivo.seek(0)
        data = self.archivo.read(Registro.longitud())
        while data:
            if data.encode('utf-8') != b'\0' * Registro.longitud():
                lista.append(registro)
            registro += 1
            data = self.archivo.read(Registro.longitud())

        return lista

    def registro(self, pos:int=0):
        self.archivo.seek(Registro.longitud() * pos)
        return Registro.from_data(self.archivo.read(Registro.longitud()))

    def busca_por_nombre(self, nombre:bytes = b''):
        num_reg = 0
        self.archivo.seek(0)
        data = Registro.from_data(self.archivo.read(Registro.longitud()))
        while data:
            if data.nombre == nombre:
                return num_reg
            num_reg += 1
            data = Registro.from_data(self.archivo.read(Registro.longitud()))
        raise RuntimeError, 'Registro no encontrado'

base = BaseDatos(archivo)
print('Los registros que tienen datos son:')
print(base.registros_validos())
for registro in base.registros_validos():
    print(base.registro(registro))

#######
# ↓ Genera el archivo con los datos ejemplo
#######
# personas = [Registro(nombre=b'Gunnar',
#                      apellido=b'Wolf',
#                      correo=b'sistop@gwolf.org',
#                      telefono=b'5556230154',
#                      otros=b''),
#             Registro(nombre=b'Fulano',
#                      apellido=b'de Tal',
#                      telefono=b'1122334455',
#                      otros=b'No tenemos su correo :-('),
#             Registro(nombre=b'Linus',
#                      apellido=b'Torvalds',
#                      telefono=b'0xDEADBEEF',
#                      correo=b'torvalds@linux.org',
#                      otros=b'Ampliamente reconocido')]
# num = 1
# for p in personas:
#     base.guarda(250 * num, p)
#     num += 1
