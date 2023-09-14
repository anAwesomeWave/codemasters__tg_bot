from core import bot, db


def run_app():
    # prepare db

    # run bot
    db.create_db()
    bot.serve()


run_app()
