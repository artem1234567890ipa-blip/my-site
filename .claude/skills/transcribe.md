---
name: transcribe
description: When user wants to transcribe audio or video to text. Triggers on: "transcribe", "transcription", "convert audio to text", "speech to text", "/transcribe", "транскрибируй", "транскрипция", "переведи аудио в текст".
---

Transcribe audio or video files to text using the Deepgram API.

## Setup (first time only)

1. Check if `D:/claude/lesson1-practice/.env` exists with `DEEPGRAM_API_KEY`
2. If not, ask the user for their Deepgram API key (deepgram.com — $200 free credits)
3. Install dependencies if needed: `cd D:/claude/lesson1-practice && uv pip install deepgram-sdk python-dotenv`

## Usage

Run the transcription script:

```bash
cd D:/claude/lesson1-practice
.\.venv\Scripts\python.exe scripts\transcribe.py <file_path_or_url>
```

- For a URL: pass the direct link to an audio/video file
- For a local file: pass the full path (e.g. `C:/Users/artem/audio.mp3`)
- Result is saved to `transcript.txt` in the current directory

## After transcription

- Show the transcript to the user
- Ask if they want to save it somewhere (Notion, file, etc.)
- Offer to summarize or format the transcript

## Supported formats

mp3, mp4, wav, flac, ogg, m4a, webm, and most common audio/video formats.
