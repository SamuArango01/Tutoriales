from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View

from .models import Inventario, Libro, Orden
from .infra.factories import PaymentFactory
from .services import CompraRapidaService, CompraService


def compra_rapida_fbv(request, libro_id):
    libro = get_object_or_404(Libro, id=libro_id)

    if request.method == 'POST':
        servicio = CompraRapidaService(procesador_pago=PaymentFactory.get_processor())

        try:
            total = servicio.procesar(libro_id, cantidad=1)
            return HttpResponse(f"Compra exitosa: {libro.titulo}")
        except ValueError as exc:
            return HttpResponse(str(exc), status=400)

    total_estimado = float(libro.precio) * 1.19
    return render(
        request,
        'tienda_app/compra_rapida.html',
        {
            'libro': libro,
            'total': total_estimado,
        },
    )


class InicioView(View):
    """
    Vista inicial: muestra los libros disponibles y enlaza a la compra.
    """

    template_name = 'tienda_app/inicio.html'

    def get(self, request):
        libros = Libro.objects.select_related('inventario').all().order_by('id')
        catalogo = []

        for libro in libros:
            inventario = getattr(libro, 'inventario', None)
            catalogo.append(
                {
                    'libro': libro,
                    'stock': inventario.cantidad if inventario else 0,
                }
            )

        return render(request, self.template_name, {'catalogo': catalogo})


class CompraRapidaView(View):
    """
    CBV: Vista Basada en Clases.
    Actúa como un "Portero": recibe la petición y delega al servicio.
    """

    template_name = 'tienda_app/compra_rapida.html'

    def setup_service(self):
        gateway = PaymentFactory.get_processor()
        return CompraRapidaService(procesador_pago=gateway)

    def get(self, request, libro_id):
        servicio = self.setup_service()
        contexto = servicio.obtener_detalle_producto(libro_id)
        return render(request, self.template_name, contexto)

    def post(self, request, libro_id):
        servicio = self.setup_service()
        try:
            total = servicio.procesar(libro_id, cantidad=1)
            return render(
                request,
                self.template_name,
                {
                    'mensaje_exito': f"¡Gracias por su compra! Total: ${total}",
                    'total': total,
                },
            )
        except (ValueError, Exception) as e:
            return render(request, self.template_name, {'error': str(e)}, status=400)


class CompraView(CompraRapidaView):
    pass
