import time
import RPi.GPIO as GPIO

# Pines BCM
PIN_PLUMA = 12
PIN_PUERTA = 13
PIN_ROJO = 17
PIN_AMARILLO = 27
PIN_VERDE = 22

# Duty cycles típicos para SG90 (ajusta si tu maqueta requiere otro ángulo)
ANGULO_CERRADO = 2.5   # ~0°
ANGULO_ABIERTO = 7.5   # ~90°

class Actuadores:
    def __init__(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        # LEDs
        for pin in (PIN_ROJO, PIN_AMARILLO, PIN_VERDE):
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)

        # Servos (50 Hz)
        GPIO.setup(PIN_PLUMA, GPIO.OUT)
        GPIO.setup(PIN_PUERTA, GPIO.OUT)
        self.pwm_pluma = GPIO.PWM(PIN_PLUMA, 50)
        self.pwm_puerta = GPIO.PWM(PIN_PUERTA, 50)
        self.pwm_pluma.start(0)
        self.pwm_puerta.start(0)

        # Estado inicial seguro
        self.mover_pluma("cerrar")
        self.mover_puerta("cerrar")
        self.set_semaforo("ROJO")

    def _mover_servo(self, pwm, duty):
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.5)
        pwm.ChangeDutyCycle(0)  # Evita zumbido y calentamiento del SG90

    def mover_pluma(self, accion):
        duty = ANGULO_ABIERTO if accion == "abrir" else ANGULO_CERRADO
        self._mover_servo(self.pwm_pluma, duty)
        print(f"[HW] Pluma vehicular -> {accion}")

    def mover_puerta(self, accion):
        duty = ANGULO_ABIERTO if accion == "abrir" else ANGULO_CERRADO
        self._mover_servo(self.pwm_puerta, duty)
        print(f"[HW] Puerta peatonal -> {accion}")

    def pulso_puerta_peatonal(self, segundos=3):
        self.mover_puerta("abrir")
        time.sleep(segundos)
        self.mover_puerta("cerrar")

    def set_semaforo(self, color):
        color = color.upper()
        GPIO.output(PIN_ROJO, GPIO.HIGH if color == "ROJO" else GPIO.LOW)
        GPIO.output(PIN_AMARILLO, GPIO.HIGH if color == "AMARILLO" else GPIO.LOW)
        GPIO.output(PIN_VERDE, GPIO.HIGH if color == "VERDE" else GPIO.LOW)
        print(f"[HW] Semáforo -> {color}")

    def limpiar(self):
        self.pwm_pluma.stop()
        self.pwm_puerta.stop()
        GPIO.cleanup()
