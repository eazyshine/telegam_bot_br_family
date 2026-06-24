from datetime import datetime

# Maps internal section keys to human-readable Russian labels
SECTION_LABELS = {
    "complaint": "Жалоба на игроков семьи",
    "deputy": "Заявка на заместителя",
    "senior": "Заявка на Старший Состав",
    "misc": "Прочее",
}


def user_mention(user_id: int, username: str | None) -> str:
    """
    Build a clickable HTML link to a Telegram user profile.

    Args:
        user_id:  Telegram user ID used in the tg:// deep link.
        username: @username to display; falls back to 'id:{user_id}' if None.

    Returns:
        HTML anchor tag that opens the user's profile when tapped.
    """
    display = f"@{username}" if username else f"id:{user_id}"
    return f'<a href="tg://user?id={user_id}">{display}</a>'


def format_admin_msg(user_id: int, username: str | None, section: str, content: str) -> str:
    """
    Format the message sent to admins when a new submission arrives.

    Args:
        user_id:  Telegram ID of the user who submitted.
        username: @username of the submitter.
        section:  Section key ('complaint', 'deputy', 'senior', 'misc').
        content:  Raw text of the submission.

    Returns:
        HTML-formatted string ready to send via parse_mode='HTML'.
    """
    label = SECTION_LABELS.get(section, section)
    mention = user_mention(user_id, username)

    icons = {
        "complaint": "📋",
        "deputy": "📝",
        "senior": "📝",
        "misc": "💬",
    }
    icon = icons.get(section, "📋")

    return f"{icon} <b>{label}</b>\n\nОт: {mention}\n\n{content}"


def confirm_msg(section: str) -> str:
    """
    Return the confirmation text sent to the user after they submit.

    Args:
        section: Section key to pick the matching confirmation text.

    Returns:
        A section-specific confirmation string.
    """
    messages = {
        "complaint": "Ваша жалоба принята на рассмотрение. Ожидайте ответ администратора.",
        "deputy": "Ваша заявка на заместителя принята на рассмотрение. Ожидайте ответ администратора.",
        "senior": "Ваша заявка на старший состав принята на рассмотрение. Ожидайте ответ администратора.",
        "misc": "Ваше сообщение принято. Ожидайте ответ администратора.",
    }
    return messages[section]


def approval_msg(section: str, comment: str | None = None) -> str:
    """
    Build the approval message sent to the user when an admin accepts.

    Args:
        section: Section key to produce the correct wording.
        comment: Optional admin comment appended to complaint approvals.

    Returns:
        Approval text tailored to the section.
    """
    if section == "complaint":
        base = "Здравствуйте, ваша жалоба была одобрена."
        return f"{base} {comment}" if comment else base
    if section == "deputy":
        return "Здравствуйте, ваша заявка на заместителя была одобрена."
    if section == "senior":
        return "Здравствуйте, ваша заявка на старший состав была одобрена."
    return "Здравствуйте, ваш запрос был рассмотрен."


def rejection_msg(section: str, reason: str) -> str:
    """
    Build the rejection message sent to the user when an admin declines.

    Args:
        section: Section key to produce the correct wording.
        reason:  The rejection reason typed by the admin.

    Returns:
        Rejection text with the reason appended.
    """
    if section == "complaint":
        return f"Здравствуйте, ваша жалоба была отклонена. Причина: {reason}"
    return f"Здравствуйте, к сожалению ваша заявка была отклонена. Причина: {reason}"


def format_submission_detail(sub: dict) -> str:
    """
    Format a single submission as a detailed HTML block for /approved or /declined.

    Args:
        sub: Submission dict from the database (all columns).

    Returns:
        Multi-line HTML string representing one submission entry.
    """
    label = SECTION_LABELS.get(sub["section"], sub["section"])
    username = f"@{sub['username']}" if sub["username"] else f"id:{sub['user_id']}"
    user_link = f'<a href="tg://user?id={sub["user_id"]}">{username}</a>'

    # aiomysql returns DATETIME columns as Python datetime objects, not strings
    raw = sub["created_at"]
    dt = raw if isinstance(raw, datetime) else datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")
    date_str = dt.strftime("%d.%m.%Y %H:%M")

    lines = [
        f"📋 <b>Заявка #{sub['id']}</b>",
        f"Раздел: {label}",
        f"От: {user_link}",
        f"Дата: {date_str}",
    ]

    status_label = "Одобрено" if sub["status"] == "approved" else "Отклонено"
    lines.append(f"Решение: {status_label}")

    if sub.get("admin_comment"):
        lines.append(f"Комментарий: {sub['admin_comment']}")

    lines.append("─" * 20)
    return "\n".join(lines)
