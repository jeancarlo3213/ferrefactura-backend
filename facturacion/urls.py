from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

# 🔹 Importa las vistas y ViewSets
from .views import (
    api_root,
    protected_endpoint,
    UsuarioViewSet,
    ProductoViewSet,
    FacturaViewSet,
    FacturaDetalleViewSet,
    PrecioEspecialViewSet,
    DescuentoViewSet,
    CajaDiariaViewSet,
    DeudorViewSet,
    PagoDeudaViewSet,         # <-- Importados para el router
    obtener_facturas_completas,
    obtener_estadisticas_facturas,
    obtener_ventas_anuales,
    obtener_ventas_por_dia,
    RegistroDeudaViewSet,
    add_print_job,
    get_pending_jobs,
    mark_as_printed,
)

# 🔹 Configurar router para los ViewSets
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet)
router.register(r'productos', ProductoViewSet)
router.register(r'facturas', FacturaViewSet)
router.register(r'facturas-detalle', FacturaDetalleViewSet)
router.register(r'precios-especiales', PrecioEspecialViewSet)
router.register(r'descuentos', DescuentoViewSet)
router.register(r'caja-diaria', CajaDiariaViewSet)  # Nuevo
router.register(r'deudores', DeudorViewSet)         # Nuevo
router.register(r'registros-deudas', RegistroDeudaViewSet)
router.register(r'pagos-deudas', PagoDeudaViewSet)  # Nuevo

urlpatterns = [
    path('', api_root, name='api-root'),
    path('', include(router.urls)),
    path('protected-endpoint/', protected_endpoint, name='protected-endpoint'),
    path('facturas-completas/', obtener_facturas_completas, name='facturas_completas'),
    path('estadisticas-facturas/', obtener_estadisticas_facturas, name='estadisticas_facturas'),
    path('ventas-anuales/', obtener_ventas_anuales, name='ventas_anuales'),
    path('ventas-diarias/', obtener_ventas_por_dia, name='ventas_diarias'),
    path('api-token-auth/', obtain_auth_token, name='api-token-auth'),
    path('add_print/', add_print_job),  # Para agregar una orden de impresión
    path('get_jobs/', get_pending_jobs),  # Para obtener las órdenes pendientes
    path('mark_printed/<int:job_id>/', mark_as_printed),  # Para marcar una orden como impresa
]
