from flask import Flask, flash, jsonify, render_template, request, redirect, url_for
from models.biblioteca import Biblioteca
from models.libro import Libro
from models.usuario import Usuario
from utils.validaciones import  validar_libro_form

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
        valido, errores = validar_libro_form(request.form)
        if not valido:
            q = request.args.get("q", "").lower()
            books = (
                [l for l in biblioteca.libros if q in l.titulo.lower()]
                if q
                else biblioteca.libros
            )
            return render_template("libros.html", books=books, q=q, errores=errores, form=request.form, active_page="libros")

        titulo = request.form["titulo"]
        autor = request.form["autor"]
        genero = request.form["genero"]
        nuevo_libro = Libro(len(biblioteca.libros) + 1, titulo, autor, genero)
        biblioteca.agregar_libro(nuevo_libro)
        return redirect(url_for("libros"))


    q = request.args.get("q", "").lower()
    campo = request.args.get("campo", "titulo")
    orden = request.args.get("orden", "Ascendente")

    if q:
        books = [l for l in biblioteca.libros if q in getattr(l, campo).lower()]
    else:
        books = biblioteca.libros

    reverse = True if orden == "Descendente" else False
    books.sort(key=lambda x: getattr(x, campo).lower(), reverse=reverse)

    return render_template(
        "libros.html",
        books=books,
        q=q,
        campo=campo,
        orden=orden,
        active_page="libros"
    )

# ---------- BÚSQUEDA libros ----------
@app.route("/buscar_libros")
def buscar_libros():
    q = request.args.get("q", "").lower()
    campo = request.args.get("campo", "titulo")
    orden = request.args.get("orden", "Ascendente")

    # Filtrar según búsqueda
    if q:
        libros_filtrados = [l for l in biblioteca.libros if q in getattr(l, campo).lower()]
    else:
        libros_filtrados = biblioteca.libros.copy()

    # Ordenar resultados
    reverse = True if orden == "Descendente" else False
    libros_filtrados.sort(key=lambda x: getattr(x, campo).lower(), reverse=reverse)

    # Devolver JSON
    return jsonify([
        {
            "id_libro": l.id_libro,
            "titulo": l.titulo,
            "autor": l.autor,
            "genero": l.genero,
            "prestado": l.prestado
        }
        for l in libros_filtrados
    ])




@app.route("/editar/<int:id_libro>", methods=["GET", "POST"])
def editar(id_libro):
    libro = next((l for l in biblioteca.libros if l.id_libro == id_libro), None)
    if not libro:
        return "Libro no encontrado", 404

    if request.method == "POST":
        valido, errores = validar_libro_form(request.form)
        if valido:
            libro.titulo = request.form["titulo"]
            libro.autor = request.form["autor"]
            libro.genero = request.form["genero"]
            return redirect(url_for("libros"))
        else:
            return render_template(
                "editar_libro.html", libro=libro, errores=errores, form=request.form
            )

    return render_template("editar_libro.html", libro=libro, errores={}, form=None)

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
        # Flask solo recibe los datos ya validados por el navegador
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        dni = request.form.get("dni", "").strip()
        telefono = request.form.get("telefono", "").strip()
        direccion = request.form.get("direccion", "").strip()
        nro_direccion = request.form.get("nro_direccion", "").strip()

        nuevo = Usuario(
            len(biblioteca.users) + 1,
            nombre,
            apellido,
            dni,
            telefono,
            direccion,
            nro_direccion
        )
        biblioteca.agregar_usuario(nuevo)
        return redirect(url_for("usuarios"))

    # GET: mostrar todos los usuarios (o buscar)
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
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    libro = next((l for l in biblioteca.libros if l.id_libro == id_libro), None)

    if not usuario or not libro:
        return jsonify({"ok": False, "msg": "Usuario o libro no encontrado."}), 404

    # Ya tiene ese libro
    if any(l.id_libro == id_libro for l in usuario.libros):
        return jsonify({
            "ok": False,
            "msg": f"El usuario {usuario.nombre} ya tiene el libro '{libro.titulo}'."
        }), 400

    # Libro ya prestado
    if getattr(libro, 'prestado', False):
        return jsonify({
            "ok": False,
            "msg": f"El libro '{libro.titulo}' ya está prestado."
        }), 400

    # Registrar préstamo
    usuario.libros.append(libro)
    libro.prestado = True

    return jsonify({
        "ok": True,
        "msg": f"Libro '{libro.titulo}' prestado correctamente a {usuario.nombre}."
    })

# Editar información de usuario
@app.route('/editar_usuario/<int:id_usuario>', methods=['GET'])
def editar_usuario(id_usuario):
    # Buscar el usuario
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    if not usuario:
        return "Usuario no encontrado", 404

    return render_template('editar_usuario.html', usuario=usuario, active_page="usuarios")

# Confirmar actualizacion de usuario
@app.route('/actualizar_usuario/<int:id_usuario>', methods=['POST'])
def actualizar_usuario(id_usuario):
    #Buscar el usuario por ID
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    if not usuario:
        return "Usuario no encontrado", 404

    # Actualizamos los campos editables
    usuario.nombre = request.form['nombre']
    usuario.apellido = request.form['apellido']
    usuario.telefono = request.form['telefono']
    usuario.direccion = request.form['direccion']
    usuario.nro_direccion = request.form['nro_direccion']

    # No se permite editar el DNI ni los libros directamente
    return redirect(url_for('usuarios'))


# ---------- ELIMINAR USUARIO ----------
@app.route("/eliminar_usuario/<int:id_usuario>", methods=["POST"])
def eliminar_usuario(id_usuario):
    biblioteca.eliminar_usuario(id_usuario)
    return redirect(url_for("usuarios"))


if __name__ == "__main__":
    app.run(debug=True)
