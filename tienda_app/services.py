from django.shortcuts import get_object_or_404

from .domain.builders import OrdenBuilder
from .domain.logic import CalculadorImpuestos
from .models import Inventario, Libro


class CompraRapidaService:
    """
    SERVICE LAYER: Orquesta la interacción entre el dominio,
    la infraestructura y la base de datos.
    """

    def __init__(self, procesador_pago):
        self.procesador_pago = procesador_pago
        self.builder = OrdenBuilder()

    def obtener_detalle_producto(self, libro_id):
        libro = get_object_or_404(Libro, id=libro_id)
        total = CalculadorImpuestos.obtener_total_con_iva(libro.precio)
        return {"libro": libro, "total": total}

    def procesar(self, libro_id, cantidad=1, direccion="", usuario=None):
        libro = get_object_or_404(Libro, id=libro_id)
        inv = Inventario.objects.filter(libro=libro).first()

        if not inv:
            raise ValueError("No hay inventario configurado para este libro.")

        if inv.cantidad < cantidad:
            raise ValueError("No hay suficiente stock para completar la compra.")

        orden = (
            self.builder
            .con_usuario(usuario)
            .con_libro(libro)
            .con_cantidad(cantidad)
            .para_envio(direccion)
            .build()
        )

        pago_exitoso = self.procesador_pago.pagar(orden.total)
        if not pago_exitoso:
            orden.delete()
            raise Exception("La transacción fue rechazada por el banco.")

        inv.cantidad -= cantidad
        inv.save()

        return orden.total

    def ejecutar_compra(self, libro_id, cantidad=1, direccion="", usuario=None):
        return self.procesar(libro_id, cantidad=cantidad, direccion=direccion, usuario=usuario)


CompraService = CompraRapidaService
