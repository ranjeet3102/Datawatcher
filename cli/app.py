import typer

from datawatcher.cli.commands.audit import audit_app

app = typer.Typer()

app.add_typer(
    audit_app,
    name="audit"
)


if __name__ == "__main__":
    app()