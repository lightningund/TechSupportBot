import datetime

from discord.ext import commands
from sqlalchemy import Column, DateTime, Integer, String

from utils.cogs import MatchPlugin
from utils.database import DatabaseHandle
from utils.helpers import get_env_value, priv_response, tagged_response

FACTOID_PREFIX = get_env_value("FACTOID_PREFIX")
COMMAND_PREFIX = get_env_value("COMMAND_PREFIX")

db_handle = DatabaseHandle()


class Factoid(db_handle.Base):
    __tablename__ = "factoids"

    pk = Column(Integer, primary_key=True)
    text = Column(String)
    channel = Column(String)
    message = Column(String)
    time = Column(DateTime, default=datetime.datetime.utcnow)


db_handle.create_all()


def setup(bot):
    if FACTOID_PREFIX == COMMAND_PREFIX:
        raise RuntimeError(
            f"Command prefix '{COMMAND_PREFIX}' cannot equal Factoid prefix"
        )
    bot.add_command(add_factoid)
    bot.add_cog(FactoidMatch(bot))
    bot.add_command(delete_factoid)


@commands.command(
    name="r",
    brief="Creates custom trigger with a specified output",
    description="Creates a custom trigger with a specified name that outputs any specified text, including mentions. All triggers are used by sending a message with a '?' appended in front of the trigger name.",
    usage="[trigger-name] [trigger-output]",
    help="Trigger Usage:\n\t?[trigger-name]\n\nLimitations:\n\tMentions should not be used as triggers.",
)
async def add_factoid(ctx, arg1, *args):
    if ctx.message.mentions:
        await priv_response(ctx, "Sorry, factoids don't work well with mentions.")
        return

    channel = str(ctx.message.channel.id)

    if not args:
        await priv_response(ctx, "Factoids must not be blank!")
        return

    db = db_handle.Session()

    try:
        # first check if key already exists
        entry = (
            db.query(Factoid)
            .filter(Factoid.text == arg1, Factoid.channel == channel)
            .first()
        )
        if entry:
            # delete old one
            db.delete(entry)
            await priv_response(ctx, "Deleting previous entry of factoid trigger...")

        # finally, add new entry
        db.add(Factoid(text=arg1.lower(), channel=channel, message=" ".join(args)))
        db.commit()
        await tagged_response(ctx, f"Successfully added factoid trigger: *{arg1}*")

    except Exception:
        await priv_response(
            ctx, "I ran into an issue handling your factoid addition..."
        )


@commands.command(
    name="r",
    brief="Creates custom trigger with a specified output",
    description="Creates a custom trigger with a specified name that outputs any specified text, including mentions. All triggers are used by sending a message with a '?' appended in front of the trigger name.",
    usage="[trigger-name] [trigger-output]",
    help="Trigger Usage:\n\t?[trigger-name]\n\nLimitations:\n\tMentions should not be used as triggers.",
)
async def delete_factoid(ctx, arg):
    if ctx.message.mentions:
        await priv_response(ctx, "Sorry, factoids don't work well with mentions.")
        return

    channel = str(ctx.message.channel.id)

    db = db_handle.Session()

    try:
        entry = (
            db.query(Factoid)
            .filter(Factoid.text == arg, Factoid.channel == channel)
            .first()
        )
        if entry:
            db.delete(entry)
            db.commit()
        await tagged_response(ctx, f"Successfully deleted factoid trigger: *{arg}*")

    except Exception:
        await priv_response(
            ctx, "I ran into an issue handling your factoid deletion..."
        )


class FactoidMatch(MatchPlugin):
    def match(self, content):
        return bool(content.startswith(FACTOID_PREFIX))

    async def response(self, ctx, arg):
        if ctx.message.mentions:
            await priv_response(ctx, "Sorry, factoids don't work well with mentions.")
            return

        channel = str(ctx.message.channel.id)

        db = db_handle.Session()

        try:
            entry = (
                db.query(Factoid)
                .filter(Factoid.text == arg[1:], Factoid.channel == channel)
                .first()
            )
            if entry:
                await tagged_response(ctx, entry.message)

        except Exception:
            await priv_response("I ran into an issue grabbing your factoid...")
