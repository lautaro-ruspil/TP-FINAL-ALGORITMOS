from flask import Flask, flash, jsonify, render_template, request, redirect, url_for
from models.biblioteca import Biblioteca
from models.libro import Libro
from models.usuario import Usuario


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
        1,"Lautaro", "Ruspil", 23457382, "2284-225443", "Tierra del Fuego", 1340, 
    )
)
biblioteca.agregar_usuario(
    Usuario(
        2,"Franco", "Dell", 12345678, "2284-124443", "Tierra del Fuego", 1123, 
    )
)
biblioteca.agregar_usuario(
    Usuario(3,"Pepe", "Martinez", 23457382, "2284-225443", "Hornos", 2020)
)


# --- RUTAS PRINCIPALES ---


@app.route("/")
def inicio():
    return render_template("index.html", biblioteca=biblioteca, active_page="inicio")


# ---------- LIBROS ----------
@app.route("/libros", methods=["GET", "POST"])
def libros():
    if request.method == "POST":
        #  Solo recibe los datos (ya validados en el front)
        titulo = request.form["titulo"]
        autor = request.form["autor"]
        genero = request.form["genero"]
        stock = int(request.form["stock"])

        nuevo_libro = Libro(
            len(biblioteca.libros) + 1,
            titulo,
            autor,
            genero,
            stock
        )
        biblioteca.agregar_libro(nuevo_libro)
        return redirect(url_for("libros"))

    # GET: mostrar lista de libros con filtros y orden
    q = request.args.get("q", "").lower()
    campo = request.args.get("campo", "titulo")
    orden = request.args.get("orden", "Ascendente")

    if q:
        books = [l for l in biblioteca.libros if q in getattr(l, campo).lower()]
    else:
        books = biblioteca.libros

    reverse = orden == "Descendente"
    books.sort(key=lambda x: getattr(x, campo).lower(), reverse=reverse)

    return render_template(
        "libros.html",
        books=books,
        q=q,
        campo=campo,
        orden=orden,
        disponibles=biblioteca.disponibles(),
        prestados=biblioteca.prestados(),
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
            "stock": l.stock,
            "prestado": l.prestados
        }
        for l in libros_filtrados
    ])




@app.route("/editar/<int:id_libro>", methods=["GET", "POST"])
def editar(id_libro):
    libro = next((l for l in biblioteca.libros if l.id_libro == id_libro), None)
    if not libro:
        return "Libro no encontrado", 404

    if request.method == "POST":
        libro.titulo = request.form["titulo"]
        libro.autor = request.form["autor"]
        libro.genero = request.form["genero"]
        nuevo_stock = int(request.form["stock"])
        # Evita que se reduzca el stock
        if nuevo_stock > libro.stock:
            diferencia = nuevo_stock - libro.stock
            libro.stock += diferencia  # solo aumenta
        else:
            # si intentan poner menos, se mantiene igual
            pass
        return redirect(url_for("libros"))

    # Si es GET, mostrar el formulario con los datos actuales
    return render_template("editar_libro.html", libro=libro)

@app.route('/devolver_libro/<int:id_usuario>', methods=['GET'])
def devolver_libro(id_usuario):
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    if not usuario:
        return "Usuario no encontrado", 404

    # Solo mostramos los libros que el usuario tiene
    return render_template('devolver_libro.html', usuario=usuario)

@app.route('/confirmar_devolucion/<int:id_usuario>/<int:id_libro>', methods=['POST'])
def confirmar_devolucion(id_usuario, id_libro):
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    libro = next((l for l in biblioteca.libros if l.id_libro == id_libro), None)

    if not usuario or not libro:
        return jsonify({"ok": False, "msg": "Usuario o libro no encontrado"}), 404

    if libro in usuario.libros:
        usuario.libros.remove(libro)
        libro.devolver()
        return jsonify({"ok": True, "msg": f"El libro '{libro.titulo}' fue devuelto correctamente."})
    else:
        return jsonify({"ok": False, "msg": "El usuario no tiene este libro prestado."})


@app.route("/eliminar/<int:id_libro>", methods=["POST"])
def eliminar(id_libro):
    biblioteca.libros = [l for l in biblioteca.libros if l.id_libro != id_libro]
    return redirect(url_for("libros"))



# ---------- USUARIOS ----------
@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    if request.method == "POST":
        #  Solo recibe los datos del formulario (ya validados en el front)
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

    # GET: Mostrar usuarios con búsqueda y orden
    q = request.args.get("q", "").lower()
    campo = request.args.get("campo", "nombre")
    orden = request.args.get("orden", "Ascendente")

    users = biblioteca.users.copy()

    # Filtrado
    if q:
        users = [
            u for u in users
            if q in getattr(u, campo).lower()
            or (campo == "libros" and any(q in l.titulo.lower() for l in u.libros))
        ]

    # Ordenamiento
    reverse = orden == "Descendente"
    users.sort(key=lambda u: getattr(u, campo).lower() if isinstance(getattr(u, campo), str) else str(getattr(u, campo)), reverse=reverse)

    return render_template(
        "usuarios.html",
        users=users,
        q=q,
        campo=campo,
        orden=orden,
        active_page="usuarios"
    )

@app.route('/buscar_usuarios')
def buscar_usuarios():
    q = request.args.get('q', '').lower()
    campo = request.args.get('campo', 'nombre')
    orden = request.args.get('orden', 'Ascendente')

    users = Usuario.query.all()
    filtrados = []

    for u in users:
        if campo == "nombre" and q in u.nombre.lower():
            filtrados.append(u)
        elif campo == "apellido" and q in u.apellido.lower():
            filtrados.append(u)
        elif campo == "dni" and q in str(u.dni):
            filtrados.append(u)
        elif campo == "libros" and any(q in l.titulo.lower() for l in u.libros):
            filtrados.append(u)

    reverse = orden == "Descendente"

    filtrados.sort(key=lambda x: getattr(x, campo if campo in ["nombre", "apellido", "dni"] else "nombre"), reverse=reverse)

    return jsonify([
        {
            "id_usuario": u.id_usuario,
            "nombre": u.nombre,
            "apellido": u.apellido,
            "dni": u.dni,
            "telefono": u.telefono,
            "direccion": u.direccion,
            "nro_direccion": u.nro_direccion,
            "libros": [{"titulo": l.titulo, "autor": l.autor} for l in u.libros]
        } for u in filtrados
    ])

@app.route('/prestar_libro_usuario/<int:id_usuario>', methods=['GET'])
def seleccionar_libro_prestamo(id_usuario):
    # Buscar el usuario por ID en la biblioteca
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    if not usuario:
        return "Usuario no encontrado", 404

    # Filtrar libros que no estén prestados
    libros_disponibles = [libro for libro in biblioteca.libros if libro.stock > 0]

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

    # No hay stock disponible
    if libro.stock <= 0:
        return jsonify({
            "ok": False,
            "msg": f"No hay ejemplares disponibles de '{libro.titulo}'."
        }), 400

    # Registrar préstamo
    usuario.libros.append(libro)
    libro.prestar()  # 👈 ahora usa el método que resta stock y suma prestados

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
