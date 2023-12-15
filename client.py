from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram import Client
from pyrogram.enums import ParseMode

# Connecting to a session
app = Client(name="session",
             parse_mode=ParseMode.HTML)

# Creating a task scheduler
scheduler = AsyncIOScheduler()
url = 'sqlite:///example.sqlite'
scheduler.add_jobstore('sqlalchemy', url=url)