#!/usr/bin/env python3
# pylint: disable=missing-docstring

from functools import wraps

from telegram import ChatAction

LIST_OF_ADMINS = [211931420]


def send_action(action: ChatAction):
    """Sends `action` while processing func command."""

    def decorator(func):
        @wraps(func)
        def command_func(bot, update, *args, **kwargs):
            bot.send_chat_action(
                chat_id=update.effective_message.chat_id, action=action
            )
            return func(bot, update, *args, **kwargs)

        return command_func

    return decorator


def restricted(func):
    """Restricts commands to admins specified in 'LIST_OF_ADMINS'"""

    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return None
        return func(bot, update, *args, **kwargs)

    return wrapped
