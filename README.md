# SATI - Sistema de Auditoría de Transacciones Inmutables 

SATI es una solución de Data Engineering diseñada para una Fintech, enfocada en garantizar la **integridad** y la **auditoría** de datos transaccionales mediante un pipeline automatizado de verificación y trazabilidad.

## Stack Tecnológico
- **Lenguaje:** Python 3.10+
- **Framework API:** FastAPI
- **Base de Datos:** PostgreSQL (Propiedades ACID)
- **Validación:** Pydantic v2
- **Seguridad:** Cifrado simétrico (Fernet) y SHA-256 (Hashing encadenado)
- **Contenedor:** Docker & Docker Compose

##  Arquitectura y Seguridad DataOps

1. **Estructura Profesional:** El proyecto sigue una arquitectura modular con separación de responsabilidades en `/src`, `/tests` y persistencia de logs en `/data_logs`.
2. **Validación Semántica:** Implementada con Pydantic. Los montos deben ser estrictamente positivos (> 0).
3. **Capa de Inmutabilidad (Core):**
   - **Hashing Encadenado:** Cada registro contiene su propio hash y el hash del registro anterior, creando una cadena de confianza (similar a una blockchain).
   - **Modo WORM (Write Once, Read Many):** Se bloquean `UPDATE` y `DELETE` por dos capas: eventos de SQLAlchemy y trigger en PostgreSQL aplicado al iniciar la app.
4. **Seguridad de Datos:**
   - **Cifrado:** Los montos se guardan cifrados en la base de datos para cumplir con normativas de privacidad.
   - **Enmascaramiento:** El ID del comercio se enmascara (ej: `CO****99`) antes de persistirse.
5. **Auditoría Permanente:** Se genera un archivo `audit_trail.log` que registra cada operación, permitiendo una trazabilidad completa.

## Instrucciones de Ejecución

### Requisitos Previos
- Docker y Docker Compose instalados.

### Despliegue con Docker
1. Clona el repositorio.
2. Ejecuta el comando:
   ```bash
   docker-compose up --build
   ```
3. La API estará disponible en `http://localhost:8000`.
4. Accede a la documentación interactiva en `http://localhost:8000/docs`.

### Ejemplo de Uso (Ingesta)
**POST** `/ingest`
```json
{
  "id": "TX-2026-001",
  "monto": 2500.75,
  "moneda": "USD",
  "comercio_id": "MERCH-9988"
}
```

### Verificación de Inmutabilidad
El endpoint **GET** `/audit/{transaction_id}` recalcula el hash esperado y valida el encadenamiento con el registro anterior.

### Endpoints de Demo
- **GET** `/health` (verifica conectividad a DB)
- **GET** `/kpis` (KPIs del sistema)
- **GET** `/audit/{transaction_id}` (verificación de integridad)
- **GET** `/verify-chain` (verificación completa de la cadena)

## Seguridad
- **API key:** header `X-API-KEY`, configurado por `API_KEY` en `.env` (valor demo: `sati-demo-key`)
- **Cifrado:** monto cifrado con `Fernet` antes de persistir
- **Masking:** `comercio_id` se enmascara antes de persistir
- **WORM:** bloqueo de `UPDATE/DELETE` por eventos SQLAlchemy y trigger aplicado al iniciar sobre PostgreSQL

## Verificación completa
El endpoint **GET** `/verify-chain` recorre toda la tabla `transactions` y valida:
- hash recalculado de cada registro
- `previous_hash` respecto del registro anterior

## Pruebas
Para ejecutar las pruebas unitarias localmente:
```bash
pip install -r requirements.txt
python -m pytest
```

## Demo
Ingesta:
```bash
curl -X POST http://localhost:8000/ingest ^
  -H "Content-Type: application/json" ^
  -H "X-API-KEY: sati-demo-key" ^
  -d "{\"id\":\"TX-2026-001\",\"monto\":2500.75,\"moneda\":\"USD\",\"comercio_id\":\"MERCH-9988\"}"
```

Auditoría:
```bash
curl http://localhost:8000/audit/TX-2026-001 -H "X-API-KEY: sati-demo-key"
```

KPIs:
```bash
curl http://localhost:8000/kpis -H "X-API-KEY: sati-demo-key"
```

Verificación full-chain:
```bash
curl http://localhost:8000/verify-chain -H "X-API-KEY: sati-demo-key"
```

---
**Desarrollado para la Evaluación Parcial 2 - Proyecto SATI**
