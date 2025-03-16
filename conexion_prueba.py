import pyodbc

server = 'ferrecampesino.database.windows.net'
database = 'FerreteriaDB'
username = 'adminferreteria'
password = 'Ferreteria2024!'
driver = 'ODBC Driver 17 for SQL Server'

try:
    connection_string = f'DRIVER={{{driver}}};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
    connection = pyodbc.connect(connection_string)
    print("¡Conexión exitosa a la base de datos!")
    connection.close()
except Exception as e:
    print("Error de conexión:", e)
