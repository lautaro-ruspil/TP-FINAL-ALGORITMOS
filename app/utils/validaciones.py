import re


def validar_usuario_form(form):
    # Expresiones regulares
    solo_letras = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúñÑ\s]+$")
    solo_numeros = re.compile(r"^\d+$")
    # Expresión regular para 4 dígitos, guion, 6 dígitos
    patron_telefono = re.compile(r"^\d{4}-\d{6}$")

    # Tomamos los valores del formulario
    nombre = form.get("nombre", "").strip()
    apellido = form.get("apellido", "").strip()
    dni = form.get("dni", "").strip()
    telefono = form.get("telefono", "").strip()
    direccion = form.get("direccion", "").strip()
    nro_direccion = form.get("nro_direccion", "").strip()

    # diccionario de errores
    errores = {}

    # Validaciones

    # Nombre
    if not nombre:
        errores["nombre"] = "El nombre es obligatorio."
    if len(nombre) < 3 or not solo_letras.match(nombre):
        errores[
            "nombre"
        ] = """El nombre debe tener al menos 3 letras 
              y solo contener letras."""

    # Apellido
    if not apellido:
        errores["apellido"] = "El apellido es obligatorio."
    if len(apellido) < 3 or not solo_letras.match(apellido):
        errores[
            "apellido"
        ] = """El apellido debe tener al menos 3 letras 
                y solo contener letras."""

    # DNI
    if not dni:
        errores["dni"] = "El DNI es obligatorio."
    if not solo_numeros.match(dni) or len(dni) < 7 or len(dni) > 8:
        errores["dni"] = "El DNI debe ser numérico con 7 u 8 dígitos."

    # Teléfono
    if not telefono:
        errores["telefono"] = "El teléfono es obligatorio."
    if not patron_telefono.match(telefono):
        errores["telefono"] = (
            "El teléfono debe tener el formato XXXX-XXXXXX (10 dígitos con guion)."
        )

    # Dirección
    if not direccion:
        errores["direccion"] = "La dirección es obligatoria."
    if len(direccion) < 2:
        errores["direccion"] = "La dirección debe tener al menos 2 caracteres."

    # Número de dirección
    if not nro_direccion:
        errores["nro_direccion"] = "El número de dirección es obligatorio."
    if not solo_numeros.match(nro_direccion):
        errores["nro_direccion"] = "El número de dirección debe contener solo números."

    # si hay errores retorna false y el diccionario de errores
    if errores:
        return False, errores
    else:
        return True, {}

############ VALIDACIÓN LIBROS #################

def validar_libro_form(form):
    # Expresiones regulares:
    solo_letras = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ\s-]+$")  # Solo letras y espacios
    letras_numeros = re.compile(r"^[A-Za-zÁÉÍÓÚáéíóúÑñ0-9\s\.,:-]+$")  # Para títulos

    titulo = form.get("titulo", "").strip()
    autor = form.get("autor", "").strip()
    genero = form.get("genero", "").strip()

    errores = {}

    # --- Validación de título ---
    if not titulo:
        errores["titulo"] = "El título es obligatorio."
    elif len(titulo) < 2:
        errores["titulo"] = "El título debe tener al menos 2 caracteres."
    elif not letras_numeros.match(titulo):
        errores["titulo"] = "El título no puede contener símbolos especiales."

    # --- Validación de autor ---
    if not autor:
        errores["autor"] = "El autor es obligatorio."
    elif len(autor) < 3:
        errores["autor"] = "El autor debe tener al menos 3 caracteres."
    elif not solo_letras.match(autor):
        errores["autor"] = "El autor solo puede contener letras y espacios."

    # --- Validación de género ---
    if not genero:
        errores["genero"] = "El género es obligatorio."
    elif len(genero) < 3:
        errores["genero"] = "El género debe tener al menos 3 caracteres."
    elif not solo_letras.match(genero):
        errores["genero"] = "El género solo puede contener letras y espacios."

    if errores:
        return False, errores
    return True, {}
