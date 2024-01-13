from channels.db import database_sync_to_async


@database_sync_to_async
def remove_channel_name_from_session(scope, channel_name):
    """Remove the channel name from the session."""
    session = scope["session"]
    try:
        channel_names = session.get("channel_names", [])
        if channel_name in channel_names:
            channel_names.remove(channel_name)
            session.modified = True
            session.save()
    except Exception as e:
        print(f"Error updating session: {e}")


@database_sync_to_async
def add_channel_name_to_session(scope, channel_name):
    """Add the channel name to the user's session for management."""
    session = scope["session"]
    channel_names = session.setdefault("channel_names", [])
    if channel_name not in channel_names:
        channel_names.append(channel_name)
        session.modified = True
        session.save()
