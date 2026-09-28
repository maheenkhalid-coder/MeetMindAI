# Handles audio transcription using Groq Whisper:
# transcribes individual audio chunks and combines them
# into one complete meeting transcript.


from core.models import get_whisper_client, WHISPER_MODEL


def transcribe_chunk(chunk_path: str, translate: bool = False) -> str:
    # Transcribes one audio chunk and optionally translates it into English.
    client = get_whisper_client()

    with open(chunk_path, "rb") as audio_file:

        if translate:
            result = client.audio.translations.create(
                file=audio_file,
                model=WHISPER_MODEL,
            )
        else:
            result = client.audio.transcriptions.create(
                file=audio_file,
                model=WHISPER_MODEL,
            )

    return result.text.strip()


def transcribe_all_chunks(chunks: list, language: str = "english") -> str:
    # Transcribes all audio chunks and combines them into one complete transcript.
    translate = language.lower() == "english"

    transcripts = []

    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i + 1}")

        text = transcribe_chunk(
            chunk,
            translate=translate
        )

        transcripts.append(text)

    print("Transcription completed")

    return " ".join(transcripts)