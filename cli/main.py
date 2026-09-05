import typer
import asyncio
from typing import Optional
from datetime import datetime
from rich.console import Console
from rich.table import Table
import sys
sys.path.insert(0, '../backend')

from api_client import PuntersEdgeClient
from models import Race, RaceResponse
from scoring import BetScorer

app = typer.Typer()
console = Console()


@app.command()
def today_bets(
    api_key: str = typer.Option(..., prompt="PuntersEdge API Key"),
    min_score: float = typer.Option(50, help="Minimum bet score (0-100)")
):
    """Show today's best betting opportunities"""
    asyncio.run(_fetch_and_display(api_key, min_score))


async def _fetch_and_display(api_key: str, min_score: float):
    """Fetch races and display best bets"""
    client = PuntersEdgeClient(api_key)
    scorer = BetScorer()

    console.print("\n[bold cyan]PunterEdge - Today's Best Bets[/bold cyan]")
    console.print(f"[dim]Minimum score threshold: {min_score}[/dim]\n")

    try:
        # Fetch next-to-go races
        races_data = await client.get_racing_next_to_go()
        races = [Race(**race) for race in races_data.get('races', [])]

        if not races:
            console.print("[yellow]No races available at this time[/yellow]")
            return

        all_predictions = []

        # Score each race
        for race in races:
            predictions = scorer.score_race(race)
            all_predictions.extend(predictions)

        # Filter by minimum score
        filtered = [p for p in all_predictions if p.score >= min_score]

        if not filtered:
            console.print(
                f"[yellow]No bets met minimum score of {min_score}[/yellow]"
            )
            return

        # Display in table
        table = Table(title=f"Top {len(filtered)} Betting Opportunities")
        table.add_column("Race", style="cyan")
        table.add_column("Runner", style="green")
        table.add_column("Best Price", justify="right")
        table.add_column("Overlay %", justify="right", style="yellow")
        table.add_column("Score", justify="right", style="magenta")
        table.add_column("Start Time", style="blue")
        table.add_column("Notes", style="dim")

        for pred in sorted(filtered, key=lambda x: x.score, reverse=True):
            table.add_row(
                f"{pred.race_venue} R{pred.race_number}",
                f"#{pred.runner_number} {pred.runner_name}",
                f"${pred.best_price:.2f}",
                f"{pred.overlay_pct:.1f}%",
                f"{pred.score:.0f}",
                pred.start_time.strftime("%H:%M"),
                pred.reasoning
            )

        console.print(table)

        # Summary
        console.print(f"\n[bold]Total selections: {len(filtered)}[/bold]")
        avg_score = sum(p.score for p in filtered) / len(filtered)
        console.print(f"Average score: {avg_score:.1f}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise


@app.command()
def list_races(
    api_key: str = typer.Option(..., prompt="PuntersEdge API Key")
):
    """List all upcoming races (no scoring)"""
    asyncio.run(_list_races(api_key))


async def _list_races(api_key: str):
    """Display all available races"""
    client = PuntersEdgeClient(api_key)

    try:
        races_data = await client.get_racing_next_to_go()
        races = [Race(**race) for race in races_data.get('races', [])]

        if not races:
            console.print("[yellow]No races available[/yellow]")
            return

        table = Table(title="Upcoming Races")
        table.add_column("Venue", style="cyan")
        table.add_column("Race #", justify="right")
        table.add_column("Category", style="green")
        table.add_column("Start Time", style="blue")
        table.add_column("Runners", justify="right")

        for race in races:
            table.add_row(
                race.venue,
                str(race.race_number),
                race.category.value,
                race.start_time.strftime("%H:%M"),
                str(len(race.runners))
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise


if __name__ == "__main__":
    app()
