from flask import Flask, jsonify, request
from db import get_db_connection

app = Flask(__name__)

# --- CONSULTAS DE ESTADO Y DATOS ---
@app.route("/api/estado", methods=["GET"])
def obtener_estado():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT semaforo, alerta, tipo_operacion FROM estado_sistema WHERE id = 1;")
    estado = cur.fetchone()
    cur.close()
    conn.close()
    return jsonify(estado)

@app.route("/api/usuarios", methods=["GET"])
def obtener_usuarios():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios_vehiculos ORDER BY id DESC;")
    filas = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(filas)

@app.route("/api/usuarios", methods=["POST"])
def crear_usuario():
    data = request.get_json()
    propietario = data.get("propietario", "").strip()
    llavero = data.get("uid_llavero", "").strip().upper()
    tarjeta = data.get("uid_tarjeta", "").strip().upper()

    if not propietario or not llavero or not tarjeta:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            """INSERT INTO usuarios_vehiculos (propietario, uid_llavero, uid_tarjeta)
               VALUES (%s, %s, %s) RETURNING id;""",
            (propietario, llavero, tarjeta)
        )
        nuevo_id = cur.fetchone()["id"]
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 409
    finally:
        cur.close()
        conn.close()

    return jsonify({"id": nuevo_id, "status": "creado"}), 201

@app.route("/api/eventos", methods=["GET"])
def obtener_eventos():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.id, COALESCE(u.propietario, 'Desconocido') AS propietario,
               e.tipo_credencial, e.accion, e.detalle, e.fecha
        FROM eventos e
        LEFT JOIN usuarios_vehiculos u ON e.registro_id = u.id
        ORDER BY e.fecha DESC
        LIMIT 50;
    """)
    filas = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(filas)

# --- CONTROL DE ACTUADORES ---
@app.route("/api/actuadores/pluma", methods=["POST"])
def controlar_pluma():
    accion = request.get_json().get("accion") # "abrir" o "cerrar"
    if accion not in ("abrir", "cerrar"):
        return jsonify({"error": "Acción inválida"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT registro_pendiente_id, tipo_operacion FROM estado_sistema WHERE id = 1;")
    est = cur.fetchone()

    if accion == "abrir":
        # TODO MQTT: publicar "abrir" en "estacionamiento/pluma" y "VERDE" en "estacionamiento/semaforo"
        cur.execute(
            "UPDATE estado_sistema SET semaforo = 'VERDE', alerta = 'Pluma abierta: vehículo en paso' WHERE id = 1;"
        )
    else:
        # TODO MQTT: publicar "cerrar" en "estacionamiento/pluma" y "ROJO" en "estacionamiento/semaforo"
        # Si había un vehículo en tránsito, actualizamos su estado en BD
        if est["registro_pendiente_id"] and est["tipo_operacion"]:
            if est["tipo_operacion"] == "SALIDA":
                cur.execute(
                    "UPDATE usuarios_vehiculos SET vehiculo_adentro = FALSE, usuario_adentro = FALSE WHERE id = %s;",
                    (est["registro_pendiente_id"],)
                )
                cur.execute(
                    "INSERT INTO eventos (registro_id, tipo_credencial, accion, detalle) VALUES (%s, 'TARJETA', 'VEHICULO_SALE', 'Pluma cerrada tras salida');",
                    (est["registro_pendiente_id"],)
                )
            elif est["tipo_operacion"] == "ENTRADA":
                cur.execute(
                    "UPDATE usuarios_vehiculos SET vehiculo_adentro = TRUE, usuario_adentro = TRUE WHERE id = %s;",
                    (est["registro_pendiente_id"],)
                )
                cur.execute(
                    "INSERT INTO eventos (registro_id, tipo_credencial, accion, detalle) VALUES (%s, 'TARJETA', 'VEHICULO_ENTRA', 'Pluma cerrada tras entrada');",
                    (est["registro_pendiente_id"],)
                )

        cur.execute(
            "UPDATE estado_sistema SET semaforo = 'ROJO', alerta = 'Sin novedades', registro_pendiente_id = NULL, tipo_operacion = NULL WHERE id = 1;"
        )

    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok", "actuador": "pluma", "accion": accion})

@app.route("/api/actuadores/puerta", methods=["POST"])
def controlar_puerta():
    accion = request.get_json().get("accion") # "abrir" o "cerrar"
    if accion not in ("abrir", "cerrar"):
        return jsonify({"error": "Acción inválida"}), 400

    # TODO MQTT: publicar accion en "estacionamiento/puerta"
    print(f"[ACTUADOR] Puerta peatonal -> {accion}")
    return jsonify({"status": "ok", "actuador": "puerta", "accion": accion})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
