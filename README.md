# Watch Party Research Agent 🎬

An LLM-powered research agent that explores movies, anime, TV shows, and other entertainment titles to generate spoiler-conscious watch party briefs backed by web research and source citations.

Built with **Python, LangGraph, Groq, and Tavily**, the project explores multi-step LLM workflows, automated research planning, evidence-based content generation, and iterative output validation.

## ✨ Features

- **Automated Research Planning:** Generates five targeted search queries covering audience reception, fan opinions, criticism, trivia, and similar titles.
- **Web Research:** Uses Tavily Search API to retrieve and collect relevant web sources.
- **Source Filtering:** Deduplicates URLs and filters results based on content length and search relevance scores.
- **Audience Insights:** Researches positive reception, criticisms, and differing opinions.
- **Behind-the-Scenes Trivia:** Searches for interesting facts and additional details.
- **Similar Title Recommendations:** Identifies recommendations explicitly supported by the retrieved sources.
- **Citation Normalization:** Standardizes citation formats before validation.
- **Citation Validation:** Checks whether referenced source IDs exist.
- **Claim Verification:** Uses an LLM-based evaluator to assess whether individual claims are supported by their cited evidence.
- **Numerical Fact Checking:** Flags numbers in the generated report that cannot be found in the retrieved source text.
- **Spoiler Detection:** Uses a separate LLM-based judge to identify potential spoilers and content that violates the brief's spoiler restrictions.
- **Conditional Revision Loop:** Routes rejected drafts back to the writer, with a configurable maximum number of drafts.

## 🏗️ Architecture

The project uses LangGraph to orchestrate a multi-step research workflow.

### Workflow

```text
             User Input
                 |
                 v
              Planner
                 |
                 v
               Search
                 |
                 v
               Writer
                 |
                 v
                Judge
                 |
           Conditional
              Routing
             /       \
            /         \
      Spoiler       No Spoiler
       Found             |
         |               v
         v             Finish
       Writer
         |
         v
        Judge
```

### Workflow Components

| Component              | Responsibility                                                                 |
| ---------------------- | ------------------------------------------------------------------------------ |
| **Planner**            | Generates five targeted search queries using an LLM.                           |
| **Search**             | Retrieves, filters, and deduplicates sources through Tavily.                   |
| **Writer**             | Generates a structured Markdown brief using retrieved evidence.                |
| **Judge**              | Evaluates the report for potential spoilers.                                   |
| **Conditional Router** | Determines whether the report should be revised or the workflow should finish. |

The revision loop is bounded to prevent endless regeneration.

Additional validation functions evaluate citation IDs, numerical claims, and individual claim-to-source support after the graph completes.

## 🛠️ Tech Stack

- **Language:** Python
- **Workflow Orchestration:** LangGraph
- **LLM Integration:** LangChain Groq
- **Writer Model:** `openai/gpt-oss-120b`
- **Judge Model:** `openai/gpt-oss-20b`
- **Web Search:** Tavily Search API
- **Environment Management:** python-dotenv

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/watch-party-research-agent.git

cd watch-party-research-agent
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project's root directory:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Obtain your API keys from:

- [Groq Console](https://console.groq.com/keys)
- [Tavily](https://tavily.com/)

**Important:** Never commit your `.env` file or expose your API keys publicly.

## ▶️ Usage

Run the LangGraph workflow:

```bash
python graph.py
```

The current example uses:

```python
{"question": "OK Computer (Radiohead)"}
```

You can change the title in `graph.py` to research another movie, anime, TV show, album, or other entertainment title.

The workflow generates a Markdown report and prints validation results, including:

- Spoiler-check verdict
- Citation validation results
- Numerical claims not found in source text
- Claims flagged by the evidence evaluator

## 📄 Example Output

The generated brief contains five sections:

1. **The Pitch** — A short introduction focusing on tone and themes.
2. **Why Fans Love It** — Positive opinions supported by sources.
3. **What Divides People** — Explicitly documented disagreements and criticisms.
4. **Trivia** — Interesting facts and relevant statistics.
5. **If You Liked This, Try** — Similar titles explicitly recommended by retrieved sources.

All factual bullet points are expected to include source citations.

## ⚠️ Current Limitations

This project is still under development. Some limitations include:

- Search quality depends on Tavily's retrieved results.
- Source filtering uses basic relevance and content-length thresholds.
- Citation validation checks source IDs, but does not independently prove that every citation supports its claim.
- Claim verification relies on an LLM and can produce incorrect evaluations.
- Numerical validation uses text matching and does not establish full factual accuracy.
- Spoiler detection is probabilistic and cannot guarantee that every spoiler will be identified.
- The revision loop currently focuses on spoiler feedback rather than all validation failures.
- The workflow uses a predefined research process and does not yet provide an interactive user interface.

## 🗺️ Roadmap

- [ ] Improve source relevance and retrieval quality.
- [ ] Strengthen citation and evidence verification.
- [ ] Improve spoiler detection and revision feedback.
- [ ] Add automated tests with pytest.
- [ ] Introduce structured output validation.
- [ ] Add more comprehensive error handling and API retries.
- [ ] Integrate validation results into conditional graph routing.
- [ ] Build an interactive user interface.
- [ ] Add customizable research preferences.
- [ ] Improve recommendation relevance and evaluation.

## 📌 Project Status

**Active Development — First Functional Version**

This is an ongoing personal AI engineering project exploring LLM-powered research, retrieval, evidence-grounded generation, validation, and graph-based workflow orchestration.
