# models.py
# pylint: disable=no-member,invalid-str-returned

from django.db import models
from django.contrib.auth.models import User


# Luego en la función:

class Token(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(
        User,
        related_name='facturacion_auth_token',
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'authtoken_token'
        managed = False  # Si no quieres migrar esta tabla por alguna razón

    def __str__(self):
        return str(self.key)

# =========================================================
#                   MODELO: USUARIOS
# =========================================================
class Usuario(models.Model):
    nombre = models.CharField(max_length=255)
    usuario = models.CharField(max_length=100, unique=True)
    contraseña = models.CharField(max_length=255)
    rol = models.CharField(
        max_length=50,
        choices=[('Cajero', 'Cajero'), ('Administrador', 'Administrador')],
        null=True,
        blank=True
    )
    habilitado = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = 'Usuarios'

    def __str__(self):
        return self.nombre

# =========================================================
#                   MODELO: PRODUCTOS
# =========================================================
class Producto(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=False,
        blank=False,
        default=0
    )
    precio_quintal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    precio_unidad = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    unidades_por_quintal = models.IntegerField(null=True, blank=True)
    categoria = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    stock = models.IntegerField(default=0, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()

    class Meta:
        db_table = 'Productos'

    def __str__(self):
        return self.nombre

# =========================================================
#                   MODELO: FACTURAS
# =========================================================
class Factura(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    nombre_cliente = models.CharField(max_length=255, null=True, blank=True)
    fecha_entrega = models.DateField(null=True, blank=True)
    costo_envio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    descuento_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    objects = models.Manager()

    class Meta:
        db_table = 'Facturas'

    def __str__(self):
        return f'Factura #{self.pk} - {self.nombre_cliente or "Sin Cliente"}'

# =========================================================
#               MODELO: FACTURAS DETALLE
# =========================================================
class FacturaDetalle(models.Model):
    factura = models.ForeignKey('Factura', on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    TIPO_VENTA_CHOICES = [
        ('Unidad', 'Unidad'),
        ('Quintal', 'Quintal'),
    ]
    tipo_venta = models.CharField(
        max_length=20,
        choices=TIPO_VENTA_CHOICES,
        default='Unidad'
    )

    objects = models.Manager()

    class Meta:
        db_table = 'Facturas_Detalle'

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        # Pylint marca error “has no 'nombre' member” por no detectar que
        # producto sí tiene un campo “nombre”. Se ignora con # pylint.
        return f'{self.producto} - {self.cantidad} {self.tipo_venta}'

# =========================================================
#             MODELO: PRECIOS ESPECIALES
# =========================================================
class PrecioEspecial(models.Model):
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    tipo_cliente = models.CharField(max_length=50)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    objects = models.Manager()

    class Meta:
        db_table = 'Precios_Especiales'

    def __str__(self):
        return f'Precio especial {self.tipo_cliente} - {self.producto}'

# =========================================================
#                 MODELO: DESCUENTOS
# =========================================================
class Descuento(models.Model):
    factura = models.ForeignKey('Factura', on_delete=models.CASCADE)
    tipo = models.CharField(
        max_length=50,
        choices=[('Total', 'Total'), ('Por unidad', 'Por unidad')],
        null=True,
        blank=True
    )
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    producto = models.ForeignKey(
        'Producto',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    objects = models.Manager()

    class Meta:
        db_table = 'Descuentos'

    def __str__(self):
        return f'Descuento {self.tipo or "N/A"} - {self.cantidad}'

# =========================================================
#                 MODELO: CAJA DIARIA
# =========================================================
class CajaDiaria(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    cuenta_banco = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sencillo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    gastos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ingreso_extra = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    comentario = models.TextField(blank=True, null=True)

    # 🔹 Campos calculados
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_sin_deuda = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_con_deuda = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        """Calcula los totales antes de guardar."""
        self.total = self.cuenta_banco + self.efectivo + self.sencillo + self.ingreso_extra - self.gastos
        self.total_sin_deuda = self.total  # Sin impacto de deuda aún
        self.total_con_deuda = self.total  # Se puede modificar si hay relación con deudas
        super().save(*args, **kwargs)
    objects = models.Manager()
# �� Campos calculados  
    class Meta:
        db_table = 'CajaDiaria'

    def __str__(self):
        return f"Caja {self.fecha_creacion.strftime('%Y-%m-%d') if self.fecha_creacion else 'Sin Fecha'}"
# =========================================================
#                 MODELO: DEUDORES
# =========================================================
class Deudor(models.Model):
    nombre = models.CharField(max_length=255)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=[('Activo', 'Activo'), ('Pagado', 'Pagado')],
        default='Activo'
    )

    class Meta:
        db_table = 'Deudores'
    objects = models.Manager()
    def __str__(self):
        return self.nombre

# =========================================================
#               MODELO: REGISTRO DE DEUDAS
# =========================================================
class RegistroDeuda(models.Model):
    deudor = models.ForeignKey('Deudor', on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    descripcion = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    comentario = models.TextField(blank=True, null=True)
    objects = models.Manager()
    class Meta:
        db_table = 'RegistrosDeudas'

    def __str__(self):
        # Evita error de Pylint “no 'deudor_id' member”.
        return f"{self.deudor.nombre if self.deudor_id else 'Sin Nombre'} - {self.descripcion}"

# =========================================================
#               MODELO: PAGO DE DEUDAS
# =========================================================
class PagoDeuda(models.Model):
    deudor = models.ForeignKey('Deudor', on_delete=models.CASCADE)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    cantidad_pagada = models.DecimalField(max_digits=10, decimal_places=2)
    caja = models.ForeignKey('CajaDiaria', on_delete=models.CASCADE)
    comentario = models.TextField(blank=True, null=True)
    objects = models.Manager()
    class Meta:
        db_table = 'PagosDeudas'
    objects = models.Manager()
    def __str__(self):
        # Evita error de Pylint “no 'deudor_id' member”.
        return (
            f"{self.deudor.nombre if self.deudor_id else 'Sin Nombre'} "
            f"- Pagó: {self.cantidad_pagada} Q"
        )


class PrintJob(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.TextField()
    printed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
  
    objects = models.Manager()  # Asegura que el modelo tenga un Manager
    class Meta:
        db_table = 'PrintJob'  # 📌 Nombre exacto de la tabla en SQL Server
        managed = False  # 📌 Evita que Django intente administrar esta tabla con migraciones

    def __str__(self):
        return f"PrintJob #{self.id} - {str(self.text)[:30]}..."
