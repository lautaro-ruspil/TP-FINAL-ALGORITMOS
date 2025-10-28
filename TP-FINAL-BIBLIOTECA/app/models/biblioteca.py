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

    def prestados(self):
        return len([l for l in self.libros if l.prestado])

    def disponibles(self):
        return len([l for l in self.libros if not l.prestado])

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

    def eliminar_usuario(self, nombre):
        for user in self.users:
            if user.nombre == nombre:
                self.users.remove(user)
                break
