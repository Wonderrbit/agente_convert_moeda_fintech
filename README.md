# CambioBot 🤖💱

> **Agente Inteligente de Otimização Cambial para Viajantes via WhatsApp**
> 
> Transforma a complexidade do câmbio em decisões simples, automatizadas e lucrativas. Economia média de **3-7%** por viagem = **R$ 300-1.500** no bolso do viajante.

---

## 🎯 O Problema

| Métrica | Valor | Fonte |
|---------|-------|-------|
| Gasto de brasileiros no exterior (2025) | **US$ 21,7 bi** | Banco Central |
| Cita câmbio como barreira principal | **37%** | Globo/Valor 2025 |
| Perda média por viagem (spread + taxas) | **3-7%** | Análise de mercado |
| Impacto financeiro médio | **R$ 300-1.500/viagem** | Cálculo próprio |

> **Gap de mercado**: Nenhuma solução atual combina **DCA automático + alertas trailing + mix por país + contexto macro** em interface nativa WhatsApp.

---

## 💡 A Solução

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUXO CAMBIOBOT                              │
├─────────────────────────────────────────────────────────────────┤
│  📥 COLETA      →  🧠 PLANEJA      →  📊 MONITORA  →  ⚡ EXECUTA  │
│  Perfil viagem    DCA + Mix país     Alertas trailing   Compra   │
│  Orçamento        Contexto macro     Tempo real        Otimizada │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    💰 MONETIZA (Afiliados + Premium + B2B)
```

### Diferenciais Competitivos

| Feature | Concorrentes (Wise, Nomad, Bancos) | **CambioBot** |
|---------|-----------------------------------|---------------|
| DCA Automático | ❌ | ✅ **Sim** |
| Alertas Trailing Stop | ❌ | ✅ **Sim** |
| Mix de Moedas por País | ❌ | ✅ **Sim** |
| Preço Médio Tempo Real | ❌ | ✅ **Sim** |
| Contexto Macro (Selic, IPCA, DXY) | ❌ | ✅ **Sim** |
| WhatsApp Nativo (Evolution API) | ❌ | ✅ **Sim** |
| White-label para Bancos/Fintechs | ❌ | ✅ **Fase 3** |

---

## 🏗️ Arquitetura Técnica

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ARQUITETURA CAMBIOBOT                           │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────┐    ┌──────────────┐    ┌────────────────────────────┐  │
│  │ WhatsApp │◄──►│  Evolution   │◄──►│  n8n Orchestrator          │  │
│  │  User    │    │  API         │    │  (Workflows + Agents)      │  │
│  └──────────┘    └──────────────┘    └──────────────┬─────────────┘  │
│                                                      │                │
│                    ┌─────────────────────────────────┼───────────┐   │
│                    ▼                                 ▼           ▼   │
│            ┌───────────────┐              ┌────────────────┐ ┌──────┐ │
│            │  PostgreSQL   │              │  Redis Cache   │ │ LLM  │ │
│            │  (Supabase/   │              │  (Taxas +      │ │Pool  │ │
│            │   Oracle)     │              │   Sessões)     │ │(GPT/ │ │
│            └───────────────┘              └────────────────┘ │Claude│ │
│                                                              │Gemini)│
│                                                              └──────┘ │
│                    ┌────────────────────────────────────────────────┐│
│                    │           OBSERVABILIDADE                      ││
│                    │  LangFuse + Grafana + Prometheus + AlertManager││
│                    └────────────────────────────────────────────────┘│
└────────────────────────────────────────────────────────────────────────┘
```

### Stack Tecnológica

| Camada | Tecnologia | Justificativa |
|--------|------------|---------------|
| **Orquestração** | n8n + TypeScript | Visual, versionável, 400+ integrações |
| **WhatsApp** | Evolution API | Open-source, multi-instância, webhooks |
| **Database** | PostgreSQL (Supabase/Oracle) | ACID, JSONB, pgvector para RAG |
| **Cache** | Redis | Sub-ms latency para taxas em tempo real |
| **LLM Pool** | OpenAI GPT-4o, Claude 3.5, Gemini 1.5 | Roteamento por tarefa, fallback automático |
| **Observabilidade** | LangFuse + Grafana + Prometheus | Traces, métricas, alertas, custo/token |
| **Deploy** | Docker + K3s (Oracle Cloud) | Custo 70% menor que AWS, controle total |
| **CI/CD** | GitHub Actions | Nativo, gratuito para open-source |

---

## 📊 MicroFish Methodology

Metodologia proprietária de **validação de produto em 5 dias** (inspirada no Design Sprint + Lean Startup):

```
DIA 1: MAPEAR     → Problema, público, hipóteses, métricas de sucesso
DIA 2: ESQUEMAR   → Jornada, fluxos, wireframes, arquitetura técnica  
DIA 3: DECIDIR    → Critérios, stack, priorização (ICE/RICE), riscos
DIA 4: PROTOTIPAR → n8n workflows funcionais, DB schema, prompts
DIA 5: TESTAR     → Entrevistas (n=12), questionnaire (n=150+), validação
```

### Resultados da Validação (MicroFish #1)

| Métrica | Target | Alcançado | Status |
|---------|--------|-----------|--------|
| Entrevistas qualitativas | 10 | **12** | ✅ |
| Questionário quantitativo | 100 | **157** | ✅ |
| Intenção de uso (top-2 box) | >60% | **73%** | ✅ |
| WTP médio (R$/mês) | >R$ 15 | **R$ 28,40** | ✅ |
| NPS estimado | >30 | **42** | ✅ |
| Técnico: n8n workflows funcionais | 3 | **5** | ✅ |

> **Insight-chave**: 68% preferem WhatsApp nativo vs app próprio. 81% pagariam por "economia automática sem pensar".

---

## 🚀 Roadmap

### Fase 0: Fundação ✅ **CONCLUÍDA** (Semanas 1-2)
- [x] MicroFish Methodology aplicada
- [x] Questionário otimizado (157 respostas)
- [x] Arquitetura técnica definida
- [x] Schema DB + Seeds (afiliados)
- [x] Prompts base + System prompts

### Fase 1: MVP WhatsApp (Semanas 3-6) 🔄 **EM ANDAMENTO**
- [ ] Evolution API + n8n em produção (Oracle Cloud K3s)
- [ ] Agente coletor de perfil de viagem
- [ ] Motor DCA + Mix por país (EUA, Europa, Argentina, Japão)
- [ ] Alertas trailing stop + notificações push
- [ ] Dashboard Grafana (custo/token, latência, conversão)
- [ ] Testes de carga (100 usuários simultâneos)

### Fase 2: Monetização (Semanas 7-12)
- [ ] Integração afiliados (Nomad, Wise, Avenue, Western Union)
- [ ] Plano Premium R$ 29,90/mês (DCA ilimitado + alertas avançados)
- [ ] Curso "Câmbio Inteligente" (Hotmart) - R$ 197
- [ ] Programa de indicação (viral loop)
- [ ] Meta: **R$ 95k MRR mês 6**

### Fase 3: B2B White-label (Mês 6+)
- [ ] API para bancos/fintechs embarcarem CambioBot
- [ ] Customização de marca, fluxos, comissionamento
- [ ] Compliance Open Banking / LGPD ready
- [ ] Meta: **R$ 580k MRR mês 12**

---

## 📁 Estrutura do Projeto

```
agente_convert_moeda_fintech/
├── .github/
│   └── workflows/           # CI/CD pipelines
├── docs/
│   ├── architecture/        # Arquitetura técnica detalhada
│   ├── microfish/           # Metodologia + resultados validação
│   ├── product/             # Especificações de produto
│   ├── research/            # Pesquisa mercado + concorrentes
│   ├── monetization/        # Modelos financeiros + projeções
│   ├── survey/              # Questionários + análise resultados
│   └── validation/          # Plano de validação contínua
├── n8n/
│   ├── workflows/           # Workflows exportados (JSON)
│   └── credentials/         # Templates de credenciais (sem secrets)
├── prompts/
│   ├── system/              # System prompts por agente
│   └── user/                # Templates de user prompts
├── scripts/
│   ├── analysis/            # Análises de dados + métricas
│   └── simulation/          # Simuladores Monte Carlo, backtesting
├── sql/
│   ├── migrations/          # Schema versionado
│   └── seeds/               # Dados de referência (afiliados, países)
├── tests/
│   ├── unit/                # Testes unitários (pytest)
│   └── integration/         # Testes integração n8n + API
├── docker-compose.yml       # Ambiente local completo
├── Dockerfile               # Imagem produção
├── Makefile                 # Comandos úteis
└── pyproject.toml           # Dependências Python
```

---

## 🛠️ Setup Local

### Pré-requisitos
- Docker + Docker Compose
- Python 3.11+
- Node.js 20+ (para n8n local)
- Conta Evolution API (ou instância local)

### Início Rápido

```bash
# Clone
git clone https://github.com/Wonderrbit/agente_convert_moeda_fintech.git
cd agente_convert_moeda_fintech

# Suba infraestrutura local
docker-compose up -d postgres redis n8n evolution-api

# Configure variáveis
cp .env.example .env
# Edite .env com suas chaves

# Rode migrações
make db-migrate

# Popule seeds
make db-seed

# Inicie n8n workflows (importar via UI em http://localhost:5678)
make n8n-import

# Testes
make test
```

### Variáveis de Ambiente

```bash
# .env.example
DATABASE_URL=postgresql://user:pass@localhost:5432/cambiobot
REDIS_URL=redis://localhost:6379/0
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=your_key
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## 📈 Métricas & Observabilidade

### Dashboards Grafana (incluídos)
- **LLM Costs**: Custo por request, tokens, modelo, latência
- **Business**: Usuários ativos, viagens criadas, DCA executado, receita afiliados
- **Technical**: Latência p50/p95/p99, error rate, queue depth, cache hit rate
- **Agent Quality**: LangFuse traces, eval scores, hallucination rate

### Alertas Críticos
| Alerta | Condição | Ação |
|--------|----------|------|
| `HighErrorRate` | Error rate > 5% 5min | PagerDuty + Slack |
| `LLMCostSpike` | Custo/hora > 2x média | Auto-throttle + alerta |
| `QueueBacklog` | Fila n8n > 100 jobs | Scale workers |
| `DBCPUHigh` | CPU > 80% 10min | Scale read replica |

---

## 💰 Modelo de Negócio

### Projeção 12 Meses

| Canal | Mês 6 | Mês 12 | Premissa |
|-------|-------|--------|----------|
| **Afiliados** (Nomad, Wise, Avenue, WU) | R$ 15k | R$ 80k | 5% conversão, ticket médio US$ 500 |
| **Premium** (R$ 29,90/mês) | R$ 30k | R$ 180k | 1.000 → 6.000 assinantes |
| **Curso Hotmart** (R$ 197) | R$ 50k | R$ 200k | 250 → 1.000 vendas |
| **B2B White-label** | - | R$ 120k | 2 contratos @ R$ 60k/ano |
| **TOTAL MRR** | **~R$ 95k** | **~R$ 580k** | |

### Unit Economics (Mês 12 Projetado)
- **CAC**: R$ 45 (orgânico + indicação + content)
- **LTV**: R$ 1.200 (premium 24m + afiliados recorrentes)
- **LTV/CAC**: **26.7x** ✅
- **Payback**: Mês 2 ✅
- **Gross Margin**: 87% (software marginal cost ~0)

---

## 🔬 Pesquisa & Validação

### Concorrência Direta
| Player | Modelo | Gap CambioBot |
|--------|--------|---------------|
| Wise | Remessa + conta | Sem DCA, sem alertas trailing, app-only |
| Nomad | Conta US + cartão | Sem mix moedas, sem contexto macro |
| Bancos (BB, Itaú, Bradesco) | Câmbio balcão/app | Spread 4-6%, UX ruim, sem automação |
| Câmbio Turismo | Físico + online | Spread 5-8%, sem tecnologia |

### TAM/SAM/SOM
- **TAM**: 19M brasileiros viajantes/ano × US$ 1.100 gasto médio = **US$ 21 bi**
- **SAM**: 5,7M viajantes digitalizados (WhatsApp + banking) = **US$ 6,3 bi**
- **SOM** (3 anos): 50k usuários ativos × R$ 1.200 LTV = **R$ 60M ARR**

---

## 🤝 Contribuindo

```bash
# 1. Fork o repo
# 2. Crie branch feature
git checkout -b feature/nova-funcionalidade

# 3. Commits convencionais
git commit -m "feat: adiciona motor DCA para Japão (JPY)"

# 4. Push + PR
git push origin feature/nova-funcionalidade
```

### Padrões de Commit
- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `refactor:` Refatoração sem mudança de comportamento
- `test:` Testes
- `chore:` Manutenção (deps, configs)

---

## 📄 Licença

**MIT License** - Veja [LICENSE](LICENSE) para detalhes.

> Livre para uso comercial, modificação, distribuição. Atribuição apreciada.

---

## 👨‍💻 Autor

**Luiz Dranka**  
🔗 [LinkedIn](https://www.linkedin.com/in/luiz-dranka-ba637620b/)  
🐙 [GitHub](https://github.com/Wonderrbit)  
📧 Engenheiro de IA / Tech Lead Automação & IA

> **Especialista em**: LangChain, LangGraph, CrewAI, LlamaIndex, Vertex AI/Gemini, FastAPI, MLOps/LLMOps, RAG, Neo4j, Observabilidade (LangFuse, Grafana), Open Banking, Fintech.

---

## 🙏 Agradecimentos

- Comunidade **n8n** e **Evolution API** pela base técnica
- **LangChain/LangGraph** pela orquestração de agentes
- **Supabase/Oracle Cloud** pela infraestrutura acessível
- Todos os **157 respondentes** do questionário de validação

---

⭐ **Se este projeto te ajuda, deixe uma estrela!**  
📢 **Compartilhe com quem viaja e perde dinheiro no câmbio**