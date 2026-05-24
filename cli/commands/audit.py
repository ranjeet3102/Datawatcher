from os import path

import typer
from rich.console import Console
from datawatcher.loaders.factory import load_dataset

audit_app = typer.Typer()

console = Console()

SUPPORTED_DOMAINS = [
    "finance",
    "timeseries",
    "healthcare",
    "time series"
]



@audit_app.command("run")
def run(
    path: str,
    target: str = None,
    domain: str = None
):

    if domain and domain not in SUPPORTED_DOMAINS:

        console.print(
            f"[bold red]Unsupported domain:[/bold red] {domain}"
        )

        raise typer.Exit()

    dataset = load_dataset(path)

    console.print(
        f"[bold green]Dataset:[/bold green] {path}"
    )

    console.print(
        f"[bold blue]Target:[/bold blue] {target}"
    )

    console.print(
        f"[bold yellow]Domain:[/bold yellow] {domain}"
    )

    console.print(
        f"[bold green]Rows:[/bold green] "
        f"{dataset.metadata['rows']}"
    )

    console.print(
        f"[bold green]Columns:[/bold green] "
        f"{dataset.metadata['columns']}"
    )

    console.print(
        f"[bold green]Memory Usage:[/bold green] "
        f"{dataset.metadata['memory_usage_mb']} MB"
    )

#     console.print(
#     "\n[bold cyan]Normalized Columns[/bold cyan]"
# )

#     for column in dataset.df.columns:

#         console.print(column)


#     console.print(
#         "\n[bold cyan]Normalized Dtypes[/bold cyan]"
#     )

#     console.print(dataset.df.dtypes)


#     console.print(
#         "\n[bold cyan]Dataset Preview[/bold cyan]"
#     )

#     console.print(dataset.df.head())

    console.print(
        "\n[bold cyan]Semantic Types[/bold cyan]"
    )

    for column, semantic_type in (
        dataset.semantic_types.items()
    ):

        console.print(
            f"{column} → {semantic_type}"
        )