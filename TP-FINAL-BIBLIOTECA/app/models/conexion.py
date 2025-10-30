import mysql.connector

def obtener_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Lautaroruspil1506",
        database="biblioteca"
    )
