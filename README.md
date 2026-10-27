# Watch Party Research Agent

An AI-powered research agent that explores movies, anime, TV shows, and other entertainment titles, then generates a spoiler-conscious watch party brief with source citations and recommendations.

## Features

- **Automated research planning:** Generates five targeted web search queries.
- **Web search:** Uses Tavily to collect relevant search results.
- **Audience insights:** Researches fan reception, common criticisms, and audience preferences.
- **Behind-the-scenes trivia:** Looks for interesting facts and details.
- **Recommendations:** Suggests similar titles found in the research sources.
- **Source citations:** Associates report claims with collected sources.
- **Spoiler checking:** Uses an LLM-based judge to identify potential spoilers.
- **Graph-based workflow:** Orchestrates the pipeline with LangGraph.

## Architecture

The current workflow consists of four nodes:

1. **Plan** — Generates research queries for the requested title.
2. **Search** — Collects and deduplicates results using Tavily.
3. **Write** — Produces a Markdown watch party brief grounded in the collected sources.
4. **Judge** — Checks the generated report for potential spoilers.

```text
User Input
    |
    v
   Plan
    |
    v
  Search
    |
    v
   Write
    |
    v
   Judge
    |
    v
 Markdown Report
```

## Tech Stack

- Python
- LangGraph
- NVIDIA AI Endpoints
- MiniMax M3.1 Flash model endpoint
- Tavily Search API
- python-dotenv

## Installation

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

Create a `.env` file in the project root:

```env
NVIDIA_API_KEY=your_nvidia_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Use your actual API keys locally. Never commit your `.env` file.

## Usage

Run the graph:

```bash
python graph.py
```

The current example researches:

`Frieren: Beyond Journey's End`

The workflow prints a Markdown report, citation-validation results, and the spoiler check.

## Current Limitations

- Search results are primarily evaluated using their titles and snippets.
- Citation validation checks source IDs but does not establish that every claim is supported by its cited source.
- Spoiler checking is an LLM-based check and is not guaranteed to detect every spoiler.
- The current graph does not automatically revise reports that fail the spoiler check.
- The project currently uses a predefined research workflow rather than an interactive user interface.

## Roadmap

- [ ] Improve citation coverage and evidence verification.
- [ ] Add conditional routing and bounded report revision.
- [ ] Improve search-result quality and error handling.
- [ ] Add automated tests.
- [ ] Add a user interface.
- [ ] Improve recommendations using user preferences.
- [ ] Add structured output validation.

## Project Status

First draft — an ongoing personal AI engineering project.

Built to explore LLM-based research workflows, web search, and graph-based orchestration.
