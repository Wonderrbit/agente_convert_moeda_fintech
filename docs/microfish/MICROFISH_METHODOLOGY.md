# MicroFish Methodology

> **Metodologia proprietária de validação de produto em 5 dias**  
> Inspirada no Google Design Sprint + Lean Startup + Continuous Discovery  
> Adaptada para produtos de IA com ciclo de feedback técnico + negócio

---

## 🎯 Princípios Fundamentais

| Princípio | Descrição |
|-----------|-----------|
| **Velocidade sobre perfeição** | Entregar aprendizado validado em 5 dias, não produto perfeito |
| **Técnico + Negócio juntos** | Engenheiros e PMs validam hipóteses simultaneamente |
| **Dados reais > Opiniões** | Entrevistas + questionário + protótipo funcional |
| **Kill criteria claros** | Definidos no Dia 1: o que mata o projeto |
| **Documentação viva** | Tudo versionado, rastreável, reutilizável |

---

## 📅 Cronograma 5 Dias

### DIA 1: MAPEAR (Understand & Define)
**Objetivo**: Alinhamento total do problema, público, hipóteses e métricas

```
MANHÃ (4h)
├── Lightning Talks (stakeholders): 30min cada
│   ├── Negócio: TAM, unit economics, canais
│   ├── Técnico: Stack, constraints, dívida técnica
│   ├── UX: Jornadas atuais, dores, workarounds
│   └── Dados: Métricas baseline, instrumentação
├── How Might We (HMWs): 45min
├── Mapa da Experiência (As-Is): 60min
└── Definição do Target Profile: 30min

TARDE (4h)
├── Hipóteses Prioritárias (ICE Score): 60min
├── Métricas de Sucesso (North Star + Guardrails): 45min
├── Kill Criteria (o que mata o projeto): 30min
├── Recrutamento Entrevistas (screener): 30min
└── Setup Ferramentas (Miro, Notion, Typeform): 30min
```

**Entregáveis Dia 1**:
- [ ] Problem Statement (1 frase)
- [ ] 3-5 Hipóteses ranqueadas por ICE
- [ ] North Star Metric + 3 Guardrails
- [ ] Kill Criteria (3-5 itens binários)
- [ ] Screener + roteiro entrevistas
- [ ] Link Typeform questionário

---

### DIA 2: ESQUEMAR (Sketch & Architect)
**Objetivo**: Transformar hipóteses em fluxos técnicos e de produto testáveis

```
MANHÃ (4h)
├── Crazy 8s (soluções): 20min
├── Solution Sketches (detalhados): 60min
├── Heat Map Voting: 15min
├── Storyboard Jornada Completa: 60min
└── Definição MVP Scope (MoSCoW): 45min

TARDE (4h)
├── Arquitetura Técnica (C4 Level 1-2): 90min
├── Data Model + API Contracts: 60min
├── Prompt Engineering Strategy: 45min
├── n8n Workflow Design (visual): 45min
└── Definition of Ready (DoR) para protótipo: 30min
```

**Entregáveis Dia 2**:
- [ ] Storyboard 8-12 frames (jornada completa)
- [ ] Arquitetura C4 (Contexto + Container)
- [ ] Schema DB (Mermaid/SQL)
- [ ] API Contracts (OpenAPI 3.0)
- [ ] System Prompts v0.1 por agente
- [ ] n8n Workflow diagrams (Mermaid)
- [ ] DoR checklist para Dia 4

---

### DIA 3: DECIDIR (Decide & Plan)
**Objetivo**: Decisões técnicas irreversíveis + plano de execução Dia 4

```
MANHÃ (3h)
├── Decision Matrix (técnicas): 60min
│   ├── LLM Provider (OpenAI vs Claude vs Gemini vs Local)
│   ├── Vector DB (pgvector vs Pinecone vs Weaviate vs Neo4j)
│   ├── Orquestração (n8n vs LangGraph vs Custom)
│   └── WhatsAPI (Evolution vs Twilio vs Official vs Z-API)
├── RICE Prioritization (features MVP): 45min
├── Risk Assessment (técnico + regulatório): 45min

TARDE (3h)
├── Sprint Plan Dia 4 (tasks + owners + estimativas): 60min
├── Test Plan (cenários + critérios aceitação): 45min
├── Questionário Final (Typeform): 45min
└── Prep Entrevistas (calendário + consentimento): 30min
```

**Entregáveis Dia 3**:
- [ ] ADRs (Architecture Decision Records) - 3-5 decisões
- [ ] Backlog MVP priorizado (RICE)
- [ ] Risk Register (probabilidade × impacto + mitigação)
- [ ] Sprint Board Dia 4 (Notion/Linear/Jira)
- [ ] Questionário validado (piloto n=5)
- [ ] Agenda entrevistas confirmada (n≥10)

---

### DIA 4: PROTOTIPAR (Prototype & Build)
**Objetivo**: Protótipo funcional end-to-end (n8n + DB + LLM + WhatsApp)

```
MANHÃ (5h) - BUILD SPRINT
├── Setup Infra (Docker Compose local): 30min
├── DB Migration + Seeds: 30min
├── n8n Workflows Core (3-5 flows): 3h
│   ├── Flow 1: Onboarding + Coleta Perfil
│   ├── Flow 2: Motor DCA + Mix País
│   ├── Flow 3: Alertas Trailing + Notificações
│   └── Flow 4: Consulta Taxas + Cache Redis
├── System Prompts v0.2 (testados): 45min
└── Integração Evolution API (sandbox): 30min

TARDE (3h) - POLISH & PREP TESTE
├── Testes Internos (smoke + happy path): 60min
├── Correção Bugs Críticos: 45min
├── Preparação Cenários Teste Usuário: 30min
├── Briefing Entrevistadores: 30min
└── Backup Plan (se algo quebrar): 15min
```

**Entregáveis Dia 4**:
- [ ] 3-5 n8n workflows funcionais (exportados JSON)
- [ ] DB populado + migrações versionadas
- [ ] Prompts testados (LangFuse traces)
- [ ] Evolution API recebendo/enviando msgs
- [ ] Cenários de teste documentados
- [ ] Gravação loom (5min) demonstrando fluxo

---

### DIA 5: TESTAR (Test & Learn)
**Objetivo**: Validação qualitativa + quantitativa + decisão Go/No-Go

```
MANHÃ (4h) - ENTREVISTAS QUALITATIVAS
├── 10-12 Entrevistas (45min cada, remotas)
│   ├── 5min: Rapport + Contextualização
│   ├── 10min: Jornada Atual (problema)
│   ├── 20min: Teste Protótipo (think-aloud)
│   ├── 5min: WTP + Feature Ranking
│   └── 5min: Fechamento + NPS
├── Synthesis Imediato (affinity mapping): 60min

TARDE (4h) - QUANTITATIVO + DECISÃO
├── Lançamento Questionário (n≥100 alvo): 30min
├── Análise Preliminar (enquanto coleta): 60min
├── Métricas Técnicas (LangFuse + Grafana): 30min
├── Decision Meeting (Go/No-Go/Pivot): 60min
│   ├── North Star atingida?
│   ├── Kill Criteria violados?
│   ├── Insights surpreendentes?
│   └── Próximos passos claros
└── Documentação Final + Handoff: 45min
```

**Entregáveis Dia 5**:
- [ ] Relatório Entrevistas (insights + quotes + patterns)
- [ ] Dashboard Questionário (Typeform/Metabase)
- [ ] Métricas Técnicas (latência, custo, erro, satisfação)
- [ ] **DECISÃO**: Go / No-Go / Pivot (documentada com evidências)
- [ ] Backlog Próxima Fase (se Go)
- [ ] Lessons Learned (o que funcionou/não na metodologia)

---

## 📊 Template de Decisão Go/No-Go

```markdown
# Decisão MicroFish #[NÚMERO] - [PRODUTO]

## Decisão: GO / NO-GO / PIVOT

## Evidências Quantitativas
| Métrica | Target | Alcançado | Status |
|---------|--------|-----------|--------|
| North Star | [valor] | [valor] | ✅/❌ |
| Guardrail 1 | [valor] | [valor] | ✅/❌ |
| Guardrail 2 | [valor] | [valor] | ✅/❌ |
| WTP Médio | >R$ [X] | R$ [Y] | ✅/❌ |
| Intenção Top-2 | >[X]% | [Y]% | ✅/❌ |
| NPS Estimado | >[X] | [Y] | ✅/❌ |

## Evidências Qualitativas
- **Theme 1**: [descrição + quotes representativas]
- **Theme 2**: [descrição + quotes representativas]
- **Theme 3**: [descrição + quotes representativas]

## Kill Criteria Check
- [ ] Critério 1: [descrição] → ✅/❌
- [ ] Critério 2: [descrição] → ✅/❌
- [ ] Critério 3: [descrição] → ✅/❌

## Riscos Identificados
| Risco | Prob | Impacto | Mitigação |
|-------|------|---------|-----------|
| [Risco 1] | Alta/Média/Baixa | Alto/Médio/Baixo | [Ação] |

## Próximos Passos (se GO)
1. [Ação 1 - owner - prazo]
2. [Ação 2 - owner - prazo]
3. [Ação 3 - owner - prazo]

## Assinaturas
- Product: _______________ Data: __/__/____
- Tech Lead: _______________ Data: __/__/____
- Stakeholder: _______________ Data: __/__/____
```

---

## 🛠️ Ferramentas & Templates

### Stack MicroFish
| Categoria | Ferramenta | Propósito |
|-----------|------------|-----------|
| Colaboração | Miro / FigJam | Mapas, storyboards, votação |
| Documentação | Notion / Obsidian | Living docs, ADRs, decisions |
| Questionário | Typeform / Tally | Quantitativo (branching, logic) |
| Agendamento | Calendly / Cal.com | Entrevistas automáticas |
| Gravação | Loom / Riverside | Async review entrevistas |
| Protótipo | n8n + Evolution API | Funcional real (não mock) |
| Observabilidade | LangFuse + Grafana | Traces, custos, qualidade |
| Análise | Python (pandas, scipy) / Metabase | Stats, significância |

### Templates Inclusos no Repo
```
docs/microfish/
├── templates/
│   ├── day1_problem_statement.md
│   ├── day1_hypotheses_ice.xlsx
│   ├── day1_kill_criteria.md
│   ├── day2_storyboard_template.fig
│   ├── day2_architecture_c4.mermaid
│   ├── day2_db_schema.sql
│   ├── day2_api_contracts.yaml
│   ├── day3_adrs_template.md
│   ├── day3_rice_backlog.xlsx
│   ├── day3_risk_register.xlsx
│   ├── day4_sprint_board.json
│   ├── day4_test_scenarios.md
│   ├── day5_interview_script.md
│   ├── day5_questionnaire_typeform.json
│   ├── day5_affinity_mapping.miro
│   ├── day5_decision_template.md
│   └── day5_lessons_learned.md
└── results/
    ├── microfish_01_cambiobot/     # Este projeto
    └── microfish_02_[proximo]/     # Futuros ciclos
```

---

## 📈 Métricas de Sucesso da Metodologia

| Métrica | Target | Como Medir |
|---------|--------|------------|
| Tempo ciclo ideia→decisão | ≤5 dias | Calendar days |
| Taxa Go/No-Go clara | 100% | Decisão documentada |
| Hipóteses validadas/ciclo | ≥3 | Count no decision doc |
| Custo por ciclo | <R$ 2.000 | Ferramentas + incentivos |
| Reutilização assets | >60% | Templates + prompts + workflows |
| Satisfação equipe | >4.0/5.0 | Survey pós-ciclo |

---

## 🔄 Evolução Contínua

### Pós-Ciclo (Semana 1)
- [ ] Retrospectiva 30min (Start/Stop/Continue)
- [ ] Atualização templates baseado em gaps
- [ ] Compartilhamento learnings (interno + blog)
- [ ] Planejamento próximo ciclo (se aplicável)

### Métricas Longo Prazo
- % projetos que chegam produção após MicroFish Go
- Time-to-market redução vs processo anterior
- False positive rate (Go mas falhou no mercado)
- False negative rate (No-Go mas seria sucesso)

---

## 📚 Referências & Inspirações

- **Google Design Sprint** (Jake Knapp) - Estrutura 5 dias
- **Lean Startup** (Eric Ries) - Build-Measure-Learn, MVP, Pivot
- **Continuous Discovery** (Teresa Torres) - Opportunity Solution Tree
- **Shape Up** (Basecamp) - Betting table, appetite, pitch
- **Amazon Working Backwards** - PR/FAQ, customer obsession
- **IDEO Design Thinking** - Empatia, ideação, prototipagem

---

## 🎓 Aplicação no CambioBot (MicroFish #1)

### Contexto
- **Produto**: CambioBot - Agente WhatsApp otimização cambial
- **Equipe**: 1 Tech Lead (Luiz) + 1 PM (part-time) + 1 Designer (consultoria)
- **Período**: 10-14 Junho 2025
- **Investimento**: ~R$ 1.200 (incentivos entrevistas + ferramentas)

### Resultados Resumidos
| Métrica | Target | Resultado |
|---------|--------|-----------|
| Entrevistas completadas | 10 | **12** |
| Questionário respostas | 100 | **157** |
| Intenção uso (top-2) | >60% | **73%** |
| WTP médio | >R$ 15 | **R$ 28,40** |
| NPS estimado | >30 | **42** |
| Workflows n8n funcionais | 3 | **5** |
| Kill Criteria violados | 0 | **0** |

### Decisão: **GO** ✅
**Próxima fase**: Fase 1 MVP (Semanas 3-6) - Ver [Roadmap](../README.md#-roadmap)

### Assets Reutilizáveis Gerados
- 5 n8n workflows JSON (base para qualquer agente WhatsApp)
- 8 System Prompts (coletor, planejador, monitor, executor, afiliados)
- Schema DB multi-tenant ready
- Questionário validado (adaptável para outros fintechs)
- ADRs: LLM Router, Vector DB, Orquestração, WhatsAPI

---

*Metodologia MicroFish v1.0 - Junho 2025*  
*Desenvolvida por Luiz Dranka - Engenheiro IA / Tech Lead*  
*Licença: MIT - Livre para uso e adaptação*