from .usuario import Usuario


class Biblioteca:
    def __init__(self, users=None):
        self.libros = []
        self.users = users if users is not None else []

    def agregar_libro(self, libro):
        self.libros.append(libro)

    def obtener_libro_por_titulo(self, titulo):
        for libro in self.libros:
            if libro.titulo.lower() == titulo.lower():
                return libro
        return None

    def total_libros(self):
        return len(self.libros)

    def disponibles(self):
        # suma de stocks de los libros que no están prestados
        return sum(l.stock for l in self.libros if not l.prestados)

    def prestados(self):
        # cuenta de libros prestados
        return sum(1 for l in self.libros if l.prestados)

    def eliminar(self, titulo):
        for libro in self.libros:
            if libro.titulo == titulo:
                self.libros.remove(libro)
                break

    def total_usuarios(self):
        return len(self.users)

    def agregar_usuario(self, usuario):
        self.users.append(usuario)

    def buscar_usuarios(self, nombre):
        texto = nombre.lower()
        return [user for user in self.users if texto in user.nombre.lower()]

    def eliminar_usuario(self, id_usuario):
        self.users = [user for user in self.users if user.id_usuario != id_usuario]
