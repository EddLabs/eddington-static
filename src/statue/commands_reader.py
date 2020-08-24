"""Reader method for settings."""
from typing import Any, List, MutableMapping, Optional

from statue.command import Command
from statue.constants import ADD_ARGS, ARGS, CLEAR_ARGS, HELP, STANDARD
from statue.excptions import InvalidCommand, UnknownCommand


def read_commands(
    commands_configuration: MutableMapping[str, Any],
    contexts: Optional[List[str]] = None,
    allow_list: Optional[List[str]] = None,
    deny_list: Optional[List[str]] = None,
) -> List[Command]:
    """
    Read commands from a settings file.

    :param commands_configuration: Dictionary. Commands configuration.
    :param contexts: List of str. a list of contexts to choose commands from.
    :param allow_list: List of allowed commands. If None, take all commands
    :param deny_list: List of denied commands. If None, take all commands
    :return: a list of :class:`Command`
    """
    commands = []
    contexts = [] if contexts is None else contexts
    for command_name in commands_configuration.keys():
        try:
            commands.append(
                read_command(
                    command_name=command_name,
                    commands_configuration=commands_configuration,
                    contexts=contexts,
                    allow_list=allow_list,
                    deny_list=deny_list,
                )
            )
        except InvalidCommand:
            continue
    return commands


def read_command(
    command_name: str,
    commands_configuration: MutableMapping[str, Any],
    contexts: Optional[List[str]] = None,
    allow_list: Optional[List[str]] = None,
    deny_list: Optional[List[str]] = None,
) -> Command:
    """
    Read command from a settings file.

    :param command_name: the name of the command to read.
    :param commands_configuration: Dictionary. Commands configuration.
    :param contexts: List of str. a list of contexts to choose commands from.
    :param allow_list: List of allowed commands. If None, take all commands
    :param deny_list: List of denied commands. If None, take all commands
    :return: a :class:`Command` instance
    :raises: :class:`UnknownCommand` if command is missing from settings file.
    :class:`InvalidCommand` of command doesn't fit the given contexts, allow list and
    deny list
    """
    command_setups = commands_configuration.get(command_name, None)
    if command_setups is None:
        raise UnknownCommand(command_name)
    if is_command_matching(
        command_name, command_setups, contexts, allow_list, deny_list
    ):
        raise InvalidCommand(
            command_name=command_name,
            contexts=contexts,
            allow_list=allow_list,
            deny_list=deny_list,
        )
    return Command(
        name=command_name,
        args=__read_args(command_setups, contexts=contexts),
        help=command_setups[HELP],
    )


def is_command_matching(
    command_name: str,
    setups: MutableMapping[str, Any],
    contexts: Optional[List[str]],
    allow_list: Optional[List[str]],
    deny_list: Optional[List[str]],
) -> bool:
    """
    Check whether a command fits the restrictions or not.

    :param command_name: the name of the command to read.
    :param setups: Dictionary. The command's configuration.
    :param contexts: List of str. a list of contexts.
    :param allow_list: List of allowed commands.
    :param deny_list: List of denied commands.
    :return: Boolean. Does the command fit the restrictions
    """
    if deny_list is not None and command_name in deny_list:
        return True
    if (
        allow_list is not None
        and len(allow_list) != 0  # noqa: W503
        and command_name not in allow_list  # noqa: W503
    ):
        return True
    if contexts is None or len(contexts) == 0:
        return not setups.get(STANDARD, True)
    for command_context in contexts:
        if not setups.get(command_context, False):
            return True
    return False


def __read_args(
    setups: MutableMapping[str, Any], contexts: Optional[List[str]]
) -> List[str]:
    base_args = list(setups.get(ARGS, []))
    if contexts is None:
        return base_args
    for command_context in contexts:
        context_obj = setups.get(command_context, None)
        if not isinstance(context_obj, dict):
            continue
        args: List[str] = context_obj.get(ARGS, None)
        if args is not None:
            return args
        add_args = context_obj.get(ADD_ARGS, None)
        if add_args is not None:
            base_args.extend(add_args)
        clear_args = context_obj.get(CLEAR_ARGS, False)
        if clear_args:
            return []
    return base_args
