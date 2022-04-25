import asyncio
import eyed3
import requests
import os

import hikari
import lightbulb

bot = lightbulb.BotApp(token="OTY4MTYxNTc4ODcwNTIxODc3.Yma0uw.l6V0k6ghM2wv61Nm_teeENXOnvA",
                       default_enabled_guilds=(966828214745972787),  # test server ID
                       prefix=";",
                       help_class=None)


@bot.command
@lightbulb.option("args", "all arguments to pass to mp3 tag editor, wrapped in quotes")
@lightbulb.command("edit", "Edit an mp3's tags")
@lightbulb.implements(lightbulb.PrefixCommand)
async def edit_tags(ctx):
    args_list = ctx.options.args.split()
    num_attachments = len(ctx.event.message.attachments)

    if not check_attachments(ctx):
        await ctx.respond("Please include an mp3 attachment.")
        return

    count = 0
    for attachment in ctx.event.message.attachments:
        count = count + 1
        if not check_mp3(attachment):
            await ctx.respond("Please make sure all attachments are mp3s.")
            return

        new_mp3 = create_new_mp3(attachment)
        audiofile = eyed3.load(new_mp3.filename)


        for i in range(len(args_list)):
            match args_list[i]:
                case "-t" | "--title":
                    audiofile.tag.title = args_list[i+1]
                case "-a" | "--artist":
                    audiofile.tag.artist = args_list[i+1]
                case "-A" | "--album":
                    audiofile.tag.album = args_list[i+1]
                case "-b" | "--album-artist":
                    audiofile.tag.album_artist = args_list[i+1]
                case "-N" | "--track-total":
                    audiofile.tag.track_num = (count, num_attachments)
                case "-Y" | "--year":
                    audiofile.tag.release_date = eyed3.core.Date(int(args_list[i+1]))
                case "-G" | "--genre":
                    audiofile.tag.genre = args_list[i + 1]
                case "-c" | "--comment":
                    audiofile.tag.comments.set(args_list[i+1])

        audiofile.tag.save(new_mp3.filename)
        await ctx.respond(new_mp3)
        os.remove(new_mp3.filename)


@bot.command
@lightbulb.command("clear", "Clear an mp3's tags")
@lightbulb.implements(lightbulb.PrefixCommand)
async def clear_tags(ctx):
    if not check_attachments(ctx):
        await ctx.respond("Please include an mp3 attachment.")
        return

    for attachment in ctx.event.message.attachments:
        if not check_mp3(attachment):
            await ctx.respond("Please make sure all attachments are mp3s.")
            return

    new_mp3 = create_new_mp3(attachment)
    audiofile = eyed3.load(new_mp3.filename)

    audiofile.tag.clear()

    audiofile.tag.save(new_mp3.filename)
    await ctx.respond(new_mp3)



HELP_MESSAGE = """
Edit the tags of attached mp3 files with [args] \n Options for args are: \n
`-t STRING, --title STRING`: Set the track title. \n
`-a STRING, --artist STRING`: Set the artist name. \n
`-A STRING, --album STRING`: Set the album name. \n
`-b STRING, --album-artist STRING`: Set the album artist name. \n
`-Y INT, --y INT`: Set the year. \n
`-G STRING, --genre STRING`: Set the genre. \n
`-c STRING, --comment STRING`: Set the comment. \n
`-N, --track-total`: Set each track's count and total track count. Ordered by upload order. \n
"""


@bot.command
@lightbulb.command("help", "Gets help for bot commands")
@lightbulb.implements(lightbulb.PrefixCommand)
async def help(ctx: lightbulb.Context) -> None:
    embed = hikari.Embed(title="Help Command", colour=0x2495bd)
    embed.add_field(";clear", "Clear the tags on the attached mp3 files.")
    embed.add_field(";edit '[args]'", HELP_MESSAGE)
    await ctx.respond(embed)


# return True if there are attachments to the message
def check_attachments(ctx):
    return ctx.event.message.attachments


# return True if attachment is an mp3
def check_mp3(attachment):
    return attachment.media_type == "audio/mpeg"


# create new mp3 file with name of {old_mp3_filename}_updated.mp3
def create_new_mp3(attachment):
    mp3 = requests.get(attachment.url)
    mp3_filename_without_extension = attachment.filename.split(".")[:-1]
    mp3_filename_without_extension = ".".join(ele for ele in mp3_filename_without_extension)
    new_mp3_filename = f"{mp3_filename_without_extension}_update.mp3"
    open(new_mp3_filename, "wb").write(mp3.content)
    new_mp3 = hikari.File(new_mp3_filename)

    return new_mp3


bot.run()
