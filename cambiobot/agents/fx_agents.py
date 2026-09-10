"""FX Analysis Agents for CambioBot - Specialized agents for currency optimization."""

from typing import Any, Literal
from dataclasses import dataclass, field
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, START, END

from ..llm_clients import create_deep_llm, create_quick_llm
from ..config import settings


@dataclass
class FXState:
    """State for FX analysis workflow."""
    # Input
    base_currency: str = "BRL"
    target_currencies: list[str] = field(default_factory=lambda: ["USD", "EUR"])
    travel_dates: dict[str, str] = field(default_factory=dict)  # currency -> date
    budget_per_currency: dict[str, float] = field(default_factory=dict)
    user_profile: dict = field(default_factory=dict)

    # Analysis results
    fundamental_analysis: dict = field(default_factory=dict)
    technical_analysis: dict = field(default_factory=dict)
    sentiment_analysis: dict = field(default_factory=dict)
    macro_analysis: dict = field(default_factory=dict)

    # Research debate
    bullish_arguments: list[str] = field(default_factory=list)
    bearish_arguments: list[str] = field(default_factory=list)
    research_consensus: str = ""

    # Trader decision
    dca_plan: dict = field(default_factory=dict)
    entry_signals: dict = field(default_factory=dict)
    risk_assessment: dict = field(default_factory=dict)

    # Final output
    recommendation: str = ""
    confidence: float = 0.0
    metadata: dict = field(default_factory=dict)


# System Prompts for FX Agents

FUNDAMENTALS_ANALYST_PROMPT = """Você é um Analista Fundamentalista de Câmbio especializado em moedas de mercados emergentes e desenvolvidos.

Sua tarefa: Analisar os fundamentos macroeconômicos que afetam o par de moedas {base}/{target}.

Foque em:
1. **Diferencial de Juros**: Taxa Selic (Brasil) vs Fed Funds Rate / ECB Rate / BOJ Rate
2. **Inflação**: IPCA vs CPI/PCE (EUA), HICP (Europa), CPI (Japão)
3. **Contas Externas**: Balanço de pagamentos, reservas internacionais, fluxo de capital
4. **Fiscal**: Déficit primário, dívida/PIB, arcabouço fiscal
5. **Commodities**: Impacto do preço do petróleo, minério de ferro, soja no BRL
6. **Política Monetária**: Forward guidance dos bancos centrais

Fontes de dados sugeridas: Banco Central do Brasil (Focus, Relatórios de Inflação), FRED, IBGE, Tesouro Nacional.

Entregue: Análise estruturada com viés direcional (alta/baixa/neutro), horizonte temporal, e nível de confiança (0-1).
"""

TECHNICAL_ANALYST_PROMPT = """Você é um Analista Técnico de Câmbio especializado em análise de tendências, momentum e padrões de preço.

Sua tarefa: Analisar tecnicamente o par {base}/{target} usando indicadores quantitativos.

Indicadores obrigatórios:
- **Tendência**: SMA 20/50/200, EMA 12/26, ADX
- **Momentum**: RSI (14), MACD, Stochastic
- **Volatilidade**: Bollinger Bands, ATR
- **Volume**: OBV, Volume Profile (se disponível)
- **Padrões**: Suportes/Resistências, Canais, Figuras de reversão/continuação

Timeframes: Diário (primário), Semanal (contexto), 4H (timing entrada).

Entregue: Sinal técnico (compra/venda/neutro), níveis-chave (suporte/resistência), stop-loss sugerido, target, horizonte temporal.
"""

SENTIMENT_ANALYST_PROMPT = """Você é um Analista de Sentimento de Mercado Cambial.

Sua tarefa: Avaliar o sentimento do mercado para {base}/{target} a partir de múltiplas fontes.

Fontes a considerar:
1. **Posicionamento**: COT Report (CFTC), Fluxo de investidores não-residentes (B3)
2. **News Sentiment**: Manchetes Bloomberg, Reuters, Valor Econômico, Infomoney
3. **Redes Sociais**: Twitter/X (#Dolar, #Câmbio, #BRL), StockTwits, Reddit (r/investimentos, r/Brasil)
4. **Expectativas**: Boletim Focus (mediana, top 5), Research de bancos (Itaú, Bradesco, BTG, XP)
5. **Risk Appetite**: VIX, DXY, EMBI+ Brasil, CDS 5Y

Metodologia: Agregue sinais em score -1 a +1 (bearish a bullish) com ponderação por fonte.

Entregue: Score de sentimento, drivers principais, risco de reversão súbita, horizonte de validade.
"""

MACRO_ANALYST_PROMPT = """Você é um Analista Macroeconômico Global especializado em fluxos de capital e ciclos cambiais.

Sua tarefa: Analisar o cenário macro global e seu impacto no {base}/{target}.

Temas prioritários:
1. **Política Monetária Global**: Fed (dot plot, QT), ECB, BOJ, PBOC - sincronização/divergência
2. **Crescimento Global**: PMI compostos, PMIs manufatura/serviços, PMIs compostos
3. **Inflação Global**: CPI/Core CPI, expectativas deinflação (breakevens)
4. **Geopolítica**: Guerras comerciais, sanções, conflitos, cadeias de suprimento
5. **Fluxos de Capital**: EM flows, carry trade positioning, dollar funding stress
6. **Dólar Index (DXY)**: Drivers estruturais vs cíclicos

Conexão com Brasil: Como o cenário externo afeta fluxo para BRL, curva de juros, expectativas Focus.

Entregue: Cenário base + 2 alternativos (otimista/pessimista), probabilidades, implicações para câmbio.
"""

RESEARCHER_BULLISH_PROMPT = """Você é um Pesquisador Otimista (Bullish) da equipe de Research Cambial.

Sua tarefa: Construir o caso MAIS FORTE possível para VALORIZAÇÃO de {target} vs {base} (ou seja, {base} se fortalece).

Use as análises dos analistas (fundamentalista, técnico, sentimento, macro) como insumos.
Selecione, enfatize e conecte os pontos que suportam sua tese.
Ignore ou minimize contra-argumentos - seu papel é advogar pela tese bullish.

Estrutura:
1. Tese central (1 frase)
2. 3-5 pilares de sustentação com evidências
3. Catalisadores de curto prazo (1-4 semanas)
4. Riscos principais e por que são gerenciáveis
5. Nível de convicção (0-1)
"""

RESEARCHER_BEARISH_PROMPT = """Você é um Pesquisador Pessimista (Bearish) da equipe de Research Cambial.

Sua tarefa: Construir o caso MAIS FORTE possível para DESVALORIZAÇÃO de {target} vs {base} (ou seja, {base} enfraquece).

Use as análises dos analistas como insumos.
Selecione, enfatize e conecte os pontos que suportam sua tese.
Ignore ou minimize contra-argumentos - seu papel é advogar pela tese bearish.

Estrutura:
1. Tese central (1 frase)
2. 3-5 pilares de sustentação com evidências
3. Catalisadores de curto prazo (1-4 semanas)
4. Riscos principais e por que são gerenciáveis
5. Nível de convicção (0-1)
"""

TRADER_PROMPT = """Você é o Trader Cambial responsável pela decisão final de execução.

Sua tarefa: Sintetizar todas as análises (fundamentalista, técnica, sentimento, macro, debate research) e produzir um PLANO DE EXECUÇÃO DCA para o viajante.

Inputs:
- Perfil do viajante: destino, datas, orçamento, tolerância a risco
- Análises da equipe
- Debate bullish/bearish
- Restrições: liquidez, custos de transação, limites regulatórios

Output obrigatório (JSON):
{{
  "dca_plan": {{
    "currency": "USD",
    "total_budget_usd": 5000,
    "installments": 8,
    "frequency": "weekly",
    "start_date": "2025-01-15",
    "end_date": "2025-03-15",
    "max_single_purchase_pct": 0.15,
    "trailing_stop_pct": 2.0,
    "take_profit_pct": 3.0
  }},
  "entry_signals": {{
    "primary": "RSI < 40 + price near support + bullish divergence",
    "confirmation": "MACD crossover + volume increase",
    "avoid": "Major central bank meetings, NFP, CPI releases"
  }},
  "risk_management": {{
    "max_drawdown_pct": 5.0,
    "position_size_pct": 0.125,
    "stop_loss_rule": "Trailing 2% from best rate achieved",
    "emergency_exit": "Daily close below 200 SMA + risk-off event"
  }},
  "confidence": 0.75,
  "rationale": "Síntese em 3-5 bullets do porquê deste plano"
}}

Regra de Ouro: O plano deve ser EXECUTÁVEL por um agente autônomo via WhatsApp com confirmação do usuário.
"""

RISK_MANAGER_PROMPT = """Você é o Gerente de Risco Cambial - protege o capital do viajante.

Sua tarefa: Avaliar o plano do Trader sob ótica de risco e aprovar/rejeitar/ajustar.

Checklist obrigatório:
1. **Risco de Mercado**: VaR 99% 10 dias, stress test (covid, 2008, 2013 taper tantrum)
2. **Risco de Liquidez**: Spread bid-ask em horários de baixa liquidez, feriados
3. **Risco Operacional**: Falha API corretora, falha Evolution API, erro de execução
4. **Risco Regulatório**: Limites CVM/BCB, compliance LGPD, regras PIX
5. **Risco de Modelo**: Viés dos LLMs, alucinação, data contamination
6. **Risco de Contraparte**: Solvência corretora, custódia fundos

Output: Aprovação condicional com ajustes OU Rejeição com justificativa.
"""

PORTFOLIO_MANAGER_PROMPT = """Você é o Portfolio Manager - decisão final de GO/NO-GO.

Sua tarefa: Revisar Trader + Risk Manager e dar veredito final.

Critérios:
- Alinhamento com objetivo do viajante (economia vs proteção vs especulação)
- Risk-adjusted return esperado > custo de oportunidade (manter em BRL)
- Plano executável dentro das restrições técnicas e regulatórias
- Consistência com decisões passadas (memory/log)

Output final: RECOMENDAÇÃO EXECUTÁVEL para o usuário via WhatsApp.
"""


class FXAnalystTeam:
    """Team of FX analysts running in parallel."""

    def __init__(self):
        self.llm = create_deep_llm(temperature=0.1)
        self.quick_llm = create_quick_llm(temperature=0.0)

    async def run_fundamentals(self, state: FXState) -> dict:
        """Run fundamental analysis for all target currencies."""
        results = {}
        for currency in state.target_currencies:
            prompt = FUNDAMENTALS_ANALYST_PROMPT.format(
                base=state.base_currency, target=currency
            )
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=f"Analise {state.base_currency}/{currency} para viagem em {state.travel_dates.get(currency, 'próximos 90 dias')}. Orçamento: {state.budget_per_currency.get(currency, 'N/A')} {currency}")
            ]
            response = await self.llm.ainvoke(messages)
            results[currency] = response.content
        return results

    async def run_technical(self, state: FXState) -> dict:
        """Run technical analysis for all target currencies."""
        results = {}
        for currency in state.target_currencies:
            prompt = TECHNICAL_ANALYST_PROMPT.format(
                base=state.base_currency, target=currency
            )
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=f"Análise técnica {state.base_currency}/{currency}")
            ]
            response = await self.llm.ainvoke(messages)
            results[currency] = response.content
        return results

    async def run_sentiment(self, state: FXState) -> dict:
        """Run sentiment analysis for all target currencies."""
        results = {}
        for currency in state.target_currencies:
            prompt = SENTIMENT_ANALYST_PROMPT.format(
                base=state.base_currency, target=currency
            )
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=f"Sentimento {state.base_currency}/{currency}")
            ]
            response = await self.llm.ainvoke(messages)
            results[currency] = response.content
        return results

    async def run_macro(self, state: FXState) -> dict:
        """Run macro analysis (single global view)."""
        prompt = MACRO_ANALYST_PROMPT.format(
            base=state.base_currency, target=state.target_currencies[0]
        )
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=f"Cenário macro global impactando {state.base_currency} vs {', '.join(state.target_currencies)}")
        ]
        response = await self.llm.ainvoke(messages)
        return {"global": response.content}


class FXResearchTeam:
    """Bullish/Bearish research debate."""

    def __init__(self):
        self.llm = create_deep_llm(temperature=0.3)  # Slightly higher for debate

    async def run_bullish(self, state: FXState) -> list[str]:
        """Generate bullish arguments."""
        args = []
        for currency in state.target_currencies:
            prompt = RESEARCHER_BULLISH_PROMPT.format(
                base=state.base_currency, target=currency
            )
            context = self._build_context(state, currency)
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=context)
            ]
            response = await self.llm.ainvoke(messages)
            args.append(f"[{currency}] {response.content}")
        return args

    async def run_bearish(self, state: FXState) -> list[str]:
        """Generate bearish arguments."""
        args = []
        for currency in state.target_currencies:
            prompt = RESEARCHER_BEARISH_PROMPT.format(
                base=state.base_currency, target=currency
            )
            context = self._build_context(state, currency)
            messages = [
                SystemMessage(content=prompt),
                HumanMessage(content=context)
            ]
            response = await self.llm.ainvoke(messages)
            args.append(f"[{currency}] {response.content}")
        return args

    def _build_context(self, state: FXState, currency: str) -> str:
        """Build context from all analyst outputs."""
        parts = []
        if state.fundamental_analysis.get(currency):
            parts.append(f"FUNDAMENTALISTA {currency}:\n{state.fundamental_analysis[currency]}")
        if state.technical_analysis.get(currency):
            parts.append(f"TÉCNICO {currency}:\n{state.technical_analysis[currency]}")
        if state.sentiment_analysis.get(currency):
            parts.append(f"SENTIMENTO {currency}:\n{state.sentiment_analysis[currency]}")
        if state.macro_analysis.get("global"):
            parts.append(f"MACRO GLOBAL:\n{state.macro_analysis['global']}")
        return "\n\n---\n\n".join(parts)


class FXTrader:
    """FX Trader - creates executable DCA plan."""

    def __init__(self):
        self.llm = create_deep_llm(temperature=0.1)

    async def create_plan(self, state: FXState) -> dict:
        """Create executable DCA plan."""
        prompt = TRADER_PROMPT.format(
            base=state.base_currency,
            targets=", ".join(state.target_currencies)
        )
        context = self._build_full_context(state)
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=context)
        ]
        response = await self.llm.ainvoke(messages)
        # Parse JSON from response
        import json
        try:
            # Extract JSON from markdown if present
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            return json.loads(content.strip())
        except Exception:
            return {"error": "Failed to parse trader output", "raw": response.content}

    def _build_full_context(self, state: FXState) -> str:
        parts = [
            f"PERFIL VIAJANTE: {state.user_profile}",
            f"MOEDAS: {state.target_currencies}",
            f"DATAS VIAGEM: {state.travel_dates}",
            f"ORÇAMENTOS: {state.budget_per_currency}",
        ]
        for currency in state.target_currencies:
            if state.fundamental_analysis.get(currency):
                parts.append(f"FUNDAMENTAL {currency}: {state.fundamental_analysis[currency][:500]}...")
            if state.technical_analysis.get(currency):
                parts.append(f"TÉCNICO {currency}: {state.technical_analysis[currency][:500]}...")
            if state.sentiment_analysis.get(currency):
                parts.append(f"SENTIMENTO {currency}: {state.sentiment_analysis[currency][:500]}...")
        if state.macro_analysis.get("global"):
            parts.append(f"MACRO: {state.macro_analysis['global'][:500]}...")
        if state.bullish_arguments:
            parts.append(f"BULLISH: {'; '.join(state.bullish_arguments[:2])}")
        if state.bearish_arguments:
            parts.append(f"BEARISH: {'; '.join(state.bearish_arguments[:2])}")
        return "\n\n".join(parts)


class FXRiskManager:
    """Risk Manager for FX plans."""

    def __init__(self):
        self.llm = create_deep_llm(temperature=0.0)

    async def assess(self, state: FXState, trader_plan: dict) -> dict:
        """Assess risk of trader plan."""
        prompt = RISK_MANAGER_PROMPT
        context = f"PLANO TRADER:\n{trader_plan}\n\nCONTEXTO: {self._build_context(state)}"
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=context)
        ]
        response = await self.llm.ainvoke(messages)
        return {"assessment": response.content, "approved": "aprov" in response.content.lower()[:100]}

    def _build_context(self, state: FXState) -> str:
        return f"Moedas: {state.target_currencies}, Orçamentos: {state.budget_per_currency}"


class FXPortfolioManager:
    """Portfolio Manager - final GO/NO-GO."""

    def __init__(self):
        self.llm = create_deep_llm(temperature=0.0)

    async def decide(self, state: FXState, trader_plan: dict, risk_assessment: dict) -> dict:
        """Final decision."""
        prompt = PORTFOLIO_MANAGER_PROMPT
        context = f"""
PLANO TRADER: {trader_plan}
RISK ASSESSMENT: {risk_assessment}
PERFIL USUÁRIO: {state.user_profile}
"""
        messages = [
            SystemMessage(content=prompt),
            HumanMessage(content=context)
        ]
        response = await self.llm.ainvoke(messages)
        return {
            "recommendation": response.content,
            "decision": "GO" if "go" in response.content.lower()[:50] else "NO-GO"
        }


# LangGraph Workflow
def create_fx_analysis_graph() -> StateGraph:
    """Create the FX analysis workflow graph."""
    from langgraph.graph import StateGraph

    workflow = StateGraph(FXState)

    # Analyst nodes (parallel)
    analyst_team = FXAnalystTeam()
    workflow.add_node("fundamentals", analyst_team.run_fundamentals)
    workflow.add_node("technical", analyst_team.run_technical)
    workflow.add_node("sentiment", analyst_team.run_sentiment)
    workflow.add_node("macro", analyst_team.run_macro)

    # Research debate nodes
    research_team = FXResearchTeam()
    workflow.add_node("bullish", research_team.run_bullish)
    workflow.add_node("bearish", research_team.run_bearish)

    # Trader + Risk + PM
    trader = FXTrader()
    risk_mgr = FXRiskManager()
    pm = FXPortfolioManager()

    workflow.add_node("trader", trader.create_plan)
    workflow.add_node("risk_manager", risk_mgr.assess)
    workflow.add_node("portfolio_manager", pm.decide)

    # Edges
    workflow.add_edge(START, "fundamentals")
    workflow.add_edge(START, "technical")
    workflow.add_edge(START, "sentiment")
    workflow.add_edge(START, "macro")

    # After all analysts complete -> research
    workflow.add_edge("fundamentals", "bullish")
    workflow.add_edge("technical", "bullish")
    workflow.add_edge("sentiment", "bullish")
    workflow.add_edge("macro", "bullish")

    workflow.add_edge("fundamentals", "bearish")
    workflow.add_edge("technical", "bearish")
    workflow.add_edge("sentiment", "bearish")
    workflow.add_edge("macro", "bearish")

    # Research -> Trader
    workflow.add_edge("bullish", "trader")
    workflow.add_edge("bearish", "trader")

    # Trader -> Risk -> PM
    workflow.add_edge("trader", "risk_manager")
    workflow.add_edge("risk_manager", "portfolio_manager")
    workflow.add_edge("portfolio_manager", END)

    return workflow.compile()


# Convenience function
async def analyze_fx(
    base_currency: str = "BRL",
    target_currencies: list[str] | None = None,
    travel_dates: dict[str, str] | None = None,
    budget_per_currency: dict[str, float] | None = None,
    user_profile: dict | None = None,
) -> dict:
    """Run full FX analysis and return recommendation."""
    if target_currencies is None:
        target_currencies = ["USD", "EUR"]

    initial_state = FXState(
        base_currency=base_currency,
        target_currencies=target_currencies,
        travel_dates=travel_dates or {},
        budget_per_currency=budget_per_currency or {},
        user_profile=user_profile or {},
    )

    graph = create_fx_analysis_graph()
    result = await graph.ainvoke(initial_state)
    return result