from flask import Flask, render_template, request, redirect, url_for
from models.biblioteca import Biblioteca
from models.libro import Libro
from models.usuario import Usuario
from models.conexion import obtener_conexion
from utils.validaciones import validar_usuario_form

app = Flask(__name__)


try:
    conn = obtener_conexion()
    print("✅ Conexión exitosa a MySQL")
    conn.close()
except Exception as e:
    print("❌ Error:", e)

# Instancia global
biblioteca = Biblioteca()


lib1 = Libro(9, "El principito", "Autor 45", "Drama")
lib2 = Libro(19, "Cien Años de soledad", "Gabriel García Márquez", "Terror")
lib3 = Libro(29, "Rayuela", "Javier Milei", "Terror")

# buscar un libro y asignarselo a un usuario inicial
lib_principito = biblioteca.obtener_libro_por_titulo("El principito")
biblioteca.agregar_usuario(
    Usuario(
        "Lautaro",
        "Ruspil",
        23457382,
        "2284-225443",
        "Tierra del fuego",
        1340,
        [lib1, lib2],
    )
)

lib_cien_años_de_soledad = biblioteca.obtener_libro_por_titulo("Cien años de soledad")
biblioteca.agregar_usuario(
    Usuario(
        "Franco",
        "Dell",
        12345678,
        "2284-124443",
        "Tierra del fuego",
        1123,
        [lib1],
    )
)

lib_rayuela = biblioteca.obtener_libro_por_titulo("Rayuela")
biblioteca.agregar_usuario(
    Usuario(
        "Pepe",
        "Martinez",
        23457382,
        "2284-225443",
        "hornos",
        2020,
        [lib3],
    )
)


# --- RUTAS PRINCIPALES ---


@app.route("/")
def inicio():
    return render_template("index.html", biblioteca=biblioteca, active_page="inicio")


# --- Ruta Libros ---


@app.route("/libros", methods=["GET", "POST"])
def libros():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    if request.method == "POST":
        # Insertar nuevo libro (sin ID, MySQL lo autogenera)
        titulo = request.form["titulo"]
        autor = request.form["autor"]
        genero = request.form["genero"]

        cursor.execute(
            "INSERT INTO libros (titulo, autor, genero, prestado) VALUES (%s, %s, %s, %s)",
            (titulo, autor, genero, False),
        )
        conexion.commit()

        cursor.close()
        conexion.close()
        return redirect(url_for("libros"))

    # --- Consultar libros (GET) ---
    q = request.args.get("q", "")

    if q:
        cursor.execute("SELECT * FROM libros WHERE titulo LIKE %s", (f"%{q}%",))
    else:
        cursor.execute("SELECT * FROM libros")

    filas = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Convertir cada fila (dict) en objeto Libro
    libros = [Libro(**fila) for fila in filas]

    return render_template("libros.html", books=libros, q=q, active_page="libros")


@app.route("/prestar/<int:id_libro>", methods=["POST"])
def prestar(id_libro):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("UPDATE libros SET prestado = TRUE WHERE id_libro = %s", (id_libro,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect(url_for("libros"))


@app.route("/devolver/<int:id_libro>", methods=["POST"])
def devolver(id_libro):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute(
        "UPDATE libros SET prestado = FALSE WHERE id_libro = %s", (id_libro,)
    )
    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect(url_for("libros"))


@app.route("/eliminar/<int:id_libro>", methods=["POST"])
def eliminar(id_libro):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM libros WHERE id_libro = %s", (id_libro,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return redirect(url_for("libros"))


# --- Ruta Prestamos ---[
@app.route("/prestamos", methods=['GET'])
def prestamos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    prestados = [l for l in biblioteca.libros if l.prestado]
    # --- Consultar libros (GET) ---
    q = request.args.get("q", "")
    if q:
        cursor.execute("SELECT * FROM libros WHERE titulo LIKE %s", (f"%{q}%",))
    else:
        cursor.execute("SELECT * FROM libros")
    

    return render_template("prestamos.html", books=prestados, active_page="prestamos")


# --- Ruta Usuarios ---


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


if __name__ == "__main__":
    app.run(debug=True)
