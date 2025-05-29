from typing import Any
from _lib.config import get_owners, get_authorized
import niobot


def is_owner() -> Any:
    """
    This decorator replaces the in-built @bot.is_owner() test.
    This is because we now have with a config file a way to parse all owners.

    Usage:
    from lib.decorators import is_owner

    @is_owner()
    async def somefunction(self, ctx: niobot.Context, ...):
        ....

    Note that we need to suppress error handling in <BASE_BOT_CODE>.on_command_error
    """
    def predicate(ctx: niobot.Context):
        owners = get_owners()
        return ctx.message.sender in owners

    return niobot.check(predicate)


def is_authorized(additional_ids: list = None) -> Any:
    """
    This decorator is an extension of `is_owner` in that we specifically only let a set of
    people actually run any command - hence "authorized" users - defined in the conf
    """

    def predicate(ctx: niobot.Context):
        authorized = get_authorized(additional_ids)
        return ctx.message.sender in authorized

    return niobot.check(predicate)
