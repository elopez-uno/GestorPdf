# UNO Documentos - Sistema de Gestión Documental

Sistema web profesional para la gestión, almacenamiento y búsqueda de documentos digitales (PDF) con control de acceso por oficinas, auditoría completa y vista previa integrada.

## Características

- **Gestión de documentos**: Subida, edición, vista previa, descarga e impresión de PDFs
- **Control de acceso**: Perfiles de usuario vinculados a oficinas/sectores
- **Roles**: Administrador (visión global) y Usuario (visión por oficina)
- **Etiquetas**: Clasificación mediante tags con CRUD independiente
- **Búsqueda avanzada**: Por texto, etiquetas, oficina y rango de fechas
- **Auditoría completa**: Registro de altas, modificaciones, ocultamientos y búsquedas
- **Vista previa**: Visor PDF integrado con navegación de páginas y zoom
- **Ocultamiento**: Los administradores pueden ocultar documentos cargados por error
- **Límite de tamaño**: Control de 5MB máximo por archivo

## Tecnologías

| Componente | Tecnología |
|------------|------------|
| Backend | Python 3.11 + Flask |
| Base de datos | PostgreSQL 15 |
| Frontend | Bootstrap 5 + PDF.js + Chart.js |
| Contenedores | Docker + Docker Compose |
| Proxy | Nginx |
| Servidor WSGI | Gunicorn |

## Estructura del proyecto

```
gestor-pdf/
├── app/
│   ├── __init__.py          # Factoría de aplicación
│   ├── config.py            # Configuración
│   ├── extensions.py        # Extensiones Flask
│   ├── models/              # Modelos SQLAlchemy
│   │   ├── user.py          # Usuarios
│   │   ├── office.py        # Oficinas
│   │   ├── tag.py           # Etiquetas
│   │   ├── document.py      # Documentos
│   │   └── audit.py         # Auditoría
│   ├── routes/              # Blueprints
│   │   ├── auth.py          # Autenticación
│   │   ├── dashboard.py     # Panel principal
│   │   ├── documents.py     # CRUD documentos
│   │   ├── tags.py          # CRUD etiquetas
│   │   ├── offices.py       # CRUD oficinas
│   │   ├── users.py         # CRUD usuarios
│   │   ├── audit.py         # Visor de auditoría
│   │   └── api.py           # API REST (stats)
│   ├── forms/               # Formularios WTForms
│   ├── utils/               # Utilidades
│   │   ├── decorators.py    # Decoradores de permisos
│   │   └── audit.py         # Helpers de auditoría
│   ├── templates/           # Templates Jinja2
│   └── static/              # Archivos estáticos
│       ├── css/style.css
│       ├── js/main.js
│       └── img/favicon.svg
├── docker-compose.yml
├── Dockerfile
├── nginx/nginx.conf
├── entrypoint.sh
├── requirements.txt
└── README.md
```

## Requisitos

- Docker 24+
- Docker Compose 2.20+

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio> gestor-pdf
cd gestor-pdf
```

### 2. Configurar variables de entorno (opcional)

```bash
cp .env.example .env
# Editar .env si se desea cambiar credenciales por defecto
```

### .env de test
```bash
### Mapeo de unidad NAS 


 .env
# --- NAS BIND MOUNT ---
# Esta variable apunta al directorio local del servidor Ubuntu donde se monta el NAS.
# Este será el nuevo almacenamiento de documentos de SeedDMS.
## Produccion
NAS_MOUNT_POINT=/mnt/dms_nas
# Desarrollo
# NAS_MOUNT_POINT=./mnt
# --- VOLUMENES DE CONFIGURACION (Locales) ---
# Almacenamiento local para configuracion de SeedDMS (settings.xml, etc.)
CONF_VOLUME=./seeddms_conf
# Almacenamiento local para extensiones
EXT_VOLUME=./seeddms_ext

# --- DATABASE (PostgreSQL) ---
DB_HOST=db-postgre
DB_USER=seedadmin
DB_PASSWORD=seedadmin369*
DB_NAME=seedadmin # nombre para ser más explícito
DB_ROOT_PASSWORD=Belgrano369*
WEB_HOST=8080
```



### 3. Iniciar los servicios

```bash
docker compose up -d --build
```

Esto levantará tres contenedores:

- **db**: PostgreSQL 15 (puerto 5432)
- **app**: Aplicación Flask + Gunicorn (puerto 5050)
- **nginx**: Proxy reverso (puerto 80)

### 4. Acceder al sistema

```
http://localhost
```

### Credenciales por defecto

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `admin` | Administrador |

> **Importante**: Cambiar la contraseña del administrador en el primer inicio de sesión.

## Puertos por defecto

| Servicio | Puerto interno | Puerto host (configurable) |
|----------|---------------|---------------------------|
| Nginx | 80 | 80 |
| App Flask | 5000 | 5050 |
| PostgreSQL | 5432 | 5432 |

## Volúmenes persistentes

| Volumen | Contenedor | Propósito |
|---------|-----------|-----------|
| `postgres_data` | db | Datos de la base de datos |
| `app_uploads` | app, nginx | Archivos PDF subidos |

## Variables de entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DB_NAME` | Nombre de la base de datos | `gestor_pdf` |
| `DB_USER` | Usuario de base de datos | `gestor_user` |
| `DB_PASSWORD` | Contraseña de base de datos | `gestor_pass_123` |
| `DB_PORT` | Puerto de base de datos | `5432` |
| `SECRET_KEY` | Clave secreta de Flask | `cambiar_esta_clave_en_produccion` |
| `FLASK_ENV` | Entorno de Flask | `production` |
| `ADMIN_EMAIL` | Email del administrador | `admin@gestorpdf.com` |
| `APP_PORT` | Puerto host de la app | `5050` |
| `NGINX_PORT` | Puerto host de Nginx | `80` |

## Uso del sistema

### Para usuarios regulares

1. Iniciar sesión con credenciales asignadas por el administrador
2. Subir documentos PDF mediante el formulario con título, descripción y etiquetas
3. Buscar documentos por criterios de texto, etiquetas o fechas
4. Visualizar, descargar e imprimir documentos
5. Editar metadatos de documentos propios

### Para administradores

1. **Usuarios**: Crear, editar, activar/desactivar usuarios
2. **Oficinas**: Gestionar oficinas y sectores
3. **Etiquetas**: CRUD completo de etiquetas
4. **Documentos**: Visión global, ocultar/mostrar documentos
5. **Auditoría**: Visualizar registros de actividad y búsquedas

## Base de datos

### Modelo entidad-relación

```
users ──┬── office_id ──► offices
        │
        ├── documents (uploader)
        │
        ├── audit_logs
        └── search_logs

documents ──┬── user_id ──► users
            ├── office_id ──► offices
            ├── hidden_by ──► users
            └── document_tags ──► tags

tags ──┬── document_tags ──► documents

audit_logs ──┬── user_id ──► users
search_logs ──┬── user_id ──► users
```

### Tablas principales

- **users**: Usuarios del sistema (roles: admin, user)
- **offices**: Oficinas o sectores
- **tags**: Etiquetas para clasificación
- **documents**: Documentos PDF digitalizados
- **document_tags**: Relación muchos a muchos entre documentos y etiquetas
- **audit_logs**: Registro de auditoría de acciones
- **search_logs**: Historial de búsquedas realizadas

## Desarrollo

### Ejecutar en modo desarrollo

```bash
# Usar Flask directamente (no Docker)
python run.py
```

### Migraciones

```bash
# Generar migración
flask db migrate -m "descripcion"

# Aplicar migración
flask db upgrade
```

## Licencia

UNO Documentos - Sistema de Gestión Documental
