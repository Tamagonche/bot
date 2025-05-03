import os
import asyncio
import random
from typing import Any

import onchebot
from dotenv import load_dotenv
from onchebot.models import Message
from supabase import create_async_client, AsyncClient
import datetime

load_dotenv()

TOPIC_ID=817382
SUPABASE_URL=os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY=os.environ.get("SUPABASE_KEY", "")
WARNING_INTERVAL = datetime.timedelta(hours=1)

WHITELIST = [
    "Tohru",
    "LeChouffin",
]

onchebot.setup(
    loki_url=os.environ.get("LOKI_URL", None),
    prometheus_port=int(os.environ.get("PROMETHEUS_PORT", 9464)),
)

supabase: AsyncClient | None = None

user = onchebot.add_user(
    username=os.environ.get("ONCHE_USERNAME", ""),
    password=os.environ.get("ONCHE_PASSWORD", ""),
)

tamagonche = onchebot.add_bot("tamagonche", user, TOPIC_ID)

def is_allowed(msg: Message) -> bool:
    if msg.username in WHITELIST:
        return True

    if msg.badges == None:
        return False
    
    badges = msg.badges.split(",")
    rangs = [s for s in badges if "rangs/" in s]

    if len(rangs) == 0:
        return False

    rang = rangs[0]

    if rang == "rangs/gitan":
        return False

    return True

async def on_action(msg: Message, action_type: str):
    if not is_allowed(msg):
        return

    try:
        await supabase.table("actions").insert({"type": action_type, "username": msg.username, "pet_id": 1}).execute()
    except:
        pass

@tamagonche.command("nourrir")
async def feed(msg: Message, _):
    await on_action(msg, "feed")

@tamagonche.command("nettoyer")
async def clean_trash(msg: Message, _):
    await on_action(msg, "clean_trash")

@tamagonche.command("doliprane")
async def give_medicine(msg: Message, _):
    await on_action(msg, "give_medicine")

@tamagonche.command("weed")
async def weed(msg: Message, _):
    await on_action(msg, "weed")

@tamagonche.command("marloute")
async def drink(msg: Message, _):
    await on_action(msg, "drink")

@tamagonche.command("branle")
async def fap(msg: Message, _):
    await on_action(msg, "fap")

@tamagonche.command("battre")
async def punch(msg: Message, _):
    await on_action(msg, "punch")

@tamagonche.command("sueur")
async def sweat(msg: Message, _):
    await on_action(msg, "sweat")

async def notify_dead():
    await tamagonche.post_message("Je suis MORT :rip:")

async def notify_hunger():
    text = random.choice([
        "J'ai faim !",
        "Je dois manger",
        "J'ai le ventre vide",
        "QUI va me donner à manger, BORDEL",
        "DE LA BOUFFE PUTAIN",
        "Je veux un burgourent",
        "Quelqu'un veut bien me donner un kebab ?",
        "Il me faut des fritent",
    ])
    await tamagonche.post_message(f"{text} :tamagonche:")

last_warning_time: datetime.datetime | None = None

async def on_pet_update(payload):
    global last_warning_time

    pet = payload["data"]["record"]
    now = datetime.datetime.now()

    try:
        if last_warning_time is None or (now - last_warning_time) >= WARNING_INTERVAL:
            last_warning_time = now
            if pet["food"] == 0:
                await notify_dead()
            elif pet["food"] <= pet["hunger_threshold"]:
                await notify_hunger()
    except:
        pass

async def init():
    global supabase
    supabase = await create_async_client(SUPABASE_URL, SUPABASE_KEY)

    def callback(payload):
        asyncio.create_task(on_pet_update(payload))

    asyncio.create_task(
        supabase.channel("prod")
        .on_postgres_changes("UPDATE", schema="public", table="pets", callback=callback)
        .subscribe()
    )

async def close():
    if supabase:
        await supabase.realtime.close()

onchebot.start(init, close)
