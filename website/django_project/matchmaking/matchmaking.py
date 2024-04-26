from channels.db import database_sync_to_async
from .models import QueueEntry, GameSession
from channels.layers import get_channel_layer
from users.consumers import update_user_session_id
from pong_app.consumers import create_game_instance_async


@database_sync_to_async
def get_queued_users():
    """
    Retrieve all users in the queue with their related User objects.

    This function uses `select_related` to fetch related User objects in the same query,
    optimizing database access and avoiding additional queries when accessing user instances.
    It returns a list instead of a QuerySet to ensure compatibility with async context.
    """
    return list(QueueEntry.objects.select_related('user').all())


@database_sync_to_async
def create_game_session_db(user1, user2):
    """Create a new game session in the database for two users."""
    return GameSession.objects.create(player1=user1, player2=user2, mode='online')


@database_sync_to_async
def delete_queue_entries(users):
    """Delete QueueEntry objects for specified users."""
    QueueEntry.objects.filter(user__in=users).delete()


async def match_users():
    """
    Match users into game sessions asynchronously.

    This function iterates through queued users, pairs them, creates game sessions,
    notifies the users of the match, and then removes them from the queue.
    """
    queued_users = await get_queued_users()
    for i in range(0, len(queued_users), 2):
        if i + 1 < len(queued_users):
            session = await create_game_session_db(queued_users[i].user, queued_users[i + 1].user)
            await create_game_instance_async(session.id)
            for user in [session.player1, session.player2]:
                await update_user_session_id(user, session.id)
            await notify_users_of_match(queued_users[i].user.id, queued_users[i + 1].user.id, session.id)
            await delete_queue_entries([queued_users[i].user, queued_users[i + 1].user])


async def notify_users_of_match(user1_id, user2_id, session_id):
    """
    Notify users of a game match asynchronously.

    This function sends a notification to the respective WebSocket groups of the users.
    """
    channel_layer = get_channel_layer()
    for user_id in [user1_id, user2_id]:
        group_name = f'queue_{user_id}'
        await channel_layer.group_send(
            group_name,
            {'type': 'game_matched', 'message': {'session_id': session_id}}
        )

