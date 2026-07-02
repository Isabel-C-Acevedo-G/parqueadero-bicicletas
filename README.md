# Sistema Web para la Gestión de Parqueaderos de Bicicletas - Medellín 🚴✨

Proyecto para gestionar accesos, cupos y registros de parqueaderos de bicicletas.

## Requisitos previos
- Docker & Docker Compose instalados
- (Opcional) Cliente `mysql` o MySQL Workbench para conectarse a la base

## Servicios y puertos
- Frontend (nginx estático): http://localhost:8080/#
- Backend (FastAPI / Uvicorn): http://localhost:8000
- MySQL (contenedor): puerto publicado 3307 -> 3306

## Inicio rápido (levantar todo)
Abre PowerShell en la raíz del proyecto (`c:\parqueadero-bicicletas`) y ejecuta:

```powershell
# (1) Bajar y eliminar volúmenes previos si quieres reinicializar la DB
docker compose down -v

# (2) Construir y levantar todos los servicios (frontend, backend, mysql)
docker compose up -d --build

# (3) Ver logs en tiempo real (opcional)
docker compose logs --follow mysql
docker compose logs --follow backend
docker compose logs --follow frontend
```

## Re-inicializar la base de datos (ejecuta si necesitas volver a correr `init.sql`)
```powershell
docker compose down -v
docker compose up -d --build
```
Esto elimina el volumen `mysql_data` y vuelve a ejecutar `mysql-init/init.sql` dentro del contenedor MySQL.

> Importante: si deseas que los registros de usuarios y datos se conserven, no uses `docker compose down -v` después de cada prueba. Ese comando borra el volumen de datos de MySQL.

## Comprobaciones y pruebas manuales
- Abrir frontend: abrir `http://localhost:8080/#` en el navegador.
- Probar endpoint de cupos:
```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/cupos' -Method Get
```
- Login de prueba:
```powershell
Invoke-RestMethod -Uri 'http://localhost:8000/login' -Method Post -Body '{"usuario":"isabel@gmail.com","contrasena":"1234"}' -ContentType 'application/json'
```
- Verificar que un usuario registrado desde el frontend quedó guardado en MySQL:
```powershell
docker exec voy_mysql mysql -uroot -proot -e "USE ParqueaderoBicicletas; SELECT IdUsuario, Documento, Correo, IdRol FROM Usuarios ORDER BY IdUsuario DESC LIMIT 5;"
```

## Archivos importantes y cambios realizados
- `docker-compose.yml`
	- Añadido servicio `mysql` (imagen `mysql:8.0`) con `MYSQL_ROOT_PASSWORD=root` y puerto mapeado `3307:3306`.
	- Backend env vars: `DB_SERVER=mysql`, `DB_PORT=3306`, `DB_DATABASE=ParqueaderoBicicletas`, `DB_UID=root`, `DB_PWD=root`.
- `mysql-init/init.sql`
	- Script de inicialización que crea la base `ParqueaderoBicicletas`, tablas (Roles, Usuarios, Bicicletas, Espacios, Ingresos, Salidas, Incidentes, Reservas) y semillas.
	- Se ejecuta automáticamente la primera vez que el volumen de MySQL se crea.
- `backend/main.py`
	- Migrado para usar `mysql-connector-python` en lugar de ODBC/SQL Server.
	- Endpoints añadidos/ajustados: `POST /register`, `POST /login`, `GET /cupos`, `POST /ingreso`, `POST /salida`, `POST /incidente`.
	- Hashing de contraseñas implementado con SHA-256 (nota: se recomienda migrar a `bcrypt`).
- `js/script.js`
	- `API_URL` configurado a `http://localhost:8000` y funciones de frontend para `login`, `register`, `cupos`, movimientos e incidentes.

## Conexión desde MySQL Workbench
- Host: `127.0.0.1`
- Puerto: `3307`
- Usuario: `root`
- Contraseña: `root`
- Base de datos: `ParqueaderoBicicletas`



