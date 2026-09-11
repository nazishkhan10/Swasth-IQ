# Phase 7 — Medical AI & RAG Engine

## AI Provider Specifications
- **Primary Model**: OpenAI GPT-5 Nano (`gpt-5-nano`).
- **Single Provider Architecture**: Dedicated OpenAI provider gateway with strict latency and token budget bounds.

## Guardrail System

```
[ User Input ] ──► [ 1. Input Guardrail (Jailbreak / Injection Detection) ]
                            │
                            ▼
                   [ 2. Privacy Guardrail (PII Masking) ]
                            │
                            ▼
                   [ 3. Retrieval Guardrail (RAG Context Quality) ]
                            │
                            ▼
                   [ 4. Medical Guardrail (Clinical Disclaimer & Scope) ]
                            │
                            ▼
                   [ 5. Output Guardrail (Hallucination & Format Check) ]
```

## Report-Scoped Session Management
- Chat history is strictly isolated per report.
- Sessions are automatically cleared when a report is closed or a new document is uploaded.
- Zero cross-report history leakage.
- SHA-256 audit hashing on every prompt package and generated response.
