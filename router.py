# Register all routers in the correct order:
# user routers first (start → sections → submissions), then admin routers
from loader import dp

from handlers.user import start, sections, submissions
from handlers.admin import callbacks, input, commands


def register_routers():
    dp.include_router(start.router)
    dp.include_router(sections.router)
    dp.include_router(submissions.router)  # must come after sections to avoid catching section buttons
    dp.include_router(callbacks.router)
    dp.include_router(input.router)
    dp.include_router(commands.router)
