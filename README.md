# 🚀 Local-AI News Intelligence Engine (V1)

A high-performance asynchronous pipeline designed to scrape, analyze, and quantify global financial news using local Large Language Models (LLMs). Optimized for **NVIDIA RTX 4070 Super** hardware using a **PyTorch 2.7** backend for low-latency inference.

## 🧠 The Problem
In 2026, financial markets are flooded with information noise. Most traders rely on expensive terminal subscriptions or delayed aggregators. This project provides a **zero-latency, private, and cost-effective** alternative by running state-of-the-art models (Llama 3.1) locally, ensuring that sensitive market queries never leave the host machine.

## 🏗️ Architecture & Data Pipeline
The system follows a modular ETL (Extract, Transform, Load) pattern:

1.  **Extraction:** Real-time RSS ingestion from Reuters, CNBC, Investing.com, and OilPrice.
2.  **Inference:** Local **Llama 3.1 (8B/70B)** via the Ollama orchestration engine.
3.  **Quantification:** A custom **Priority Scoring** algorithm to filter "Golden Signals":
    $$Priority = \frac{Impact (1-10) \times Confidence (0-100)}{100}$$
4.  **Visualization:** Interactive Streamlit dashboard with Plotly-powered time-series and sector analytics.

### 🛠️ Tech Stack
- **Language:** Python 3.10.19
- **AI Backend:** PyTorch 2.7.1 + CUDA 11.8
- **LLM Orchestration:** Ollama 0.6.1
- **Data Handling:** Pandas 2.3.3
- **UI/UX:** Streamlit 1.54.0 & Plotly 6.5.2

## ⚡ Key Features
- **Local-First Inference:** Data privacy guaranteed. Zero API costs and no external dependency on cloud providers.
- **Structured Intelligence:** Automatically transforms unstructured news prose into strictly validated JSON schemas.
- **Weighted Sentiment:** Uses "Bullish/Bearish/Neutral" classification adapted for high-frequency macro analysis.
- **Hardware Context:** "Hardware Context: Developed and tested on NVIDIA RTX 4070 Super (12GB VRAM)

## 🚀 Getting Started

1. **Clone and Install Dependencies:**
   ```bash
   git clone [https://github.com/yourusername/news-intelligence-bot.git](https://github.com/yourusername/news-intelligence-bot.git)
   cd news-intelligence-bot
   pip install -r requirements.txt

2. **Download the AI Model:**
   Depending on your VRAM (GPU memory), choose one:
   ```bash
    # Balanced (Recommended for 8GB+ VRAM)
    ollama pull llama3.1:8b

    # High Intelligence (Recommended for RTX 3090/4090/5090)
    ollama pull llama3.1:70b

3. **Ensure Ollama is running Llama 3.1:**
   ```bash
   ollama run llama3.1:latest

4. **Start the Intelligence Engine:**
   ```bash
   python get_news_bot.py

5. **Launch the Visual Dashboard:**
   ```bash
   streamlit run dashboard.py

## 📊 Logic & Scoring System
The engine is instructed via a sophisticated System Prompt to avoid "neutrality bias". It forces the LLM to take decisive stances on market impact, using the full 1-10 scale. This ensures that the dashboard highlights genuine "Black Swan" events (Score > 7.0) versus routine market noise.

> **Disclaimer:** This project is for research and educational purposes only. It does not constitute financial advice. The author is not responsible for any financial losses incurred from the use of this software.