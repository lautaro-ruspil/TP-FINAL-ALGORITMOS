class Libro:
    def __init__(self, id_libro=None, titulo="", autor="", genero="", stock= 1):
        self.id_libro = id_libro  
        self.titulo = titulo
        self.autor = autor
        self.genero = genero
        self.prestados = 0
        self.stock = stock

    def prestar(self):
        if self.stock > 0:
            self.stock -= 1
            self.prestados += 1

    def devolver(self):
        if self.prestados > 0:
            self.stock += 1
            self.prestados -= 1
