import typer

app = typer.Typer()


@app.command()
def cli(command: str = typer.Argument(...)):
    typer.echo(f"Running command: {command}")


if __name__ == "__main__":
    app()
