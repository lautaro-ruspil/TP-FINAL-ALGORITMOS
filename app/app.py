from flask import Flask, flash, render_template, request, redirect, url_for
from models.biblioteca import Biblioteca
from models.libro import Libro
from models.usuario import Usuario
from utils.validaciones import validar_usuario_form

app = Flask(__name__)

biblioteca = Biblioteca()

# Cargar libros manualmente
lib1 = Libro(1, "El principito", "Antoine de Saint-Exupéry", "Drama")
lib2 = Libro(2, "Cien Años de Soledad", "Gabriel García Márquez", "Realismo mágico")
lib3 = Libro(3, "Rayuela", "Julio Cortázar", "Ficción")

biblioteca.agregar_libro(lib1)
biblioteca.agregar_libro(lib2)
biblioteca.agregar_libro(lib3)

# Cargar usuarios iniciales
biblioteca.agregar_usuario(
    Usuario(
        1,"Lautaro", "Ruspil", 23457382, "2284-225443", "Tierra del Fuego", 1340, [lib1, lib2]
    )
)
biblioteca.agregar_usuario(
    Usuario(
        2,"Franco", "Dell", 12345678, "2284-124443", "Tierra del Fuego", 1123, [lib1]
    )
)
biblioteca.agregar_usuario(
    Usuario(3,"Pepe", "Martinez", 23457382, "2284-225443", "Hornos", 2020, [lib3])
)


# --- RUTAS PRINCIPALES ---


@app.route("/")
def inicio():
    return render_template("index.html", biblioteca=biblioteca, active_page="inicio")


# ---------- LIBROS ----------
@app.route("/libros", methods=["GET", "POST"])
def libros():
    if request.method == "POST":
        titulo = request.form["titulo"]
        autor = request.form["autor"]
        genero = request.form["genero"]
        nuevo_libro = Libro(len(biblioteca.libros) + 1, titulo, autor, genero)
        biblioteca.agregar_libro(nuevo_libro)
        return redirect(url_for("libros"))

    q = request.args.get("q", "").lower()
    books = (
        [l for l in biblioteca.libros if q in l.titulo.lower()]
        if q
        else biblioteca.libros
    )
    return render_template("libros.html", books=books, q=q, active_page="libros")


@app.route("/prestar/<int:id_libro>", methods=["POST"])
def prestar(id_libro):
    for libro in biblioteca.libros:
        if libro.id_libro == id_libro:
            libro.prestado = True
            break
    return redirect(url_for("libros"))


@app.route("/devolver/<int:id_libro>", methods=["POST"])
def devolver(id_libro):
    for libro in biblioteca.libros:
        if libro.id_libro == id_libro:
            libro.prestado = False
            break
    return redirect(url_for("libros"))


@app.route("/eliminar/<int:id_libro>", methods=["POST"])
def eliminar(id_libro):
    biblioteca.libros = [l for l in biblioteca.libros if l.id_libro != id_libro]
    return redirect(url_for("libros"))


# ---------- PRÉSTAMOS ----------
@app.route("/prestamos", methods=["GET"])
def prestamos():
    q = request.args.get("q", "")
    prestados = [l for l in biblioteca.libros if l.prestado]
    if q:
        prestados = [l for l in prestados if q.lower() in l.titulo.lower()]
    return render_template("prestamos.html", books=prestados, active_page="prestamos")


# ---------- USUARIOS ----------
@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    if request.method == "POST":
        valido, errores = validar_usuario_form(request.form)
        if not valido:
            users = biblioteca.users
            return render_template(
                "usuarios.html",
                errores=errores,
                datos=request.form,
                users=users,
                active_page="usuarios",
            )

        nuevo = Usuario(
            len(biblioteca.users) + 1,
            request.form["nombre"],
            request.form["apellido"],
            request.form["dni"],
            request.form["telefono"],
            request.form["direccion"],
            request.form["nro_direccion"],
        )
        biblioteca.agregar_usuario(nuevo)
        return redirect(url_for("usuarios"))

    q = request.args.get("q", "")
    users = biblioteca.buscar_usuarios(q) if q else biblioteca.users
    return render_template("usuarios.html", users=users, active_page="usuarios")

@app.route('/prestar_libro_usuario/<int:id_usuario>', methods=['GET'])
def seleccionar_libro_prestamo(id_usuario):
    # Buscar el usuario por ID en la biblioteca
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    if not usuario:
        return "Usuario no encontrado", 404

    # Filtrar libros que no estén prestados
    libros_disponibles = [libro for libro in biblioteca.libros if not getattr(libro, 'prestado', False)]

    return render_template(
        'libros_disponibles.html',
        usuario=usuario,
        libros=libros_disponibles
    )


@app.route('/confirmar_prestamo/<int:id_usuario>/<int:id_libro>', methods=['POST'])
def confirmar_prestamo(id_usuario, id_libro):
    # Buscar usuario y libro en memoria
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    libro = next((l for l in biblioteca.libros if l.id_libro == id_libro), None)

    if not usuario or not libro:
        return "Usuario o libro no encontrado", 404

    # Si el libro ya está prestado, mostrar mensaje
    if getattr(libro, 'prestado', False):
        return f"El libro '{libro.titulo}' ya está prestado.", 400

    # Asignar libro al usuario
    usuario.libros.append(libro)

    # Marcar como prestado
    libro.prestado = True

    # Redirigir con mensaje
    return redirect(url_for('usuarios'))



# ---------- ELIMINAR USUARIO ----------
@app.route("/eliminar_usuario/<int:id_usuario>", methods=["POST"])
def eliminar_usuario(id_usuario):
    biblioteca.eliminar_usuario(id_usuario)
    return redirect(url_for("usuarios"))


if __name__ == "__main__":
    app.run(debug=True)
