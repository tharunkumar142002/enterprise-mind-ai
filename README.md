# EnterpriseMind AI

EnterpriseMind AI is an enterprise knowledge and workflow automation platform
being built through a fourteen-stage RAG and agent engineering roadmap. Its
knowledge domains cover HR, IT/security, finance, products, customer support,
and technical documentation.

**Current scope: EM-001 project scaffolding.** This repository contains a Python
3.12 package, dependency-free smoke tests, repository protections and design
documentation. RAG, agents, APIs and a user interface are planned features.
This scaffold does not claim production readiness.

## Documentation

- [Exact fourteen-stage roadmap](docs/project/roadmap.md)
- [Requirements and EM-001 acceptance criteria](docs/project/requirements.md)
- [Architecture and future module structure](docs/architecture/overview.md)
- [Complete technology inventory: primary tools and alternatives](docs/architecture/technology-inventory.md)
- [Enterprise dataset and provenance plan](docs/data/dataset-plan.md)
- [Codex and contributor instructions](AGENTS.md)
- [GitHub Copilot instructions](.github/copilot-instructions.md)

## Files created for EM-001

```text
enterprise-mind-ai-new11/
├── .gitignore
├── .dockerignore
├── .env.example
├── AGENTS.md
├── README.md
├── pyproject.toml
├── .github/copilot-instructions.md
├── src/enterprise_mind/__init__.py
├── tests/test_smoke.py
└── docs/
    ├── project/{roadmap,requirements}.md
    ├── architecture/{overview,technology-inventory}.md
    └── data/dataset-plan.md
```

The existing `.git/` and `.venv/` are preserved. Future modules are documented
and will be created when their stages begin; empty module trees are unnecessary.

## Run the smoke tests

Use a working Python 3.12 interpreter. No application dependency or package
installation is needed for these tests; discovery loads the package from `src/`.

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

If Python 3.12 is already on PATH, the equivalent command is:

```powershell
python -B -m unittest discover -s tests -v
```

At the initial workspace inspection, `.venv/pyvenv.cfg` referenced Python 3.12.10
at a missing base-interpreter path. The environment was left intact. A working
interpreter is required before runtime validation can be completed; repairing
or replacing the environment requires a separately authorized task.

The package has no runtime dependencies in EM-001. Building/installing it needs
the setuptools build backend and is deferred until dependency installation is
approved. Add task-specific dependencies and reproducible locks when a working
feature needs them, rather than installing the entire technology inventory.

## Cost, data and security boundaries

- Target zero additional spend using existing hardware and local services.
- Primary inference is planned around Ollama with a license-reviewed Qwen model.
- No datasets, model weights, dependencies or containers are downloaded in EM-001.
- Public documents require source-specific license and attribution review.
- Fictional enterprise records must be visibly labeled and contain no real PII.
- `.env.example` contains blank placeholders, not credentials or active settings.
- Secrets, runtime datasets, vector indexes and model artifacts are ignored by
  Git and excluded from future container build contexts.
- Hosted services and cloud resources are optional concepts, not prerequisites.
  Free allowances are finite; no paid fallback or automatic provisioning is allowed.
- Copilot and Codex use existing access. Neither is an application runtime dependency.

Ignore rules do not sanitize logs, remove previously tracked files, or guarantee
that a secret cannot be force-added. Review changes and add secret scanning in
the development/CI stages. Enterprise access control, security testing, quality
evaluation and operational validation are prerequisites for production release.
