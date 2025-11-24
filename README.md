
# InterVista AI – Mock Interview Platform

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Tech Stack](#tech-stack)
5. [Installation & Setup](#installation--setup)
6. [Implementation Details](#implementation-details)
7. [Design Decisions](#design-decisions)
8. [Usage](#usage)
9. [Future Improvements](#future-improvements)

## Project Overview
InterVista AI is a mock interview platform that lets candidates practice interviews with real-time AI-generated questions, micro-feedback, and detailed post-interview summaries. It supports both text and voice interactions, adaptive questioning, and structured feedback mechanisms.

## Features
- Role-based interview simulation (Technical / HR / Mixed)
- AI-generated follow-up questions based on candidate responses
- Real-time micro-feedback (scores, strengths, improvements)
- Complete conversation history
- Voice input for candidate answers
- Text-to-speech for AI interviewer
- Post-interview summary with exemplar answers & resources
- Adaptive difficulty engine (DIPE)

## Architecture

### 1. Frontend (Streamlit)
- Handles text + voice input
- Displays chat and micro-feedback
- Manages interview flow

### 2. Backend (FastAPI)
- Receives user answers
- Calls LLM for feedback + next question
- Implements DIPE engine
- Returns structured JSON

### 3. LLM Services
- Generates context-aware questions
- Produces JSON-based micro-feedback
- Creates post-interview reports

### 4. Voice I/O
- speech_recognition for capturing answers
- pyttsx3 for TTS

## Tech Stack
- Frontend: Streamlit
- Backend: FastAPI
- LLM: Gemini Chat
- Voice: speech_recognition, pyttsx3
- Storage: Streamlit session state
- Async: asyncio

## Installation & Setup

### 1. Clone repository
```
git clone https://github.com/kirthi244/intervista-ai.git
cd intervista-ai
```

### 2. Create virtual environment
```
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Run Streamlit frontend
```
streamlit run app.py
```

### 5. Run backend (if separate)
```
uvicorn services.api:app --reload
```

## Implementation Details

### 1. Frontend UI
- Chat panel, feedback panel, role selector, voice input
- Session state: history, role, question, feedback, turn counts
- Auto-processing of answers
- TTS integration

### 2. Backend API
- `/interview` endpoint
- Validates payload → calls LLM → processes DIPE logic
- Returns: next question + micro-feedback

### 3. LLM Prompting
- STRUCTURED_INTERVIEW_INSTRUCTION
- QUESTION_GEN_INSTRUCTION
- FEEDBACK_TPL

### 4. Voice I/O
- Captures voice with speech_recognition
- Bot speech using pyttsx3
- TTS queue prevents overlapping audio

### 5. Session Management
- Tracks full conversation history
- Prevents repeating questions
- Handles async reflection signals

## Design Decisions
- Persistent session state
- Async reflection for non-blocking flow
- Structured JSON for stable parsing
- DIPE for adaptive difficulty
- TTS queue to avoid audio collisions

## Usage
1. Open Streamlit app  
2. Enter candidate name, role, and experience  
3. Answer via text or voice  
4. View micro-feedback  
5. Complete interview (default 10 turns)  
6. Review full feedback report  

## Future Improvements
- Database storage  
- Multi-panel interviews  
- Neural TTS  
- WebSocket chat  
- Smarter adaptive difficulty  
