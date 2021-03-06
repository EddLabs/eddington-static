"""History CLI."""
import time
from pathlib import Path
from typing import Union

import click

from statue.cache import Cache
from statue.cli.cli import statue as statue_cli
from statue.constants import DATETIME_FORMAT
from statue.evaluation import CommandEvaluation, Evaluation


def evaluation_status(evaluation: Union[Evaluation, CommandEvaluation]) -> str:
    """Get styled evaluation string."""
    if evaluation.success:
        return click.style("Success", fg="green")
    return click.style("Failure", fg="red")


def evaluation_datetime(evaluation_path: Path) -> str:
    """Get styled time string for evaluation path."""
    parsed_time = time.localtime(int(evaluation_path.stem.split("-")[-1]))
    return click.style(time.strftime(DATETIME_FORMAT, parsed_time), fg="yellow")


def evaluation_success_ratio(evaluation: Evaluation) -> str:
    """Get evaluation ratio string."""
    return f"{evaluation.successful_commands_number}/{evaluation.commands_number}"


def positive_validation(  # pylint: disable=unused-argument
    ctx: click.Context, param: click.Parameter, value: int
) -> int:
    """Validate number is 1 or greater."""
    if value < 1:
        raise click.BadParameter(f"Number should be 1 or greater. got {value}")
    return value


@statue_cli.group("history")
def history_cli() -> None:
    """History related actions such as list, show, etc."""


@history_cli.command("list")
@click.option("--head", type=int, help="Show only the nth recent evaluations")
def list_evaluations(head):
    """List all recent evaluations."""
    evaluation_paths = Cache.all_evaluation_paths()
    if len(evaluation_paths) == 0:
        click.echo("No previous evaluations.")
        return
    if head is not None:
        evaluation_paths = evaluation_paths[:head]
    for i, evaluation_path in enumerate(evaluation_paths, start=1):
        evaluation = Evaluation.load_from_file(evaluation_path)
        click.echo(
            f"{i}) "
            f"{evaluation_datetime(evaluation_path)} - {evaluation_status(evaluation)} "
            f"({evaluation_success_ratio(evaluation)} successful)"
        )


@history_cli.command("show")
@click.option(
    "-n",
    "number",
    type=int,
    default=1,
    callback=positive_validation,
    help="Show nth recent evaluation. 1 by default",
)
def show_evaluation(number):
    """Show past evaluation."""
    evaluation_path = Cache.evaluation_path(number - 1)
    evaluation = Evaluation.load_from_file(evaluation_path)
    click.echo(
        f"{evaluation_datetime(evaluation_path)} - {evaluation_status(evaluation)} "
        f"({evaluation_success_ratio(evaluation)} successful)"
    )
    for source, source_evaluation in evaluation.items():
        click.echo(f"{source}:")
        for command_evaluation in source_evaluation.commands_evaluations:
            click.echo(
                f"\t{command_evaluation.command.name} - "
                f"{evaluation_status(command_evaluation)}"
            )
