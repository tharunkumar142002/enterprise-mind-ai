# Complete technology inventory

## Selection policy

This inventory preserves all requested tools and concepts. **Primary** means the
planned path for a relevant stage, not installed software. **Alternative** means
a comparative implementation or experiment after its need is established.
**Hosted optional** services are documented concepts, not application prerequisites.
EM-001 installs nothing and has zero runtime dependencies.

Use existing hardware and local OSS components by default. Exact versions,
artifact licenses, compatibility and reproducible dependency locks are selected
when implementation begins. Do not download every tool or select every backend
for one deployment. Hardware-heavy training is conditional on existing capacity.

## Runtime, models and retrieval

| Technology/concept | Position | Planned role / stage |
| --- | --- | --- |
| Python 3.12 | Primary | Application and evaluation runtime; Stage 1 onward |
| Ollama | Primary, local | Local inference service; Stage 2 onward; avoid cloud models |
| Qwen | Primary model family candidate | Pick an exact license-reviewed, hardware-sized model; Stage 2 |
| Hugging Face | Primary ecosystem | Model cards, artifacts and libraries; approved downloads only |
| Sentence Transformers | Primary | Local embeddings and cross-encoders; Stages 3/5 |
| NumPy | Primary baseline | Explicit similarity calculations for basic RAG; Stage 3 |
| ChromaDB | Alternative, local | Lightweight persistent RAG prototype; Stage 3 comparison |
| FAISS | Alternative, local | In-process vector-search comparison; Stage 3 |
| Qdrant | Alternative, self-hosted | Dedicated vector engine and filtering; Stage 5 |
| Pinecone | Hosted optional | Managed-vector adapter concept; no required account/service |
| pgvector | Primary integrated target | PostgreSQL vectors and metadata/permission alignment; Stages 5/11 |
| BM25 | Primary concept | Sparse keyword retrieval; Stage 5 |
| RRF (reciprocal rank fusion) | Primary concept | Fuse dense and sparse rankings; Stage 5 |
| Cross-encoder reranking | Primary concept | Locally rerank candidate passages; Stage 5 |
| Hybrid search | Primary concept | Combine dense, keyword and permission-aware retrieval; Stage 5 |
| llama.cpp | Alternative, local | Lower-level inference path retained from the architecture proposal |

## Orchestration and training

| Technology/concept | Position | Planned role / stage |
| --- | --- | --- |
| LangChain | Primary integration | Framework adapters around baseline components; Stage 4 |
| LangGraph | Primary integration | Stateful bounded agent workflows; Stage 6 |
| MCP | Primary protocol | Scoped client/server tool interoperability; Stage 7 |
| Tool calling | Primary concept | Validated tool schemas, permissions, audit and approvals; Stage 7 |
| Multi-agent systems | Primary concept | Bounded researcher/verifier/synthesizer coordination; Stage 7 |
| PyTorch | Primary training runtime | Local model training/inference libraries; Stage 8 |
| Transformers | Primary | Model/tokenizer loading and training integration; Stage 8 |
| TRL | Primary training option | Supervised fine-tuning recipes; Stage 8 |
| PEFT | Primary | Parameter-efficient adapter training; Stage 8 |
| LoRA | Primary concept | Low-rank adapter training; Stage 8 |
| QLoRA | Hardware-dependent concept | Quantized-base adapter training; Stage 8 |
| Unsloth | Alternative, hardware-dependent | Compare optimized training after platform compatibility review |

## Security, evaluation and LLMOps

| Technology/concept | Position | Planned role / stage |
| --- | --- | --- |
| NeMo Guardrails | Alternative supplemental control | Policy/conversation rails around shared authorization; Stage 9 |
| Presidio | Primary PII tooling candidate | Detect/redact sensitive content; Stage 9; not a perfect detector |
| Ragas | Primary evaluation candidate | RAG evaluation with explicitly configured local models; Stage 10 |
| DeepEval | Alternative evaluation framework | Compare local/custom-model answer and agent checks; Stage 10 |
| LangSmith | Hosted optional | Framework tracing/evaluation comparison under authorized free limits |
| MLflow | Primary, self-hosted | Experiment, model/adapter and run lineage; Stages 8/13 |
| OpenTelemetry | Primary | Redacted vendor-neutral traces and metrics; Stage 13 |
| Prometheus | Primary, self-hosted | Operational metrics and alerting; Stage 13 |
| Grafana | Primary, OSS self-hosted | Quality/performance dashboards; Stage 13 |

Deterministic citation, retrieval and authorization checks precede model judges.
Ragas/DeepEval configurations must explicitly use local evaluators; do not allow
default paid-provider calls. Review trace content for secrets/PII before export.

## Application, persistence and delivery

| Technology/concept | Position | Planned role / stage |
| --- | --- | --- |
| FastAPI | Primary | Validated backend, streaming and job APIs; Stage 11 |
| Pydantic | Primary | Typed settings and API/domain contracts as needed |
| PostgreSQL | Primary, self-hosted | Durable metadata, permissions, sessions and vectors; Stage 11 |
| Redis | Optional, self-hosted | Cache/job coordination when measurements justify it; Stage 11 |
| SQLAlchemy | Primary | Relational persistence contracts; Stage 11 |
| Alembic | Primary companion | Reversible, reviewed database migrations; Stage 11 |
| Streamlit | Primary early demo | Demonstrate end-to-end features before a full UI; Stage 11 |
| React | Primary production UI target | Chat, sources, ingestion and agent-run views; Stage 11 |
| TypeScript / Vite | Primary frontend companions | Typed UI and frontend build tooling |
| Docker | Primary container format/tooling concept | Dockerfiles and portable images; Stage 12 |
| Docker Compose | Primary deployment concept | Reproducible local multi-service configuration; Stage 12 |
| Podman | OSS runtime alternative | Use if Docker tooling/licensing is unsuitable for the environment |
| GitHub Actions | Hosted CI concept | Tests/scans/builds within verified included capacity; Stage 12 |
| AWS deployment concepts | Optional cloud design | IAM, networking, storage, containers, secrets, monitoring and budgets |
| unittest | Primary EM-001 tests | Standard-library smoke checks with no dependency installation |
| pytest / Ruff / mypy | Later quality tooling | Behavior tests, lint/format and types once installation is approved |
| Gitleaks / pip-audit | Later security tooling | Secret and dependency checks, local/CI adoption |
| GitHub Copilot / Codex | Existing development access | AI-assisted engineering, outside the app runtime |

## Cost and licensing boundaries

- Pinecone and LangSmith hosted services are not OSS runtime requirements. Keep
  them disabled unless explicitly approved; verify current free limits and prevent
  automatic paid upgrade or overage. If limits are unsuitable, use local adapters.
- GitHub Actions, Hugging Face hosted compute and AWS are hosted services with
  terms/limits. This plan does not promise unlimited free CI, GPUs or cloud hosting.
  AWS remains conceptual until resources, quotas and spending controls are reviewed.
- Docker Desktop has separate licensing terms. Preserve Docker/Compose concepts;
  use a permitted existing installation or an OSS runtime such as Podman.
- Redis licensing varies by version. Review the exact release and select a
  suitable OSS license option (Redis 8 offers an AGPLv3 option); no Redis Cloud
  dependency is required. See [Redis's license announcement](https://redis.io/blog/agplv3/).
- Qwen/model family names do not replace model-card review. Verify the exact
  weights, quantization derivative and dataset licenses, including commercial use.
- Existing Copilot/Codex access does not imply unlimited usage or make hosted
  assistants an open-source service. No additional subscription is required here.

## Primary references

These are upstream references, not commands to install or enable services. Verify
terms again at adoption; technology choices and services can change.

- [Ollama](https://github.com/ollama/ollama), [Qwen](https://github.com/QwenLM/Qwen3),
  [Hugging Face documentation](https://huggingface.co/docs),
  [Sentence Transformers](https://github.com/huggingface/sentence-transformers)
- [ChromaDB](https://github.com/chroma-core/chroma),
  [FAISS](https://github.com/facebookresearch/faiss),
  [Qdrant](https://github.com/qdrant/qdrant),
  [Pinecone plans](https://www.pinecone.io/pricing/),
  [pgvector](https://github.com/pgvector/pgvector)
- [LangChain](https://github.com/langchain-ai/langchain),
  [LangGraph](https://github.com/langchain-ai/langgraph),
  [MCP](https://modelcontextprotocol.io/)
- [PyTorch](https://pytorch.org/),
  [Transformers](https://github.com/huggingface/transformers),
  [TRL](https://github.com/huggingface/trl), [PEFT](https://github.com/huggingface/peft),
  [Unsloth](https://github.com/unslothai/unsloth)
- [NeMo Guardrails](https://github.com/NVIDIA-NeMo/Guardrails),
  [Presidio](https://github.com/microsoft/presidio),
  [Ragas](https://github.com/explodinggradients/ragas),
  [DeepEval](https://github.com/confident-ai/deepeval),
  [LangSmith plans](https://www.langchain.com/pricing),
  [MLflow](https://github.com/mlflow/mlflow)
- [FastAPI](https://fastapi.tiangolo.com/), [PostgreSQL](https://www.postgresql.org/),
  [Redis licenses](https://redis.io/legal/licenses/),
  [SQLAlchemy](https://www.sqlalchemy.org/), [Streamlit](https://streamlit.io/),
  [React](https://react.dev/)
- [Docker](https://docs.docker.com/), [Docker Compose](https://docs.docker.com/compose/),
  [Podman](https://github.com/podman-container-tools/podman),
  [GitHub Actions](https://docs.github.com/en/actions), [AWS](https://docs.aws.amazon.com/)
- [OpenTelemetry](https://opentelemetry.io/docs/),
  [Prometheus](https://github.com/prometheus/prometheus),
  [Grafana](https://github.com/grafana/grafana)
