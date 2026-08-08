import json
import re
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

WHATSAPP_LINE_RE = re.compile(
    r'^\s*(?P<date>\d{1,2}/\d{1,2}/\d{2,4}),\s*'
    r'(?P<time>\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\s*-\s*'
    r'(?P<sender>[^:]+):\s*(?P<message>.*)$'
)

SYSTEM_MESSAGE_PATTERNS = (
    'messages and calls are end-to-end encrypted',
)


def parse_whatsapp_chat(filename):
    """Parse a WhatsApp chat export into a list of message dictionaries."""
    messages = []

    if not Path(filename).exists():
        raise FileNotFoundError(f"Chat file not found: {filename}")

    current_message = None

    with open(filename, 'r', encoding='utf-8') as chat_file:
        for raw_line in chat_file:
            line = raw_line.rstrip('\n')

            if not line.strip():
                continue

            # Skip system messages like WhatsApp's security notice.
            normalized_line = line.strip().lower()
            if any(pattern in normalized_line for pattern in SYSTEM_MESSAGE_PATTERNS):
                continue

            match = WHATSAPP_LINE_RE.match(line)

            if match:
                # Finalize the previous message before starting a new one.
                if current_message is not None:
                    messages.append(current_message)

                current_message = {
                    'date': match.group('date').strip(),
                    'time': match.group('time').strip(),
                    'sender': match.group('sender').strip(),
                    'message': match.group('message').strip(),
                }
            else:
                # Continuation line belonging to the current message.
                if current_message is not None:
                    current_message['message'] += '\n' + line
                else:
                    # Ignore any non-matching line that appears before a real message.
                    continue

    if current_message is not None:
        messages.append(current_message)

    with open('parsed_messages.json', 'w', encoding='utf-8') as output_file:
        json.dump(messages, output_file, ensure_ascii=False, indent=2)

    print(f"Found {len(messages)} messages.")
    return messages


if __name__ == '__main__':
    parse_whatsapp_chat('chat.txt')
