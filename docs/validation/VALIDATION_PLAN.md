# Plano de Validação Contínua - CambioBot

> **Pós-MicroFish** | **Framework: Continuous Discovery + Experimentação** | **Owner: Tech Lead**

---

## 🎯 Princípios de Validação Contínua

| Princípio | Implementação |
|-----------|---------------|
| **Discovery contínuo** | Entrevistas semanais (3-5) + questionário trimestral (n≥100) |
| **Experimentação rigorosa** | A/B tests em produção (feature flags), MDE 10%, poder 80% |
| **Métricas leading > lagging** | Ativação, engajamento, NPS → Revenue (resultado) |
| **Kill switches claros** | Cada feature tem criteria de sunset automático |
| **Documentação viva** | Learning log versionado, compartilhado, acionável |

---

## 📊 North Star & Guardrails

### North Star Metric (NSM)
> **Usuários Ativos Semanais com DCA Executado (WAU-DCA)**
> 
> *Definição*: Usuários únicos que tiveram ≥1 compra DCA executada na semana (via agente)
> *Por que*: Captura valor real (dinheiro movido) + engajamento + retenção

### Guardrails (Não Ultrapassar)
| Guardrail | Threshold | Ação se Violado |
|-----------|-----------|-----------------|
| **Custo LLM / Usuário Ativo Mês** | > US$ 2,00 | Auto-throttle + revisão prompts |
| **Taxa Erro Crítico (compra falha)** | > 1% | Rollback imediato + incident |
| **Latência p95 msg→resposta** | > 5s | Scale workers + cache review |
| **Churn Mês 1 (Free)** | > 40% | Investigação qualitativa urgente |
| **NPS Trimestral** | < 30 | Discovery sprint + pivô se necessário |

---

## 🔬 Programa de Experimentação

### Cadência
| Atividade | Frequência | Owner | Output |
|-----------|------------|-------|--------|
| Entrevistas usuários | Semanal (3-5) | PM/Tech Lead | Learning log + insights |
| Questionário NPS/CSAT | Mensal (in-app) | PM | Dashboard + alertas |
| A/B Test ativo | Contínuo (max 3 simultâneos) | Tech Lead | Resultados + decisão |
| Quarterly Survey (n≥100) | Trimestral | PM | Relatório tendências |
| MicroFish Cycle (nova feature grande) | Semestral | Squad | Go/No-Go documentado |

### Pipeline de Experimentos

```
BACKLOG → PRIORIZAÇÃO (ICE) → DESIGN (hypothesis + MDE) → BUILD (feature flag) 
                                                            ↓
                                              LAUNCH (ramp 10%→50%→100%)
                                                            ↓
                                              ANALYZE (stats + guardrails)
                                                            ↓
                                              DECIDE (Ship / Iterate / Kill)
                                                            ↓
                                              DOCUMENT (learning log)
```

### Template Experiment Doc
```markdown
# EXP-[NUM] - [Nome]

## Hipótese
Se [mudança], então [métrica] mudará [direção] em [magnitude], porque [racional].

## Métricas
- **Primary**: [NSM ou proxy] - MDE: [X]% - Poder: 80% - Significância: 95%
- **Guardrails**: [lista]
- **Secondary**: [outras]

## Design
- **Variante A (Control)**: [descrição]
- **Variante B (Treatment)**: [descrição]
- **Randomização**: User-level / Session-level
- **Duração estimada**: [dias] (calculado via power analysis)
- **Amostra mínima**: [n por variante]

## Riscos
- [Risco 1]: Mitigação
- [Risco 2]: Mitigação

## Resultados (pós-experimento)
- **Primary**: [valor A] vs [valor B] → p-value: [X] → **Significativo/NS**
- **Guardrails**: [status cada]
- **Decisão**: SHIP / ITERATE / KILL
- **Learning**: [insight principal]
```

---

## 🧪 Experimentos Planejados (Próximos 6 Meses)

| # | Experimento | Hipótese | Primary Metric | MDE | Status |
|---|-------------|----------|----------------|-----|--------|
| EXP-01 | Onboarding: Perguntas progressivas vs tudo de uma vez | Progressivo ↑ completion rate 15% | Onboarding completion | 10% | Planejado |
| EXP-02 | DCA: Frequência semanal vs quinzenal | Semanal ↑ volume comprado 20% | USD comprado/usuário/mês | 15% | Planejado |
| EXP-03 | Alertas: Push imediato vs digest diário | Imediato ↑ CTR 25% | Alert CTR | 15% | Planejado |
| EXP-04 | Copy: "Economize R$ X" vs "Compre no melhor momento" | Loss aversion ↑ conversão 18% | DCA setup rate | 10% | Planejado |
| EXP-05 | Afiliados: Card único vs carrossel | Carrossel ↑ CTR afiliado 30% | Affiliate CTR | 15% | Backlog |
| EXP-06 | Gamificação: Streak DCA + badges | Streak ↑ retenção mês 2 25% | M2 Retention | 15% | Backlog |
| EXP-07 | Onboarding: Vídeo 30s vs texto | Vídeo ↓ time-to-value 40% | Time to first DCA | 20% | Backlog |
| EXP-08 | Pricing: R$ 29,90 vs R$ 39,90 vs R$ 19,90 | R$ 29,90 ótimo revenue (curva) | ARPU | 10% | Mês 3 |

---

## 📈 Instrumentação & Analytics

### Eventos-Chave (Tracking Plan)
```javascript
// Eventos obrigatórios (implementados no n8n + frontend)
events = {
  // Ativação
  'trip_created': {user_id, destination, budget_usd, travel_date},
  'dca_plan_created': {user_id, trip_id, installments, frequency, mix_config},
  'first_dca_executed': {user_id, trip_id, amount_usd, rate, savings_estimated},
  
  // Engajamento
  'alert_received': {user_id, alert_type, currency, rate, channel},
  'alert_clicked': {user_id, alert_id, action: 'buy_now'|'snooze'|'dismiss'},
  'dca_executed': {user_id, trip_id, installment_num, amount_usd, rate, savings_realized},
  'report_viewed': {user_id, trip_id, report_type: 'weekly'|'post_trip'},
  
  // Monetização
  'affiliate_click': {user_id, partner, product_type, url},
  'affiliate_conversion': {user_id, partner, revenue_brl},
  'premium_started': {user_id, plan, payment_method},
  'premium_cancelled': {user_id, reason, tenure_days},
  
  // Qualidade
  'llm_interaction': {user_id, agent, tokens_in, tokens_out, cost_usd, latency_ms, eval_score},
  'error_occurred': {user_id, flow, error_type, error_msg, severity},
  'feedback_submitted': {user_id, type: 'nps'|'csat'|'bug'|'feature', score, comment}
}
```

### Dashboards Grafana (Já Configurados)
| Dashboard | Métricas Principais | Refresh | Alertas |
|-----------|---------------------|---------|---------|
| **Business Overview** | WAU-DCA, MRR, ARPU, Churn, Affiliate Rev | 5min | Churn >40%, MRR drop >20% |
| **Agent Performance** | Custo/1k, Latência p50/p95, Error Rate, Eval Score | 1min | Custo >$2, Latência >5s, Error >1% |
| **Funnel Activation** | Trip Created → DCA Plan → First DCA → Week 2 Active | 15min | Drop >30% any step |
| **Affiliate Performance** | Clicks, Conversions, Revenue/partner, CPA | 30min | CPA > LTV/3 |
| **Experiment Results** | Auto-updated per EXP-[NUM] | Real-time | Significância + Guardrails |

---

## 🎓 Learning Log (Template)

```markdown
# LEARNING-[YYYY-MM-DD] - [Título]

## Contexto
[O que estávamos testando/descobrindo]

## Descoberta
[Insight principal - 1-2 frases]

## Evidência
[Dados: quantitativos (link dashboard) + qualitativos (quotes)]

## Ação Tomada
[O que mudamos: feature, copy, fluxo, pricing, arquitetura]

## Impacto Esperado
[Métrica alvo + magnitude esperada]

## Próximos Passos
- [ ] [Ação 1]
- [ ] [Ação 2]

## Tags
#onboarding #pricing #retention #trust #activation
```

### Learning Log Index (Exemplos Reais Pós-Launch)
| ID | Data | Descoberta | Ação | Impacto |
|----|------|------------|------|---------|
| L-001 | 2025-07-15 | Usuários não entendem "DCA" → termo técnico | Renomear "Compra Programada" + tooltip | +23% completion onboarding |
| L-002 | 2025-07-22 | Alertas 6h manhã → 3x mais cliques que 20h | Default alert time = 06:00 local | +67% alert CTR |
| L-003 | 2025-08-05 | Argentina: usuários querem "Dólar Blue" não oficial | Adicionar fonte DolarBlue.net + disclaimer | +45% ativação ARG |
| L-004 | 2025-08-18 | Free users fazem 1 DCA e param → limit 5/mês | Tier free: 5 DCA/mês + 3 alerts | +34% M2 retention free |

---

## 🛡️ Governança de Validação

### Comitê de Decisão (Semanal 30min)
- **Tech Lead** (Luiz) - Decisão técnica + arquitetura
- **PM** (ou Luiz acumulando) - Decisão produto + negócio
- **Stakeholder** (conforme necessário) - Contexto estratégico

### RACI por Atividade
| Atividade | Tech Lead | PM | Dev | Designer | Jurídico |
|-----------|-----------|-----|-----|----------|----------|
| Definir experimento | R/A | R | C | C | I |
| Build feature flag | R/A | I | R | I | I |
| Analisar resultados | R/A | R | C | I | I |
| Decidir Ship/Kill | A | R | C | I | C (se regulatório) |
| Documentar learning | R | A | C | C | I |

---

## 📅 Cronograma Validação Fase 1 (8 Semanas)

| Semana | Atividades Validação | Entregáveis |
|--------|---------------------|-------------|
| 1-2 | Setup instrumentação + dashboards + feature flags | Tracking 100% + Grafana live |
| 2-3 | Beta fechado (50 users) + entrevistas semanais | 10 entrevistas + learning log |
| 3-4 | EXP-01 (Onboarding) + EXP-02 (DCA freq) | 2 experiment results |
| 4-5 | EXP-03 (Alertas) + EXP-04 (Copy) | 2 experiment results |
| 5-6 | Launch público + Questionário Mês 1 (n≥100) | Survey results + NPS baseline |
| 6-7 | EXP-05 (Afiliados) + EXP-06 (Gamificação) | 2 experiment results |
| 7-8 | Quarterly Survey #1 + Revisão NSM/Guardrails | Relatório trimestral + ajustes |

---

## 🔄 Integração com MicroFish

### Quando Disparar Novo MicroFish Cycle
- [ ] Nova feature grande (ex: B2B White-label, Novo país complexo)
- [ ] Pivot estratégico (ex: Muda canal, muda modelo receita)
- [ ] Kill criteria NSM violado 2 meses consecutivos
- [ ] Oportunidade mercado >R$ 100k MRR não endereçada

### Assets Reutilizáveis MicroFish → Contínuo
- Templates entrevista/questionário → Adaptação rápida
- ADRs → Base decisões arquitetura novos experimentos
- n8n workflows → Feature flags para variantes
- LangFuse/Grafana → Instrumentação já pronta
- Decision log → Histórico decisões para evitar retrabalho

---

## 📚 Referências Metodológicas

- **Continuous Discovery Habits** - Teresa Torres (Opportunity Solution Tree)
- **Trustworthy Online Controlled Experiments** - Kohavi, Tang, Xu (A/B testing rigoroso)
- **Measure What Matters** - John Doerr (OKRs + Guardrails)
- **Lean Analytics** - Croll & Yoskovitz (Métricas por estágio)
- **MicroFish Methodology** - Este repo (Validação rápida 5 dias)

---

*Plano vivo - Atualizado a cada learning log*  
*Owner: Luiz Dranka | Última atualização: Junho 2025 | Versão: 1.0*