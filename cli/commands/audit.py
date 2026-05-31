from os import path

import typer
from rich.console import Console
from datawatcher.loaders.factory import load_dataset

from datawatcher.core.audit_registry import (
    AuditRegistry
)

from datawatcher.core.audit_engine import (
    AuditEngine
)

from datawatcher.audits.structural.shape_audit import (
    ShapeAudit
)

from datawatcher.audits.structural.dtype_audit import (
    DtypeAudit
)

from datawatcher.audits.structural.memory_usage_audit import (
    MemoryUsageAudit
)

from datawatcher.audits.structural.schema_consistency_audit import (
    SchemaConsistencyAudit
)

from datawatcher.audits.quality.missing_value_audit import (
    MissingValueAudit
)

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
    
    registry = AuditRegistry()

    registry.register(
        ShapeAudit()
    )

    registry.register(
    DtypeAudit()
    )

    registry.register(
    MemoryUsageAudit()
    )

    registry.register(
    SchemaConsistencyAudit()
    )

    registry.register(
    MissingValueAudit()
    )

    engine = AuditEngine(
        registry
    )

    results = engine.run(dataset)

    console.print(
    "\n[bold magenta]Audit Results[/bold magenta]"
)

    for result in results:

        console.print(
            f"\nAudit: {result.audit_name}"
        )

        console.print(
            f"Category: {result.category}"
        )

        console.print(
            f"Passed: {result.passed}"
        )

        console.print(
            f"Severity: {result.severity}"
        )

        console.print(
            f"Findings: {result.findings}"
        )