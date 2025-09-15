import niobot

from _lib.decorators import is_owner
from _lib.enums import ReactionEmojis
from _lib.matrix import resolve_room


class AdminCommands(niobot.Module):
    def __init__(self, bot: niobot.NioBot):
        super().__init__(bot)
        print("Loaded AdminCommands")

    @niobot.command(descripton="Checks the latency between observed Matrix events",
                    hidden=True)
    @is_owner()
    async def latency(self, ctx: niobot.Context):
        await ctx.respond(f"Latency between observed Matrix events: {ctx.latency} ms",
                          message_type="m.notice")

    @niobot.command(description="Lists all rooms and IDs the bot is currently in.",
                    hidden=True)
    @is_owner()
    async def rooms(self, ctx: niobot.Context):
        msg = "Bot is in rooms:\n"
        rooms = self.bot.rooms
        for room_id in rooms.keys():
            msg += f" - {rooms[room_id].display_name} ({room_id})\n"
        await ctx.respond(msg.rstrip('\r\n'), message_type="m.notice")

    @niobot.command(description="Instructs the bot to join a room.",
                    hidden=True)
    @is_owner()
    async def join_room(self, ctx: niobot.Context, room: str):
        room_id = await resolve_room(self.bot, room)
        if room_id not in self.bot.rooms.keys():
            await self.bot.join(room_id)
            await self.bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.CHECK_MARK.value)
        else:
            await self.bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.CROSS_MARK.value)

    @niobot.command(description="(Owner Only) Instructs the bot to leave a room.",
                    hidden=True)
    @is_owner()
    async def leave_room(self, ctx: niobot.Context, room: str = None):
        if not room:
            await self.bot.room_leave(ctx.room.room_id)
        else:
            room_id = await resolve_room(self.bot, room)
            if room_id not in self.bot.rooms.keys():
                await self.bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.CROSS_MARK.value)
            else:
                try:
                    await self.bot.room_leave(room_id)
                except AttributeError as e:
                    if "'DirectRoomsErrorResponse' object has no attribute 'rooms'" in str(e):
                        return
                if room_id != ctx.room.room_id:
                    await self.bot.add_reaction(ctx.room, ctx.message,
                                                ReactionEmojis.CHECK_MARK.value)

    @niobot.command(description="(Owner Only) Blacklist a user from using the bot.", hidden=True)
    @is_owner()
    async def blacklist_user(self, ctx: niobot.Context, user: str):
        if not user:
            await self.bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.QUESTION_MARK.value)

        else:
            self.blacklist_user.append(user)
            await self.bot.add_reaction(ctx.room, ctx.message, ReactionEmojis.CHECK_MARK.value)

    @niobot.command(description="(Owner Only) Runs a raw python call. DANGEROUS", hidden=True)
    @is_owner()
    async def python(self, ctx: niobot.Context, *args):
        res = eval("".join(args))
        await ctx.respond(res)
