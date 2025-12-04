class Usuario:
    def __init__(
        self, id_usuario, nombre, apellido, dni, telefono, direccion, nro_direccion, libros=None
    ):
        self.id_usuario = id_usuario
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni
        self.telefono = telefono
        self.direccion = direccion
        self.nro_direccion = nro_direccion
        self.libros = libros if libros is not None else []
