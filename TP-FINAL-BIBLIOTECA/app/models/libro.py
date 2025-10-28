class Libro:
    def __init__(self, id_libro=None, titulo="", autor="", genero="", prestado=False):
        self.id_libro = id_libro  # El ID lo pone MySQL automáticamente
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        self.prestado = prestado

    def prestar(self):
        self.prestado = True

    def devolver(self):
        self.prestado = False
