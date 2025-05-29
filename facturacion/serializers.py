from rest_framework import serializers
from .models import Usuario, Producto, Factura, FacturaDetalle, PrecioEspecial, Descuento, CajaDiaria, Deudor, RegistroDeuda, PagoDeuda
from .models import Noviazgo
# ===========================
#   SERIALIZER: USUARIOS
# ===========================
class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'

#   SERIALIZER: PRODUCTOS
# ===========================
class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

    def validate_precio(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio no puede ser negativo.")
        return value


# ===========================
#   SERIALIZER: FACTURAS
# ===========================
class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = '__all__'

    def validate_descuento_total(self, value):
        if value < 0:
            raise serializers.ValidationError("El descuento total no puede ser negativo.")
        return value


# ===========================
#   SERIALIZER: DETALLES DE FACTURA
# ===========================
class FacturaDetalleSerializer(serializers.ModelSerializer):
    # Información adicional del producto (solo lectura)
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    precio_quintal = serializers.DecimalField(source="producto.precio_quintal", max_digits=10, decimal_places=2, read_only=True)
    precio_unidad = serializers.DecimalField(source="producto.precio_unidad", max_digits=10, decimal_places=2, read_only=True)
    categoria = serializers.CharField(source="producto.categoria", read_only=True)

    class Meta:
        model = FacturaDetalle
        fields = [
            "id",
            "factura",
            "producto",
            "producto_nombre",
            "cantidad",
            "precio_unitario",
            "tipo_venta",
            "precio_quintal",
            "precio_unidad",
            "categoria",
        ]


# ===========================
#   SERIALIZER: FACTURA CON DETALLES ANIDADOS
# ===========================
class FacturaConDetallesSerializer(serializers.ModelSerializer):
    detalles = FacturaDetalleSerializer(many=True, read_only=True, source='facturadetalle_set')

    class Meta:
        model = Factura
        fields = [
            'id', 
            'fecha_creacion', 
            'usuario', 
            'nombre_cliente',
            'fecha_entrega', 
            'costo_envio', 
            'descuento_total',
            'detalles'
        ]


# ===========================
#   SERIALIZER: PRECIOS ESPECIALES
# ===========================
class PrecioEspecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrecioEspecial
        fields = '__all__'

    def validate_precio(self, value):
        if value <= 0:
            raise serializers.ValidationError("El precio especial debe ser mayor a 0.")
        return value


# ===========================
#   SERIALIZER: DESCUENTOS
# ===========================
class DescuentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Descuento
        fields = '__all__'

    def validate_cantidad(self, value):
        if value < 0:
            raise serializers.ValidationError("El descuento no puede ser negativo.")
        return value


# ===========================
#   SERIALIZER: CAJA DIARIA
# ===========================
class CajaDiariaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CajaDiaria
        fields = '__all__'

    def validate(self, data):
        """Validar que los valores sean correctos antes de guardar"""
        if data['cuenta_banco'] < 0:
            raise serializers.ValidationError("La cuenta del banco no puede ser negativa.")
        if data['efectivo'] < 0:
            raise serializers.ValidationError("El efectivo no puede ser negativo.")
        if data['sencillo'] < 0:
            raise serializers.ValidationError("El sencillo no puede ser negativo.")
        if data['gastos'] < 0:
            raise serializers.ValidationError("Los gastos no pueden ser negativos.")
        if data['ingreso_extra'] < 0:
            raise serializers.ValidationError("El ingreso extra no puede ser negativo.")
        return data

# ===========================
#   SERIALIZER: DEUDORES
# ===========================
class DeudorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deudor
        fields = '__all__'


# ===========================
#   SERIALIZER: REGISTRO DE DEUDAS
# ===========================
class RegistroDeudaSerializer(serializers.ModelSerializer):
    deudor_nombre = serializers.CharField(source='deudor.nombre', read_only=True)

    class Meta:
        model = RegistroDeuda
        fields = '__all__'

    def validate_cantidad(self, value):
        if value < 0:
            raise serializers.ValidationError("La cantidad no puede ser negativa.")
        return value


# ===========================
#   SERIALIZER: PAGO DE DEUDAS
# ===========================
class PagoDeudaSerializer(serializers.ModelSerializer):
    deudor_nombre = serializers.CharField(source='deudor.nombre', read_only=True)

    class Meta:
        model = PagoDeuda
        fields = '__all__'

    def validate_cantidad_pagada(self, value):
        if value < 0:
            raise serializers.ValidationError("El pago no puede ser negativo.")
        return value
    

    def validate_usuario(self, value):
        if not value.strip():
            raise serializers.ValidationError("El nombre de usuario no puede estar vacío.")
        return value


# ===========================

class NoviazgoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Noviazgo
        fields = ['id', 'nombre', 'fecha_aceptacion']