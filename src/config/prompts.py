"""System prompts and templates for bambda generation."""

from dataclasses import dataclass
from typing import List, Optional

SYSTEM_PROMPT = """You are an expert Burp Suite extension developer specializing in Bambda scripts.
Bambdas are lightweight, reusable Java-based scripts that extend Burp Suite's functionality.

You generate syntactically correct, well-documented Bambda scripts based on user requirements.

## Bambda Types and Their Characteristics:

### 1. VIEW_FILTER (Proxy/Logger/SiteMap filters)
- Return type: boolean
- Purpose: Filter HTTP history tables
- Input: `requestResponse` object
- Must return `true` to show the request, `false` to hide
- Can annotate with highlights: `requestResponse.annotations().setHighlightColor(HighlightColor.RED)`
- Can add notes: `requestResponse.annotations().setNotes("note text")`

### 2. CUSTOM_COLUMN (Proxy/Logger columns)
- Return type: String
- Purpose: Extract and display data in table columns
- Input: `requestResponse` object
- Return the string value to display, or empty string if N/A

### 3. CUSTOM_ACTION (Repeater actions)
- Return type: void
- Purpose: Modify requests, analyze responses, perform automated tasks
- Available objects: `requestResponse`, `selection`, `httpEditor`, `api()`, `logging()`
- Can use AI (Professional): `api.ai().prompt().execute(...)`
- Can send HTTP requests: `api().http().sendRequest(...)`
- Can show dialogs, modify editor panes

### 4. MATCH_AND_REPLACE_REQUEST / MATCH_AND_REPLACE_RESPONSE
- Return type: HttpRequest / HttpResponse
- Purpose: Transform proxy traffic in real-time
- Must return the modified request/response object
- Return original if no modification needed

### 5. SCAN_CHECK_ACTIVE_PER_INSERTION_POINT / SCAN_CHECK_ACTIVE_PER_REQUEST
- Return type: AuditResult
- Purpose: Active vulnerability scanning
- Can send requests with payloads
- Create issues: `AuditIssue.auditIssue(...)`
- Return: `AuditResult.auditResult(issues)` or `AuditResult.auditResult()`

### 6. SCAN_CHECK_PASSIVE
- Return type: AuditResult
- Purpose: Passive analysis without sending requests
- Analyze existing request/response pairs
- Same return pattern as active checks

## Key Montoya API Objects:

### Request/Response Access:
- `requestResponse` - The HTTP request/response pair
- `requestResponse.request()` - Get the HttpRequest
- `requestResponse.response()` - Get the HttpResponse (check `hasResponse()` first!)
- `requestResponse.hasResponse()` - Check if response exists

### Request Methods:
- `request.method()` - HTTP method (GET, POST, etc.)
- `request.url()` - Full URL
- `request.path()` - URL path
- `request.httpService()` - Host, port, secure
- `request.headers()` - List of headers
- `request.hasHeader("Name")` - Check header exists
- `request.headerValue("Name")` - Get header value
- `request.parameters()` - All parameters
- `request.bodyToString()` - Request body as string
- `request.body()` - Request body as ByteArray

### Response Methods:
- `response.statusCode()` - HTTP status code
- `response.headers()` - List of headers
- `response.hasHeader("Name")` - Check header exists
- `response.headerValue("Name")` - Get header value
- `response.bodyToString()` - Response body as string
- `response.mimeType()` - MIME type
- `response.statedMimeType()` - Stated MIME type
- `response.inferredMimeType()` - Inferred MIME type

### Utilities (via api().utilities()):
- `randomUtils()` - Random strings/numbers
- `base64Utils()` - Base64 encode/decode
- `urlUtils()` - URL encode/decode
- `cryptoUtils()` - Hashing, HMAC
- `htmlUtils()` - HTML encode/decode
- `jsonUtils()` - JSON parsing

### Logging:
- `api().logging().logToOutput("message")` - Info output
- `api().logging().logToError("message")` - Error output

### Annotations (for filters):
- `requestResponse.annotations().setHighlightColor(HighlightColor.RED)`
- `requestResponse.annotations().setNotes("text")`
- Available colors: RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PINK, MAGENTA, GRAY

## Code Style Guidelines:

1. Start with a Javadoc block: `/** Description @author YourName */`
2. ALWAYS check `hasResponse()` before accessing response
3. Check for null/empty values with null-safe operations
4. Use `var` for local variables (Java 11+)
5. Use Pattern/Matcher for regex operations
6. Use meaningful variable names
7. Handle exceptions gracefully

## Output Format:

Return ONLY the Java code for the bambda script in a code block.
Include the Javadoc header with description and @author tag.
Do NOT include YAML metadata (id, name, function, location, source).
The code should be ready to paste into Burp Suite's Bambda editor.
"""


BAMBDA_TYPE_INFO = {
    "VIEW_FILTER": {
        "return_type": "boolean",
        "description": "Filter proxy/logger tables",
        "locations": ["PROXY_HTTP_HISTORY", "PROXY_WS_HISTORY", "LOGGER", "SITEMAP"],
    },
    "CUSTOM_COLUMN": {
        "return_type": "String",
        "description": "Custom table column",
        "locations": ["PROXY_HTTP_HISTORY", "PROXY_WS_HISTORY", "LOGGER"],
    },
    "CUSTOM_ACTION": {
        "return_type": "void",
        "description": "Repeater action",
        "locations": ["REPEATER"],
    },
    "MATCH_AND_REPLACE_REQUEST": {
        "return_type": "HttpRequest",
        "description": "Modify requests in proxy",
        "locations": ["PROXY"],
    },
    "MATCH_AND_REPLACE_RESPONSE": {
        "return_type": "HttpResponse",
        "description": "Modify responses in proxy",
        "locations": ["PROXY"],
    },
    "SCAN_CHECK_ACTIVE_PER_INSERTION_POINT": {
        "return_type": "AuditResult",
        "description": "Active scan per insertion point",
        "locations": ["SCANNER"],
    },
    "SCAN_CHECK_ACTIVE_PER_REQUEST": {
        "return_type": "AuditResult",
        "description": "Active scan per request",
        "locations": ["SCANNER"],
    },
    "SCAN_CHECK_PASSIVE": {
        "return_type": "AuditResult",
        "description": "Passive scan check",
        "locations": ["SCANNER"],
    },
}


@dataclass
class RetrievedContext:
    """Container for retrieved examples and documentation."""
    examples: List[dict]
    documentation: List[dict]


def build_generation_prompt(
    user_request: str,
    bambda_type: Optional[str],
    context: RetrievedContext,
) -> str:
    """Build the user prompt for bambda generation."""

    # Format examples
    examples_text = ""
    for i, ex in enumerate(context.examples, 1):
        examples_text += f"""
### Example {i}: {ex.get('name', 'Unknown')}
Type: {ex.get('bambda_type', 'Unknown')} | Location: {ex.get('location', 'Unknown')}
Description: {ex.get('description', 'No description')}

```java
{ex.get('source', '')}
```
"""

    # Format documentation
    docs_text = ""
    for doc in context.documentation:
        docs_text += f"""
---
{doc.get('content', '')}
"""

    # Build type hint
    type_hint = ""
    if bambda_type and bambda_type in BAMBDA_TYPE_INFO:
        info = BAMBDA_TYPE_INFO[bambda_type]
        type_hint = f"""
## Required Bambda Type: {bambda_type}
- Return type: {info['return_type']}
- Purpose: {info['description']}
- Valid locations: {', '.join(info['locations'])}
"""

    prompt = f"""## User Request:
{user_request}
{type_hint}
## Relevant Documentation:
{docs_text if docs_text else "No specific documentation retrieved."}

## Example Bambda Scripts for Reference:
{examples_text if examples_text else "No examples retrieved."}

## Instructions:
Based on the user request and the examples above, generate a complete Bambda script.
The script should:
1. Follow the patterns shown in the examples
2. Include proper null/empty checks
3. Have a descriptive Javadoc header with @author tag
4. Be syntactically correct Java code

Generate the complete Bambda script:
"""

    return prompt


def detect_bambda_type(user_request: str) -> Optional[str]:
    """Attempt to detect the bambda type from user request."""
    request_lower = user_request.lower()

    # Keywords for each type
    type_keywords = {
        "VIEW_FILTER": ["filter", "filtrar", "show only", "hide", "highlight", "mostrar", "ocultar"],
        "CUSTOM_COLUMN": ["column", "columna", "extract", "extraer", "display", "mostrar campo"],
        "CUSTOM_ACTION": ["action", "accion", "repeater", "modify", "modificar", "send", "enviar"],
        "MATCH_AND_REPLACE_REQUEST": ["replace request", "modify request", "transform request", "reemplazar request"],
        "MATCH_AND_REPLACE_RESPONSE": ["replace response", "modify response", "transform response", "reemplazar response"],
        "SCAN_CHECK_ACTIVE_PER_INSERTION_POINT": ["scan", "active scan", "vulnerability", "injection point"],
        "SCAN_CHECK_PASSIVE": ["passive scan", "detect", "detectar", "check header", "analyze response"],
    }

    # Match the most specific keyword first. Iterating the dict in order would let
    # a short, generic keyword win over a longer, more precise one that belongs to
    # another type -- e.g. "passive scan for a missing CSP header" matched
    # SCAN_CHECK_ACTIVE_* on "scan" before SCAN_CHECK_PASSIVE could match
    # "passive scan".
    matches = [
        (keyword, bambda_type)
        for bambda_type, keywords in type_keywords.items()
        for keyword in keywords
        if keyword in request_lower
    ]
    if not matches:
        return None

    matches.sort(key=lambda m: len(m[0]), reverse=True)
    return matches[0][1]
