# System Design

This document explains the architecture of the Multi-Context RAG Chatbot.

---

## Overview

The system is designed to handle multi-domain queries using a combination of intent detection, vector search, and LLM-based response generation.

---

## Architecture Flow

User Input → Intent Router → Context Retrieval → LLM → Response

---

## Components

### 1. Frontend (Streamlit)
- Provides chat interface
- Takes user input
- Displays responses

---

### 2. Intent Router
- Determines query type:
  - General
  - NEC
  - Wattmonk

---

### 3. Context Retriever
- Uses ChromaDB
- Retrieves relevant document chunks
- Based on semantic similarity

---

### 4. Knowledge Base
- NEC PDF
- Wattmonk PDF
- Converted into vector embeddings

---

### 5. Response Engine
- Uses Gemini API
- Combines query + retrieved context
- Generates final answer

---

## RAG Pipeline

1. Query received
2. Relevant context retrieved from vector DB
3. Context injected into prompt
4. LLM generates grounded response

---

## Key Features

- Multi-context query handling
- Context-aware follow-up support
- Modular backend design
- Separation of concerns (routing, retrieval, generation)

---

## Deployment Design

- Streamlit used for UI and execution
- Backend modules imported directly
- Vector store generated at runtime
