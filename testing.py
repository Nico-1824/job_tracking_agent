from tools.gmail_tools import get_unread_messages, get_message_content
import json

if __name__ == "__main__":

    unread_messages = get_unread_messages()
    messages = get_message_content(service, unread_messages)
    print(f"Unread messages: {json.dumps(messages)}")
    