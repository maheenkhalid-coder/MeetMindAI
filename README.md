# 🧠 MeetMind AI

> AI-powered meeting and video assistant that transforms long conversations into searchable, summarized, and actionable information.

## 🚀 Live Demo

**[Open MeetMind AI](https://meetmind-video-ai.streamlit.app/)**

> Hosted on Streamlit Community Cloud. The app may take a little longer to respond after a period of inactivity.

---

## 📌 What It Does

MeetMind AI analyzes **YouTube videos and audio/video files** and automatically generates:

* 🎙️ **Transcript**
* 📝 **Meeting Summary**
* 🏷️ **Meeting Title**
* ✅ **Action Items**
* 🔑 **Key Decisions**
* ❓ **Open Questions**
* 💬 **AI Meeting Chat**

The transcript is also converted into embeddings and stored in **ChromaDB**, allowing users to ask questions about the meeting using **Retrieval-Augmented Generation (RAG)**.

---

## ✨ Features

### 🎥 Video & Audio Processing

Supports YouTube URLs and local audio/video files.

```text
YouTube / Audio / Video
          ↓
     Audio Extraction
          ↓
      16 kHz Mono
          ↓
      Audio Chunks
```

Audio processing is handled using **yt-dlp, FFmpeg, and pydub**.

---

### 🎙️ AI Transcription

MeetMind AI uses **Groq's Whisper API** for speech-to-text transcription.

```text
Audio Chunks
     ↓
Groq Whisper
     ↓
Transcript
```

The Whisper model runs through Groq's API rather than locally.

---

### 📝 AI Meeting Analysis

The transcript is analyzed using the Groq LLM to generate:

* Meeting title
* Summary
* Action items
* Key decisions
* Open questions

---

### 💬 RAG Meeting Chat

MeetMind AI uses **Retrieval-Augmented Generation (RAG)** to answer questions based on the meeting transcript.

```text
Transcript
     ↓
Text Chunking
     ↓
Hugging Face Embeddings
     ↓
ChromaDB
     ↓
Similarity Search
     ↓
Relevant Transcript Context
     ↓
Groq LLM
     ↓
Answer
```

The AI is instructed to answer **only from the retrieved meeting transcript context**.

---

## 🏗️ Architecture

```text
                YouTube / Local File
                         ↓
                  yt-dlp + FFmpeg
                         ↓
                   pydub Processing
                         ↓
                   Audio Chunks
                         ↓
                  Groq Whisper API
                         ↓
                     Transcript
                         ↓
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
       Summary       Extraction       Title
                         ↓
              ┌──────────┼──────────┐
              ↓          ↓          ↓
        Action Items  Decisions  Questions
                         ↓
                  Text Chunking
                         ↓
              Hugging Face Embeddings
                         ↓
                      ChromaDB
                         ↓
                  Similarity Search
                         ↓
                Relevant Context
                         ↓
                    Groq LLM
                         ↓
                    RAG Answer
```

---

## 🛠️ Tech Stack

| Technology           | Purpose                            |
| -------------------- | ---------------------------------- |
| **Python**           | Core application                   |
| **Streamlit**        | Web UI & deployment                |
| **Groq**             | LLM and speech-to-text API         |
| **GPT-OSS 120B**     | Meeting analysis and RAG answers   |
| **Whisper Large V3** | Speech-to-text                     |
| **LangChain**        | LLM orchestration and RAG pipeline |
| **ChromaDB**         | Vector database                    |
| **Hugging Face**     | Text embeddings                    |
| **all-MiniLM-L6-v2** | Embedding model                    |
| **yt-dlp**           | YouTube media processing           |
| **pydub**            | Audio processing                   |
| **FFmpeg**           | Audio conversion                   |
| **deep-translator**  | Translation support                |

---

## 🤖 AI Models

### 🧠 Large Language Model

```text
openai/gpt-oss-120b
```

Used for:

* Meeting summaries
* Meeting titles
* Action-item extraction
* Key-decision extraction
* Open-question extraction
* RAG question answering

The model is accessed through the **Groq API**.

### 🎙️ Speech-to-Text

```text
whisper-large-v3
```

Used to transcribe meeting and video audio through the **Groq API**.

### 🔎 Embeddings

```text
all-MiniLM-L6-v2
```

Used to convert transcript chunks into vector embeddings for semantic search with ChromaDB.

---

## 🧩 RAG Pipeline

MeetMind AI uses a vector-based RAG pipeline:

```text
Meeting Transcript
       ↓
Recursive Text Splitting
       ↓
500 Character Chunks
       ↓
all-MiniLM-L6-v2
       ↓
Vector Embeddings
       ↓
ChromaDB
       ↓
Top 4 Similar Chunks
       ↓
Meeting Context
       ↓
GPT-OSS 120B
       ↓
Final Answer
```

This allows users to ask questions such as:

```text
"What decisions were made about the project?"

"Who was assigned the testing task?"

"What are the open questions?"

"What was discussed about the deadline?"
```
---

## ☁️ Deployment

MeetMind AI is deployed using **Streamlit Community Cloud**.

### Live Application

**[Launch MeetMind AI →](https://meetmind-video-ai.streamlit.app/)**

The application uses environment secrets for the Groq API key rather than storing credentials in the repository.

---

## 🔮 Future Improvements

* 🎤 Speaker identification
* ⏱️ Timestamp-based answers
* 📄 PDF/Word export
* 📚 Multiple meeting management
* ☁️ Persistent cloud vector storage
* 🔐 User authentication
* 🌍 Expanded multilingual support
* 🔎 More advanced semantic search
* 📊 Meeting analytics and insights

## 🚀 Try MeetMind AI

**[Launch the live app →](https://meetmind-video-ai.streamlit.app/)**
