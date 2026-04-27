# Taller 1 — E-commerce con Chat IA

> API REST de e-commerce de zapatos con asistente virtual inteligente powered by **Google Gemini AI**.  
> Implementada con **Clean Architecture** (Domain → Application → Infrastructure).  
> **Universidad EAFIT** — Taller de Construcción de Software

---

## Tabla de Contenidos

1. [Descripción del Proyecto](#descripción-del-proyecto)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Tecnologías Utilizadas](#tecnologías-utilizadas)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Requisitos Previos](#requisitos-previos)
6. [Instalación y Configuración](#instalación-y-configuración)
7. [Ejecución con Docker](#ejecución-con-docker)
8. [Endpoints de la API](#endpoints-de-la-api)
9. [Ejemplos de Uso](#ejemplos-de-uso)
10. [Tests](#tests)
11. [Convenciones de Git](#convenciones-de-git)

---

## Descripción del Proyecto

**SneakerStore API** es una API REST completa para un e-commerce de zapatos con las siguientes funcionalidades:

- **Catálogo de productos**: Listado, búsqueda y filtrado de zapatos por marca, categoría y disponibilidad.
- **Chat inteligente con IA**: Asistente virtual que conoce el inventario completo y mantiene memoria conversacional.
- **Integración con Google Gemini**: Respuestas naturales y contextualizadas para cada cliente.
- **Persistencia**: Base de datos SQLite con historial de conversaciones.
- **Containerización**: Aplicación lista para producción con Docker.

---

## Arquitectura del Sistema

El proyecto implementa **Clean Architecture** con 3 capas bien definidas:

```
┌─────────────────────────────────────┐
│        INFRASTRUCTURE LAYER         │
│  FastAPI · SQLAlchemy · Gemini AI   │
│    (detalles técnicos e I/O)        │
└──────────────────┬──────────────────┘
                   │ usa
┌──────────────────▼──────────────────┐
│         APPLICATION LAYER           │
│   ProductService · ChatService      │
│   DTOs con validación Pydantic      │
└──────────────────┬──────────────────┘
                   │ usa
┌──────────────────▼──────────────────┐
│           DOMAIN LAYER              │
│  Product · ChatMessage · Entities   │
│  IProductRepository · Interfaces    │
│  Excepciones del negocio            │
└─────────────────────────────────────┘
```

**Regla de dependencias:** Las capas internas nunca dependen de las externas.

---

## Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|---|---|---|
| **Python** | 3.11 | Lenguaje principal |
| **FastAPI** | 0.104.1 | Framework web REST |
| **SQLAlchemy** | 2.0.23 | ORM para base de datos |
| **SQLite** | built-in | Base de datos ligera |
| **Pydantic** | 2.5.0 | Validación de datos |
| **Google Gemini** | 0.3.2 | IA conversacional |
| **Docker** | latest | Containerización |
| **Pytest** | 7.4.3 | Tests unitarios |

---

## Estructura del Proyecto

```
e-commerce-chat-ai/
│
├── src/
│   ├── config.py                          # Configuración global
│   │
│   ├── domain/                            # CAPA DE DOMINIO
│   │   ├── entities.py                    # Product, ChatMessage, ChatContext
│   │   ├── repositories.py                # IProductRepository, IChatRepository
│   │   └── exceptions.py                  # ProductNotFoundError, ChatServiceError
│   │
│   ├── application/                       # CAPA DE APLICACIÓN
│   │   ├── dtos.py                        # DTOs con validación Pydantic
│   │   ├── product_service.py             # Casos de uso de productos
│   │   └── chat_service.py                # Caso de uso de chat con IA
│   │
│   └── infrastructure/                    # CAPA DE INFRAESTRUCTURA
│       ├── api/
│       │   └── main.py                    # FastAPI: endpoints HTTP
│       ├── db/
│       │   ├── database.py                # Configuración SQLAlchemy
│       │   ├── models.py                  # Modelos ORM
│       │   └── init_data.py               # Datos iniciales (12 productos)
│       ├── repositories/
│       │   ├── product_repository.py      # SQLProductRepository
│       │   └── chat_repository.py         # SQLChatRepository
│       └── llm_providers/
│           └── gemini_service.py          # Integración Google Gemini
│
├── tests/
│   ├── conftest.py                        # Fixtures de pytest
│   └── test_ecommerce.py                  # Tests unitarios e integración
│
├── evidencias/                            # Screenshots para entrega
├── data/                                  # Base de datos SQLite (auto-generada)
│
├── .env.example                           # Plantilla de variables de entorno
├── .gitignore
├── .dockerignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── README.md
```

---

## Requisitos Previos

- **Python** 3.11 o superior
- **Docker Desktop** (para ejecución con contenedores)
- **Git** para control de versiones
- **API Key de Google Gemini** (gratuita en https://aistudio.google.com/app/apikey)
- **Postman** o **Insomnia** para probar la API

---

## Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/e-commerce-chat-ai.git
cd e-commerce-chat-ai
```

### 2. Crear y activar entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar en Mac/Linux:
source venv/bin/activate

# Activar en Windows:
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar plantilla
cp .env.example .env

# Editar .env con tu API key real de Gemini
# GEMINI_API_KEY=AIzaSy...
```

### 5. Ejecutar en modo desarrollo (sin Docker)

```bash
uvicorn src.infrastructure.api.main:app --reload --port 8000
```

Accede a:
- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## Ejecución con Docker

### Construir y ejecutar

```bash
# Construir imagen y levantar contenedor
docker-compose up --build

# Ejecutar en segundo plano
docker-compose up --build -d
```

### Comandos útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f

# Ver logs del contenedor
docker logs sneakerstore-api

# Ver contenedores activos
docker ps

# Detener contenedores
docker-compose down
```

La API quedará disponible en http://localhost:8000

---

## Endpoints de la API

### Información General

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/` | Información de la API |
| GET | `/docs` | Documentación Swagger UI |
| GET | `/redoc` | Documentación ReDoc |

### Productos

| Método | Endpoint | Descripción |
|---|---|---|
| GET | `/products` | Lista todos los productos |
| GET | `/products?brand=Nike` | Filtra por marca |
| GET | `/products?category=Running` | Filtra por categoría |
| GET | `/products?available_only=true` | Solo productos con stock |
| GET | `/products/{id}` | Obtiene producto por ID |

### Chat con IA

| Método | Endpoint | Descripción |
|---|---|---|
| POST | `/chat` | Envía mensaje al asistente IA |
| GET | `/chat/history/{session_id}` | Historial de conversación |
| DELETE | `/chat/history/{session_id}` | Limpia historial de sesión |

---

## Ejemplos de Uso

### Listar productos

```bash
curl http://localhost:8000/products
```

### Chat con el asistente de IA

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "cliente_001",
    "message": "Busco zapatos Nike para correr, talla 42"
  }'
```

**Respuesta esperada:**
```json
{
  "session_id": "cliente_001",
  "user_message": "Busco zapatos Nike para correr, talla 42",
  "assistant_message": "¡Hola! Tenemos el Nike Air Zoom Pegasus 40 en talla 42 por $120. Es ideal para running con excelente amortiguación. ¿Te gustaría más información sobre este modelo?",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Obtener historial

```bash
curl http://localhost:8000/chat/history/cliente_001?limit=10
```

---

## Tests

### Ejecutar todos los tests

```bash
pytest
```

### Con cobertura de código

```bash
pytest --cov=src --cov-report=term-missing
```

### Tests específicos

```bash
# Solo tests de dominio
pytest tests/test_ecommerce.py::TestProductEntity -v

# Solo tests de repositorios
pytest tests/test_ecommerce.py::TestSQLProductRepository -v
```

---

## Convenciones de Git

Los commits siguen la especificación **Conventional Commits**:

```
<tipo>(<alcance>): <descripción breve>
```

### Tipos de commit

| Tipo | Descripción |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `docs` | Documentación |
| `test` | Tests |
| `refactor` | Refactoring |
| `chore` | Tareas de mantenimiento |
| `style` | Formato/estilo de código |

### Ejemplos

```bash
git commit -m "feat(domain): implementar entidades Product y ChatMessage con validaciones"
git commit -m "feat(infrastructure): configurar SQLAlchemy y modelos ORM"
git commit -m "feat(api): agregar endpoints de productos y chat con FastAPI"
git commit -m "feat(ai): integrar Google Gemini para respuestas conversacionales"
git commit -m "docs(readme): agregar instrucciones de instalación y uso"
git commit -m "test(domain): agregar tests unitarios para entidades de dominio"
git commit -m "chore(docker): configurar Dockerfile y docker-compose para despliegue"
```

---

## Autor

Helen Valentina Sanabria — Universidad EAFIT  
Ingeniería de Sistemas — Taller de Construcción de Software

---

## Licencia

Este proyecto es desarrollado con fines académicos para la Universidad EAFIT.
