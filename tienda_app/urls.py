from django.urls import path
from .api.views import CompraAPIView
from .views import CompraRapidaView, CompraView, InicioView, compra_rapida_fbv

urlpatterns = [
    path('', InicioView.as_view(), name='inicio'),
    path('compra-rapida/<int:libro_id>/', compra_rapida_fbv, name='compra_rapida_fbv'),
    # Usamos .as_view() para habilitar la CBV
    path('compra/<int:libro_id>/', CompraRapidaView.as_view(), name='finalizar_compra'),
    path('cbv/compra-rapida/<int:libro_id>/', CompraRapidaView.as_view(), name='compra_rapida_cbv'),
    path('api/v1/comprar/', CompraAPIView.as_view(), name='api_comprar'),
]