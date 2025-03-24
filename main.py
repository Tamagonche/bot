import os
import asyncio
import random
from typing import Any

import onchebot
from dotenv import load_dotenv
from onchebot.models import Message
from supabase import create_async_client, AsyncClient

load_dotenv()

TOPIC_ID=817382
SUPABASE_URL=os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY=os.environ.get("SUPABASE_KEY", "")

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

@tamagonche.command("nourrir")
async def feed(msg: Message, _):
    try:
        await supabase.table("actions").insert({"type": "feed", "username": msg.username, "pet_id": 1}).execute()
    except:
        pass

@tamagonche.command("nettoyer")
async def clean_trash(msg: Message, _):
    try:
        await supabase.table("actions").insert({"type": "clean_trash", "username": msg.username, "pet_id": 1}).execute()
    except:
        pass

@tamagonche.command("doliprane")
async def give_medicine(msg: Message, _):
    try:
        await supabase.table("actions").insert({"type": "give_medicine", "username": msg.username, "pet_id": 1}).execute()
    except:
        pass

@tamagonche.command("weed")
async def weed(msg: Message, _):
    try:
        await supabase.table("actions").insert({"type": "weed", "username": msg.username, "pet_id": 1}).execute()
    except:
        pass

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

prev_pet: dict[str, Any] | None = None

async def on_pet_update(payload):
    global prev_pet

    pet = payload["data"]["record"]

    try:
        if prev_pet and prev_pet["food"] != pet["food"]:
            if pet["food"] == 0:
                await notify_dead()
            elif pet["food"] <= pet["hunger_threshold"]:
                await notify_hunger()
    except:
        pass

    prev_pet = pet

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
