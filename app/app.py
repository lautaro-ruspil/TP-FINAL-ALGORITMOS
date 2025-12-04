# Importamos Flask, que es el framework web principal
from flask import Flask, jsonify, render_template, request, redirect, url_for
# Importamos las clases de nuestros modelos personalizados
from models.biblioteca import Biblioteca
from models.libro import Libro
from models.usuario import Usuario


# Creamos la instancia de la aplicación Flask
app = Flask(__name__)

# Creamos una instancia de Biblioteca que almacenará todos los datos en memoria
biblioteca = Biblioteca()

# ========== DATOS INICIALES ==========
# Agregamos 3 libros de prueba al iniciar la aplicación
# Cada libro recibe: id, título, autor, género, y stock por defecto
biblioteca.agregar_libro(Libro(1, "El principito", "Antoine de Saint-Exupéry", "Drama"))
biblioteca.agregar_libro(Libro(2, "Cien Años de Soledad", "Gabriel García Márquez", "Realismo mágico"))
biblioteca.agregar_libro(Libro(3, "Rayuela", "Julio Cortázar", "Ficción"))

# Agregamos 3 usuarios de prueba al iniciar la aplicación
# Cada usuario recibe: id, nombre, apellido, dni, teléfono, dirección, número de dirección
biblioteca.agregar_usuario(
    Usuario(
        1, "Lautaro", "Ruspil", 23457382, "2284-225421", "Avenida Pellegrini", 2700, 
    )
)

biblioteca.agregar_usuario(
    Usuario(
        2, "Franco", "Dell' Arciprete", 12345678, "2284-124443", "Piedras", 1123, 
    )
)

biblioteca.agregar_usuario(
    Usuario(3, "Alma", "Leguizamón", 124556321, "2284-565443", "San martín", 2020)
)


# ========== RUTA PRINCIPAL (INICIO) ==========
# Decorador que define la ruta raíz "/"
@app.route("/")
def inicio():
    # Renderiza la página de inicio y le pasa la biblioteca y la página activa para el menú
    return render_template("index.html", biblioteca=biblioteca, active_page="inicio")


# ========== GESTIÓN DE LIBROS ==========
# Esta ruta maneja tanto GET (mostrar libros) como POST (agregar nuevo libro)
@app.route("/libros", methods=["GET", "POST"])
def libros():
    # Si la petición es POST, significa que se está agregando un nuevo libro
    if request.method == "POST":
        # Extraemos los datos del formulario enviado desde el frontend
        # Los datos ya vienen validados por JavaScript en el frontend
        titulo = request.form["titulo"]
        autor = request.form["autor"]
        genero = request.form["genero"]
        stock = int(request.form["stock"])  # Convertimos el stock a entero

        # Creamos un nuevo objeto Libro
        # El ID se calcula como la cantidad actual de libros + 1
        nuevo_libro = Libro(
            len(biblioteca.libros) + 1,
            titulo,
            autor,
            genero,
            stock
        )
        # Agregamos el libro a la biblioteca
        biblioteca.agregar_libro(nuevo_libro)
        # Redirigimos a la misma página para ver la lista actualizada
        return redirect(url_for("libros"))

    # Si la petición es GET, mostramos la lista de libros con filtros
    # Obtenemos los parámetros de búsqueda de la URL (si existen)
    q = request.args.get("q", "").lower()  # Texto de búsqueda (convertido a minúsculas)
    campo = request.args.get("campo", "titulo")  # Campo por el cual filtrar (por defecto: título)
    orden = request.args.get("orden", "Ascendente")  # Orden ascendente o descendente

    # Si hay texto de búsqueda, filtramos los libros
    if q:
        # Filtramos libros donde el texto de búsqueda esté contenido en el campo especificado
        books = [l for l in biblioteca.libros if q in getattr(l, campo).lower()]
    else:
        # Si no hay búsqueda, mostramos todos los libros
        books = biblioteca.libros

    # Determinamos si el orden es descendente (True) o ascendente (False)
    reverse = orden == "Descendente"
    # Ordenamos los libros por el campo especificado
    books.sort(key=lambda l: getattr(l, campo).lower(), reverse=reverse)

    # Renderizamos la plantilla HTML con los libros filtrados y ordenados
    return render_template(
        "libros.html",
        books=books,
        q=q,  # Pasamos el texto de búsqueda para mantenerlo en el input
        campo=campo,  # Pasamos el campo seleccionado
        orden=orden,  # Pasamos el orden seleccionado
        active_page="libros"  # Indica qué página está activa en el menú
    )

# ========== BÚSQUEDA DINÁMICA DE LIBROS (AJAX) ==========
# Esta ruta se usa para búsquedas en tiempo real sin recargar la página
@app.route("/buscar_libros")
def buscar_libros():
    # Obtenemos los parámetros de búsqueda de la URL
    q = request.args.get("q", "").lower()
    campo = request.args.get("campo", "titulo")
    orden = request.args.get("orden", "Ascendente")

    # Filtramos según el texto de búsqueda
    if q:
        # Si hay búsqueda, filtramos por el campo especificado
        libros_filtrados = [l for l in biblioteca.libros if q in getattr(l, campo).lower()]
    else:
        # Si no hay búsqueda, copiamos todos los libros
        libros_filtrados = biblioteca.libros.copy()

    # Determinamos la dirección del ordenamiento
    reverse = True if orden == "Descendente" else False
    # Ordenamos los resultados
    libros_filtrados.sort(key=lambda l: getattr(l, campo).lower(), reverse=reverse)

    # Devolvemos los resultados en formato JSON para que JavaScript los procese
    return jsonify([
        {
            "id_libro": l.id_libro,
            "titulo": l.titulo,
            "autor": l.autor,
            "genero": l.genero,
            "stock": l.stock,
            "prestados": l.prestados
        }
        for l in libros_filtrados
    ])


# ========== EDITAR LIBRO ==========
# Esta ruta maneja tanto GET (mostrar formulario) como POST (guardar cambios)
@app.route("/editar/<int:id_libro>", methods=["GET", "POST"])
def editar(id_libro):
    # Buscamos el libro por su ID en la lista de libros
    # next() devuelve el primer elemento que cumple la condición, o None si no encuentra
    libro = next((l for l in biblioteca.libros if l.id_libro == id_libro), None)
    
    # Si no encontramos el libro, devolvemos error 404
    if not libro:
        return "Libro no encontrado", 404

    # Si la petición es POST, guardamos los cambios
    if request.method == "POST":
        # Actualizamos los campos básicos del libro
        libro.titulo = request.form["titulo"]
        libro.autor = request.form["autor"]
        libro.genero = request.form["genero"]
        
        # Procesamos el stock de manera especial
        nuevo_stock = int(request.form["stock"])
        # Solo permitimos AUMENTAR el stock, no reducirlo
        if nuevo_stock > libro.stock:
            diferencia = nuevo_stock - libro.stock
            libro.stock += diferencia  # Aumentamos el stock
        else:
            # Si intentan poner menos stock, lo mantenemos igual (no hacemos nada)
            pass
        
        # Redirigimos a la lista de libros
        return redirect(url_for("libros"))

    # Si es GET, mostramos el formulario de edición con los datos actuales
    return render_template("editar_libro.html", libro=libro)

# ========== DEVOLVER LIBRO - PASO 1: SELECCIONAR LIBRO ==========
# Muestra la lista de libros que el usuario tiene prestados
@app.route('/devolver_libro/<int:id_usuario>', methods=['GET'])
def devolver_libro(id_usuario):
    # Buscamos el usuario por su ID
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    
    # Si no existe el usuario, devolvemos error 404
    if not usuario:
        return "Usuario no encontrado", 404

    # Mostramos la página con los libros que el usuario tiene prestados
    return render_template('devolver_libro.html', usuario=usuario)

# ========== DEVOLVER LIBRO - PASO 2: CONFIRMAR DEVOLUCIÓN ==========
# Procesa la devolución de un libro específico
@app.route('/confirmar_devolucion/<int:id_usuario>/<int:id_libro>', methods=['POST'])
def confirmar_devolucion(id_usuario, id_libro):
    # Buscamos el usuario y el libro por sus IDs
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    libro = next((l for l in biblioteca.libros if l.id_libro == id_libro), None)

    # Si no encontramos el usuario o el libro, devolvemos error
    if not usuario or not libro:
        return jsonify({"ok": False, "msg": "Usuario o libro no encontrado"}), 404

    # Verificamos que el usuario realmente tenga este libro prestado
    if libro in usuario.libros:
        # Removemos el libro de la lista de libros del usuario
        usuario.libros.remove(libro)
        # Llamamos al método devolver() del libro para actualizar su stock
        libro.devolver()
        # Devolvemos respuesta exitosa en JSON
        return jsonify({"ok": True, "msg": f"El libro '{libro.titulo}' fue devuelto correctamente."})
    else:
        # Si el usuario no tiene este libro, devolvemos error
        return jsonify({"ok": False, "msg": "El usuario no tiene este libro prestado."})


# ========== ELIMINAR LIBRO ==========
# Elimina un libro de la biblioteca (con validaciones)
@app.route("/eliminar/<int:id_libro>", methods=["POST"])
def eliminar(id_libro):
    # Buscamos el libro por su ID
    libro = next((l for l in biblioteca.libros if l.id_libro == id_libro), None)
    
    # Si no existe el libro, devolvemos error
    if not libro:
        return jsonify({"ok": False, "msg": "Libro no encontrado"}), 404
    
    # VALIDACIÓN IMPORTANTE: No se puede eliminar un libro si está prestado
    if libro.prestados > 0:
        # Devolvemos un mensaje de error indicando cuántos ejemplares están prestados
        return jsonify({
            "ok": False, 
            "msg": f"No se puede eliminar el libro '{libro.titulo}' porque tiene {libro.prestados} ejemplar(es) prestado(s)."
        }), 400
    
    # Si el libro no está prestado, lo eliminamos de la lista
    biblioteca.libros = [l for l in biblioteca.libros if l.id_libro != id_libro]
    # Redirigimos a la lista de libros
    return redirect(url_for("libros"))


# ========== GESTIÓN DE USUARIOS ==========
# Esta ruta maneja tanto GET (mostrar usuarios) como POST (agregar nuevo usuario)
@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    # Si la petición es POST, agregamos un nuevo usuario
    if request.method == "POST":
        # Extraemos los datos del formulario (ya validados en el frontend)
        # Usamos .strip() para eliminar espacios en blanco al inicio y final
        nombre = request.form.get("nombre", "").strip()
        apellido = request.form.get("apellido", "").strip()
        dni = request.form.get("dni", "").strip()
        telefono = request.form.get("telefono", "").strip()
        direccion = request.form.get("direccion", "").strip()
        nro_direccion = request.form.get("nro_direccion", "").strip()

        # Creamos un nuevo objeto Usuario
        # El ID se calcula como la cantidad actual de usuarios + 1
        nuevo = Usuario(
            len(biblioteca.users) + 1,
            nombre,
            apellido,
            dni,
            telefono,
            direccion,
            nro_direccion
        )
        # Agregamos el usuario a la biblioteca
        biblioteca.agregar_usuario(nuevo)
        # Redirigimos a la página de usuarios
        return redirect(url_for("usuarios"))

    # Si la petición es GET, mostramos la lista de usuarios con filtros
    # Obtenemos los parámetros de búsqueda de la URL
    q = request.args.get("q", "").lower()
    campo = request.args.get("campo", "nombre")  # Por defecto filtramos por nombre
    orden = request.args.get("orden", "Ascendente")

    # Creamos una copia de la lista de usuarios
    users = biblioteca.users.copy()

    # Aplicamos el filtro de búsqueda
    if q:
        users = [
            u for u in users
            # Buscamos en el campo especificado
            if q in getattr(u, campo).lower()
            # O si el campo es "libros", buscamos en los títulos de los libros del usuario
            or (campo == "libros" and any(q in l.titulo.lower() for l in u.libros))
        ]

    # Ordenamos los usuarios
    reverse = orden == "Descendente"
    # La función lambda maneja tanto strings como otros tipos de datos
    users.sort(key=lambda u: getattr(u, campo).lower() if isinstance(getattr(u, campo), str) else str(getattr(u, campo)), reverse=reverse)

    # Renderizamos la plantilla con los usuarios filtrados y ordenados
    return render_template(
        "usuarios.html",
        users=users,
        q=q,
        campo=campo,
        orden=orden,
        active_page="usuarios"
    )

# ========== BÚSQUEDA DINÁMICA DE USUARIOS (AJAX) ==========
# Esta ruta se usa para búsquedas en tiempo real sin recargar la página
@app.route('/buscar_usuarios')
def buscar_usuarios():
    # Obtenemos los parámetros de búsqueda
    q = request.args.get('q', '').lower()
    campo = request.args.get('campo', 'nombre')
    orden = request.args.get('orden', 'Ascendente')

    # Obtenemos todos los usuarios
    users = biblioteca.users
    filtrados = []

    # Filtramos según el campo seleccionado
    for u in users:
        # Si buscamos por nombre
        if campo == "nombre" and q in u.nombre.lower():
            filtrados.append(u)
        # Si buscamos por apellido
        elif campo == "apellido" and q in u.apellido.lower():
            filtrados.append(u)
        # Si buscamos por DNI (convertimos a string para buscar)
        elif campo == "dni" and q in str(u.dni):
            filtrados.append(u)
        # Si buscamos por libros, buscamos en los títulos de los libros del usuario
        elif campo == "libros" and any(q in l.titulo.lower() for l in u.libros):
            filtrados.append(u)

    # Determinamos la dirección del ordenamiento
    reverse = orden == "Descendente"

    # Ordenamos los resultados filtrados
    # Si el campo es nombre, apellido o dni lo usamos, sino ordenamos por nombre
    filtrados.sort(key=lambda x: getattr(x, campo if campo in ["nombre", "apellido", "dni"] else "nombre"), reverse=reverse)

    # Devolvemos los resultados en formato JSON
    return jsonify([
        {
            "id_usuario": u.id_usuario,
            "nombre": u.nombre,
            "apellido": u.apellido,
            "dni": u.dni,
            "telefono": u.telefono,
            "direccion": u.direccion,
            "nro_direccion": u.nro_direccion,
            # Incluimos la lista de libros que tiene el usuario (título y autor de cada uno)
            "libros": [{"titulo": l.titulo, "autor": l.autor} for l in u.libros]
        } for u in filtrados
    ])

# ========== PRESTAR LIBRO - PASO 1: SELECCIONAR LIBRO ==========
# Muestra la lista de libros disponibles para prestar a un usuario específico
@app.route('/prestar_libro_usuario/<int:id_usuario>', methods=['GET'])
def seleccionar_libro_prestamo(id_usuario):
    # Buscamos el usuario por su ID
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    
    # Si no existe el usuario, devolvemos error 404
    if not usuario:
        return "Usuario no encontrado", 404

    # Filtramos solo los libros que tienen stock disponible (stock > 0)
    libros_disponibles = [libro for libro in biblioteca.libros if libro.stock > 0]

    # Renderizamos la página con el usuario y los libros disponibles
    return render_template(
        'libros_disponibles.html',
        usuario=usuario,
        libros=libros_disponibles
    )


# ========== PRESTAR LIBRO - PASO 2: CONFIRMAR PRÉSTAMO ==========
# Procesa el préstamo de un libro a un usuario
@app.route('/confirmar_prestamo/<int:id_usuario>/<int:id_libro>', methods=['POST'])
def confirmar_prestamo(id_usuario, id_libro):
    # Buscamos el usuario y el libro por sus IDs
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    libro = next((l for l in biblioteca.libros if l.id_libro == id_libro), None)

    # Si no encontramos el usuario o el libro, devolvemos error
    if not usuario or not libro:
        return jsonify({"ok": False, "msg": "Usuario o libro no encontrado."}), 404

    # VALIDACIÓN 1: Verificar que el usuario no tenga ya este libro
    if any(l.id_libro == id_libro for l in usuario.libros):
        return jsonify({
            "ok": False,
            "msg": f"El usuario {usuario.nombre} ya tiene el libro '{libro.titulo}'."
        }), 400

    # VALIDACIÓN 2: Verificar que haya stock disponible
    if libro.stock <= 0:
        return jsonify({
            "ok": False,
            "msg": f"No hay ejemplares disponibles de '{libro.titulo}'."
        }), 400

    # Si todas las validaciones pasan, registramos el préstamo
    # Agregamos el libro a la lista de libros del usuario
    usuario.libros.append(libro)
    # Llamamos al método prestar() del libro para actualizar su stock
    libro.prestar()
    
    # Devolvemos respuesta exitosa
    return jsonify({
        "ok": True,
        "msg": f"Libro '{libro.titulo}' prestado correctamente a {usuario.nombre}."
    })

# ========== EDITAR USUARIO - PASO 1: MOSTRAR FORMULARIO ==========
# Muestra el formulario de edición con los datos actuales del usuario
@app.route('/editar_usuario/<int:id_usuario>', methods=['GET'])
def editar_usuario(id_usuario):
    # Buscamos el usuario por su ID
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    
    # Si no existe el usuario, devolvemos error 404
    if not usuario:
        return "Usuario no encontrado", 404

    # Renderizamos el formulario de edición con los datos del usuario
    return render_template('editar_usuario.html', usuario=usuario, active_page="usuarios")

# ========== EDITAR USUARIO - PASO 2: GUARDAR CAMBIOS ==========
# Procesa la actualización de los datos del usuario
@app.route('/actualizar_usuario/<int:id_usuario>', methods=['POST'])
def actualizar_usuario(id_usuario):
    # Buscamos el usuario por su ID
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    
    # Si no existe el usuario, devolvemos error 404
    if not usuario:
        return "Usuario no encontrado", 404

    # Actualizamos solo los campos editables
    usuario.nombre = request.form['nombre']
    usuario.apellido = request.form['apellido']
    usuario.telefono = request.form['telefono']
    usuario.direccion = request.form['direccion']
    usuario.nro_direccion = request.form['nro_direccion']

    # NOTA: No se permite editar el DNI ni los libros prestados directamente
    # El DNI es único e inmutable, y los libros se manejan con préstamos/devoluciones

    # Redirigimos a la lista de usuarios
    return redirect(url_for('usuarios'))


# ========== ELIMINAR USUARIO ==========
# Elimina un usuario de la biblioteca (con validaciones)
@app.route("/eliminar_usuario/<int:id_usuario>", methods=["POST"])
def eliminar_usuario(id_usuario):
    # Buscamos el usuario por su ID
    usuario = next((u for u in biblioteca.users if u.id_usuario == id_usuario), None)
    
    # Si no existe el usuario, devolvemos error
    if not usuario:
        return jsonify({"ok": False, "msg": "Usuario no encontrado"}), 404
    
    # VALIDACIÓN IMPORTANTE: No se puede eliminar un usuario si tiene libros prestados
    if len(usuario.libros) > 0:
        # Creamos una lista con los títulos de los libros prestados
        titulos = ", ".join([l.titulo for l in usuario.libros])
        # Devolvemos un mensaje de error con los libros que debe devolver
        return jsonify({
            "ok": False,
            "msg": f"No se puede eliminar al usuario {usuario.nombre} {usuario.apellido} porque tiene libro(s) prestado(s): {titulos}"
        }), 400
    
    # Si el usuario no tiene libros prestados, lo eliminamos
    biblioteca.eliminar_usuario(id_usuario)
    # Redirigimos a la lista de usuarios
    return redirect(url_for("usuarios"))


# ========== INICIAR LA APLICACIÓN ==========
# Este bloque solo se ejecuta si el archivo se ejecuta directamente (no si se importa)
if __name__ == "__main__":
    # Iniciamos el servidor Flask en modo debug
    # debug=True permite ver errores detallados y reinicia automáticamente al hacer cambios
    app.run(debug=True)