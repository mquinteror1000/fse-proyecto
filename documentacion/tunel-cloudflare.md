## Configuración del túnel de cloudflare.

La anterior arquitectura que involucraba una base de datos como medio de comunicación entre la interfaz de usuario y la Raspberry Pi resultó ser demasiado complicada. Afortunadamente después de hacer la práctica 5 y poner el práctica el protocolo MQTT se ha llegar a una solución mas oṕtima en la que se prescinde por completo de la nube.

Nueva arquitectura del sistema

```plantuml
@startuml
left to right direction
skinparam shadowing false

actor "Operador" as U

cloud "Cloudflare" {
  agent "fse.mquinteror.net\n(Cloudflare Tunnel)" as CF
}

node "Raspberry Pi (Red Local)" {
  agent "cloudflared" as Tunnel
  component "Interfaz Web (UI)" as UI
  queue "Broker MQTT\n(Mosquitto)" as MQTT
  component "Script Controlador\n(GPIO / Sensores)" as App
}

U <--> CF : HTTPS
CF <--> Tunnel : Túnel cifrado
Tunnel <--> UI : HTTP local
UI <--> MQTT : Pub / Sub (WebSockets)
MQTT <--> App : Pub / Sub (TCP 1883)
@enduml
```
