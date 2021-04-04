# Copyright (C) 2020 - 2021 Divkix. All rights reserved. Source code available under the AGPL.
#
# This file is part of Alita_Robot.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from traceback import format_exc

from pyrogram.errors import PeerIdInvalid, RPCError
from pyrogram.types import Message

from alita import LOGGER, eor
from alita.bot_class import Alita
from alita.database.group_blacklist import GroupBlacklist
from alita.utils.custom_filters import dev_command

# initialise database
db = GroupBlacklist()


@Alita.on_message(dev_command("blchat"))
async def blacklist_chat(c: Alita, m: Message):
    if len(m.text.split()) >= 2:
        chat_ids = m.text.split()[1:]
        replymsg = await eor(m, text=f"Adding {len(chat_ids)} chats to blacklist")
        LOGGER.info(f"{m.from_user.id} blacklisted {chat_ids} groups for bot")
        for chat in chat_ids:
            try:
                get_chat = await c.get_chat(chat)
                chat_id = get_chat.id
                db.add_chat(chat_id)
            except PeerIdInvalid:
                await eor(
                    "Haven't seen this group in this session, maybe try again later?",
                )
            except RPCError as ef:
                LOGGER.error(ef)
                LOGGER.error(format_exc())
        await eor(
            f"Added the following chats to Blacklist.\n<code>{', '.join(chat_ids)}</code>.",
        )
    return


@Alita.on_message(
    dev_command(["rmblchat", "unblchat"]),
)
async def unblacklist_chat(c: Alita, m: Message):
    if len(m.text.split()) >= 2:
        chat_ids = m.text.split()[1:]
        replymsg = await eor(m, text=f"Removing {len(chat_ids)} chats from blacklist")
        LOGGER.info(f"{m.from_user.id} removed blacklisted {chat_ids} groups for bot")
        bl_chats = db.list_all_chats()
        for chat in chat_ids:
            try:
                get_chat = await c.get_chat(chat)
                chat_id = get_chat.id
                if chat_id not in bl_chats:
                    # If chat is not blaklisted, continue loop
                    continue
                db.remove_chat(chat_id)
            except PeerIdInvalid:
                await eor(
                    "Haven't seen this group in this session, maybe try again later?",
                )
            except RPCError as ef:
                LOGGER.error(ef)
                LOGGER.error(format_exc())
        await eor(
            f"Removed the following chats to Blacklist.\n<code>{', '.join(chat_ids)}</code>.",
        )
    return


@Alita.on_message(
    dev_command(["blchatlist", "blchats"]),
)
async def list_blacklist_chats(_, m: Message):
    bl_chats = db.list_all_chats()
    LOGGER.info(f"{m.from_user.id} checking group blacklists in {m.chat.id}")
    if bl_chats:
        txt = (
            "These Chats are Blacklisted:\n"
            + "\n".join([f"<code>{i}</code>" for i in bl_chats]),
        )
    else:
        txt = "No chats are currently blacklisted!"
    await eor(m, text=txt)
    return
