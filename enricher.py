import json
import os
import time
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
MODEL = "gemini-3.5-flash"

SYSTEM_PROMPT = """You are a scholar of classical Telugu literature and Sanskrit scripture who also has a gift for writing for general audiences. The following messages are from the Shiva Mahapurana shared in a WhatsApp group, written in classical Telugu with embedded Sanskrit shlokas.

For Telugu narrative prose: Translate into clear, warm, accessible English that a general reader with no background in Hindu scripture can understand and enjoy. Use simple modern English. Avoid Sanskrit jargon unless necessary. Keep the spiritual feeling but make it feel like a beautiful story being told to a friend.

For Sanskrit shlokas (verses with patterns like 'నమో', 'నమస్తు', or ending with '!!' or '||'): Translate poetically, preserving the devotional reverence, beauty and sacred meaning.

Return ONLY a valid JSON array with no other text before or after it, like this:
[
  {"enriched_english": "translation of message 1"},
  {"enriched_english": "translation of message 2"}
]"""

def load_messages():
    with open("parsed_messages.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_messages(messages):
    with open("enriched_messages.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def already_enriched(message):
    return (
        "enriched_english" in message
        and message["enriched_english"] != "Translation unavailable"
        and message["enriched_english"] != ""
    )

def enrich_batch(batch):
    prompt = SYSTEM_PROMPT + "\n\nMessages to translate:\n"
    for i, msg in enumerate(batch, 1):
        prompt += f"{i}: {msg['message']}\n"

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )
        raw = response.text.strip()

        # Clean up markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        results = json.loads(raw)

        if len(results) != len(batch):
            raise ValueError(f"Expected {len(batch)} results, got {len(results)}")

        return [r["enriched_english"] for r in results]

    except Exception as e:
        raise RuntimeError(f"Batch failed: {e}")

def main():
    messages = load_messages()

    # Load existing enriched messages if available
    if os.path.exists("enriched_messages.json"):
        with open("enriched_messages.json", "r", encoding="utf-8") as f:
            existing = json.load(f)
        # Merge existing enrichments
        for i, msg in enumerate(existing):
            if already_enriched(msg):
                messages[i]["enriched_english"] = msg["enriched_english"]

    total = len(messages)
    batch_size = 5
    successfully_translated = 0

    i = 0
    while i < total:
        # Skip already enriched messages
        batch_indices = []
        while i < total and len(batch_indices) < batch_size:
            if already_enriched(messages[i]):
                successfully_translated += 1
                i += 1
            else:
                batch_indices.append(i)
                i += 1

        if not batch_indices:
            continue

        batch = [messages[idx] for idx in batch_indices]
        start = batch_indices[0] + 1
        end = batch_indices[-1] + 1
        print(f"Processing messages {start}-{end} of {total}...")

        try:
            translations = enrich_batch(batch)
            for idx, translation in zip(batch_indices, translations):
                messages[idx]["enriched_english"] = translation
                successfully_translated += 1
            save_messages(messages)

        except RuntimeError as e:
            error_text = str(e)
            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text or "rate limit" in error_text.lower():
                print(f"Batch failed with rate limit: {e}")
                print("Waiting 90 seconds before retrying...")
                time.sleep(90)
                try:
                    translations = enrich_batch(batch)
                    for idx, translation in zip(batch_indices, translations):
                        messages[idx]["enriched_english"] = translation
                        successfully_translated += 1
                    save_messages(messages)
                except RuntimeError as e2:
                    print(f"Retry failed: {e2}")
                    for idx in batch_indices:
                        messages[idx]["enriched_english"] = "Translation unavailable"
                    save_messages(messages)
            else:
                print(f"Batch failed: {e}")
                for idx in batch_indices:
                    messages[idx]["enriched_english"] = "Translation unavailable"
                save_messages(messages)

        if i < total:
            print(f"Waiting 20 seconds...")
            time.sleep(20)

    print(f"\nDone! Successfully translated {successfully_translated} of {total} messages.")
    print("Results saved to enriched_messages.json")

if __name__ == "__main__":
    main()