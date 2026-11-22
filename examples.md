# Ejemplos de Comandos - Bambda Generator

## Filtros Avanzados

```bash
# Detectar vulnerabilidades OWASP en parámetros
python bambda-gen.py generate "filtrar requests que tengan parámetros vulnerables a SQLi, XSS, SSRF, LFI o RCE y highlightear en rojo" -t filter

# Detectar secrets/API keys en responses
python bambda-gen.py generate "filtrar responses que contengan API keys, tokens AWS, passwords o secrets en el body" -t filter

# Detectar headers de seguridad faltantes
python bambda-gen.py generate "filtrar responses que no tengan CSP, X-Frame-Options o Strict-Transport-Security" -t filter

# Mostrar solo errores de servidor
python bambda-gen.py generate "filtrar responses con status 500, 502, 503 y highlightear en rojo" -t filter

# Detectar información sensible en responses
python bambda-gen.py generate "filtrar responses que contengan emails, IPs privadas, paths de servidor o stack traces" -t filter

# Filtrar por content-type específico
python bambda-gen.py generate "mostrar solo responses JSON que contengan campos password, token o secret" -t filter

# Detectar redirects sospechosos
python bambda-gen.py generate "filtrar responses 301/302 donde Location apunte a dominio externo" -t filter

# JWT en requests
python bambda-gen.py generate "filtrar requests que tengan JWT en Authorization header o cookies" -t filter

# GraphQL introspection
python bambda-gen.py generate "filtrar requests GraphQL que contengan __schema o __type" -t filter

# Websocket upgrades
python bambda-gen.py generate "filtrar requests con header Upgrade: websocket" -t filter
```

## Custom Actions (Repeater)

```bash
# Race condition testing
python bambda-gen.py generate "enviar el request 50 veces en paralelo y mostrar cuántos tuvieron respuestas diferentes para detectar race conditions" -t action

# Cookie injection testing
python bambda-gen.py generate "tomar cada parámetro del request y probarlo como cookie para detectar cookie injection" -t action

# CORS bypass checker
python bambda-gen.py generate "probar el request con diferentes Origins maliciosos para detectar CORS misconfiguration" -t action

# JWT manipulation
python bambda-gen.py generate "decodificar el JWT del request, mostrar claims, y generar versiones con alg:none y firma vacía" -t action

# Parameter pollution
python bambda-gen.py generate "duplicar cada parámetro con valores maliciosos para probar HTTP parameter pollution" -t action

# Bruteforce simple
python bambda-gen.py generate "enviar el request reemplazando un parámetro con valores de una lista y mostrar responses diferentes" -t action

# Extraer URLs del response
python bambda-gen.py generate "extraer todas las URLs y endpoints del response body y mostrarlos en consola" -t action

# Decodificar Base64 en response
python bambda-gen.py generate "buscar strings Base64 en el response, decodificarlos y mostrar el contenido" -t action

# Comparar responses
python bambda-gen.py generate "enviar el request 2 veces y mostrar diferencias entre las responses" -t action

# Method tampering
python bambda-gen.py generate "probar el mismo request con métodos GET, POST, PUT, DELETE, PATCH y mostrar diferencias en responses" -t action

# Header injection testing
python bambda-gen.py generate "probar inyectar CRLF en headers del request y detectar reflection en response" -t action

# Content-Type bypass
python bambda-gen.py generate "enviar el request con diferentes Content-Types para detectar bypasses de validación" -t action
```

## Scan Checks Activos

```bash
# SSTI detection
python bambda-gen.py generate "probar payloads de SSTI como {{7*7}} en cada parámetro y detectar si la respuesta contiene 49" -t scan-active

# Prototype pollution
python bambda-gen.py generate "detectar server-side prototype pollution probando __proto__ y constructor.prototype en JSON bodies" -t scan-active

# Open redirect
python bambda-gen.py generate "probar open redirect en parámetros que contengan url, redirect, next, return, goto" -t scan-active

# Host header injection
python bambda-gen.py generate "probar host header injection cambiando el Host header y detectando reflection en response" -t scan-active

# Path traversal
python bambda-gen.py generate "probar path traversal con payloads como ../ y ....// en parámetros de archivo" -t scan-active

# SSRF básico
python bambda-gen.py generate "probar SSRF con payloads de localhost, 127.0.0.1, y metadata endpoints en parámetros URL" -t scan-active

# SQL injection time-based
python bambda-gen.py generate "probar SQLi time-based con SLEEP y BENCHMARK, detectar si response tarda más de 5 segundos" -t scan-active

# XXE injection
python bambda-gen.py generate "probar XXE en requests XML con payloads de external entity" -t scan-active

# Command injection
python bambda-gen.py generate "probar command injection con payloads como ;id, |whoami, `id` en parámetros" -t scan-active

# LDAP injection
python bambda-gen.py generate "probar LDAP injection con payloads como *, )(, y caracteres especiales LDAP" -t scan-active
```

## Scan Checks Pasivos

```bash
# Headers de seguridad
python bambda-gen.py generate "detectar responses sin Content-Security-Policy header" -t scan-passive

# Información sensible
python bambda-gen.py generate "detectar responses que expongan versiones de software en headers Server o X-Powered-By" -t scan-passive

# Cookies inseguras
python bambda-gen.py generate "detectar cookies sin flags HttpOnly, Secure o SameSite" -t scan-passive

# Mixed content
python bambda-gen.py generate "detectar responses HTTPS que carguen recursos HTTP" -t scan-passive

# CORS permisivo
python bambda-gen.py generate "detectar responses con Access-Control-Allow-Origin: * o credentials: true" -t scan-passive

# Debug/error info
python bambda-gen.py generate "detectar responses con stack traces, errores SQL o paths de servidor" -t scan-passive

# Clickjacking
python bambda-gen.py generate "detectar responses HTML sin X-Frame-Options o CSP frame-ancestors" -t scan-passive

# Information disclosure
python bambda-gen.py generate "detectar responses que contengan emails internos, IPs privadas o paths Windows/Linux" -t scan-passive
```

## Custom Columns

```bash
# JWT analysis
python bambda-gen.py generate "extraer y mostrar el algoritmo, issuer y expiration del JWT en Authorization o cookies" -t column

# Response time
python bambda-gen.py generate "mostrar response time en milisegundos" -t column

# Technology detection
python bambda-gen.py generate "extraer tecnologías del response: Server header, X-Powered-By, cookies de framework" -t column

# Content length
python bambda-gen.py generate "mostrar el Content-Length del response" -t column

# Cookies count
python bambda-gen.py generate "mostrar cantidad de cookies en el response" -t column

# Redirect location
python bambda-gen.py generate "mostrar el header Location para responses 3xx" -t column

# CORS origin
python bambda-gen.py generate "mostrar el valor de Access-Control-Allow-Origin" -t column

# Auth type
python bambda-gen.py generate "mostrar el tipo de autenticación usado: Bearer, Basic, API-Key, Cookie" -t column

# GraphQL operation
python bambda-gen.py generate "extraer el nombre de la operación GraphQL del request" -t column

# Parameter count
python bambda-gen.py generate "mostrar cantidad de parámetros en el request" -t column
```

## Match & Replace

```bash
# Auto-sign requests
python bambda-gen.py generate "agregar header X-Signature con HMAC-SHA256 del body usando una clave configurable" -t match-request

# Bypass WAF
python bambda-gen.py generate "reemplazar payloads comunes de SQLi con versiones ofuscadas usando comentarios" -t match-request

# Add custom header
python bambda-gen.py generate "agregar header X-Custom-Auth con valor fijo a todos los requests" -t match-request

# Remove security headers
python bambda-gen.py generate "remover headers de seguridad del response para testing" -t match-response

# Modify User-Agent
python bambda-gen.py generate "cambiar User-Agent a un valor custom en todos los requests" -t match-request

# URL encode params
python bambda-gen.py generate "double URL encode todos los valores de parámetros" -t match-request

# Add timestamp
python bambda-gen.py generate "agregar parámetro timestamp con epoch actual a todos los requests" -t match-request
```

## Uso Interactivo

```bash
# Iniciar modo interactivo
python bambda-gen.py interactive

# Comandos dentro del modo interactivo:
# /type filter     - Cambiar a tipo filter
# /type action     - Cambiar a tipo action
# /type column     - Cambiar a tipo column
# /type scan-active - Cambiar a scan activo
# /type scan-passive - Cambiar a scan pasivo
# /save nombre     - Guardar último bambda
# /copy            - Copiar al clipboard
# /clear           - Volver a auto-detect
# /quit            - Salir
```
