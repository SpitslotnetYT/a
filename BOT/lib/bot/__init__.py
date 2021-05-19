from asyncio import sleep
from datetime import datetime
from glob import glob
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import (
    CommandNotFound,
    Context,
    BadArgument,
    MissingRequiredArgument,
    CommandOnCooldown,
)
from discord.errors import HTTPException, Forbidden
from discord import Intents, Embed, File, DMChannel, Colour
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger


PREFIX = "."
OWNER_IDS = [269165863515586560]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]


class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"{cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()
        self.guild = None
        super().__init__(
            command_prefix=PREFIX,
            owner_ids=OWNER_IDS,
            intents=Intents.all(),
        )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog loaded")

        print("Cog setup complete")

    def run(self, version):
        self.VERSION = version

        print("Running Cog Setup...")
        self.setup()

        with open("./BOT/lib/bot/token", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print("Running Bot...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send("Bot is still setting up please wait.")

    async def on_connect(self):
        print("Bot Connected")

    async def on_disconnect(self):
        print("Bot Disconnected")

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send("Something went wrong...")

        else:
            await self.stdout.send("An error has occured.")

        raise

    async def on_command_error(self, ctx, exc):
        if isinstance(exc, CommandNotFound):
            pass

        elif isinstance(exc, BadArgument):
            await ctx.send(
                f"You inputed an invalid argument, use {self.PREFIX}help to see all the required arguments."
            )

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send(
                f"You left out a vital argument, use {self.PREFIX}help to see all the required arguments."
            )

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(
                f"This command is on cooldown for {exc.retry_after:,.2f} more seconds."
            )

        elif isinstance(exc, HTTPException):
            await ctx.send("I was unable to send the message.")

        elif hasattr(exc, "original"):
            if isinstance(exc.original, Forbidden):
                await ctx.send("I do not have permission to do that.")

            else:
                raise exc.original

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(544213180193308672)
            self.stdout = self.get_channel(798387562012082217)

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            await self.stdout.send("Bot Ready")
            print("Bot Ready")

            # meta = self.get_cog("Meta")
            # await meta.set()

        else:
            print("Bot Reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            if not isinstance(message.channel, DMChannel):
                await self.process_commands(message)


bot = Bot()