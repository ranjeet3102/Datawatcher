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
from datawatcher.audits.quality.duplicate_audit import (
    DuplicateAudit
)

from datawatcher.audits.quality.constant_feature_audit import (
    ConstantFeatureAudit
)

from datawatcher.audits.quality.near_constant_audit import (
    NearConstantAudit
)

from datawatcher.audits.quality.invalid_value_audit import (
    InvalidValueAudit
)

from datawatcher.audits.statistical.descriptive_stats_audit import (
    DescriptiveStatsAudit
)

from datawatcher.audits.statistical.variance_audit import (
    VarianceAudit
)
from datawatcher.audits.statistical.skewness_audit import (
    SkewnessAudit
)
from datawatcher.audits.statistical.kurtosis_audit import (
    KurtosisAudit
)
from datawatcher.audits.statistical.outlier_audit import (
    OutlierAudit
)
from datawatcher.audits.categorical.category_frequency_audit import (
    CategoryFrequencyAudit
)
from datawatcher.audits.categorical.rare_category_audit import (
    RareCategoryAudit
)
from datawatcher.audits.categorical.category_imbalance_audit import (
    CategoryImbalanceAudit
)
from datawatcher.audits.ml.cardinality_audit import (
    CardinalityAudit
)
from datawatcher.audits.ml.identifier_risk_audit import (
    IdentifierRiskAudit
)
from datawatcher.audits.ml.target_validation_audit import (
    TargetValidationAudit
)
from datawatcher.audits.ml.class_imbalance_audit import (
    ClassImbalanceAudit
)
from datawatcher.audits.ml.leakage_audit import (
    LeakageAudit
)  
from datawatcher.scoring.readiness_scorer import (
    calculate_ml_readiness_score
) 
from datawatcher.scoring.risk_summary import (
    generate_risk_summary
)
from datawatcher.domains.plugin_registry import (
    DOMAIN_PLUGINS
)
from datawatcher.domains.finance.audits.currency_consistency_audit import (
    CurrencyConsistencyAudit
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

    registry.register(
    DuplicateAudit()
    )

    registry.register(
    ConstantFeatureAudit()
    )

    registry.register(
    NearConstantAudit()
    )

    registry.register(
    InvalidValueAudit()
    )

    registry.register(
    DescriptiveStatsAudit()
    )

    registry.register(
    VarianceAudit()
    )

    registry.register(
        SkewnessAudit()
    )

    registry.register(
        KurtosisAudit()
    )

    registry.register(
        OutlierAudit()
    )

    registry.register(
    CategoryFrequencyAudit()
    )

    registry.register(
        RareCategoryAudit()
    )

    registry.register(
    CategoryImbalanceAudit()
    )

    registry.register(
        CardinalityAudit()
    )

    registry.register(
        IdentifierRiskAudit()
    )

    registry.register(
        TargetValidationAudit()
    )

    registry.register(
        ClassImbalanceAudit()
    )
    
    registry.register(
        LeakageAudit()
    )


    if domain:

        plugin = (
            DOMAIN_PLUGINS.get(
                domain
            )
        )

        if plugin:

            plugin.register_audits(
                registry
            )

    print("\nREGISTERED AUDITS")

    for audit in registry.get_audits():

        print(
            audit.audit_name
        )

    
    engine = AuditEngine(
        registry
    )

    results = engine.run(
    dataset,
    context={
        "target": target
    }
    )
    
    for result in results:

        if result.category in [
            "finance",
            "timeseries",
            "healthcare"
        ]:

            print(
                "\nFOUND DOMAIN AUDIT"
            )

            print(
                result.audit_name
            )

            print(
                result.category
            )

            print(
                result.findings
            )

    # console.print(
    #     f"\nAudit: {result.audit_name}"
    # )

    # console.print(
    #     f"Category: {result.category}"
    # )

    # console.print(
    #     f"Passed: {result.passed}"
    # )

    # console.print(
    #     f"Severity: {result.severity}"
    # )

    # console.print(
    #     f"Findings: {result.findings}"
    # )

    readiness = (
    calculate_ml_readiness_score(
        results
    )
    )

    risk_summary = (
    generate_risk_summary(
        results
    )
    )

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

    console.print(
    "\n[bold green]ML Readiness[/bold green]"
    )

    console.print(
    f"Score: "
    f"{readiness['ml_readiness_score']}/100"
    )

    console.print(
    f"Grade: "
    f"{readiness['grade']}"
    )

    console.print(
    "\n[bold red]Dataset Risk Summary[/bold red]"
    )

    console.print(
        f"Risk Level: "
        f"{risk_summary['risk_level']}"
    )

    console.print(
        f"Top Risks: "
        f"{risk_summary['top_risks']}"
    )