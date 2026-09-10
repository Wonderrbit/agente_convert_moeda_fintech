"""CLI for CambioBot."""

import asyncio
from decimal import Decimal
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..config import settings
from ..dataflows import get_fx_aggregator, calculate_dca_simulation
from ..agents import analyze_fx
from ..integrations import get_fx_tradingagents, TRADINGAGENTS_AVAILABLE

app = typer.Typer(
    name="cambiobot",
    help="CambioBot - Agente Inteligente de Otimização Cambial para Viajantes via WhatsApp",
    add_completion=False,
)
console = Console()


@app.command()
def version():
    """Show version information."""
    console.print(Panel.fit(
        f"[bold blue]CambioBot[/bold blue] v{settings.app_version}\n"
        f"Environment: {settings.environment}\n"
        f"LLM Provider: {settings.llm_provider}\n"
        f"TradingAgents: {'Available' if TRADINGAGENTS_AVAILABLE else 'Not installed'}",
        title="Version Info",
    ))


@app.command()
def config():
    """Show current configuration (non-sensitive)."""
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")

    configs = {
        "App Name": settings.app_name,
        "Version": settings.app_version,
        "Environment": settings.environment,
        "Debug": str(settings.debug),
        "LLM Provider": settings.llm_provider,
        "Deep Think LLM": settings.deep_think_llm,
        "Quick Think LLM": settings.quick_think_llm,
        "Temperature": str(settings.temperature),
        "Max Tokens": str(settings.max_tokens),
        "TradingAgents Enabled": str(settings.tradingagents_enabled),
        "Database": settings.database_url.split("@")[-1] if "@" in settings.database_url else "Not configured",
        "Redis": settings.redis_url,
        "Evolution API": settings.evolution_api_url,
    }

    for key, value in configs.items():
        table.add_row(key, value)

    console.print(table)


# FX Rates Commands
rates_app = typer.Typer(help="FX Rates commands")
app.add_typer(rates_app, name="rates")


@rates_app.command("spot")
def rates_spot(
    base: str = typer.Option("BRL", help="Base currency"),
    target: str = typer.Option(..., help="Target currency"),
):
    """Get current spot rate."""
    async def _get_rate():
        aggregator = get_fx_aggregator()
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(f"Fetching {base}/{target}...", total=None)
            rate = await aggregator.get_spot_rate(base.upper(), target.upper())
            progress.update(task, completed=True)

        table = Table(title=f"Spot Rate: {rate.base}/{rate.target}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        table.add_row("Rate", f"{rate.rate:.6f}")
        table.add_row("Source", rate.source)
        table.add_row("Timestamp", rate.timestamp.isoformat())
        if rate.bid:
            table.add_row("Bid", f"{rate.bid:.6f}")
        if rate.ask:
            table.add_row("Ask", f"{rate.ask:.6f}")
        if rate.spread_pct:
            table.add_row("Spread %", f"{rate.spread_pct:.4f}%")

        console.print(table)

    asyncio.run(_get_rate())


@rates_app.command("multi")
def rates_multi(
    base: str = typer.Option("BRL", help="Base currency"),
    targets: str = typer.Option(..., help="Comma-separated target currencies (e.g., USD,EUR,GBP)"),
):
    """Get spot rates for multiple targets."""
    target_list = [t.strip().upper() for t in targets.split(",")]

    async def _get_rates():
        aggregator = get_fx_aggregator()
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(f"Fetching {len(target_list)} rates...", total=None)
            rates = await aggregator.get_multiple_spot_rates(base.upper(), target_list)
            progress.update(task, completed=True)

        table = Table(title=f"Spot Rates: {base.upper()} → {', '.join(target_list)}")
        table.add_column("Target", style="cyan")
        table.add_column("Rate", style="green", justify="right")
        table.add_column("Source", style="yellow")
        table.add_column("Timestamp", style="dim")

        for target, rate in rates.items():
            if rate:
                table.add_row(target, f"{rate.rate:.6f}", rate.source, rate.timestamp.strftime("%H:%M:%S"))
            else:
                table.add_row(target, "[red]Failed[/red]", "-", "-")

        console.print(table)

    asyncio.run(_get_rates())


# DCA Commands
dca_app = typer.Typer(help="DCA (Dollar Cost Averaging) commands")
app.add_typer(dca_app, name="dca")


@dca_app.command("simulate")
def dca_simulate(
    base: str = typer.Option("BRL", help="Base currency"),
    target: str = typer.Option(..., help="Target currency"),
    amount: float = typer.Option(..., help="Total amount in base currency"),
    installments: int = typer.Option(8, help="Number of installments"),
    frequency: int = typer.Option(7, help="Frequency in days"),
    lookback: int = typer.Option(365, help="Historical lookback in days"),
):
    """Simulate DCA strategy on historical data."""
    async def _simulate():
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(f"Simulating DCA {base}/{target}...", total=None)
            result = await calculate_dca_simulation(
                base=base.upper(),
                target=target.upper(),
                total_amount=Decimal(str(amount)),
                installments=installments,
                frequency_days=frequency,
                lookback_days=lookback,
            )
            progress.update(task, completed=True)

        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            return

        # Summary panel
        console.print(Panel.fit(
            f"[bold]DCA Simulation Results[/bold]\n\n"
            f"Strategy: {result['strategy']}\n"
            f"Installments: {result['installments']} (every {result['frequency_days']} days)\n"
            f"Total Spent: {result['total_base_spent']:,.2f} {base}\n"
            f"Total Purchased: {result['total_target_purchased']:,.4f} {target}\n"
            f"Average Rate: {result['average_rate']:.6f}\n"
            f"Final Rate: {result['final_rate']:.6f}\n"
            f"Current Value: {result['current_value']:,.2f} {base}\n"
            f"P&L: {result['pnl']:,.2f} {base} ({result['pnl_pct']:+.2f}%)\n\n"
            f"[bold]vs Lump Sum:[/bold] {result['comparison']['dca_advantage_pct']:+.2f}% advantage",
            title="DCA Simulation",
        ))

    asyncio.run(_simulate())


# Analysis Commands
analysis_app = typer.Typer(help="Multi-agent FX Analysis commands")
app.add_typer(analysis_app, name="analysis")


@analysis_app.command("fx")
def analysis_fx(
    base: str = typer.Option("BRL", help="Base currency"),
    targets: str = typer.Option("USD,EUR", help="Comma-separated target currencies"),
    budget: str = typer.Option("", help="Budget per currency (e.g., USD=5000,EUR=3000)"),
    days: int = typer.Option(90, help="Days until travel"),
):
    """Run multi-agent FX analysis."""
    target_list = [t.strip().upper() for t in targets.split(",")]

    # Parse budget
    budget_dict = {}
    if budget:
        for pair in budget.split(","):
            if "=" in pair:
                curr, amt = pair.split("=")
                budget_dict[curr.strip().upper()] = float(amt)

    # Travel dates (approximate)
    from datetime import datetime, timedelta
    travel_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    travel_dates = {curr: travel_date for curr in target_list}

    async def _analyze():
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(f"Running multi-agent analysis for {len(target_list)} currencies...", total=None)
            result = await analyze_fx(
                base_currency=base.upper(),
                target_currencies=target_list,
                travel_dates=travel_dates,
                budget_per_currency=budget_dict,
                user_profile={"risk_tolerance": "moderate", "experience": "intermediate"},
            )
            progress.update(task, completed=True)

        console.print(Panel.fit(
            f"[bold]FX Analysis Complete[/bold]\n\n"
            f"Recommendation: {result.get('recommendation', 'N/A')[:200]}...\n"
            f"Confidence: {result.get('confidence', 0):.0%}\n"
            f"DCA Plan: {result.get('dca_plan', {})}",
            title="Analysis Result",
        ))

    asyncio.run(_analyze())


@analysis_app.command("tradingagents")
def analysis_tradingagents(
    base: str = typer.Option("BRL", help="Base currency"),
    targets: str = typer.Option("USD,EUR", help="Comma-separated target currencies"),
    date: Optional[str] = typer.Option(None, help="Analysis date (YYYY-MM-DD)"),
):
    """Run TradingAgents analysis on FX pairs."""
    if not TRADINGAGENTS_AVAILABLE:
        console.print("[red]TradingAgents not installed. Install with: pip install -e '.[tradingagents]'[/red]")
        return

    target_list = [t.strip().upper() for t in targets.split(",")]

    async def _analyze():
        wrapper = get_fx_tradingagents()
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            task = progress.add_task(f"Running TradingAgents analysis...", total=None)
            results = await wrapper.analyze_multiple_pairs(base.upper(), target_list, date)
            progress.update(task, completed=True)

        for target, result in results.items():
            if "error" in result:
                console.print(f"[red]{target}: {result['error']}[/red]")
            else:
                console.print(Panel(
                    f"Proxy: {result.get('proxy_ticker', 'N/A')}\n"
                    f"Decision: {result.get('decision', 'N/A')[:300]}...",
                    title=f"TradingAgents: {base}/{target}",
                ))

    asyncio.run(_analyze())


# Server Commands
server_app = typer.Typer(help="Server commands")
app.add_typer(server_app, name="server")


@server_app.command("api")
def server_api(
    host: str = typer.Option("0.0.0.0", help="Host to bind"),
    port: int = typer.Option(8000, help="Port to bind"),
    reload: bool = typer.Option(False, help="Enable auto-reload"),
):
    """Start the FastAPI server."""
    import uvicorn
    console.print(f"[green]Starting API server on {host}:{port}[/green]")
    uvicorn.run(
        "cambiobot.api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level=settings.log_level.lower(),
    )


@server_app.command("worker")
def server_worker():
    """Start the background worker (n8n workflows processor)."""
    console.print("[yellow]Worker not yet implemented[/yellow]")


# Database Commands
db_app = typer.Typer(help="Database commands")
app.add_typer(db_app, name="db")


@db_app.command("migrate")
def db_migrate():
    """Run database migrations."""
    console.print("[yellow]Run: alembic upgrade head[/yellow]")


@db_app.command("seed")
def db_seed():
    """Seed database with reference data."""
    console.print("[yellow]Seed not yet implemented[/yellow]")


if __name__ == "__main__":
    app()