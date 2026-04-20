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
