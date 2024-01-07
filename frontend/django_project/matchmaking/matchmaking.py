from channels.db import database_sync_to_async
from .models import QueueEntry, GameSession
from channels.layers import get_channel_layer
from django.db.models import Prefetch

@database_sync_to_async
def get_queued_users():
    return list(QueueEntry.objects.prefetch_related('user').order_by('joined_at'))

@database_sync_to_async
def create_game_session_db(user1, user2):
    return GameSession.objects.create(player1=user1, player2=user2)

@database_sync_to_async
def delete_queue_entries(users):
    QueueEntry.objects.filter(user__in=users).delete()

async def match_users():
    queued_users = await get_queued_users()
    for i in range(0, len(queued_users), 2):
        if i + 1 < len(queued_users):
            session = await create_game_session_db(queued_users[i].user, queued_users[i + 1].user)
            await notify_users_of_match(queued_users[i].user.id, queued_users[i + 1].user.id, session.id)
            await delete_queue_entries([queued_users[i].user, queued_users[i + 1].user])

async def notify_users_of_match(user1_id, user2_id, session_id):
    channel_layer = get_channel_layer()
    for user_id in [user1_id, user2_id]:
        group_name = f'queue_{user_id}'
        await channel_layer.group_send(
            group_name,
            {'type': 'game_matched', 'message': {'session_id': session_id}}
        )
        print(f'{group_name}: notify_users_of_match')
