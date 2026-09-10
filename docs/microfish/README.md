# MicroFish - Metodologia de Validação Rápida

> **Valide seu produto de IA em 5 dias** - Técnico + Negócio juntos, dados reais, decisão documentada.

---

## 🎯 O que é MicroFish?

MicroFish é uma **metodologia proprietária** de validação de produto que combina:
- **Design Sprint** (Google) - Estrutura 5 dias
- **Lean Startup** (Eric Ries) - Build-Measure-Learn, hipóteses testáveis
- **Continuous Discovery** (Teresa Torres) - Opportunity Solution Tree
- **Engenharia de IA Moderna** - Protótipos funcionais com LLMs, não mocks

**Resultado**: Decisão **Go/No-Go/Pivot** baseada em evidências qualitativas + quantitativas + técnicas em **5 dias úteis**.

---

## 📦 Este Repositório

```
docs/microfish/
├── MICROFISH_METHODOLOGY.md    # Metodologia completa (dia a dia)
├── RELATORIO_OPINIAO_PUBLICA.md # Resultados CambioBot (MicroFish #1)
├── templates/                  # Templates prontos para uso
│   ├── day1_*.md
│   ├── day2_*.md
│   ├── day3_*.md
│   ├── day4_*.md
│   └── day5_*.md
└── results/
    └── microfish_01_cambiobot/ # Evidências brutas (anexos)
```

---

## 🚀 Quick Start - Use no Seu Projeto

### 1. Clone os Templates
```bash
git clone https://github.com/Wonderrbit/agente_convert_moeda_fintech.git
cd agente_convert_moeda_fintech/docs/microfish/templates
```

### 2. Adapte para Seu Contexto
- Edite `day1_problem_statement.md` com seu problema
- Ajuste `day1_hypotheses_ice.xlsx` com suas hipóteses
- Configure `day3_adrs_template.md` com suas decisões técnicas

### 3. Execute o Ciclo
```
Segunda: MAPEAR    → Problema, hipóteses, kill criteria
Terça:   ESQUEMAR  → Jornada, arquitetura, prompts
Quarta:  DECIDIR   → Stack, priorização, riscos
Quinta:  PROTOTIPAR → n8n + LLM + DB funcionando
Sexta:   TESTAR    → Entrevistas + questionário + DECISÃO
```

---

## 📊 MicroFish #1: CambioBot (Junho 2025)

### Contexto
| Item | Detalhe |
|------|---------|
| **Produto** | Agente WhatsApp otimização cambial viajantes |
| **Problema** | 37% citam câmbio como barreira; perda média 3-7% |
| **Equipe** | 1 Tech Lead + 1 PM part-time + 1 Designer consultoria |
| **Investimento** | ~R$ 1.200 (incentivos + ferramentas) |

### Resultados
| Métrica | Target | Alcançado | Status |
|---------|--------|-----------|--------|
| Entrevistas qualitativas | 10 | **12** | ✅ |
| Questionário quantitativo | 100 | **157** | ✅ |
| Intenção uso (top-2 box) | >60% | **73%** | ✅ |
| WTP médio (R$/mês) | >R$ 15 | **R$ 28,40** | ✅ |
| NPS estimado | >30 | **42** | ✅ |
| Workflows n8n funcionais | 3 | **5** | ✅ |
| Kill Criteria violados | 0 | **0** | ✅ |

### Decisão: **GO** ✅

> **Próxima fase**: MVP WhatsApp (8 semanas) - Ver [Roadmap](../../README.md#-roadmap)

### Assets Gerados (Reutilizáveis)
- ✅ 5 n8n workflows JSON (base para agentes WhatsApp)
- ✅ 8 System Prompts (coletor, planejador, monitor, executor, afiliados)
- ✅ Schema DB PostgreSQL multi-tenant ready
- ✅ Questionário validado (Typeform JSON exportável)
- ✅ 4 ADRs: LLM Router, Vector DB, Orquestração, WhatsAPI
- ✅ Risk Register + RICE Backlog + Decision Template

---

## 🛠️ Stack Recomendada MicroFish

| Categoria | Ferramenta | Por que |
|-----------|------------|---------|
| **Orquestração** | n8n | Visual, versionável, 400+ nodes, self-hosted |
| **WhatsApp** | Evolution API | Open-source, multi-instância, webhooks robustos |
| **LLM** | OpenAI + Anthropic + Google | Roteamento por tarefa, fallback, custo otimizado |
| **Database** | PostgreSQL + pgvector | ACID, JSONB, vetorial nativo, custo zero |
| **Cache** | Redis | Sub-ms para taxas tempo real |
| **Observabilidade** | LangFuse + Grafana | Traces, custos, evals, dashboards business |
| **Deploy** | Docker + K3s | Controle total, custo 70% < AWS |
| **Questionário** | Typeform | Logic jumps, bonito, API para análise |

---

## 📈 Quando Usar MicroFish

| Cenário | Fit |
|---------|-----|
| Nova feature de IA (RAG, Agente, Chatbot) | ✅ **Perfeito** |
| Pivot de produto existente | ✅ **Perfeito** |
| Validação pré-investimento (Pre-Seed/Seed) | ✅ **Perfeito** |
| Discovery contínuo (trimestral) | ✅ **Bom** |
| Projeto regulado (Open Banking, Saúde) | ⚠️ **Adaptar** (add compliance day) |
| Hardware / Deep Tech | ❌ **Não recomendado** |

---

## 🤝 Contribuindo

MicroFish é **open-source (MIT)**. Contribuições bem-vindas:

1. **Melhorias na metodologia** → PR na `MICROFISH_METHODOLOGY.md`
2. **Novos templates** → Add em `templates/`
3. **Case studies** → Add em `results/microfish_XX_[nome]/`
4. **Traduções** → PT/EN/ES welcome

---

## 📚 Recursos Complementares

| Recurso | Link |
|---------|------|
| Metodologia Completa | [MICROFISH_METHODOLOGY.md](MICROFISH_METHODOLOGY.md) |
| Relatório CambioBot | [RELATORIO_OPINIAO_PUBLICA.md](RELATORIO_OPINIAO_PUBLICA.md) |
| Templates Prontos | [`templates/`](templates/) |
| CambioBot Repo Principal | [../../README.md](../../README.md) |

---

## 👨‍💻 Autor

**Luiz Dranka** - Engenheiro IA / Tech Lead Automação & IA  
🔗 [LinkedIn](https://www.linkedin.com/in/luiz-dranka-ba637620b/) | 🐙 [GitHub](https://github.com/Wonderrbit)

> Desenvolvida na prática validando CambioBot.  
> Livre para usar, adaptar, melhorar.  
> **Crédito apreciado, não obrigatório.**

---

## 📄 Licença

**MIT License** - Veja [LICENSE](../../LICENSE)

> Use em projetos comerciais, acadêmicos, pessoais.  
> Compartilhe melhorias de volta à comunidade se quiser 🤝