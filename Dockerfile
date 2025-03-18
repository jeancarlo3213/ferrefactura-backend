# Usa una imagen oficial de Python con soporte para SQL Server
FROM python:3.11

# Instala dependencias del sistema
RUN apt-get update && \
    apt-get install -y unixodbc unixodbc-dev curl gnupg && \
    curl https://packages.microsoft.com/keys/microsoft.asc | tee /etc/apt/trusted.gpg.d/microsoft.asc && \
    echo "deb [arch=amd64] https://packages.microsoft.com/ubuntu/20.04/prod focal main" | tee /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql17 && \
    rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos del proyecto
COPY . .

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto 8000
EXPOSE 8000

# Comando para ejecutar la aplicación en Railway
CMD ["gunicorn", "FerreFac.wsgi:application", "--bind", "0.0.0.0:8000"]
