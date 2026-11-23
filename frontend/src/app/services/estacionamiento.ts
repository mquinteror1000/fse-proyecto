import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface EstadoSistema {
  semaforo: 'ROJO' | 'AMARILLO' | 'VERDE';
  alerta: string;
  tipo_operacion: string | null;
}

export interface UsuarioVehiculo {
  id: number;
  propietario: string;
  uid_llavero: string;
  uid_tarjeta: string;
  usuario_adentro: boolean;
  vehiculo_adentro: boolean;
}

export interface Evento {
  id: number;
  propietario: string;
  tipo_credencial: string;
  accion: string;
  detalle: string;
  fecha: string;
}

@Injectable({ providedIn: 'root' })
export class Estacionamiento {
  private apiUrl = '/api';

  constructor(private http: HttpClient) {}

  getEstado(): Observable<EstadoSistema> {
    return this.http.get<EstadoSistema>(`${this.apiUrl}/estado`);
  }

  getUsuarios(): Observable<UsuarioVehiculo[]> {
    return this.http.get<UsuarioVehiculo[]>(`${this.apiUrl}/usuarios`);
  }

  crearUsuario(propietario: string, uid_llavero: string, uid_tarjeta: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/usuarios`, { propietario, uid_llavero, uid_tarjeta });
  }

  getEventos(): Observable<Evento[]> {
    return this.http.get<Evento[]>(`${this.apiUrl}/eventos`);
  }

  moverPluma(accion: 'abrir' | 'cerrar'): Observable<any> {
    return this.http.post(`${this.apiUrl}/actuadores/pluma`, { accion });
  }

  moverPuerta(accion: 'abrir' | 'cerrar'): Observable<any> {
    return this.http.post(`${this.apiUrl}/actuadores/puerta`, { accion });
  }
}
