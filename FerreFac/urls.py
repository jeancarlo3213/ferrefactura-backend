from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from facturacion.views import api_root  # Importa api_root para la ruta raíz
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Configuración de la documentación con drf-yasg
schema_view = get_schema_view(
    openapi.Info(
        title="FerreFactura API",
        default_version='v1',
        description="Documentación interactiva de la API de FerreFactura",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="soporte@ferrefactura.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('', api_root, name='api-root'),  # Página de bienvenida de la API
    path('admin/', admin.site.urls),  # Panel de administración de Django
    path('api/', include('facturacion.urls')),  # Incluye las rutas de la app "facturacion"
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),  # Endpoint de autenticación

    # Documentación de la API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
