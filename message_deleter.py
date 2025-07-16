import requests
import time


class MessageDeleter:
    def __init__(self, user_token):
        """
        Initialize the message deleter with user token.

        Args:
            user_token (str): Discord user token (NOT bot token)
        """
        self.token = user_token
        self.headers = {
            'Authorization': user_token,
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.base_url = 'https://discord.com/api/v10'
        self.deleted_count = 0

    def get_user_messages(self, channel_id, limit=100, before=None):
        """
        Fetch messages from a specific channel.

        Args:
            channel_id (str): Channel ID to search
            limit (int): Number of messages to fetch (max 100)
            before (str): Message ID to fetch messages before

        Returns:
            List of messages
        """
        url = f"{self.base_url}/channels/{channel_id}/messages"
        params = {
            'limit': limit
        }

        if before:
            params['before'] = before

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching messages: {e}")
            return []

    def delete_message(self, channel_id, message_id):
        """
        Delete a specific message.

        Args:
            channel_id (str): Channel ID
            message_id (str): Message ID to delete

        Returns:
            bool: True if successful, False otherwise
        """
        url = f"{self.base_url}/channels/{channel_id}/messages/{message_id}"

        try:
            response = requests.delete(url, headers=self.headers)
            if response.status_code == 204:
                self.deleted_count += 1
                return True
            elif response.status_code == 429:
                # Rate limited
                retry_after = response.json().get('retry_after', 1)
                print(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self.delete_message(channel_id, message_id)
            else:
                print(f"Failed to delete message {message_id}: {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error deleting message: {e}")
            return False

    def get_user_id(self):
        """Get the current user's ID to filter their messages."""
        url = f"{self.base_url}/users/@me"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()['id']
        except requests.exceptions.RequestException as e:
            print(f"Error getting user ID: {e}")
            return None

    def delete_user_messages_in_channel(self, channel_id, max_messages=None):
        user_id = self.get_user_id()
        if not user_id:
            print("Unable to get user ID")
            return

        print(f"Starting deletion for user {user_id} in channel {channel_id}")

        processed = 0
        last_message_id = None

        while True:
            if max_messages and processed >= max_messages:
                break

            messages = self.get_user_messages(channel_id, before=last_message_id)

            if not messages:
                break

            user_messages = [msg for msg in messages if msg['author']['id'] == user_id]

            if not user_messages:
                # No more user messages, but continue searching older messages
                last_message_id = messages[-1]['id']
                processed += len(messages)
                continue

            for message in user_messages:
                if max_messages and self.deleted_count >= max_messages:
                    break

                message_id = message['id']
                timestamp = message['timestamp']
                content = message['content'][:50] + '...' if len(message['content']) > 50 else message['content']

                print(f"Deleting message: {content} (ID: {message_id}, Time: {timestamp})")

                if self.delete_message(channel_id, message_id):
                    print(f"✓ Deleted message {message_id}")
                else:
                    print(f"✗ Failed to delete message {message_id}")

                # Rate limiting
                time.sleep(1.25)

            last_message_id = messages[-1]['id']
            processed += len(messages)

            print(f"Processed {processed} messages, deleted {self.deleted_count} so far...")


def main():
    print("=" * 30)

    # Get user token
    print("\n1. Enter your Discord user token:")
    print("   (Find this in browser dev tools: F12 > Network > XHR > Request Headers > Authorisation)")
    user_token = input("Token: ").strip()

    if not user_token:
        print("❌ No token provided. Exiting.")
        return

    deleter = MessageDeleter(user_token)

    # Test if Token is valid
    user_id = deleter.get_user_id()
    if not user_id:
        print("❌ Invalid token or connection error. Exiting.")
        return

    print(f"✅ Connected as user ID: {user_id}")

    max_messages = None
    limit_input = input("\n3. Enter max messages to delete (or press Enter for all): ").strip()
    if limit_input.isdigit():
        max_messages = int(limit_input)

    channel_id = input("\n4. Enter channel ID: ").strip()
    if channel_id:
        deleter.delete_user_messages_in_channel(channel_id, max_messages)

    print(f"\n✅ Operation completed!")
    print(f"Total messages deleted: {deleter.deleted_count}")


if __name__ == "__main__":
    try:
        print("⚠️  DISCORD MESSAGE DELETER ⚠️")
        print("Usage of this tool is against Discords Terms of Service and may result in a ban. Use at your own risk.")
        print("This tool will permanently delete messages.")
        print("This action cannot be undone.")
        print("\nDo you want to continue? (type 'yes' to confirm)")

        confirmation = input().strip().lower()
        if confirmation == 'yes':
            main()
        else:
            print("Operation cancelled.")
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")

    input("\nPress Enter to exit...")