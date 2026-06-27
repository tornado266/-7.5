# IELTS Writing AI Examiner

A Streamlit IELTS Writing Task 2 examiner that uses DeepSeek to return structured scoring, feedback, rewrite suggestions, and local progress history.

## What It Does

- Uses the DeepSeek API through `requests.post`.
- Returns structured IELTS scoring when the model provides valid JSON.
- Shows Overall Band Score and four criteria scores.
- Gives concrete feedback with quoted student sentences.
- Produces sentence-level corrections, a Band 7.5 rewrite, useful expressions, and a next practice plan.
- Saves local history records with raw AI output and structured metadata.
- Shows a progress trend when at least two scored essays are available.
- Includes a sidebar `Test DeepSeek Connection` check with latency.
- Falls back safely to the raw examiner report if structured parsing fails.

## Screenshot

Place screenshots here before publishing the project:

```text
screenshots/
  dashboard.png
  report.png
  history.png
```

Suggested first screenshot: the main Streamlit workspace after a completed essay correction.

## How It Works

```text
Essay Question + Student Essay
        |
        v
Streamlit Input Form
        |
        v
IELTS Examiner Prompt
        |
        v
DeepSeek API request with requests.post
        |
        v
Score Cards + Structured Feedback + Local Markdown/JSON History
```

## Features

- Task 2 question and essay input
- Overall band score and four criteria scores
- Word count warning for IELTS minimum requirements
- Main problems with quoted original sentences
- Sentence-level corrections
- Band 7.5 rewrite
- Useful expressions for review
- Next practice plan
- Local history trend chart
- Error book saved to `records/error_book.md`
- Sidebar DeepSeek connection test with latency
- Raw report fallback when JSON parsing fails

## Example Input

Essay question:

```text
Some people believe that university students should study whatever they like.
Others believe they should only study subjects that will be useful in the future,
such as science and technology.

Discuss both views and give your own opinion.
```

Student essay:

```text
Some people think students should choose any subject they enjoy, while others
believe they should study useful subjects. I think students should consider both
their interest and future job opportunities.
```

## Example Output

The app asks the model for JSON in this shape:

```text
{
  "overall_band": 6.0,
  "criteria_scores": {
    "task_response": 6.0,
    "coherence_and_cohesion": 6.5,
    "lexical_resource": 6.0,
    "grammatical_range_and_accuracy": 6.0
  },
  "top_3_problems": [],
  "sentence_level_corrections": [],
  "band_75_rewrite": "",
  "useful_expressions": [],
  "next_practice_plan": []
}
```

Actual output depends on the essay length, quality, and the AI model response.

## Setup

### 1. Clone and enter the project

```bash
git clone https://github.com/tornado266/-7.5.git
cd ielts-writing-skill
```

If you downloaded the project as a ZIP file, just open the extracted project folder.

### 2. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your DeepSeek API key

Create a `.env` file in the project root:

```text
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

The DeepSeek grading request currently uses:

```text
POST https://api.deepseek.com/v1/chat/completions
```

through `requests.post`.

The app reads Streamlit Secrets first and falls back to local environment variables,
so a local `.env` file is only used during development.

### 5. Run the app

Preferred launcher:

```bash
python start.py
```

Or run Streamlit directly:

```bash
streamlit run app.py
```

Open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

## Deploy To Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open [Streamlit Community Cloud](https://share.streamlit.io/) and create an app.
3. Select repository `tornado266/-7.5`, branch `main`, and entrypoint `app.py`.
4. Open **Advanced settings** and add the following Secrets:

```toml
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# Optional, only when using the OpenAI provider.
OPENAI_API_KEY = "your_openai_api_key_here"
```

5. Keep the default supported Python version and click **Deploy**.

Never commit `.streamlit/secrets.toml` or `.env`. Both are excluded by
`.gitignore`. Files written under `records/` on Community Cloud are ephemeral and
may be cleared when the app restarts.

## Recommended Demo Flow

1. Start Streamlit.
2. Click `Test DeepSeek Connection` in the sidebar.
3. Paste an IELTS question and essay.
4. Click `Grade My Essay`.
5. Review the score cards, structured feedback, saved record, and history trend.

## Project Structure

```text
ielts-writing-skill/
  app.py
  requirements.txt
  README.md
  src/
    ai_grader.py
    error_book.py
    prompts.py
    result_parser.py
    storage.py
    text_utils.py
  records/
  screenshots/
```

## FAQ

### Why does the API key not work?

Check that `.env` is in the project root and contains `DEEPSEEK_API_KEY`. After editing `.env`, restart Streamlit so the app reloads the key.

### Why does the request fail even though the page opens?

The page can load even if the AI API request fails. Use `Test DeepSeek Connection` in the sidebar. Also check your network, DeepSeek account balance, and whether port `8501` is already occupied by another Streamlit process.

### Why is the score not always exactly the same?

AI scoring is probabilistic. The report should be treated as guided practice feedback, not an official IELTS result. For more stable practice, compare trends across several essays instead of relying on one score.

### Why does the page look strange in the browser?

Browser translation plugins can modify Streamlit text and layout. Turn off translation for `localhost` if buttons or labels behave unexpectedly.

## Tech Stack

- Python
- Streamlit
- DeepSeek API
- `requests.post` for DeepSeek grading
- OpenAI Python SDK for optional OpenAI provider
- Local Markdown and JSON files for history
