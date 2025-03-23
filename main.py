import os
import onchebot
from onchebot.models import Message
from supabase import create_client, Client

TOPIC_ID=817382
SUPABASE_URL=os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY=os.environ.get("SUPABASE_KEY", "")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

user = onchebot.add_user(
    username=os.environ.get("ONCHE_USERNAME", ""),
    password=os.environ.get("ONCHE_PASSWORD", ""),
)

tamagonche = onchebot.add_bot("tamagonche", user, TOPIC_ID)

@tamagonche.command("nourrir")
async def feed(msg: Message, _):
    try:
        supabase.table("actions").insert({"type": "feed", "username": msg.username, "pet_id": 1}).execute()
    except:
        pass

@tamagonche.command("nettoyer")
async def clean_trash(msg: Message, _):
    try:
        supabase.table("actions").insert({"type": "clean_trash", "username": msg.username, "pet_id": 1}).execute()
    except:
        pass

@tamagonche.command("doliprane")
async def give_medicine(msg: Message, _):
    try:
        supabase.table("actions").insert({"type": "give_medicine", "username": msg.username, "pet_id": 1}).execute()
    except:
        pass

onchebot.start()
