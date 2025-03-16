from django.http import JsonResponse, HttpResponse
from django.db import transaction, connection
from django.db.models import Sum, F
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# 🔹 IMPORTA todos tus Modelos
from .models import (
    Usuario,
    Producto,
    Factura,
    FacturaDetalle,
    PrecioEspecial,
    Descuento,
    CajaDiaria,
    Deudor,
    PagoDeuda,
    RegistroDeuda,
    
)

# 🔹 IMPORTA todos tus Serializers
from .serializers import (
    UsuarioSerializer,
    ProductoSerializer,
    FacturaSerializer,
    FacturaDetalleSerializer,
    PrecioEspecialSerializer,
    DescuentoSerializer,
    FacturaConDetallesSerializer,
    CajaDiariaSerializer,
    DeudorSerializer,
    PagoDeudaSerializer,
    RegistroDeudaSerializer,
 
)

# =========================================================
#                VISTAS BÁSICAS
# =========================================================

def api_root(request):
    return JsonResponse({"message": "Bienvenido a la API de FerreFactura"})

def home(request):
    return HttpResponse("¡Bienvenido a FerreFactura!")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_endpoint(request):
    return Response({"message": "Access granted!"})


# =========================================================
#                 VIEWSETS DE TUS MODELOS
# =========================================================

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]


class FacturaViewSet(viewsets.ModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return FacturaConDetallesSerializer
        return FacturaSerializer

    def create(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                factura_data = {
                    "usuario_id": request.data["usuario_id"],
                    "nombre_cliente": request.data["nombre_cliente"],
                    "fecha_entrega": request.data["fecha_entrega"],
                    "costo_envio": request.data.get("costo_envio", 0),
                    "descuento_total": request.data.get("descuento_total", 0),
                }
                factura = Factura.objects.create(**factura_data)

                for detalle in request.data.get("productos", []):
                    producto = get_object_or_404(Producto, id=detalle["producto_id"])
                    FacturaDetalle.objects.create(
                        factura=factura,
                        producto=producto,
                        cantidad=detalle["cantidad"],
                        precio_unitario=detalle["precio_unitario"],
                        tipo_venta=detalle.get("tipo_venta", "Unidad"),
                    )

                return Response({"message": "Factura creada con éxito!", "id": factura.id})
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class FacturaDetalleViewSet(viewsets.ModelViewSet):
    queryset = FacturaDetalle.objects.all()
    serializer_class = FacturaDetalleSerializer
    permission_classes = [IsAuthenticated]


class PrecioEspecialViewSet(viewsets.ModelViewSet):
    queryset = PrecioEspecial.objects.all()
    serializer_class = PrecioEspecialSerializer
    permission_classes = [IsAuthenticated]


class DescuentoViewSet(viewsets.ModelViewSet):
    queryset = Descuento.objects.all()
    serializer_class = DescuentoSerializer
    permission_classes = [IsAuthenticated]


# 🔹 ViewSet para CajaDiaria
class CajaDiariaViewSet(viewsets.ModelViewSet):
    queryset = CajaDiaria.objects.all()
    serializer_class = CajaDiariaSerializer
    permission_classes = [IsAuthenticated]


# 🔹 ViewSet para Deudores
class DeudorViewSet(viewsets.ModelViewSet):
    queryset = Deudor.objects.all()
    serializer_class = DeudorSerializer
    permission_classes = [IsAuthenticated]

class RegistroDeudaViewSet(viewsets.ModelViewSet):
    queryset = RegistroDeuda.objects.all()
    serializer_class = RegistroDeudaSerializer
    permission_classes = [IsAuthenticated]

# 🔹 ViewSet para Pagos de Deudas
class PagoDeudaViewSet(viewsets.ModelViewSet):
    queryset = PagoDeuda.objects.all()
    serializer_class = PagoDeudaSerializer
    permission_classes = [IsAuthenticated]


# =========================================================
#     VISTAS PERSONALIZADAS (ESTADÍSTICAS, ETC.)
# =========================================================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_facturas_completas(_request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM vw_FacturasCompletas")
        columnas = [col[0] for col in cursor.description]
        filas = cursor.fetchall()
        facturas = [dict(zip(columnas, fila)) for fila in filas]

    return Response(facturas)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_estadisticas_facturas(request):
    hoy = now().date()
    mes_actual = now().month

    facturas_hoy = Factura.objects.filter(fecha_creacion__date=hoy).count()
    facturas_mes = Factura.objects.filter(fecha_creacion__month=mes_actual).count()

    total_ventas = FacturaDetalle.objects.aggregate(
        total=Sum(F('cantidad') * F('precio_unitario'))
    )['total'] or 0

    ganancias_mes = FacturaDetalle.objects.filter(
        factura__fecha_creacion__month=mes_actual
    ).aggregate(
        total=Sum(F('cantidad') * F('precio_unitario'))
    )['total'] or 0

    return Response({
        "facturas_hoy": facturas_hoy,
        "facturas_mes": facturas_mes,
        "total_ventas": round(total_ventas, 2),
        "ganancias_mes": round(ganancias_mes, 2)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_ventas_anuales(request):
    año_actual = now().year

    ventas_mensuales = (
        FacturaDetalle.objects
        .filter(factura__fecha_creacion__year=año_actual)
        .annotate(venta_total=F('cantidad') * F('precio_unitario'))
        .values('factura__fecha_creacion__month')
        .annotate(total_ventas=Sum('venta_total'))
        .order_by('factura__fecha_creacion__month')
    )

    ventas_por_mes = {i: 0 for i in range(1, 13)}
    for venta in ventas_mensuales:
        mes = venta['factura__fecha_creacion__month']
        ventas_por_mes[mes] = float(venta['total_ventas'])

    return Response({"ventas_por_mes": ventas_por_mes})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def obtener_ventas_por_dia(request):
    hoy = now().date()
    mes_actual = hoy.month
    año_actual = hoy.year

    ventas_diarias = (
        FacturaDetalle.objects
        .filter(factura__fecha_creacion__year=año_actual, factura__fecha_creacion__month=mes_actual)
        .annotate(venta_total=F('cantidad') * F('precio_unitario'))
        .values('factura__fecha_creacion__day')
        .annotate(total_ventas=Sum('venta_total'))
        .order_by('factura__fecha_creacion__day')
    )

    ventas_por_dia = {i: 0 for i in range(1, 32)}
    for venta in ventas_diarias:
        dia = venta['factura__fecha_creacion__day']
        ventas_por_dia[dia] = float(venta['total_ventas'])

    return Response({"ventas_por_dia": ventas_por_dia})
