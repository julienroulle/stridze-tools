import typer
from typing_extensions import Annotated

from stridze.data.sync_dataset import main as sync_dataset

app = typer.Typer()


@app.command()
def main(
    sync: Annotated[
        bool,
        typer.Option(help="Say hi formally."),
    ] = False,
):
    """ """
    if sync:
        sync_dataset()


if __name__ == "__main__":
    app()
