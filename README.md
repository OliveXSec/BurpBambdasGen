# BurpBambdasGen

> **Natural language in, working Burp Suite Bambdas out.** Describe the filter,
> column, scan check or match-and-replace rule you need, and get Java that
> compiles in Burp's Bambda editor — grounded in 94 real-world examples rather
> than generated from memory.

---

## Overview

**What it does.** BurpBambdasGen turns a plain-language description into a
functional Bambda script for Burp Suite. Bambdas are the Java snippets that
drive Burp's custom filters, table columns, Repeater actions, scan checks and
proxy rewrite rules; writing them means knowing the Montoya API, its null-safety
rules and the return contract of each Bambda type. This tool removes that
barrier.

**How it works.** Every request runs through a retrieval-augmented pipeline.
The tool first infers the Bambda type from the request, then ranks a local
corpus of 94 production Bambdas by keyword overlap and type match, and injects
the three closest examples — full source included — into the prompt alongside
the relevant Montoya API reference. Claude writes the script against those
examples, not against recollection. The output is then checked for the return
contract of its type, balanced delimiters, missing `hasResponse()` guards and
null-safety gaps before it reaches you. Everything runs locally against a JSON
index; no vector database, no external service beyond the Claude API.

**Why it matters for bug hunters.** Custom tooling is what separates a
systematic hunt from a manual one. A filter that surfaces only the requests
carrying a JWT in a cookie, a column that extracts the signing algorithm of
every token in the proxy history, a passive check that flags a specific
misconfiguration across an entire scope — each takes minutes of your attention
instead of an afternoon of API documentation. The cost of asking "could I see
this traffic differently?" drops low enough that you actually ask it.

**Why it matters for organisations.** Security teams encode their own detection
logic — internal header conventions, in-house authentication schemes, the
specific anti-patterns their developers repeat — as reusable Bambdas that every
tester loads on day one. Review knowledge stops living in one engineer's head
and becomes tooling the whole team shares.

**Results.** A described filter or column typically comes back ready to paste.
Generated scripts arrive with Javadoc, null-safe access patterns and a
validation report naming any unmet requirement, and export to `.bambda` (YAML)
for direct import into Burp. The knowledge base is extensible: point the ingest
script at your own `.bambda` collection and the generator starts producing code
in your team's style.

---

## Descripción general

**Qué hace.** BurpBambdasGen convierte una descripción en lenguaje natural en un
script Bambda funcional para Burp Suite. Los Bambdas son los fragmentos de Java
que gobiernan los filtros personalizados, las columnas de tabla, las acciones de
Repeater, los chequeos del scanner y las reglas de reescritura del proxy;
escribirlos exige conocer la API Montoya, sus reglas de null-safety y el
contrato de retorno de cada tipo de Bambda. Esta herramienta elimina esa
barrera.

**Cómo funciona.** Cada pedido atraviesa un pipeline de generación aumentada por
recuperación (RAG). La herramienta infiere primero el tipo de Bambda, luego
ordena un corpus local de 94 Bambdas reales por coincidencia de palabras clave y
de tipo, e inyecta los tres ejemplos más cercanos —con su código completo— en el
prompt junto con la referencia pertinente de la API Montoya. Claude escribe el
script apoyado en esos ejemplos, no en su memoria. La salida se valida después
contra el contrato de retorno de su tipo, el balanceo de delimitadores, la
ausencia de `hasResponse()` y los accesos sin protección de nulos antes de
llegar a tus manos. Todo corre localmente sobre un índice JSON: sin base de
datos vectorial y sin más servicio externo que la API de Claude.

**Para qué sirve a un bug hunter.** El tooling propio es lo que separa una
cacería sistemática de una manual. Un filtro que aísla solo las requests con un
JWT en una cookie, una columna que extrae el algoritmo de firma de cada token
del historial, un chequeo pasivo que marca una mala configuración puntual en
todo el scope: cada uno pasa a costar minutos de atención en lugar de una tarde
de documentación. El costo de preguntarse "¿y si miro este tráfico de otra
forma?" baja lo suficiente como para que efectivamente te lo preguntes.

**Para qué sirve a una empresa.** Los equipos de seguridad codifican su propia
lógica de detección —convenciones internas de headers, esquemas de autenticación
propios, los antipatrones que sus desarrolladores repiten— como Bambdas
reutilizables que cada tester carga desde el primer día. El conocimiento de
revisión deja de vivir en la cabeza de una persona y se convierte en herramienta
compartida.

**Resultados.** Un filtro o una columna descritos suelen volver listos para
pegar. Los scripts generados llegan con Javadoc, patrones de acceso seguros ante
nulos y un informe de validación que nombra cualquier requisito incumplido, y se
exportan a `.bambda` (YAML) para importarlos directo en Burp. La base de
conocimiento es extensible: apuntá el script de ingesta a tu propia colección de
`.bambda` y el generador empieza a producir código con el estilo de tu equipo.

---

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
