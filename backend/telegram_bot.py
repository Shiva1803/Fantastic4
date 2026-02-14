"""
Telegram Bot for con.ai Spaces.

Lets users save messages/files to Spaces and query them
directly from Telegram. Uses python-telegram-bot v21+.

Usage:
    1. Set TELEGRAM_BOT_TOKEN in backend/.env
    2. Run: python backend/telegram_bot.py
"""

import os
import sys
import logging
import tempfile
from pathlib import Path

# Add project root to path so we can import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from backend.services.space_manager import SpaceManager
from backend.services.content_manager import ContentManager
from backend.services.query_engine import QueryEngine

# Load env
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Shared service instances
space_manager = SpaceManager()
content_manager = ContentManager()
query_engine = QueryEngine(content_manager)

# Per-user active space: {tg_user_id: space_id}
active_spaces: dict[int, str] = {}


# ── helpers ──────────────────────────────────────────────────────────

def tg_user_id(update: Update) -> str:
    """Map Telegram user to con.ai userId."""
    return f"tg_{update.effective_user.id}"


def get_active_space(update: Update) -> str | None:
    return active_spaces.get(update.effective_user.id)


def set_active_space(update: Update, space_id: str):
    active_spaces[update.effective_user.id] = space_id


# ── /start & /help ──────────────────────────────────────────────────

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Welcome to con.ai* 🗂\n\n"
        "I help you save messages and files into *Spaces*, "
        "then answer questions about them using AI.\n\n"
        "*Quick start:*\n"
        "1️⃣ `/create trip planning` — create a space\n"
        "2️⃣ Forward messages or send files here\n"
        "3️⃣ `/ask How much was the Airbnb?`\n\n"
        "Type /help to see all commands.",
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "*Commands:*\n\n"
        "/spaces — list your spaces\n"
        "/create `<name>` — create a new space\n"
        "/select `<name>` — set active space\n"
        "/current — show active space\n"
        "/search `<query>` — search active space\n"
        "/ask `<question>` — AI-powered Q\\&A\n"
        "/help — show this message\n\n"
        "*Saving content:*\n"
        "Forward any message or send a file — "
        "it will be saved to your active space.",
        parse_mode="Markdown",
    )


# ── /spaces ─────────────────────────────────────────────────────────

async def cmd_spaces(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = tg_user_id(update)
    spaces = space_manager.get_spaces(uid)

    if not spaces:
        await update.message.reply_text(
            "You don't have any spaces yet.\n"
            "Create one with `/create <name>`",
            parse_mode="Markdown",
        )
        return

    active = get_active_space(update)
    lines = ["*Your Spaces:*\n"]
    for s in spaces:
        marker = " ✅" if s.id == active else ""
        item_count = len(content_manager.get_items(s.id))
        lines.append(f"• *{s.name}*{marker} — {item_count} items")

    lines.append(f"\n_Use /select <name> to switch spaces._")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


# ── /create ─────────────────────────────────────────────────────────

# Conversation states
CREATE_WAITING_NAME = 0


async def cmd_create(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    # If name provided inline: /create college trip
    if ctx.args:
        name = " ".join(ctx.args)
        return await _do_create_space(update, name)

    # Otherwise ask for the name
    await update.message.reply_text("What would you like to name this space?")
    return CREATE_WAITING_NAME


async def create_receive_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if not name:
        await update.message.reply_text("Name can't be empty. Try again:")
        return CREATE_WAITING_NAME
    await _do_create_space(update, name)
    return ConversationHandler.END


async def create_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END


async def _do_create_space(update: Update, name: str):
    uid = tg_user_id(update)
    try:
        space = space_manager.create_space(uid, name)
        set_active_space(update, space.id)
        await update.message.reply_text(
            f"Space *{space.name}* created and set as active.\n"
            f"Now forward messages or send files here!",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"Error creating space: {e}")
    return ConversationHandler.END


# ── /select ─────────────────────────────────────────────────────────

async def cmd_select(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not ctx.args:
        await update.message.reply_text(
            "Usage: `/select <space name>`",
            parse_mode="Markdown",
        )
        return

    name = " ".join(ctx.args).lower()
    uid = tg_user_id(update)
    spaces = space_manager.get_spaces(uid)

    match = next((s for s in spaces if s.name.lower() == name), None)
    if not match:
        # Fuzzy: try partial match
        match = next((s for s in spaces if name in s.name.lower()), None)

    if match:
        set_active_space(update, match.id)
        await update.message.reply_text(
            f"Active space set to *{match.name}*.",
            parse_mode="Markdown",
        )
    else:
        names = ", ".join(f"_{s.name}_" for s in spaces) or "none"
        await update.message.reply_text(
            f"No space matching \"{name}\".\nYour spaces: {names}",
            parse_mode="Markdown",
        )


# ── /current ────────────────────────────────────────────────────────

async def cmd_current(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    space_id = get_active_space(update)
    if not space_id:
        await update.message.reply_text(
            "No active space. Use `/select <name>` or `/create <name>`.",
            parse_mode="Markdown",
        )
        return

    space = space_manager.get_space(space_id)
    if not space:
        await update.message.reply_text("Active space not found. Please select again.")
        return

    item_count = len(content_manager.get_items(space_id))
    await update.message.reply_text(
        f"Active: *{space.name}* — {item_count} items",
        parse_mode="Markdown",
    )


# ── /search ─────────────────────────────────────────────────────────

async def cmd_search(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    space_id = get_active_space(update)
    if not space_id:
        await update.message.reply_text(
            "Set an active space first with `/select <name>`.",
            parse_mode="Markdown",
        )
        return

    if not ctx.args:
        await update.message.reply_text(
            "Usage: `/search <query>`\nExample: `/search airbnb booking`",
            parse_mode="Markdown",
        )
        return

    query = " ".join(ctx.args)
    await update.message.reply_text("Searching...")

    try:
        results = content_manager.search_items(space_id, query, top_k=5)
        if not results:
            await update.message.reply_text("No results found.")
            return

        lines = [f"*Search results for:* _{query}_\n"]
        for i, r in enumerate(results, 1):
            score = int(r.get("score", 0) * 100)
            content = r.get("content", "")[:100]
            rtype = r.get("type", "message")
            icon = "📎" if rtype == "file" else "💬"
            lines.append(f"{i}. {icon} {content} ({score}%)")

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Search error: {e}")


# ── /ask ────────────────────────────────────────────────────────────

async def cmd_ask(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    space_id = get_active_space(update)
    if not space_id:
        await update.message.reply_text(
            "Set an active space first with `/select <name>`.",
            parse_mode="Markdown",
        )
        return

    if not ctx.args:
        await update.message.reply_text(
            "Usage: `/ask <question>`\n"
            "Example: `/ask How much was the Airbnb?`",
            parse_mode="Markdown",
        )
        return

    question = " ".join(ctx.args)
    await update.message.reply_text("Thinking...")

    try:
        result = query_engine.query(space_id, question)
        answer = result.get("answer", "No answer generated.")
        sources = result.get("sources", [])

        text = f"*Q:* {question}\n\n{answer}"
        if sources:
            text += "\n\n_Sources:_"
            for s in sources[:3]:
                preview = s.get("content", "")[:60]
                text += f"\n• {preview}"

        await update.message.reply_text(text, parse_mode="Markdown")
    except ValueError as e:
        await update.message.reply_text(f"Error: {e}")
    except RuntimeError as e:
        await update.message.reply_text(f"AI error: {e}")


# ── Message handler (forwarded / plain text) ────────────────────────

async def handle_message(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    space_id = get_active_space(update)
    if not space_id:
        await update.message.reply_text(
            "No active space. Use `/create <name>` first.",
            parse_mode="Markdown",
        )
        return

    text = update.message.text or update.message.caption or ""
    if not text.strip():
        await update.message.reply_text("Empty message, nothing saved.")
        return

    # Build note with forwarding info
    note = None
    if update.message.forward_origin:
        note = "Forwarded message"

    try:
        item = content_manager.save_message(space_id, text, notes=note)
        space = space_manager.get_space(space_id)
        space_name = space.name if space else "unknown"
        await update.message.reply_text(
            f"Saved to *{space_name}*.",
            parse_mode="Markdown",
        )
    except Exception as e:
        await update.message.reply_text(f"Error saving: {e}")


# ── Document / file handler ─────────────────────────────────────────

async def handle_document(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    space_id = get_active_space(update)
    if not space_id:
        await update.message.reply_text(
            "No active space. Use `/create <name>` first.",
            parse_mode="Markdown",
        )
        return

    doc = update.message.document
    if not doc:
        await update.message.reply_text("No file found in message.")
        return

    # Check file size (10 MB limit)
    if doc.file_size and doc.file_size > 10 * 1024 * 1024:
        await update.message.reply_text("File too large (max 10 MB).")
        return

    await update.message.reply_text(f"Uploading _{doc.file_name}_...", parse_mode="Markdown")

    try:
        # Download file from Telegram
        tg_file = await ctx.bot.get_file(doc.file_id)
        
        # Save to temp file
        suffix = Path(doc.file_name).suffix if doc.file_name else ""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            await tg_file.download_to_drive(tmp.name)
            tmp_path = tmp.name

        # Create a werkzeug-compatible file object
        from werkzeug.datastructures import FileStorage as WerkzeugFileStorage
        with open(tmp_path, "rb") as f:
            werkzeug_file = WerkzeugFileStorage(
                stream=f,
                filename=doc.file_name or "unnamed",
                content_type=doc.mime_type or "application/octet-stream",
            )
            note = update.message.caption or None
            item = content_manager.save_file(space_id, werkzeug_file, notes=note)

        # Clean up temp file
        os.unlink(tmp_path)

        space = space_manager.get_space(space_id)
        space_name = space.name if space else "unknown"
        await update.message.reply_text(
            f"File *{doc.file_name}* saved to *{space_name}*.",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"File upload error: {e}", exc_info=True)
        await update.message.reply_text(f"Error uploading file: {e}")


# ── Photo handler ───────────────────────────────────────────────────

async def handle_photo(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    space_id = get_active_space(update)
    if not space_id:
        await update.message.reply_text(
            "No active space. Use `/create <name>` first.",
            parse_mode="Markdown",
        )
        return

    # Get the largest photo
    photo = update.message.photo[-1]
    await update.message.reply_text("Uploading photo...")

    try:
        tg_file = await ctx.bot.get_file(photo.file_id)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            await tg_file.download_to_drive(tmp.name)
            tmp_path = tmp.name

        from werkzeug.datastructures import FileStorage as WerkzeugFileStorage
        with open(tmp_path, "rb") as f:
            werkzeug_file = WerkzeugFileStorage(
                stream=f,
                filename=f"photo_{photo.file_unique_id}.jpg",
                content_type="image/jpeg",
            )
            note = update.message.caption or None
            item = content_manager.save_file(space_id, werkzeug_file, notes=note)

        os.unlink(tmp_path)

        space = space_manager.get_space(space_id)
        space_name = space.name if space else "unknown"
        await update.message.reply_text(
            f"Photo saved to *{space_name}*.",
            parse_mode="Markdown",
        )
    except Exception as e:
        logger.error(f"Photo upload error: {e}", exc_info=True)
        await update.message.reply_text(f"Error uploading photo: {e}")


# ── Main ────────────────────────────────────────────────────────────

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("ERROR: Set TELEGRAM_BOT_TOKEN in backend/.env")
        print("Get one from @BotFather on Telegram.")
        sys.exit(1)

    app = ApplicationBuilder().token(token).build()

    # Register commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("spaces", cmd_spaces))
    # /create uses a ConversationHandler for the two-step flow
    create_conv = ConversationHandler(
        entry_points=[CommandHandler("create", cmd_create)],
        states={
            CREATE_WAITING_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_receive_name)
            ],
        },
        fallbacks=[CommandHandler("cancel", create_cancel)],
    )
    app.add_handler(create_conv)

    app.add_handler(CommandHandler("select", cmd_select))
    app.add_handler(CommandHandler("current", cmd_current))
    app.add_handler(CommandHandler("search", cmd_search))
    app.add_handler(CommandHandler("ask", cmd_ask))

    # Content handlers (order matters — commands first, then messages)
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("con.ai Telegram bot is running! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
