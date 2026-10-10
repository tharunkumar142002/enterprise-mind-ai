# EnterpriseMind AI: exact fourteen-stage roadmap

The stage names and sequence below are fixed. Security, modularity, cost control
and meaningful tests apply throughout; dedicated later stages deepen them.

| Stage | Exact stage name | Planned implementation and evidence |
| --- | --- | --- |
| 1 | Project setup and real-world dataset | EM-001 scaffold; then a licensed, multi-domain public/fictional corpus, provenance manifest and reviewed evaluation questions. No acquisition in EM-001. |
| 2 | LLM fundamentals and prompt engineering | Ollama/Qwen local inference, Hugging Face model selection, token budgets, versioned prompts, structured output and prompt comparisons. |
| 3 | Basic RAG from scratch | Explicit parsing, chunking, Sentence Transformers embeddings, NumPy similarity, citation-backed answers and abstention; compare FAISS/ChromaDB where appropriate. |
| 4 | LangChain integration | Adapt the shared ingestion/retrieval/generation contracts into LangChain; verify baseline parity rather than duplicating business logic. |
| 5 | Advanced RAG | BM25 plus dense hybrid search, RRF, cross-encoder reranking, query rewriting, permission filters and incremental indexing; benchmark Qdrant/pgvector and optional Pinecone. |
| 6 | LangGraph and agentic RAG | Stateful retrieve/verify/answer workflows, checkpoints, bounded retries, cancellation and recovery. |
| 7 | Tool calling, MCP and multi-agent systems | Typed tools, permission-scoped MCP clients/servers, bounded multi-agent roles and confirmation for workflow mutations. |
| 8 | Fine-tuning, LoRA and QLoRA | PyTorch, Transformers, TRL and PEFT training recipes; LoRA/QLoRA and optional Unsloth; run only on compatible existing hardware; hold out evaluation data. |
| 9 | Guardrails and production security | Authentication, tenant isolation, injection/egress defenses, upload validation, audit, Presidio redaction and optional NeMo Guardrails. |
| 10 | RAG evaluations and agent testing | Deterministic metrics plus locally configured Ragas/DeepEval; test citations, groundedness, abstention, permission boundaries and agent/tool outcomes. |
| 11 | Backend, databases and frontend | FastAPI, PostgreSQL/pgvector, SQLAlchemy/Alembic, optional Redis; Streamlit demo then React UI, streaming chat, document jobs and agent-run inspection. |
| 12 | Docker, CI/CD and cloud deployment | Dockerfiles, Docker Compose, GitHub Actions, scanned/reproducible builds, local deployment, backup/restore and AWS deployment concepts; no assumed free cloud capacity. |
| 13 | LLMOps and production monitoring | Local MLflow, OpenTelemetry, Prometheus, Grafana; prompt/model/index lineage, alerts, runbooks and optional authorized LangSmith tracing. |
| 14 | Advanced extensions and portfolio presentation | Evidence-driven extensions, architecture diagrams, reproducible benchmarks, demo walkthrough, deployment notes and portfolio case study. |

## EM-001 boundary

Create only repository protections, essential documentation, Python 3.12 package
metadata, the root package and standard-library smoke tests. Do not install
dependencies, acquire datasets/models, add future empty modules, commit/push or
deploy. Review the scaffold before the next task.

## Stage progression

Each work item names its stage, requirements, outputs, cost assumptions and
acceptance checks. Select exact dependency/model versions only when adopting
them, record licenses and reproducible configurations, and retain comparison
results. Feature code appears when needed, including early tests and security
checks. A completed scaffold is not a completed production application.
