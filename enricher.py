import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()

SYSTEM_PROMPT = (
    "You are a scholar of classical Telugu literature and Sanskrit scripture who also has a gift for writing for general audiences. "
    "The following text is from the Shiva Mahapurana, shared in a WhatsApp group, written in classical Telugu with embedded Sanskrit shlokas.\n\n"
    "For Telugu narrative prose: Translate into clear, warm, accessible English that a general reader with no background in Hindu scripture can understand and enjoy. Use simple modern English. Avoid Sanskrit jargon unless necessary. Where cultural context helps understanding, weave it in naturally. Keep the spiritual feeling but make it feel like a beautiful story being told to a friend.\n\n"
    "For Sanskrit shlokas (verses with patterns like 'నమో', 'నమస్తు', or ending with '!!' or '||'): Translate poetically, preserving the devotional reverence, beauty and sacred meaning. These can retain spiritual depth and poetic style.\n\n"
    "Keep responses concise — 3 to 5 sentences maximum."
)


def enrich_messages(parsed_file='parsed_messages.json', output_file='enriched_messages.json'):
    """Read parsed WhatsApp messages, enrich each with Gemini translation, and save JSON output."""
    if not Path(parsed_file).exists():
        raise FileNotFoundError(f"Parsed messages file not found: {parsed_file}")

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError('GEMINI_API_KEY is not set in the environment or .env file.')

    client = genai.Client(api_key=api_key)

    with open(parsed_file, 'r', encoding='utf-8') as infile:
        messages = json.load(infile)

    total = len(messages)

    for index, message in enumerate(messages, start=1):
        print(f"Processing message {index} of {total}...")

        prompt = f"{SYSTEM_PROMPT}\n\n{message.get('message', '')}"

        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash',
                contents=prompt
            )
            enriched_text = response.text.strip()
        except Exception as exc:
            print(f"Error processing message {index}: {exc}")
            enriched_text = 'Translation unavailable'

        message['enriched_english'] = enriched_text

        if index < total:
            time.sleep(2)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        json.dump(messages, outfile, ensure_ascii=False, indent=2)

    print(f"Saved {len(messages)} enriched messages to {output_file}.")
    return messages


if __name__ == '__main__':
    enrich_messages()
