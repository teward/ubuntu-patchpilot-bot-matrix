import traceback

import niobot
from _lib.config import get_owners
import requests

from _lib.decorators import is_owner, is_poweruser
from _lib.enums import ReactionEmojis


class PatchPilotCommands(niobot.Module):
    def __init__(self, bot: niobot.NioBot):
        super().__init__(bot)
        self.pilots = []
        self.blacklist = []
        self.authorized_members = []
        try:
            with open('store/pilots.txt', mode='r') as f:
                self.pilots.extend(f.readlines())
        except FileNotFoundError:
            f = open('store/pilots.txt', mode='w')
            f.close()

        try:
            with open('store/user_blacklist', mode='r') as f:
                self.blacklist.extend(f.readlines())
        except FileNotFoundError:
            f = open('store/user_blacklist', mode='w')
            f.close()

        try:
            with open('store/authorized_members', mode='r') as f:
                self.authorized_members.extend(f.readlines())
        except FileNotFoundError:
            f = open('store/user_blacklist', mode='w')
            f.close()

        print("Loaded PatchPilotCommands")

    def load_authorized(self) -> None:
        # Nils provides an API at
        # https://maubot.haxxors.com/launchpad/api/groups/members/GROUP/
        r = requests.get("https://maubot.haxxors.com/launchpad/api/groups/members/motu/")
        motu = r.json()['mxids']
        r = requests.get("https://maubot.haxxors.com/launchpad/api/groups/members/ubuntu-core-dev/")
        coredev = r.json()['mxids']
        self.authorized_members.extend(get_owners())
        self.authorized_members.extend(motu)
        self.authorized_members.extend(coredev)

    async def write(self) -> None:
        with open('store/pilots.txt', mode='w') as f:
            f.writelines([f"{pilot}\n" for pilot in self.pilots])
        with open('store/user_blacklist', mode='w') as f:
            f.writelines([f"{user}\n" for user in self.blacklist])
        with open('store/authorized_members', mode='w') as f:
            f.writelines([f"{user}\n" for user in self.authorized_members])

    @niobot.command(description="Allows a patch pilot to show themselves as in or out")
    async def pilot(self, ctx: niobot.Context, action: str):
        room_topic = str(ctx.room.topic)
        split_room_topic = room_topic.split("\n")
        # patch_pilots_index = -1
        # for i in range(len(split_room_topic) - 1):
        #     if split_room_topic[i].startswith("Patch Pilots: "):
        #         patch_pilots_index = i
        #         break

        if ctx.message.sender not in self.authorized_members:
            await self.bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.CROSS_MARK.value)
            return
        else:
            if action.lower() not in ["in", "out"]:
                await self.bot.add_reaction(ctx.room, ctx.message,
                                            ReactionEmojis.QUESTION_MARK.value)
            else:
                if action.lower() == "in":
                    self.pilots.append(ctx.message.sender)
                    await self.write()
                    await self.bot.add_reaction(ctx.room, ctx.message,
                                                ReactionEmojis.CHECK_MARK.value)

                if action.lower() == "out":
                    if ctx.message.sender in self.pilots:
                        self.pilots.remove(ctx.message.sender)
                        await self.write()

                    await self.bot.add_reaction(ctx.room, ctx.message,
                                                ReactionEmojis.CHECK_MARK.value)



    @niobot.command(description="Allows the bot owner to reset the state of the"
                                "active patch pilots list to empty. Also triggers a refresh of "
                                "the authorized users list.",
                    hidden=True)
    @is_poweruser()
    async def reset_pilots(self, ctx: niobot.Context):
        self.pilots = []

        await self.write()
        await self.reload_acl()
        await self.bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.BOOM.value)

    @niobot.command(name="pilots",
                    description="Lists all currently present patch pilots.")
    async def patchpilots(self, ctx: niobot.Context):
        msg = "Currently present patch pilots:"
        if len(self.pilots) == 0:
            msg += " (None)"
        else:
            msg += "\n"
            for pilot in self.pilots:
                msg += f"\n - `{pilot}`"

        await ctx.respond(msg)

    @niobot.command(name="reload_acl", description="(Authorized Only) Refreshes the list of Matrix IDs who can "
                                                   "use the commands.")
    @is_poweruser()
    async def reload_acl(self, ctx: niobot.Context):
        self.load_authorized()
        # await self.bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.CHECK_MARK.value())

