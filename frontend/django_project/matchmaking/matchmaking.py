from channels.db import database_sync_to_async
from .models import QueueEntry, GameSession
from channels.layers import get_channel_layer

# Function to get all users in the queue, pre-fetching related user objects
# to prevent additional database queries when accessing user instances
@database_sync_to_async
def get_queued_users():
    # Use select_related to fetch related User objects in the same query
    # Convert QuerySet to list to avoid lazy loading outside async context
    return list(QueueEntry.objects.select_related('user').all())

# Function to create a new game session in the database
@database_sync_to_async
def create_game_session_db(user1, user2):
    # Create and return a new GameSession instance
    return GameSession.objects.create(player1=user1, player2=user2)

# Function to delete specified queue entries from the database
@database_sync_to_async
def delete_queue_entries(users):
    # Delete QueueEntry objects for the given users
    QueueEntry.objects.filter(user__in=users).delete()

# Asynchronous function to match users into game sessions
async def match_users():
    # Retrieve and iterate through the queue
    queued_users = await get_queued_users()
    for i in range(0, len(queued_users), 2):
        # Check if there is a pair of users to match
        if i + 1 < len(queued_users):
            # Create a game session for the pair
            session = await create_game_session_db(queued_users[i].user, queued_users[i + 1].user)
            # Notify both users of the match
            await notify_users_of_match(queued_users[i].user.id, queued_users[i + 1].user.id, session.id)
            # Remove the matched users from the queue
            await delete_queue_entries([queued_users[i].user, queued_users[i + 1].user])

# Asynchronous function to notify users of a match
async def notify_users_of_match(user1_id, user2_id, session_id):
    # Get the default channel layer for sending group messages
    channel_layer = get_channel_layer()
    # Notify both users in their respective WebSocket groups
    for user_id in [user1_id, user2_id]:
        group_name = f'queue_{user_id}'
        # Send a 'game_matched' message to the group
        await channel_layer.group_send(
            group_name,
            {'type': 'game_matched', 'message': {'session_id': session_id}}
        )
        print(f'{group_name}: notify_users_of_match')
