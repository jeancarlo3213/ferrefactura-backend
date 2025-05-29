from django.http import JsonResponse, HttpResponse
from django.db import transaction, connection
from django.db.models import Sum, F
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Noviazgo
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import PrintJob
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



@csrf_exempt
def add_print_job(request):
    if request.method == "POST":
        data = json.loads(request.body)
        text = data.get("text", "")

        job = PrintJob.objects.create(text=text)
        return JsonResponse({"message": "Orden de impresión guardada", "job_id": job.id})

    return JsonResponse({"error": "Método no permitido"}, status=405)

# Endpoint para obtener órdenes de impresión pendientes
def get_pending_jobs(request):
    jobs = PrintJob.objects.filter(printed=False).order_by("created_at")  # Solo las NO impresas
    return JsonResponse({"jobs": list(jobs.values())})

# Endpoint para marcar una orden como impresa
@csrf_exempt
def mark_as_printed(request, job_id):
    if request.method == "POST":
        try:
            job = PrintJob.objects.get(id=job_id)
            job.printed = True  # 🔹 Marcar como impresa
            job.save()
            return JsonResponse({"message": "Orden marcada como impresa"})
        except PrintJob.DoesNotExist:
            return JsonResponse({"error": "Orden no encontrada"}, status=404)
    return JsonResponse({"error": "Método no permitido"}, status=405)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_ganancias_producto(request):
    """
    Devuelve la ganancia total por producto (unidad/quintal), incluyendo el margen porcentual.
    """
    resultados = []

    detalles = FacturaDetalle.objects.select_related('producto')

    for detalle in detalles:
        producto = detalle.producto
        cantidad = detalle.cantidad
        tipo = detalle.tipo_venta

        if tipo == "Unidad" and producto.precio_compra_unidad is not None:
            ganancia_unitaria = float(producto.precio) - float(producto.precio_compra_unidad)
            ganancia_total = ganancia_unitaria * cantidad
            margen = (ganancia_unitaria / float(producto.precio_compra_unidad)) * 100

        elif tipo == "Quintal" and producto.precio_compra_quintal is not None:
            ganancia_quintal = float(producto.precio_quintal) - float(producto.precio_compra_quintal)
            ganancia_total = ganancia_quintal * cantidad
            margen = (ganancia_quintal / float(producto.precio_compra_quintal)) * 100

        else:
            ganancia_total = None
            margen = None

        resultados.append({
            "producto": producto.nombre,
            "tipo_venta": tipo,
            "cantidad_vendida": cantidad,
            "ganancia_total": round(ganancia_total, 2) if ganancia_total is not None else "Sin datos",
            "margen_porcentual": round(margen, 2) if margen is not None else "Sin datos"
        })

    return Response(resultados)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_ganancias_por_producto(request):
    """
    Devuelve un resumen agrupado por producto con su ganancia total.
    """
    resultados = {}

    detalles = FacturaDetalle.objects.select_related('producto')

    for detalle in detalles:
        producto = detalle.producto
        tipo = detalle.tipo_venta
        key = f"{producto.id}_{tipo}"

        if key not in resultados:
            resultados[key] = {
                "producto": producto.nombre,
                "tipo_venta": tipo,
                "cantidad_total": 0,
                "ganancia_total": 0.0,
                "margen_porcentual": None
            }

        resultados[key]["cantidad_total"] += detalle.cantidad

        if tipo == "Unidad" and producto.precio_compra_unidad is not None:
            ganancia_unitaria = float(producto.precio) - float(producto.precio_compra_unidad)
            resultados[key]["ganancia_total"] += ganancia_unitaria * detalle.cantidad
            resultados[key]["margen_porcentual"] = round((ganancia_unitaria / float(producto.precio_compra_unidad)) * 100, 2)

        elif tipo == "Quintal" and producto.precio_compra_quintal is not None:
            ganancia_quintal = float(producto.precio_quintal) - float(producto.precio_compra_quintal)
            resultados[key]["ganancia_total"] += ganancia_quintal * detalle.cantidad
            resultados[key]["margen_porcentual"] = round((ganancia_quintal / float(producto.precio_compra_quintal)) * 100, 2)

        else:
            resultados[key]["ganancia_total"] = "Sin datos"
            resultados[key]["margen_porcentual"] = "Sin datos"

    return Response(list(resultados.values()))


# facturacion/views.py

from .models import Noviazgo
from .serializers import NoviazgoSerializer

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def guardar_noviazgo(request):
    """
    Crea un Noviazgo usando auto_now_add de Django
    """
    nombre = request.data.get("nombre", "Anónimo")
    nov = Noviazgo.objects.create(nombre=nombre)    # ← usa ORM
    serializer = NoviazgoSerializer(nov)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def obtener_noviazgo(request):
    """
    Recupera el último registro (o devuelve mensaje si no hay)
    """
    try:
        nov = Noviazgo.objects.latest('fecha_aceptacion')
    except Noviazgo.DoesNotExist:
        return Response({"mensaje": "Aún no hay registro de noviazgo."})
    serializer = NoviazgoSerializer(nov)
    return Response(serializer.data)
