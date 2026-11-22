# Knowledge base

`bambdas.json` holds the 94 Bambda examples the generator retrieves from. Each
entry keeps its original `@author` in `metadata.author` — those scripts come from
[PortSwigger's public Bambdas repository](https://github.com/PortSwigger/bambdas)
and belong to their respective authors.

`documentation.json` is **not** shipped with this repository: it would be a
verbatim copy of PortSwigger's documentation. Generate it yourself:

```bash
python scripts/ingest.py /path/to/knowledge-base
```

The ingest script expects this layout:

```
knowledge-base/
├── bambdas/      # .bambda files
├── docs          # Bambda documentation (plain text)
└── API           # Montoya API reference (plain text)
```

Anything missing is simply skipped. The generator works without
`documentation.json` — it just retrieves fewer context chunks.
