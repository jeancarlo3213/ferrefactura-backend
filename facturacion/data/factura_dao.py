from facturacion.models import Factura, FacturaDetalle, Descuento, Producto

class FacturaDAO:
    @staticmethod
    def obtener_factura(id):
        return Factura.objects.filter(id=id).first()

    @staticmethod
    def crear_factura(datos):
        return Factura.objects.create(
            usuario_id=datos["usuario_id"],
            nombre_cliente=datos.get("nombre_cliente", ""),
            fecha_entrega=datos.get("fecha_entrega", None),
            costo_envio=datos.get("costo_envio", 0),
            descuento_total=datos.get("descuento_total", 0)
        )

    @staticmethod
    def agregar_detalle_factura(factura_id, producto_data):
        producto = Producto.objects.get(id=producto_data["producto_id"])
        cantidad = producto_data["cantidad"]
        precio_unitario = producto.precio
        
        # Aplicar descuento por unidad si existe
        descuento_por_unidad = producto_data.get("descuento_por_unidad", 0)
        precio_final = max(0, precio_unitario - descuento_por_unidad)  # Evitar precios negativos

        detalle = FacturaDetalle.objects.create(
            factura_id=factura_id,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=precio_final
        )

        # Registrar el descuento si se aplicó
        if descuento_por_unidad > 0:
            Descuento.objects.create(
                factura_id=factura_id,
                tipo="Por unidad",
                cantidad=descuento_por_unidad,
                producto=producto
            )

        return detalle
