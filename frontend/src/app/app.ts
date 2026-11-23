import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Estacionamiento, EstadoSistema, UsuarioVehiculo, Evento } from './services/estacionamiento';

@Component({
  selector: 'app-root',
  imports: [CommonModule, FormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit, OnDestroy {
  estado: EstadoSistema = { semaforo: 'ROJO', alerta: 'Cargando...', tipo_operacion: null };
  usuarios: UsuarioVehiculo[] = [];
  eventos: Evento[] = [];

  nuevoPropietario = '';
  nuevoLlavero = '';
  nuevaTarjeta = '';
  mensajeEstado = '';
  private intervalo: any;

  constructor(private api: Estacionamiento) {}

  ngOnInit(): void {
    this.cargarTodo();
    this.intervalo = setInterval(() => this.cargarTodo(), 2000);
  }

  ngOnDestroy(): void {
    if (this.intervalo) clearInterval(this.intervalo);
  }

  cargarTodo(): void {
    this.api.getEstado().subscribe(e => this.estado = e);
    this.api.getUsuarios().subscribe(u => this.usuarios = u);
    this.api.getEventos().subscribe(ev => this.eventos = ev);
  }

  registrarUsuario(): void {
    if (!this.nuevoPropietario || !this.nuevoLlavero || !this.nuevaTarjeta) return;
    this.api.crearUsuario(this.nuevoPropietario, this.nuevoLlavero, this.nuevaTarjeta).subscribe({
      next: () => {
        this.mensajeEstado = `Usuario ${this.nuevoPropietario} registrado.`;
        this.nuevoPropietario = '';
        this.nuevoLlavero = '';
        this.nuevaTarjeta = '';
        this.cargarTodo();
      },
      error: (err) => this.mensajeEstado = `Error: ${err.error?.error || 'No se pudo registrar'}`
    });
  }

  accionPluma(accion: 'abrir' | 'cerrar'): void {
    this.api.moverPluma(accion).subscribe(() => {
      this.mensajeEstado = `Pluma vehicular: ${accion}`;
      this.cargarTodo();
    });
  }

  accionPuerta(accion: 'abrir' | 'cerrar'): void {
    this.api.moverPuerta(accion).subscribe(() => {
      this.mensajeEstado = `Puerta peatonal: ${accion}`;
    });
  }
}
