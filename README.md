# EnterpriseMind AI

EnterpriseMind AI is an enterprise knowledge and workflow automation platform
being built through a fourteen-stage RAG and agent engineering roadmap. Its
knowledge domains cover HR, IT/security, finance, products, customer support,
and technical documentation.

**Current scope: EM-002 enterprise data collection.** Five public-source artifacts
(Python, GNOME, GovInfo, LibreOffice and Bitext) are collected with verified
checksums, provenance and license bundles. Five deterministic, fictional HR
policies complete the six-category seed inventory. Generated HR records live in
ignored `data/synthetic/hr/v1/`; versioned templates and the generator reproduce
them without a network or model. GitLab remains blocked and unapproved.
See the [dataset inventory](data/README.md) and
[final quality review](docs/data/final-data-quality-review.md).
Collection approval does not authorize indexing, training or publication.
Indexing and public demonstration remain blocked by the
[mandatory follow-up gates](docs/project/backlog.md): Bitext record exclusions,
LibreOffice passage exclusion or document hold, validated finance PDF extraction,
preserved HR labels and separate rights/use approval.
RAG, agents,
APIs and a user interface remain planned features; no chunking or embeddings are
implemented. This increment does not claim production readiness.

## Documentation

- [Exact fourteen-stage roadmap](docs/project/roadmap.md)
- [Requirements and EM-001 acceptance criteria](docs/project/requirements.md)
- [Architecture and future module structure](docs/architecture/overview.md)
- [Complete technology inventory: primary tools and alternatives](docs/architecture/technology-inventory.md)
- [Enterprise dataset and provenance plan](docs/data/dataset-plan.md)
- [EM-002 collection usage and approval workflow](docs/data/collection.md)
- [Researched source manifest](data/sources.yaml)
- [Collected dataset inventory and verification](data/README.md)
- [Dataset license and attribution index](data/LICENSES.md)
- [Reproduce and verify synthetic HR](docs/data/synthetic-hr.md)
- [Mandatory data-use gates and follow-up backlog](docs/project/backlog.md)
- [EM-002 proposed commit and pull-request review](docs/project/em-002-pr.md)
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

## Run offline tests

Use a working Python 3.12 interpreter. No application dependency or package
installation is needed; discovery loads the package from `src/`. Collection
tests use fictional bytes, temporary directories and fake HTTP responses, with
network connection guards. Tests never download real documents.

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

If Python 3.12 is already on PATH, the equivalent command is:

```powershell
python -B -m unittest discover -s tests -v
```

The existing Python 3.12.10 environment now runs the complete offline suite:
82 tests, 81 passed and one host-restricted symlink test skipped (2026-10-12).
The environment was preserved. An agent sandbox may require permission to access
its base interpreter; this is not a reason to install or rebuild the environment.

The package still has no runtime dependencies in EM-002. Building/installing it needs
the setuptools build backend and is deferred until dependency installation is
approved. Add task-specific dependencies and reproducible locks when a working
feature needs them, rather than installing the entire technology inventory.

## EM-002 collection command

From the repository root, with an existing working interpreter:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion validate
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion collect --source technical-python-tutorial
```

These commands are offline and do not create download directories. The manifest
uses JSON-formatted YAML 1.2 so it can be read with the standard library. General
YAML syntax is unsupported. See [the collection guide](docs/data/collection.md)
for required metadata, safety limits, approval gates and snapshot provenance.
The optional installed entry point is `enterprise-mind-collect`; installation is
not performed in this task.

The existing public artifacts must not be downloaded again for the HR task.
To verify the generated fictional edition without writing:

```powershell
$env:PYTHONPATH = (Resolve-Path .\src).Path
.\.venv\Scripts\python.exe -B -m enterprise_mind.ingestion.synthetic_hr --check
```

On a fresh checkout, use the [synthetic HR guide](docs/data/synthetic-hr.md) to
generate it from the versioned templates. No preprocessing is implemented yet.

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
