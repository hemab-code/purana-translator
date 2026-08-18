import json
from datetime import datetime
from pathlib import Path
from html import escape


def build_website(input_file='enriched_messages.json', output_file='index.html'):
    """Build a static HTML page from enriched WhatsApp chat messages."""
    if not Path(input_file).exists():
        raise FileNotFoundError(f"Enriched messages file not found: {input_file}")

    with open(input_file, 'r', encoding='utf-8') as infile:
        messages = json.load(infile)

    grouped = {}
    for message in messages:
        date = message.get('date', 'Unknown Date')
        grouped.setdefault(date, []).append(message)

    html_parts = []
    html_parts.append(r'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>శివ మహాపురాణం</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Crimson+Text:ital,wght@0,400;0,600;1,400;1,600&family=Noto+Sans+Telugu:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #2a211a;
      --bg-soft: #352b24;
      --bg-panel: #453922;
      --text: #f8eadc;
      --text-soft: #d1bba4;
      --text-muted: #b5a184;
      --text-faint: #9b886e;
      --saffron: #d4a43a;
      --saffron-light: #f3dd96;
      --saffron-deep: #9a6513;
      --line: #80613b;
      --shadow: rgba(0, 0, 0, 0.34);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Crimson Text', serif;
      background:
        radial-gradient(circle at 50% 0%, rgba(120, 90, 30, 0.22), transparent 25%),
        linear-gradient(135deg, #221b17 0%, #30271d 52%, #211a13 100%);
      color: var(--text);
      line-height: 1.6;
      min-height: 100vh;
      padding: 36px 14px;
    }

    .container {
      max-width: 1100px;
      margin: 0 auto;
    }

    header {
      text-align: center;
      padding: 34px 20px 44px;
      position: relative;
    }

    header::after {
      content: '';
      display: block;
      width: 140px;
      height: 2px;
      background: var(--saffron);
      margin: 20px auto 0;
      opacity: 0.95;
    }

    h1 {
      font-size: clamp(2.35rem, 5vw, 4rem);
      line-height: 1.06;
      font-weight: 600;
      letter-spacing: 0.02em;
      color: var(--saffron-light);
    }

    .subtitle {
      margin-top: 12px;
      font-size: clamp(1rem, 2.1vw, 1.45rem);
      color: var(--text-soft);
      font-style: italic;
    }

    .date-group {
      margin-top: 28px;
    }

    .date-heading {
      font-size: 0.88rem;
      letter-spacing: 0.09em;
      color: var(--saffron-light);
      text-transform: uppercase;
      border-bottom: 1px solid var(--line);
      padding-bottom: 9px;
      margin-bottom: 18px;
    }

    .message-card {
      background: rgba(74, 60, 35, 0.62);
      border: 1px solid rgba(212, 164, 58, 0.38);
      border-radius: 14px;
      padding: 20px 20px 18px;
      margin-bottom: 16px;
      box-shadow: 0 6px 22px var(--shadow);
      backdrop-filter: blur(2px);
    }

    .meta {
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--text-muted);
      font-size: 0.74rem;
      letter-spacing: 0.07em;
      margin-bottom: 10px;
    }

    .meta .dot {
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--saffron);
      display: inline-block;
    }

    .telugu-text {
      font-family: 'Noto Sans Telugu', sans-serif;
      font-size: clamp(1rem, 2.3vw, 1.34rem);
      color: var(--text);
      line-height: 1.88;
      white-space: pre-wrap;
    }

    .divider {
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--saffron), transparent);
      margin: 14px 0 12px;
    }

    .translation {
      font-size: clamp(0.98rem, 2vw, 1.1rem);
      font-style: italic;
      color: var(--text-soft);
      line-height: 1.78;
      white-space: pre-wrap;
    }

    .footer {
      text-align: center;
      color: var(--text-faint);
      font-size: 0.76rem;
      margin-top: 40px;
    }

    @media (max-width: 640px) {
      body {
        padding: 16px 8px;
      }

      header {
        padding-top: 12px;
      }

      .message-card {
        padding: 17px 14px;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>శివ మహాపురాణం</h1>
      <div class="subtitle">Shiva Mahapurana — Enriched English Translations</div>
    </header>
''')

    for date in sorted(grouped.keys(), key=lambda d: d if d != 'Unknown Date' else ''):
        html_parts.append('    <section class="date-group">\n')
        html_parts.append(f'      <h2 class="date-heading">{escape(date)}</h2>\n')

        for message in grouped[date]:
            original = escape(message.get('message', ''))
            enriched = escape(message.get('enriched_english', 'Translation unavailable'))
            date_value = escape(message.get('date', ''))
            time_value = escape(message.get('time', ''))
            sender = escape(message.get('sender', 'Unknown'))

            html_parts.append('      <article class="message-card">\n')
            html_parts.append('        <div class="meta">\n')
            html_parts.append('          <span class="dot"></span>\n')
            html_parts.append(f'          <span>{date_value}, {time_value}</span>\n')
            html_parts.append('        </div>\n')
            html_parts.append(f'        <div class="telugu-text">{original}</div>\n')
            html_parts.append('        <div class="divider"></div>\n')
            html_parts.append(f'        <div class="translation">{enriched}</div>\n')
            html_parts.append('      </article>\n')

        html_parts.append('    </section>\n')

    html_parts.append('''
    <div class="footer">
      Sacred Reflections
    </div>
  </div>
</body>
</html>
''')

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(''.join(html_parts))

    print('Website built! Open index.html in your browser.')
    return output_file


if __name__ == '__main__':
    build_website()
