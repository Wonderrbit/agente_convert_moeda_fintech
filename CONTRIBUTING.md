# Contributing to CambioBot

Obrigado por considerar contribuir com o CambioBot! Este documento explica como contribuir de forma efetiva.

## 🎯 Como Contribuir

### Reportando Bugs
1. Verifique se o bug já foi reportado nas [Issues](https://github.com/Wonderrbit/agente_convert_moeda_fintech/issues)
2. Se não existe, crie uma nova issue com:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs atual
   - Logs/errores relevantes
   - Ambiente (OS, Python version, etc.)

### Sugerindo Features
1. Abra uma issue com label `enhancement`
2. Descreva o problema que a feature resolve
3. Explique a solução proposta
4. Considere impactos em performance, segurança, UX

### Pull Requests
1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/nome-da-feature` ou `fix/nome-do-fix`
3. Faça commits pequenos e atômicos
4. Siga os padrões de commit (ver abaixo)
5. Rode os testes localmente
6. Abra o PR com descrição clara

## 📝 Padrões de Commit

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação (não afeta lógica)
- `refactor`: Refatoração sem mudança de comportamento
- `perf`: Melhoria de performance
- `test`: Adição/correção de testes
- `chore`: Manutenção (deps, configs, etc.)
- `ci`: CI/CD
- `build`: Sistema de build

### Exemplos
```
feat(agents): adiciona agente de análise macro
fix(api): corrige validação de webhook Evolution API
docs(readme): atualiza instruções de deploy
refactor(dataflows): simplifica FXDataAggregator
test(integration): adiciona testes para DCA simulation
chore(deps): atualiza langgraph para 0.4.8
```

## 🛠️ Setup de Desenvolvimento

### Pré-requisitos
- Python 3.11+
- Poetry 1.8+
- Docker + Docker Compose
- PostgreSQL 16+ (ou use Docker)
- Redis 7+ (ou use Docker)

### Instalação

```bash
# Clone o fork
git clone https://github.com/SEU_USUARIO/agente_convert_moeda_fintech.git
cd agente_convert_moeda_fintech

# Configure variáveis
cp .env.example .env
# Edite .env com suas chaves

# Instale dependências
poetry install --with=dev,tradingagents

# Suba infraestrutura
docker-compose up -d postgres redis

# Rode migrações
poetry run alembic upgrade head

# Rode testes
poetry run pytest

# Inicie API
poetry run cambiobot-api
```

### Comandos Úteis

```bash
# Linting
poetry run ruff check .
poetry run ruff format .

# Type checking
poetry run mypy cambiobot

# Testes
poetry run pytest -v
poetry run pytest --cov=cambiobot

# CLI
poetry run cambiobot --help
poetry run cambiobot rates spot --target USD
poetry run cambiobot dca simulate --target USD --amount 5000
```

## 🏗️ Arquitetura

```
cambiobot/
├── agents/          # Agentes de IA (FX analysis, DCA, etc.)
├── api/             # FastAPI endpoints
├── cli/             # Typer CLI commands
├── dataflows/       # Data providers (FX rates, FRED, etc.)
├── integrations/    # Integrações externas (TradingAgents)
├── llm_clients/     # Abstração LLM multi-provider
├── config.py        # Configurações centralizadas
└── schemas/         # Pydantic models
```

## 🧪 Testes

### Estrutura
```
tests/
├── unit/           # Testes unitários isolados
├── integration/    # Testes com serviços externos
├── e2e/           # Testes end-to-end
└── conftest.py    # Fixtures compartilhadas
```

### Boas Práticas
- Testes unitários: rápidos, sem I/O externo
- Testes integração: marcados com `@pytest.mark.integration`
- Use fixtures para setup comum
- Mock APIs externas com `responses` ou `pytest-mock`

## 🔒 Segurança

- **NUNCA** commite secrets (.env, chaves API, passwords)
- Use `trufflehog` ou `git-secrets` para scan local
- Dependências: `poetry run pip-audit`
- Reportes de vulnerabilidade: abra issue com label `security` (privado se crítico)

## 📚 Documentação

- Docstrings: Google style
- Type hints obrigatórios em APIs públicas
- README atualizado para mudanças visíveis ao usuário
- ADRs (Architecture Decision Records) para decisões importantes em `docs/architecture/adrs/`

## 🚀 Release Process

1. Versionamento: [SemVer](https://semver.org/)
2. Changelog: `CHANGELOG.md` (Keep a Changelog format)
3. Tags: `v{major}.{minor}.{patch}`
4. GitHub Release com notas
5. Docker image publicada automaticamente via CD

## 🤝 Código de Conduta

- Seja respeitoso e inclusivo
- Foque no código, não na pessoa
- Aceite feedback construtivamente
- Ajude novatos a contribuir

## 📞 Contato

- **Issues**: [GitHub Issues](https://github.com/Wonderrbit/agente_convert_moeda_fintech/issues)
- **Discussões**: [GitHub Discussions](https://github.com/Wonderrbit/agente_convert_moeda_fintech/discussions)
- **Email**: luiz@wonderrbit.dev
- **LinkedIn**: [Luiz Dranka](https://www.linkedin.com/in/luiz-dranka-ba637620b/)

---

**Obrigado por contribuir!** 🚀