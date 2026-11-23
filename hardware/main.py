import paho.mqtt.client as mqtt
from rfid_actuadores import Actuadores
from rfid_reader import LectorRFID

actuadores = Actuadores()

def on_connect(client, userdata, flags, reason_code, properties=None):
    print("[MQTT] Conectado al broker local")
    client.subscribe("estacionamiento/#")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode().strip()
    print(f"[MQTT] Recibido -> {topic}: {payload}")

    if topic == "estacionamiento/pluma":
        actuadores.mover_pluma(payload)
    elif topic == "estacionamiento/puerta":
        actuadores.mover_puerta(payload)
    elif topic == "estacionamiento/semaforo":
        actuadores.set_semaforo(payload)

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("127.0.0.1", 1883, 60)
    client.loop_start()  # Escucha MQTT en segundo plano

    lector = LectorRFID(actuadores)
    try:
        lector.bucle_lectura()
    except KeyboardInterrupt:
        print("\nDeteniendo servicio de hardware...")
    finally:
        client.loop_stop()
        actuadores.limpiar()

if __name__ == "__main__":
    main()
