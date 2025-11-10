import re

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
