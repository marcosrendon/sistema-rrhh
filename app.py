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
# GUARDAR POSTULACIÓN (VERSIÓN CORREGIDA)
# ===============================
@app.route("/guardar", methods=["POST"])
def guardar():
    try:
        # 1. Usamos .get() para evitar que la app explote si un dato llega vacío
        nombre = request.form.get("nombre", "Sin nombre")
        
        # 2. Validamos que los números no rompan la aplicación
        experiencia_str = request.form.get("experiencia", "0")
        experiencia = int(experiencia_str) if experiencia_str.isdigit() else 0
        
        agro = request.form.get("agro", "no")
        
        negociacion_str = request.form.get("negociacion", "1")
        negociacion = int(negociacion_str) if negociacion_str.isdigit() else 1
        
        disponibilidad = request.form.get("campo", "ciudad")
        tecnica = request.form.get("tecnica", "Ninguna")

        # Calculamos el puntaje
        puntaje = calcular_puntaje(experiencia, agro, negociacion, disponibilidad)

        # 3. Agregamos timeout por si Render tarda en abrir el archivo SQLite
        conn = sqlite3.connect("rrhh.db", timeout=15)
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
        <br>
        <a href="/">Volver al inicio</a>
        """
    
    except Exception as e:
        # 4. Red de seguridad: Muestra el error exacto en pantalla en vez del Error 500 genérico
        return f"""
        <h2>Error al guardar en la base de datos 🚨</h2>
        <p>El servidor de Render bloqueó la acción por este motivo:</p>
        <p style="color:red; font-weight:bold;">{str(e)}</p>
        <br>
        <a href="/">Volver a intentar</a>
        """, 500


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

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

    


