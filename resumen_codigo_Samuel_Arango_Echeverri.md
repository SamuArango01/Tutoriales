# Resumen de Codigo - Tutorial Django SOLID

Estudiante: Samuel Arango Echeverri

## Archivo: tienda_app/services.py

```python
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
        inv = get_object_or_404(Inventario, libro=libro)

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
```

## Archivo: tienda_app/views.py

```python
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
```

## Archivo: tienda_app/infra/factories.py

```python
import os

from .gateways import BancoNacionalProcesador


class MockPaymentProcessor:
    def pagar(self, monto: float) -> bool:
        print(f"[DEBUG] Mock Payment: Procesando pago de ${monto} sin cargo real.")
        return True


class PaymentFactory:
    @staticmethod
    def get_processor():
        provider = os.getenv('PAYMENT_PROVIDER', 'BANCO').strip().upper()

        if provider == 'MOCK':
            return MockPaymentProcessor()

        return BancoNacionalProcesador()
```

## Archivo: tienda_app/domain/builders.py

```python
from decimal import Decimal

from .logic import CalculadorImpuestos
from ..models import Orden


class OrdenBuilder:
    def __init__(self):
        self.reset()

    def reset(self):
        self._usuario = None
        self._libro = None
        self._cantidad = 1
        self._direccion = ""

    def con_usuario(self, usuario):
        self._usuario = usuario
        return self

    def con_libro(self, libro):
        self._libro = libro
        return self

    def con_cantidad(self, cantidad):
        self._cantidad = cantidad
        return self

    def para_envio(self, direccion):
        self._direccion = direccion
        return self

    def build(self) -> Orden:
        if not self._libro:
            raise ValueError("Datos insuficientes para crear la orden.")

        total_unitario = CalculadorImpuestos.obtener_total_con_iva(self._libro.precio)
        total = Decimal(total_unitario) * self._cantidad

        orden = Orden.objects.create(
            usuario=self._usuario,
            libro=self._libro,
            total=total,
            direccion_envio=self._direccion,
        )
        self.reset()
        return orden
```

## Párrafo explicativo: 

OrdenBuilder reduce el riesgo de errores porque concentra en un solo punto la validacion y la construccion de la orden. En lugar de repetir en vistas o servicios la asignacion de campos, el calculo de IVA y la creacion en base de datos, el builder aplica siempre la misma secuencia y verifica que existan datos minimos antes de persistir. Esto evita omisiones comunes (por ejemplo, olvidar direccion, total o validaciones) y hace que el flujo de compra sea mas claro, mantenible y facil de extender cuando cambien reglas de negocio.

## Tutorial 03 - Introduccion a APIs con DRF

### Archivo: tienda_app/api/serializers.py

```python
from rest_framework import serializers

from tienda_app.models import Libro


class LibroSerializer(serializers.ModelSerializer):
    stock_actual = serializers.SerializerMethodField()

    class Meta:
        model = Libro
        fields = ['id', 'titulo', 'precio', 'stock_actual']

    def get_stock_actual(self, obj):
        inventario = getattr(obj, 'inventario', None)
        return inventario.cantidad if inventario else 0


class OrdenInputSerializer(serializers.Serializer):
    libro_id = serializers.IntegerField()
    direccion_envio = serializers.CharField(max_length=200)
    cantidad = serializers.IntegerField(min_value=1, default=1)
```

### Archivo: tienda_app/api/views.py

```python
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from tienda_app.infra.factories import PaymentFactory
from tienda_app.services import CompraService

from .serializers import OrdenInputSerializer


class CompraAPIView(APIView):
    """
    Endpoint para procesar compras via JSON.
    POST /api/v1/comprar/
    Payload: {"libro_id": 1, "direccion_envio": "Calle 123", "cantidad": 1}
    """

    def post(self, request):
        serializer = OrdenInputSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        datos = serializer.validated_data

        try:
            gateway = PaymentFactory.get_processor()
            servicio = CompraService(procesador_pago=gateway)
            usuario = request.user if request.user.is_authenticated else None
            resultado = servicio.ejecutar_compra(
                libro_id=datos['libro_id'],
                cantidad=datos.get('cantidad', 1),
                direccion=datos['direccion_envio'],
                usuario=usuario,
            )

            return Response(
                {
                    'estado': 'exito',
                    'mensaje': f'Orden creada. Total: {resultado}',
                },
                status=status.HTTP_201_CREATED,
            )

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
        except Exception:
            return Response({'error': 'Error interno'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

### Archivo: tienda_app/urls.py

```python
from django.urls import path
from .api.views import CompraAPIView
from .views import CompraRapidaView, CompraView, InicioView, compra_rapida_fbv

urlpatterns = [
    path('', InicioView.as_view(), name='inicio'),
    path('compra-rapida/<int:libro_id>/', compra_rapida_fbv, name='compra_rapida_fbv'),
    path('compra/<int:libro_id>/', CompraRapidaView.as_view(), name='finalizar_compra'),
    path('cbv/compra-rapida/<int:libro_id>/', CompraRapidaView.as_view(), name='compra_rapida_cbv'),
    path('api/v1/comprar/', CompraAPIView.as_view(), name='api_comprar'),
]
```

### Evidencia sugerida para la entrega

1. Levantar servidor y verificar catalogo HTML en la ruta raiz.
2. Enviar POST a /api/v1/comprar/ con payload JSON, por ejemplo:

```json
{
  "libro_id": 1,
  "direccion_envio": "Calle 123",
  "cantidad": 1
}
```

3. Confirmar que el inventario baja en la vista HTML despues del POST.
4. Confirmar que se genera el archivo de log de pagos en la raiz del proyecto.
5. Adjuntar captura de Postman o interfaz web de DRF y evidencia del cambio de inventario/log.
