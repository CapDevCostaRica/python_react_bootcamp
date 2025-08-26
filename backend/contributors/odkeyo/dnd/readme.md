
Endpoints

List Monsters
POST /list
Body:
{ "resource": "monsters" }

Respuesta:
{
  "count": 325,
  "results": [
    { "index": "aboleth", "name": "Aboleth" },
    { "index": "acolyte", "name": "Acolyte" }
  ]
}

Get Monster Detail
POST /get
Body:
{ "monster_index": "adult-black-dragon" }

Respuesta:
{
  "index": "adult-black-dragon",
  "name": "Adult Black Dragon",
  "data": {
    "size": "Huge",
    "type": "dragon",
    "alignment": "chaotic evil",
    "armor_class": 19,
    "hit_points": 195,
    "challenge_rating": 14,
    "...": "..."
  }
}

Tecnologías

Flask: framework web para los endpoints.
SQLAlchemy: ORM para cacheo de datos en PostgreSQL.
Alembic: migraciones de DB.
Marshmallow: validación de entrada y salida.
Requests: cliente HTTP para la API de D&D.
Docker Compose: orquestación de contenedores (Flask + Postgres).

Estructura de archivos
contributors/odkeyo/dnd/
  ├── clients.py   # Cliente HTTP para el API de D&D
  ├── main.py      # Handlers Flask
  ├── schemas.py   # Validación con Marshmallow
  ├── service.py   # Lógica de cacheo en DB
  └── README.md    # (este archivo)
framework/
  ├── database.py  # Configuración de DB
  └── models.py    # Modelos SQLAlchemy (incluye odkeyo_monsters y odkeyo_monster_details)

Cómo correrlo
Construir e iniciar los servicios con Docker Compose:
docker compose up --build


Usar Postman para probar los endpoints.
Validaciones

Entrada:

http://localhost:4000/list 
requiere { "resource": "monsters" }.

http://localhost:4000/get 
requiere { "monster_index": "<index>" }.

Salida:

List devuelve siempre { "count", "results" }.
Get devuelve { "index", "name", "data" }.

Nota para usuarios de Windows

Si al levantar los contenedores aparece el error:

$'\r': command not found


significa que el archivo run_local.sh tiene saltos de línea de Windows (CRLF) en lugar de Unix (LF).
Bash en Linux no reconoce los \r y falla al ejecutar el script.

🔧 Soluciones

Conversión rápida en PowerShell (ejecutar una vez):

(Get-Content -Raw .\backend\run_local.sh).Replace("`r`n","`n") |
  Set-Content -NoNewline -Encoding ascii .\backend\run_local.sh


Configurar Git para que siempre guarde .sh con saltos LF
Agregar un archivo .gitattributes en la raíz del proyecto con:

*.sh text eol=lf


En VS Code
Abrir backend/run_local.sh, cambiar CRLF → LF (abajo a la derecha en la barra de estado) y guardar.