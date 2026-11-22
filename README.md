# BurpBambdasGen

Generador de scripts Bambda para Burp Suite usando IA (Claude) + RAG.

## ¿Qué es?

Una herramienta que genera scripts Bambda funcionales a partir de descripciones en lenguaje natural. Usa RAG (Retrieval-Augmented Generation) para encontrar ejemplos similares y mejorar la calidad del código generado.

## ¿Cómo funciona?

```
┌─────────────────────────────────────────────────────────────────┐
│  1. TU PROMPT                                                   │
│     "filter para mostrar solo respuestas 403"                   │
└─────────────────────┬───────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. BÚSQUEDA EN RAG (data/bambdas.json)                         │
│     - Busca bambdas similares por keywords                      │
│     - Encuentra 3 ejemplos relevantes del repositorio           │
│     - Busca documentación relacionada                           │
└─────────────────────┬───────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. CONSTRUYE PROMPT PARA CLAUDE                                │
│                                                                 │
│     SYSTEM: "Eres experto en Bambdas, tipos, API Montoya..."    │
│                                                                 │
│     USER:                                                       │
│       - Tu descripción                                          │
│       - Tipo detectado (VIEW_FILTER, CUSTOM_ACTION, etc.)       │
│       - Documentación relevante                                 │
│       - 3 ejemplos de bambdas similares (código completo)       │
└─────────────────────┬───────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. CLAUDE API                                                  │
│     - Recibe el prompt enriquecido con contexto RAG             │
│     - Genera código Java basado en los ejemplos reales          │
└─────────────────────┬───────────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. OUTPUT                                                      │
│     - Valida sintaxis básica                                    │
│     - Muestra código generado                                   │
│     - Opción de guardar como .bambda                            │
└─────────────────────────────────────────────────────────────────┘
```

## Instalación

```bash
git clone https://github.com/OliveXSec/BurpBambdasGen.git
cd BurpBambdasGen

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar API key
echo "ANTHROPIC_API_KEY=tu-api-key" > .env
```

## Uso

### 1. Generar Bambdas

Los 94 ejemplos de bambdas ya vienen en `data/bambdas.json`, así que podés generar
directamente. La documentación de PortSwigger **no** se distribuye con el repo
(ver [`data/README.md`](data/README.md)); sin ella el generador funciona igual,
solo recupera menos contexto.

### 2. Ampliar el knowledge base (opcional)

```bash
python scripts/ingest.py /ruta/al/knowledge-base
```

Indexa `.bambda` adicionales y, si los tenés localmente, la documentación de
Bambdas y la referencia de la API Montoya.

**Comando directo:**
```bash
python bambda-gen.py generate "filter para mostrar solo respuestas 403" -t filter
```

**Modo interactivo:**
```bash
python bambda-gen.py interactive
```

## Comandos CLI

```bash
python bambda-gen.py --help

Comandos:
  generate     Generar bambda desde descripción
  ingest       Ingestar documentos en la base de datos
  list         Listar ejemplos de bambdas
  types        Mostrar tipos de bambdas disponibles
  interactive  Modo interactivo
  status       Estado de la base de datos
```

### Opciones de Generate

```bash
python bambda-gen.py generate "descripción" [OPCIONES]

Opciones:
  -t, --type       Tipo: filter, column, action, scan-active, scan-passive
  -o, --output     Guardar en archivo
  -c, --copy       Copiar al clipboard
  -e, --examples   Número de ejemplos a usar (default: 3)
```

## Tipos de Bambdas

| Tipo | Alias | Return | Descripción |
|------|-------|--------|-------------|
| VIEW_FILTER | filter | boolean | Filtrar tablas de proxy/logger |
| CUSTOM_COLUMN | column | String | Columna personalizada en tablas |
| CUSTOM_ACTION | action | void | Acción en Repeater |
| SCAN_CHECK_ACTIVE_* | scan-active | AuditResult | Scan activo |
| SCAN_CHECK_PASSIVE | scan-passive | AuditResult | Scan pasivo |
| MATCH_AND_REPLACE_REQUEST | match-request | HttpRequest | Modificar requests |
| MATCH_AND_REPLACE_RESPONSE | match-response | HttpResponse | Modificar responses |

## Ejemplos de Prompts

**Filtros:**
```bash
python bambda-gen.py generate "mostrar solo requests con JWT en cookies" -t filter
python bambda-gen.py generate "highlight en rojo las respuestas 500" -t filter
python bambda-gen.py generate "filtrar requests que contengan SQLi patterns" -t filter
```

**Columnas:**
```bash
python bambda-gen.py generate "extraer el header Server" -t column
python bambda-gen.py generate "mostrar el algoritmo JWT del token" -t column
python bambda-gen.py generate "mostrar tiempo de respuesta en ms" -t column
```

**Acciones:**
```bash
python bambda-gen.py generate "enviar request 10 veces para race condition" -t action
python bambda-gen.py generate "decodificar Base64 en el response" -t action
python bambda-gen.py generate "extraer todas las URLs del body" -t action
```

**Scan Checks:**
```bash
python bambda-gen.py generate "detectar header CSP faltante" -t scan-passive
python bambda-gen.py generate "probar CORS misconfiguration" -t scan-active
python bambda-gen.py generate "detectar SSTI" -t scan-active
```

## Estructura del Proyecto

```
BurpBambdasGen/
├── bambda-gen.py          # Entry point CLI
├── requirements.txt       # Dependencias
├── .env                   # API key (crear manualmente)
│
├── src/
│   ├── config/
│   │   ├── settings.py    # Configuración
│   │   └── prompts.py     # System prompt y templates
│   │
│   ├── ingestion/
│   │   ├── loader.py      # Cargar .bambda y docs
│   │   └── chunker.py     # Dividir documentación
│   │
│   ├── retrieval/
│   │   ├── vectorstore.py # Almacenamiento JSON + búsqueda
│   │   └── retriever.py   # Lógica de búsqueda
│   │
│   ├── generation/
│   │   ├── generator.py   # Integración Claude API
│   │   └── validator.py   # Validación de código
│   │
│   └── cli/
│       └── main.py        # Aplicación CLI (Typer)
│
├── data/
│   └── bambdas.json       # Base de datos de ejemplos (94 bambdas)
│
└── scripts/
    └── ingest.py          # Script de ingesta
```

## Variables de Entorno

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-...    # Requerido
MODEL_NAME=claude-opus-5-5      # Modelo Claude
MAX_TOKENS=4096                 # Límite de tokens de salida
N_EXAMPLES=3                    # Ejemplos RAG por defecto
DATA_DIR=data                   # Directorio de datos
```

> Los modelos actuales de Claude no aceptan el parámetro `temperature` (devuelven
> HTTP 400), por eso la herramienta no lo expone.

## ¿Por qué RAG?

Sin RAG, Claude genera código "de memoria" que puede tener errores de sintaxis o no seguir los patrones correctos de la API Montoya.

Con RAG:
- Claude ve **ejemplos reales** de bambdas que funcionan
- Aprende los **patrones correctos** de cada tipo
- Usa la **documentación oficial** como referencia
- Genera código más **preciso y funcional**

## Dependencias

| Paquete | Uso |
|---------|-----|
| `anthropic` | Cliente API de Claude |
| `typer` + `rich` | CLI interactivo |
| `python-dotenv` | Cargar variables de `.env` |
| `pyyaml` | Exportar bambdas en formato YAML |
| `pyperclip` | Copiar al clipboard (opcional) |

## Requisitos

- Python 3.10+
- API key de Anthropic (Claude)

## Tests

```bash
pip install -e ".[dev]"
pytest
```

## Créditos

Los 94 ejemplos de bambdas provienen del
[repositorio público de PortSwigger](https://github.com/PortSwigger/bambdas) y
conservan el `@author` original en `metadata.author`.

## Licencia

MIT. Ver [LICENSE](LICENSE).
