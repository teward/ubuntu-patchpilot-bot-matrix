import traceback

import niobot

import requests

from _lib.decorators import is_owner
from _lib.enums import ReactionEmojis


class PatchPilotCommands(niobot.Module):
    def __init__(self, bot: niobot.NioBot):
        super().__init__(bot)
        self.pilots = []
        # self.members = []
        self.blacklist = []
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

        # self.load_authorized()
        print("Loaded PatchPilotCommands")

    # def load_authorized(self) -> None:
    #     # Nils provides an API at
    #     # https://maubot.haxxors.com/launchpad/api/groups/members/ubuntumembers/
    #     r = requests.get("https://maubot.haxxors.com/launchpad/api/groups/members/ubuntumembers/")
    #     ubuntu_members = r.json()['mxids']
    #     self.members = get_authorized(ubuntu_members)

    async def write(self) -> None:
        with open('store/pilots.txt', mode='w') as f:
            f.writelines([f"{pilot}\n" for pilot in self.pilots])
        with open('store/user_blacklist', mode='w') as f:
            f.writelines([f"{user}\n" for user in self.blacklist])

    @niobot.command(description="Allows a patch pilot to show themselves as in or out")
    async def pilot(self, ctx: niobot.Context, action: str):
        room_topic = str(ctx.room.topic)
        split_room_topic = room_topic.split("\n")
        patch_pilots_index = -1
        for i in range(len(split_room_topic) - 1):
            if split_room_topic[i].startswith("Patch Pilots: "):
                patch_pilots_index = i
                break


        if (ctx.message.sender in self.blacklist or not ctx.message.sender.endswith(":ubuntu.com")
                or not ctx.message.sender.endswith(":darkchaos.dev")
                or not ctx.message.sender.endswith(":matrix.debian.social")):
            await self.bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.CROSS_MARK.value)
            return

        if action.lower() not in ["in", "out"]:
            await self.bot.add_reaction(ctx.room, ctx.message,
                                        ReactionEmojis.QUESTION_MARK.value)
        else:
            if action.lower() == "in":
                self.pilots.append(ctx.message.sender)
                await self.write()
                await self.bot.add_reaction(ctx.room, ctx.message,
                                            ReactionEmojis.CHECK_MARK.value)

                if patch_pilots_index == -1:
                    await self.bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.BOOM.value)
                    return
                else:
                    pilots = ""
                #     if len(self.pilots) == 0:
                #         split_room_topic[patch_pilots_index] = "Patch Pilots: (none, consider a @pilot in!)"
                #     else:
                #         for pilot in self.pilots:
                #             pilots += f"{pilot}, "
                #         split_room_topic[patch_pilots_index] = "Patch Pilots: " + pilots.rstrip(', ')
                #
                # try:
                #     await self.bot.update_room_topic(ctx.room.room_id, "\n".join(split_room_topic))
                # except Exception as e:
                #     traceback.print_exception(e)
                #     await self.bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.BOOM.value)

            if action.lower() == "out":
                if ctx.message.sender in self.pilots:
                    self.pilots.remove(ctx.message.sender)
                    await self.write()

                await self.bot.add_reaction(ctx.room, ctx.message,
                                            ReactionEmojis.CHECK_MARK.value)

                if patch_pilots_index == -1:
                    await self.bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.BOOM.value)
                    return
                else:
                    pilots = ""
                    # if len(self.pilots) == 0:
                    #     split_room_topic[patch_pilots_index] = "Patch Pilots: (none, consider a @pilot in!)"
                    # else:
                    #     for pilot in self.pilots:
                    #         pilots += f"{pilot}, "
                    #     split_room_topic[patch_pilots_index] = "Patch Pilots: " + pilots.rstrip(', ')

                # try:
                #     await self.bot.update_room_topic(ctx.room.room_id, "\n".join(split_room_topic))
                # except Exception as e:
                #     traceback.print_exception(e)
                #     await self.bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.BOOM.value)



    @niobot.command(description="Allows the bot owner to reset the state of the"
                                "active patch pilots list to empty. Also triggers a refresh of "
                                "the authorized users list.",
                    hidden=True)
    @is_owner()
    async def reset_pilots(self, ctx: niobot.Context):
        room_topic = str(ctx.room.topic)
        split_room_topic = room_topic.split("\n")
        patch_pilots_index = -1
        for i in range(len(split_room_topic) - 1):
            if split_room_topic[i].startswith("Patch Pilots: "):
                patch_pilots_index = i
                break

        self.pilots = []

        if patch_pilots_index == -1:
            pass
        else:
            split_room_topic[patch_pilots_index] = "Patch Pilots: (none, consider a @pilot in!)"
            try:
                await self.bot.update_room_topic(ctx.room.room_id, "\n".join(split_room_topic))
            except Exception as e:
                traceback.print_exception(e)

        await self.write()
        # self.load_authorized()
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

    # @niobot.command(name="reload_members",
    #                 description="(Authorized Only) Refreshes the list of ~ubuntumembers matrix IDs "
    #                             "and adds them to the Authorized list for patch pilot commands.")
    # async def refresh_authorized(self, ctx: niobot.Context):
    #     self.load_authorized()
    #     await self.bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.CHECK_MARK.value())

    # @niobot.command(name="list_members",
    #                 description="(Owner Only) Dumps the list of current authorized matrix IDs")
    # async def list_members(self, ctx: niobot.Context):
    #     msg = "List of patch pilot authorized matrix IDs:"
    #     if not self.members:
    #         msg += " (None)"
    #     else:
    #         msg += "\n"
    #         for mxid in self.members:
    #             msg += f" - `{mxid}`\n"
    #     await ctx.respond(msg.rstrip('\r\n'))

    # @niobot.command(name="isauthorized",
    #                 description="Allows any user to check if they are allowed to use patch pilot "
    #                             "commands. If they specify a user ID and are already authorized, "
    #                             "it will check that user ID.")
    # async def is_authorized(self, ctx: niobot.Context, uid: str = None):
    #     if uid and not uid.startswith('@'):
    #         uid = f"@{uid}"
    #
    #     if ctx.message.sender in self.members and uid:
    #         if uid in self.members:
    #             await ctx.respond(f"User `{uid}` is allowed to use patch pilot commands.",
    #                               message_type="m.notice")
    #         else:
    #             await ctx.respond(f"User `{uid}` is not allowed to use patch pilot "
    #                               f"commands.", message_type="m.notice")
    #     else:
    #         if ctx.message.sender in self.members:
    #             await ctx.respond("You are allowed to use patch pilot commands.",
    #                               message_type="m.notice")
    #         else:
    #             await ctx.respond("You are not allowed to use patch pilot commands.",
    #                               message_type="m.notice")
