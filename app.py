from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)

# ===============================
# CREAR BASE DE DATOS (NUEVA ESTRUCTURA)
# ===============================
def init_db():
    conn = sqlite3.connect("rrhh.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS postulantes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombres TEXT,
        apellidos TEXT,
        celular TEXT, 
        fecha_nacimiento TEXT,
        ciudad TEXT,
        estudios TEXT,
        salario INTEGER,
        licencia TEXT,
        ventas TEXT,
        excel TEXT,
        disponibilidad TEXT,
        tecnica TEXT,
        puntaje INTEGER
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ===============================
# SISTEMA INTELIGENTE DE PUNTUACIÓN (110 pts)
# ===============================
def calcular_puntaje(estudios, salario, licencia, ventas, excel, disponibilidad, tecnica):
    puntaje = 0

    if estudios == "Estudios Superiores": puntaje += 20
    elif estudios == "Secundario": puntaje += 10
    elif estudios == "Primario": puntaje += 5

    if ventas == "Si": puntaje += 25
    if licencia == "Si": puntaje += 15

    if excel == "Experto": puntaje += 15
    elif excel == "Medio": puntaje += 10
    elif excel == "Basico": puntaje += 5

    if disponibilidad == "Ciudad y provincias": puntaje += 15
    elif disponibilidad == "Solo ciudad": puntaje += 5

    if salario <= 2500: puntaje += 10
    elif salario <= 3500: puntaje += 5

    if len(tecnica.strip()) > 3: 
        puntaje += 10

    return puntaje

# ===============================
# RUTAS DE LA APLICACIÓN
# ===============================
@app.route("/")
def formulario():
    return render_template("index.html")

@app.route("/guardar", methods=["POST"])
def guardar():
    try:
        nombres = request.form.get("nombres", "Sin nombre")
        apellidos = request.form.get("apellidos", "")
        celular = request.form.get("celular", "")
        fecha_nacimiento = request.form.get("fecha_nacimiento", "")
        ciudad = request.form.get("ciudad", "")
        estudios = request.form.get("estudios", "Primario")
        salario = int(request.form.get("salario", "3000"))
        licencia = request.form.get("licencia", "No")
        ventas = request.form.get("ventas", "No")
        excel = request.form.get("excel", "Basico")
        disponibilidad = request.form.get("campo", "Solo ciudad")
        tecnica = request.form.get("tecnica", "")

        puntaje = calcular_puntaje(estudios, salario, licencia, ventas, excel, disponibilidad, tecnica)

        conn = sqlite3.connect("rrhh.db", timeout=15)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO postulantes 
            (nombres, apellidos, celular, fecha_nacimiento, ciudad, estudios, salario, licencia, ventas, excel, disponibilidad, tecnica, puntaje)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nombres, apellidos, celular, fecha_nacimiento, ciudad, estudios, salario, licencia, ventas, excel, disponibilidad, tecnica, puntaje))
        conn.commit()
        conn.close()

        return f"""
        <div style="text-align: center; margin-top: 10vh; font-family: Arial, sans-serif;">
            <h1 style="color: #2e7d32; font-size: 3rem;">✅</h1>
            <h2 style="color: #2e7d32;">¡Postulación enviada exitosamente!</h2>
            <p style="font-size: 1.2rem; margin-top: 20px;">Gracias <strong>{nombres}</strong>. Nuestro equipo de Recursos Humanos evaluará tu perfil.</p>
            <br><br>
            <a href="/" style="padding: 12px 25px; background-color: #2e7d32; color: white; text-decoration: none; border-radius: 8px; font-weight: bold;">Volver al inicio</a>
        </div>
        """
    except Exception as e:
        return f"""
        <div style="text-align: center; margin-top: 10vh; font-family: Arial, sans-serif;">
            <h2 style='color:red;'>🚨 Error al guardar los datos</h2>
            <p>El servidor dice:</p>
            <p style='color:red; font-weight:bold;'>{str(e)}</p>
            <br>
            <a href="/">Volver a intentar</a>
        </div>
        """, 500

@app.route("/admin")
def admin():
    conn = sqlite3.connect("rrhh.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM postulantes ORDER BY puntaje DESC")
    datos = cursor.fetchall()
    conn.close()

    resultado = """
    <div style="max-width: 900px; margin: 40px auto; font-family: Arial, sans-serif;">
        <h2 style='color: #2e7d32; text-align: center; font-weight: bold;'>Panel de Selección - Agromel S.R.L.</h2>
        <hr style="border: 2px solid #2e7d32; margin-bottom: 30px;">
    """
    
    if not datos:
        return resultado + "<p style='text-align:center; font-size: 1.2rem;'>Aún no hay postulantes registrados.</p></div>"

    for index, d in enumerate(datos):
        es_el_mejor = ""
        estilo_borde = "border: 1px solid #ccc; background-color: #fdfdfd;"
        
        if index == 0:
            es_el_mejor = "<span style='background-color: gold; color: black; padding: 4px 10px; border-radius: 20px; font-size: 14px; margin-left: 10px; font-weight: bold;'>👑 MEJOR CANDIDATO</span>"
            estilo_borde = "border: 3px solid gold; background-color: #fffdf0;"

        # Nota: Con la nueva columna, el celular es d[3] y el puntaje pasó a ser d[13]
        resultado += f"""
        <div style="{estilo_borde} padding: 20px; margin-bottom: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                <h3 style="margin: 0; color: #333; font-size: 1.5rem;">#{index + 1} - {d[1]} {d[2]} {es_el_mejor}</h3>
                <h4 style="margin: 0; color: white; background-color: #2e7d32; padding: 8px 15px; border-radius: 5px;">{d[13]} / 110 pts</h4>
            </div>
            
            <div style="font-size: 15px; line-height: 1.8; color: #555; background: white; padding: 15px; border-radius: 8px; border: 1px solid #eee;">
                <strong>📱 Celular:</strong> <a href="https://wa.me/591{d[3]}" target="_blank" style="color: #2e7d32; font-weight: bold; text-decoration: none;">+591 {d[3]}</a> (Clic para WhatsApp)<br>
                <strong>📍 Origen:</strong> {d[5]} | <strong>🎂 Nacimiento:</strong> {d[4]}<br>
                <strong>🎓 Estudios:</strong> {d[6]} | <strong>💰 Salario Esperado:</strong> {d[7]} Bs.<br>
                <strong>💼 Exp. Ventas:</strong> {d[9]} | <strong>🚗 Licencia:</strong> {d[8]}<br>
                <strong>📊 Nivel Excel:</strong> {d[10]} | <strong>⏰ Disponibilidad:</strong> {d[11]}<br>
                <strong>🌱 Conocimiento Agro:</strong> <span style="font-style: italic;">"{d[12]}"</span>
            </div>
        </div>
        """
    
    resultado += "</div>"
    return resultado
