import boto3
import requests
import json
from utils.secrets import read_secret

def get_bot_token():
    """Get bot token from Docker secrets"""
    try:
        token = read_secret('telegram_bot_token')
        print(f"Retrieved bot token: {token}")
        return token
    except Exception as e:
        print(f"❌ Error getting bot token: {str(e)}")
        return None

def test_bot_token(bot_token):
    """Test if the bot token is valid"""
    url = f"https://api.telegram.org/bot{bot_token}/getme"
    response = requests.get(url)
    if response.status_code == 200:
        print("✅ Bot token is valid!")
        bot_info = response.json()
        print(f"Bot name: {bot_info['result']['first_name']}")
        print(f"Bot username: @{bot_info['result']['username']}")
        return True
    else:
        print("❌ Bot token is invalid!")
        print(f"Error: {response.text}")
        return False

def save_chat_id_to_secrets_manager(chat_id):
    """Save chat ID to AWS Secrets Manager"""
    try:
        session = boto3.session.Session()
        client = session.client('secretsmanager', region_name='us-east-2')
        
        response = client.create_secret(
            Name='/forex-trader/telegram/chat-id',
            SecretString=str(chat_id)
        )
        print("✅ Chat ID saved to Secrets Manager successfully!")
        return True
    except client.exceptions.ResourceExistsException:
        # If secret already exists, update it
        try:
            response = client.update_secret(
                SecretId='/forex-trader/telegram/chat-id',
                SecretString=str(chat_id)
            )
            print("✅ Chat ID updated in Secrets Manager successfully!")
            return True
        except Exception as e:
            print(f"❌ Error updating chat ID in Secrets Manager: {str(e)}")
            return False
    except Exception as e:
        print(f"❌ Error saving chat ID to Secrets Manager: {str(e)}")
        return False

def get_chat_id():
    # Get bot token from Secrets Manager
    bot_token = get_bot_token()
    if not bot_token:
        return
    
    # Test if token is valid
    print("\nTesting bot token...")
    if not test_bot_token(bot_token):
        return
    
    try:
        print("\nGetting updates from bot...")
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        response = requests.get(url)
        data = response.json()
        
        if not data.get('ok'):
            print(f"❌ Error getting updates. Response: {data}")
            print("\nPlease verify that:")
            print("1. You're using the correct bot token")
            print("2. You've interacted with the bot in Telegram")
            return
            
        if not data['result']:
            print("\n No messages found. Please:")
            print("1. Open Telegram")
            print("2. Find your bot")
            print("3. Send /start to your bot")
            print("4. Send any message to your bot")
            print("5. Run this script again")
            return
            
        # Get the chat ID from the first message
        chat_id = data['result'][0]['message']['chat']['id']
        print(f"\n✅ Success! Your chat ID is: {chat_id}")
        
        # Save to AWS Secrets Manager
        if save_chat_id_to_secrets_manager(chat_id):
            print("\nYou can now use this chat ID in your application!")
        
        return chat_id
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Verify your AWS credentials")
        print("3. Make sure you've interacted with the bot in Telegram")

if __name__ == "__main__":
    print("🤖 Telegram Chat ID Finder")
    print("=======================")
    get_chat_id() 