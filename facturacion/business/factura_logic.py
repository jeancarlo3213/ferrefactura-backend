from facturacion.data.factura_dao import FacturaDAO
from facturacion.models import FacturaDetalle, Descuento

class FacturaLogic:
    @staticmethod
    def procesar_factura(datos):
        if 'descuento_total' in datos and datos['descuento_total'] < 0:
            raise ValueError("El descuento total no puede ser negativo.")
        
        # Crear la factura
        factura = FacturaDAO.crear_factura(datos)

        # Si hay productos en la factura, agregarlos con su respectivo descuento
        if "productos" in datos:
            for producto_data in datos["productos"]:
                FacturaDAO.agregar_detalle_factura(factura.id, producto_data)

        return factura
