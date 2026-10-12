# Workout Plan Generator

A beginner-friendly Streamlit app that uses the Groq API to generate a structured weekly workout plan from a user's fitness goal, experience level, available days, equipment, and optional limitations.

## Features

- Structured inputs instead of a single free-text prompt
- Groq LLM integration
- Prompt instructions that emphasize equipment, schedule, experience, and limitation constraints
- Friendly handling for missing API keys, rate limits, connection issues, API errors, and empty responses
- Generated plan stored in `st.session_state`
- Download the plan as Markdown
- Regenerate a different variation

## 1. Requirements

- Python 3.10 or newer
- A Groq API key

Create or obtain a key at [Groq Console](https://console.groq.com/keys).

## 2. Set up the project

Open a terminal in this project folder.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows PowerShell

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. Add your Groq API key

### Option A: Environment variable

Copy `.env.example` to `.env` and add your key. The example app reads environment variables, but does not automatically load `.env` files. To use this option, set the variable in your terminal before launching the app.

macOS / Linux:

```bash
export GROQ_API_KEY="your_real_key_here"
```

Windows PowerShell:

```powershell
$env:GROQ_API_KEY="your_real_key_here"
```

Do not commit your real API key to GitHub.

### Option B: Streamlit secrets

Create a folder named `.streamlit` and a file named `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your_real_key_here"
```

The `.gitignore` excludes this secrets file.

## 4. Run the app

```bash
streamlit run app.py
```

Streamlit prints a local URL, usually `http://localhost:8501`. Open it in your browser.

## How the code works

1. **Streamlit form** collects structured preferences.
2. **`build_workout_prompt()`** creates a detailed prompt with explicit constraints and output formatting.
3. **`generate_workout_plan()`** validates inputs, calls Groq, and checks that the response is usable.
4. **Error handling** catches common API failures and shows user-friendly messages.
5. **Session state** preserves the generated plan when Streamlit reruns.
6. **Download button** lets the user save the result as a Markdown file.

## Assignment requirements checklist

- [x] Fitness goal dropdown
- [x] Experience level dropdown
- [x] Days per week slider (1–7)
- [x] Equipment dropdown
- [x] Optional injuries or limitations field
- [x] Generate Plan button
- [x] Typed Python functions
- [x] Prompt respects equipment, schedule, experience, and limitations
- [x] API call wrapped in error handling at the UI layer
- [x] Missing API key and invalid input messages
- [x] Empty or suspiciously short response handling
- [x] Day-by-day Markdown output
- [x] Optional stretch goals: session state, download, regenerate

## Before submitting

1. Run the app locally and test it with different goals, experience levels, schedules, and equipment.
2. Test with and without an API key to confirm the missing-key message appears.
3. Check that the plan contains exactly the selected number of training days.
4. Check that the generated exercises match the selected equipment and limitations.
5. Create a **public GitHub repository** and push the project files, but never upload `.env` or `.streamlit/secrets.toml`.
6. Submit the public repository link using the assignment's submission flow.

## Safety note

This app provides general fitness information, not medical advice. Users with injuries or health concerns should consult a qualified healthcare professional before beginning or changing an exercise program.
