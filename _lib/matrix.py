import requests

from niobot import Context, NioBot


# When dealing with Matrix, we sometimes have delegation.
# Base niobot and matrix-nio DO NOT check for delegation of servers for domains,
# and thus we have to define it ourselves.
def check_homeserver_wellknown(domain: str, https: bool = True, port: int = 443) -> str:
    url = (f"{'https://' if https else 'http://'}{domain}" +
           f"{':'+str(port) if port != 443 else ''}/.well-known/matrix/server")
    r = requests.get(url)
    if r.status_code == 200:
        return f"https://{r.json()['m.server']}"
    else:
        # TODO: Add DNS SRV tests for legacy matrix delegations.
        # For now: just return the domain entered.
        return f"https://domain:port"


async def resolve_room(bot: NioBot, roomstr: str):
    if roomstr.startswith("!"):
        return roomstr
    else:
        resolved = await bot.room_resolve_alias(roomstr)
        return resolved.room_id
