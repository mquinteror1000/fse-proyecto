DROP TABLE IF EXISTS accesos, tarjetas;

-- Cada usuario tiene su llavero (peatonal) y su tarjeta (vehículo)
CREATE TABLE usuarios_vehiculos (
    id SERIAL PRIMARY KEY,
    propietario VARCHAR(100) NOT NULL,
    uid_llavero VARCHAR(32) UNIQUE NOT NULL,   -- Acceso peatonal
    uid_tarjeta VARCHAR(32) UNIQUE NOT NULL,   -- Acceso vehicular
    usuario_adentro BOOLEAN DEFAULT FALSE,     -- ¿Ya pasó su llavero?
    vehiculo_adentro BOOLEAN DEFAULT TRUE,     -- ¿Está el coche guardado?
    creado_en TIMESTAMPTZ DEFAULT NOW()
);

-- Historial de todo lo que pasa en el estacionamiento
CREATE TABLE eventos (
    id SERIAL PRIMARY KEY,
    registro_id INT REFERENCES usuarios_vehiculos(id) ON DELETE SET NULL,
    tipo_credencial VARCHAR(15) NOT NULL,      -- 'LLAVERO' o 'TARJETA'
    accion VARCHAR(40) NOT NULL,               -- 'PEATON_ENTRA', 'PEATON_SALE', 'VEHICULO_ENTRA', 'VEHICULO_SALE', 'DENEGADO'
    detalle TEXT,
    fecha TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE estado_sistema (
    id SMALLINT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
    semaforo VARCHAR(10) NOT NULL DEFAULT 'ROJO', -- 'ROJO', 'AMARILLO', 'VERDE'
    alerta TEXT DEFAULT 'Sin novedades',
    registro_pendiente_id INT REFERENCES usuarios_vehiculos(id) ON DELETE SET NULL,
    tipo_operacion VARCHAR(10) -- 'ENTRADA' o 'SALIDA'
);

INSERT INTO estado_sistema (id) VALUES (1) ON CONFLICT DO NOTHING;
