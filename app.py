from __future__ import annotations

import os
from typing import Final

import streamlit as st
from groq import Groq
from groq import APIConnectionError, APIStatusError, RateLimitError


APP_TITLE: Final[str] = "Personalized Workout Plan Generator"
MODEL_NAME: Final[str] = "llama-3.3-70b-versatile"


def get_groq_api_key() -> str | None:
    """Read the Groq API key from Streamlit secrets or the environment."""
    try:
        # Streamlit secrets are convenient when deploying on Streamlit Community Cloud.
        secret_key = st.secrets.get("GROQ_API_KEY")
    except (FileNotFoundError, KeyError):
        secret_key = None

    return secret_key or os.getenv("GROQ_API_KEY")


def build_workout_prompt(
    fitness_goal: str,
    experience_level: str,
    days_per_week: int,
    equipment: str,
    limitations: str,
) -> str:
    """Create clear instructions that guide the model toward a practical plan."""
    limitations_text = limitations.strip() or "None provided"

    injury_note = ""
    if limitations.strip():
        injury_note = (
            "\nThe user reported an injury or limitation. Do not diagnose, treat, or make "
            "medical claims. Avoid exercises that obviously conflict with the stated limitation, "
            "offer conservative alternatives where appropriate, and include a brief reminder to "
            "consult a qualified healthcare professional if they are unsure what is safe."
        )

    return f"""
Create a practical weekly workout plan using the profile below.

USER PROFILE
- Fitness goal: {fitness_goal}
- Experience level: {experience_level}
- Available training days per week: {days_per_week}
- Equipment access: {equipment}
- Injuries or limitations: {limitations_text}

NON-NEGOTIABLE REQUIREMENTS
1. Schedule exactly {days_per_week} training day(s), labeled Day 1 through Day {days_per_week}.
2. Use only equipment the user has access to. If "No equipment" is selected, use bodyweight exercises only.
3. Account for the experience level. Keep a beginner plan simple and manageable; do not prescribe advanced techniques to beginners.
4. Align exercise selection and conditioning with the stated fitness goal.
5. For each training day, include:
   - The focus of the session
   - A short warm-up
   - Exercises with sets, reps or duration, and rest periods
   - A brief cool-down or mobility suggestion
6. Include a simple progression tip and a rest/recovery recommendation.
7. If an exercise may not suit the stated limitation, do not include it; choose a safer general alternative instead.
8. Do not promise specific results, diagnose conditions, or make medical claims.
9. Format the response in readable Markdown with headings and bullet points. Do not return one long paragraph.
10. If a detail is unknown, make a reasonable conservative assumption rather than inventing personal medical information.
{injury_note}

Start with a short summary of the plan, then provide the day-by-day schedule.
Keep the plan realistic and usable. This is general fitness information, not medical advice.
""".strip()


def generate_workout_plan(
    fitness_goal: str,
    experience_level: str,
    days_per_week: int,
    equipment: str,
    limitations: str,
    api_key: str,
) -> str:
    """Call Groq and return a generated workout plan.

    Raises a ValueError for invalid inputs or an empty/malformed response.
    API errors are allowed to reach the UI layer, where they are handled gracefully.
    """
    if not 1 <= days_per_week <= 7:
        raise ValueError("Choose between 1 and 7 training days per week.")
    if not fitness_goal.strip() or not experience_level.strip() or not equipment.strip():
        raise ValueError("Please complete all required workout preferences.")
    if not api_key.strip():
        raise ValueError("Groq API key is missing.")

    prompt = build_workout_prompt(
        fitness_goal=fitness_goal,
        experience_level=experience_level,
        days_per_week=days_per_week,
        equipment=equipment,
        limitations=limitations,
    )

    client = Groq(api_key=api_key)
    completion = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.7,
        max_tokens=3000,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a careful fitness-planning assistant. Follow the user's stated "
                    "constraints exactly. Produce practical, clearly structured general fitness "
                    "guidance, and never present it as medical advice."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )

    if not completion.choices:
        raise ValueError("The AI returned no plan. Please try again.")
    content = completion.choices[0].message.content
    if not isinstance(content, str) or not content.strip():
        raise ValueError("The AI returned an empty plan. Please try again.")
    if len(content.strip()) < 80:
        raise ValueError("The AI response looks incomplete. Please generate the plan again.")

    return content.strip()


st.set_page_config(page_title=APP_TITLE, page_icon="💪", layout="centered")
st.title("💪 Workout Plan Generator")
st.write(
    "Tell us about your goals, experience, schedule, and equipment to generate a practical "
    "weekly workout plan."
)
st.caption("General fitness information only. Stop if an exercise causes pain.")

with st.form("workout_preferences"):
    st.subheader("Your workout preferences")

    fitness_goal = st.selectbox(
        "Fitness goal",
        ["Build muscle", "Lose fat", "General fitness", "Improve endurance"],
    )
    experience_level = st.selectbox(
        "Experience level",
        ["Beginner", "Intermediate", "Advanced"],
    )
    days_per_week = st.slider(
        "Days available per week",
        min_value=1,
        max_value=7,
        value=3,
        help="Choose how many days you can realistically train.",
    )
    equipment = st.selectbox(
        "Equipment access",
        ["No equipment", "Home dumbbells", "Full gym"],
    )
    limitations = st.text_area(
        "Injuries or limitations (optional)",
        placeholder="For example: bad knees, no overhead pressing, or leave blank.",
        help="Share only what you are comfortable sharing. The app provides general guidance, not medical advice.",
    )
    submitted = st.form_submit_button("Generate Plan", type="primary", use_container_width=True)

if submitted:
    if not 1 <= days_per_week <= 7:
        st.error("Please select between 1 and 7 training days.")
    else:
        api_key = get_groq_api_key()
        if not api_key:
            st.error(
                "Groq API key not found. Add GROQ_API_KEY to a local .env file (see README) "
                "or to Streamlit secrets before generating a plan."
            )
        else:
            with st.spinner("Building your personalized plan..."):
                try:
                    plan = generate_workout_plan(
                        fitness_goal=fitness_goal,
                        experience_level=experience_level,
                        days_per_week=days_per_week,
                        equipment=equipment,
                        limitations=limitations,
                        api_key=api_key,
                    )
                    st.session_state["workout_plan"] = plan
                    st.session_state["workout_profile"] = {
                        "goal": fitness_goal,
                        "level": experience_level,
                        "days": days_per_week,
                        "equipment": equipment,
                    }
                except ValueError as exc:
                    st.error(str(exc))
                except RateLimitError:
                    st.error("The Groq API rate limit was reached. Please wait a little and try again.")
                except APIConnectionError:
                    st.error("Could not connect to Groq. Check your internet connection and try again.")
                except APIStatusError as exc:
                    if exc.status_code == 401:
                        st.error("Groq rejected the API key. Check that GROQ_API_KEY is correct.")
                    elif exc.status_code == 429:
                        st.error("Groq is temporarily rate-limiting requests. Please try again shortly.")
                    else:
                        st.error(f"Groq returned an API error (status {exc.status_code}). Please try again.")
                except Exception:
                    # Avoid showing credentials or internal exception details to the user.
                    st.error("Something went wrong while generating the plan. Please try again.")

if "workout_plan" in st.session_state:
    st.divider()
    st.subheader("Your weekly workout plan")
    profile = st.session_state.get("workout_profile", {})
    if profile:
        st.caption(
            f"{profile.get('goal', '')} · {profile.get('level', '')} · "
            f"{profile.get('days', '')} day(s)/week · {profile.get('equipment', '')}"
        )
    st.markdown(st.session_state["workout_plan"])
    st.download_button(
        "Download plan as Markdown",
        data=st.session_state["workout_plan"],
        file_name="workout_plan.md",
        mime="text/markdown",
        use_container_width=True,
    )
    if st.button("Regenerate plan", use_container_width=True):
        api_key = get_groq_api_key()
        if not api_key:
            st.error("Groq API key not found. Add it before regenerating the plan.")
        else:
            profile = st.session_state.get("workout_profile", {})
            with st.spinner("Generating another variation..."):
                try:
                    new_plan = generate_workout_plan(
                        fitness_goal=profile["goal"],
                        experience_level=profile["level"],
                        days_per_week=int(profile["days"]),
                        equipment=profile["equipment"],
                        limitations=limitations,
                        api_key=api_key,
                    )
                    st.session_state["workout_plan"] = new_plan
                    st.rerun()
                except RateLimitError:
                    st.error("The Groq API rate limit was reached. Please wait and try again.")
                except (APIConnectionError, APIStatusError):
                    st.error("Groq could not generate another plan. Check your connection and API key.")
                except ValueError as exc:
                    st.error(str(exc))
                except Exception:
                    st.error("Something went wrong while regenerating. Please try again.")
