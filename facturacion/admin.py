from django.contrib import admin
from .models import Usuario, Producto, Factura, FacturaDetalle, PrecioEspecial, Descuento ,Token


admin.site.register(Usuario)
admin.site.register(Producto)
admin.site.register(Factura)
admin.site.register(FacturaDetalle)
admin.site.register(PrecioEspecial)
admin.site.register(Descuento)
admin.site.register(Token)
