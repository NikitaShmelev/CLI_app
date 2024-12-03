import os
import typer

from file_parser import (
    add_transaction,
    set_field,
    get_field,
)
from utils import generate_example_file, validate_file
from enum import Enum

app = typer.Typer(help="Fixed-width file management CLI.")


class Currency(str, Enum):
    PLN = "PLN"
    USD = "USD"
    EUR = "EUR"


@app.command()
def validate(file: str = typer.Argument(..., help="Path to the fixed-width file.")):
    """
    Validate the file structure.
    """
    if not os.path.exists(file):
        raise FileNotFoundError("The specified file does not exist.")
    validate_file(file)


@app.command()
def add(
    file: str = typer.Argument(..., help="Path to the fixed-width file."),
    amount: int = typer.Option(..., help="Transaction's amount (positive integer)."),
    currency: Currency = typer.Option(..., help="Currency of the transaction."),
):
    """
    Add a new transaction to the file.
    """
    if not os.path.exists(file):
        raise FileNotFoundError("The specified file does not exist.")
    add_transaction(file_path=file, currency=currency.value, amount=amount)
    typer.echo("Transaction added successfully.")


@app.command(name="set")
def set_field_value(
    file: str = typer.Argument(..., help="Path to the fixed-width file."),
    index: int = typer.Option(..., help="Index of the record to modify (0-based)."),
    field: str = typer.Option(..., help="Field name to modify."),
    value: str = typer.Option(..., help="New value for the field."),
):
    if not os.path.exists(file):
        raise FileNotFoundError("The specified file does not exist.")
    set_field(file, index, field, value)
    typer.echo("Field updated successfully.")


@app.command(name="get")
def get_field_value(
    file: str = typer.Argument(..., help="Path to the fixed-width file."),
    index: int = typer.Option(
        ..., help="Index of the record to retrieve the field value (0-based)."
    ),
    field: str = typer.Option(..., help="Field name to retrieve."),
):
    """
    Get the value of a specific field from the file.
    """
    if not os.path.exists(file):
        raise FileNotFoundError("The specified file does not exist.")
    value = get_field(file, index, field)
    typer.echo(f"The value of the field '{field}' is: {value}")


@app.command()
def generate(
    file: str = typer.Argument(..., help="Path to the output file."),
    transactions: int = typer.Option(..., help="Number of transactions to generate."),
):
    generate_example_file(file, transactions)
    validate_file(file)
    typer.echo("Example file generated and validated successfully.")


if __name__ == "__main__":
    app()
