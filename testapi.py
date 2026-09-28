from core.vector_store import build_vector_store
import time

print("Starting large vector store test...")

# Simulate a realistic meeting transcript
base_transcript = """
The team discussed the progress of the AI meeting assistant project.
Maheen explained that the application uses FastAPI for the backend
and a modern frontend for the user interface.

The team discussed video processing, audio extraction, transcription,
translation, summarization, and retrieval augmented generation.

The project uses Groq Whisper for transcription and a language model
for generating meeting summaries and answering questions.

The team decided that videos should be limited to ten minutes
to control API usage and processing time.

Maheen will prepare the documentation and improve the frontend.
The team will test the application before deployment.

The next meeting will focus on deployment and performance testing.
"""

# Repeat the transcript to simulate a larger real transcript
test_transcript = base_transcript * 100

print(f"Test transcript length: {len(test_transcript)} characters")

start_time = time.time()

vector_store = build_vector_store(test_transcript)

elapsed = time.time() - start_time

print(f"Vector store test completed in {elapsed:.2f} seconds")

# Test similarity search
results = vector_store.similarity_search(
    "What did the team decide about video length?",
    k=4
)

print("\nSearch results:")

for i, doc in enumerate(results, start=1):
    print(f"\nResult {i}:")
    print(doc.page_content[:300])

print("\nLarge vector store test completed successfully!")