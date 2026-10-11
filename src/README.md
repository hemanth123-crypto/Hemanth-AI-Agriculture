# Source layout map

The running backend's canonical package is `app/`; it is intentionally kept in
place to preserve imports and existing application behavior. The requested
`src/` submission layout maps to these implementation directories:

| Submission path | Canonical implementation |
|---|---|
| `src/api/` | `app/api/` |
| `src/agents/` | `app/agents/` |
| `src/rag/` | `app/rag/` |
| `src/services/` | `app/services/` |
| `src/utils/` | `app/utils/` |
| `src/main.py` | launcher importing `app.main:app` |

Do not duplicate these packages under `src/`: imports, model loading, data paths,
indexes, and application startup currently use `app/` and repository-root paths.
