import os
import sys
import time
from mfrc522 import SimpleMFRC522

# Permite importar db.py desde ../backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../backend")))
from db import get_db_connection

class LectorRFID:
    def __init__(self, actuadores):
        self.reader = SimpleMFRC522()
        self.actuadores = actuadores

    def leer_uid_hex(self):
        uid_int, _ = self.reader.read()
        return f"{uid_int:X}".upper()

    def procesar_uid(self, uid):
        self.actuadores.beep()
        print(f"[RFID] Detectado UID: {uid}")
        conn = get_db_connection()
        cur = conn.cursor()

        try:
            # 1. ¿Es un llavero (peatón)?
            cur.execute("SELECT * FROM usuarios_vehiculos WHERE uid_llavero = %s;", (uid,))
            usuario = cur.fetchone()
            if usuario:
                nuevo_estado = not usuario["usuario_adentro"]
                accion = "PEATON_ENTRA" if nuevo_estado else "PEATON_SALE"
                detalle = "Acceso peatonal autorizado"

                cur.execute(
                    "UPDATE usuarios_vehiculos SET usuario_adentro = %s WHERE id = %s;",
                    (nuevo_estado, usuario["id"])
                )
                cur.execute(
                    "INSERT INTO eventos (registro_id, tipo_credencial, accion, detalle) VALUES (%s, 'LLAVERO', %s, %s);",
                    (usuario["id"], accion, detalle)
                )
                conn.commit()
                self.actuadores.pulso_puerta_peatonal(3)
                return

            # 2. ¿Es una tarjeta (vehículo)?
            cur.execute("SELECT * FROM usuarios_vehiculos WHERE uid_tarjeta = %s;", (uid,))
            usuario = cur.fetchone()
            if usuario:
                if usuario["vehiculo_adentro"]:
                    # Quiere SALIR: debe haber pasado su llavero antes
                    if not usuario["usuario_adentro"]:
                        cur.execute(
                            "INSERT INTO eventos (registro_id, tipo_credencial, accion, detalle) VALUES (%s, 'TARJETA', 'DENEGADO', 'Intento de salida sin registro peatonal previo');",
                            (usuario["id"],)
                        )
                        cur.execute(
                            "UPDATE estado_sistema SET semaforo = 'ROJO', alerta = %s WHERE id = 1;",
                            (f"DENEGADO: {usuario['propietario']} no registró entrada peatonal",)
                        )
                        conn.commit()
                        self.actuadores.set_semaforo("ROJO")
                        return

                    # Salida válida -> Semáforo amarillo y alerta al operador
                    alerta = f"Vehículo de {usuario['propietario']} listo para SALIR"
                    cur.execute(
                        "UPDATE estado_sistema SET semaforo = 'AMARILLO', alerta = %s, registro_pendiente_id = %s, tipo_operacion = 'SALIDA' WHERE id = 1;",
                        (alerta, usuario["id"])
                    )
                    conn.commit()
                    self.actuadores.set_semaforo("AMARILLO")
                else:
                    # Quiere ENTRAR -> Semáforo amarillo y alerta al operador
                    alerta = f"Vehículo de {usuario['propietario']} solicitando ENTRADA"
                    cur.execute(
                        "UPDATE estado_sistema SET semaforo = 'AMARILLO', alerta = %s, registro_pendiente_id = %s, tipo_operacion = 'ENTRADA' WHERE id = 1;",
                        (alerta, usuario["id"])
                    )
                    conn.commit()
                    self.actuadores.set_semaforo("AMARILLO")
                return

            # 3. Credencial desconocida
            cur.execute(
                "INSERT INTO eventos (registro_id, tipo_credencial, accion, detalle) VALUES (NULL, 'DESCONOCIDO', 'DENEGADO', %s);",
                (f"UID no registrado: {uid}",)
            )
            conn.commit()
            print(f"[RFID] UID no registrado: {uid}")
        finally:
            cur.close()
            conn.close()

    def bucle_lectura(self):
        print("[RFID] Esperando tarjetas/llaveros...")
        while True:
            uid = self.leer_uid_hex()
            self.procesar_uid(uid)
            time.sleep(2)  # Pausa anti-rebote para no leer dos veces seguidas
