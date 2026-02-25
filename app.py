from flask import Flask, request, render_template
import sqlite3
import qrcode
import socket

app = Flask(__name__)

# ===============================
# CREAR BASE DE DATOS
# ===============================
def init_db():
    conn = sqlite3.connect("rrhh.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS postulantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        experiencia INTEGER,
        agro TEXT,
        negociacion INTEGER,
        disponibilidad TEXT,
        tecnica TEXT,
        puntaje INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ===============================
# CALCULAR PUNTAJE AUTOMÁTICO
# ===============================
def calcular_puntaje(experiencia, agro, negociacion, disponibilidad):
    puntaje = 0

    # Experiencia general
    puntaje += experiencia * 2

    # Experiencia agro
    if agro == "si":
        puntaje += 10

    # Negociación
    puntaje += negociacion * 3

    # Disponibilidad
    if disponibilidad == "provincias":
        puntaje += 5

    return puntaje


# ===============================
# FORMULARIO WEB
# ===============================
@app.route("/")
def formulario():
    return render_template("index.html")


# ===============================
# GUARDAR POSTULACIÓN
# ===============================
@app.route("/guardar", methods=["POST"])
def guardar():
    nombre = request.form["nombre"]
    experiencia = int(request.form["experiencia"])
    agro = request.form["agro"]
    negociacion = int(request.form["negociacion"])
    disponibilidad = request.form["campo"]
    tecnica = request.form["tecnica"]

    puntaje = calcular_puntaje(experiencia, agro, negociacion, disponibilidad)

    conn = sqlite3.connect("rrhh.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO postulantes 
        (nombre, experiencia, agro, negociacion, disponibilidad, tecnica, puntaje)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nombre, experiencia, agro, negociacion, disponibilidad, tecnica, puntaje))
    conn.commit()
    conn.close()

    return f"""
    <h2>Postulación enviada correctamente ✅</h2>
    <h3>Puntaje obtenido: {puntaje}</h3>
    <a href="/">Volver</a>
    """


# ===============================
# PANEL ADMINISTRADOR
# ===============================
@app.route("/admin")
def admin():
    conn = sqlite3.connect("rrhh.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM postulantes ORDER BY puntaje DESC")
    datos = cursor.fetchall()
    conn.close()

    resultado = "<h2>Ranking de Postulantes - Asesor de Ventas</h2>"

    for d in datos:
        resultado += f"""
        <p>
        <strong>{d[1]}</strong><br>
        Experiencia: {d[2]} años<br>
        Agro: {d[3]}<br>
        Negociación: {d[4]}<br>
        Disponibilidad: {d[5]}<br>
        Puntaje Total: <strong>{d[7]}</strong>
        </p>
        <hr>
        """

    return resultado


# ===============================
# GENERAR QR
# ===============================
if __name__ == "__main__":
    # NO pongas app.run aquí
    