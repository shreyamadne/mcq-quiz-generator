
import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai

# ---------------------------------------
# 1. CONFIGURATION
# ---------------------------------------

load_dotenv()

st.set_page_config(
    page_title="MCQ Quiz Generator",
    page_icon="📝",
    layout="centered"
)

MODEL_NAME = "gemini-3.5-flash-lite"

# ---------------------------------------
# 2. INITIALIZE GEMINI
# ---------------------------------------

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not found. Please check your .env file.")
    st.stop()

client = genai.Client(api_key=api_key)


# ---------------------------------------
# 3. GENERATE MCQS USING GEMINI
# ---------------------------------------

def generate_mcqs(text, number, difficulty):

    prompt = f"""
    You are an expert educational quiz generator.

    Read the study material provided below and generate
    exactly {number} multiple-choice questions.

    Difficulty level: {difficulty}

    IMPORTANT RULES:
    1. Generate questions only from the supplied material.
    2. Each question must have exactly four options.
    3. Only one option must be correct.
    4. Avoid duplicate questions.
    5. Make the wrong options realistic.
    6. Include a short explanation for every answer.
    7. Do not invent facts not supported by the material.
    8. Return valid JSON only.

    Required JSON structure:

    {{
        "questions": [
            {{
                "question": "Question text",
                "options": [
                    "Option A",
                    "Option B",
                    "Option C",
                    "Option D"
                ],
                "answer": "Correct option text",
                "explanation": "Explanation of the answer"
            }}
        ]
    }}

    STUDY MATERIAL:
    {text}
    """

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "temperature": 0.3
        }
    )

    data = json.loads(response.text)

    questions = data.get("questions")

    if not isinstance(questions, list):
        raise ValueError("Invalid question format returned by AI.")

    if len(questions) != number:
        raise ValueError(
            f"Expected {number} questions but received {len(questions)}."
        )

    # Validate every question
    for q in questions:

        if not all(
            key in q
            for key in ["question", "options", "answer", "explanation"]
        ):
            raise ValueError("A question is missing required information.")

        options = q["options"]

        if not isinstance(options, list) or len(options) != 4:
            raise ValueError("Every question must have four options.")

        if len(set(options)) != 4:
            raise ValueError("Duplicate options detected.")

        if q["answer"] not in options:
            raise ValueError("Correct answer is not among the options.")

    return questions


# ---------------------------------------
# 4. APPLICATION HEADER
# ---------------------------------------

st.title("📝 MCQ Quiz Generator")

st.write(
    "Generate interactive multiple-choice quizzes "
    "instantly from your study material using Generative AI."
)

st.divider()

# ---------------------------------------
# 5. INPUT SECTION
# ---------------------------------------

st.subheader("Create Your Quiz")

study_text = st.text_area(
    "Paste your chapter or study material here:",
    height=220,
    placeholder="Paste your chapter content here..."
)

col1, col2 = st.columns(2)

with col1:
    number = st.selectbox(
        "Number of questions",
        [5, 10, 15, 20]
    )

with col2:
    difficulty = st.selectbox(
        "Difficulty level",
        ["Easy", "Medium", "Hard"]
    )

generate_button = st.button(
    "✨ Generate Quiz",
    use_container_width=True,
    type="primary"
)

# ---------------------------------------
# 6. GENERATE QUIZ
# ---------------------------------------

if generate_button:

    if len(study_text.strip()) < 100:
        st.warning("Please enter at least 100 characters of study material.")

    else:
        try:
            with st.spinner("AI is generating your quiz..."):

                questions = generate_mcqs(
                    study_text,
                    number,
                    difficulty
                )

                st.session_state.questions = questions
                st.session_state.submitted = False
                st.session_state.quiz_generated = True

        except json.JSONDecodeError:
            st.error("AI returned invalid JSON. Please try again.")

        except Exception as e:
            st.error(f"Quiz generation failed: {e}")


# ---------------------------------------
# 7. DISPLAY QUIZ
# ---------------------------------------

if st.session_state.get("quiz_generated", False):

    questions = st.session_state.questions

    st.divider()
    st.subheader("Your Generated Quiz")

    st.caption(f"{len(questions)} Questions | {difficulty} Difficulty")

    if not st.session_state.get("submitted", False):

        with st.form("quiz_form"):

            for i, q in enumerate(questions):

                st.markdown(f"**Question {i + 1}. {q['question']}**")

                st.radio(
                    "Select your answer:",
                    q["options"],
                    index=None,
                    key=f"answer_{i}"
                )

                st.divider()

            submit_button = st.form_submit_button(
                "Submit Quiz",
                use_container_width=True,
                type="primary"
            )

        if submit_button:

            unanswered = [
                i + 1
                for i in range(len(questions))
                if st.session_state.get(f"answer_{i}") is None
            ]

            if unanswered:
                st.warning(
                    "Please answer all questions before submitting. "
                    f"Unanswered: {unanswered}"
                )

            else:
                st.session_state.submitted = True
                st.rerun()

    # -----------------------------------
    # 8. SCORE CALCULATION
    # -----------------------------------

    if st.session_state.get("submitted", False):

        score = 0

        for i, q in enumerate(questions):

            selected = st.session_state.get(f"answer_{i}")

            if selected == q["answer"]:
                score += 1

        percentage = (score / len(questions)) * 100

        st.divider()
        st.subheader("🏆 Your Quiz Results")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Questions", len(questions))
        col2.metric("Correct Answers", score)
        col3.metric("Percentage", f"{percentage:.1f}%")

        st.progress(percentage / 100)

        if percentage >= 80:
            st.success("Excellent work! 🎉")
        elif percentage >= 50:
            st.info("Good effort! Keep practising.")
        else:
            st.warning("Keep learning. You can improve!")

        # --------------------------------
        # 9. ANSWER REVIEW
        # --------------------------------

        st.subheader("Answer Review")

        for i, q in enumerate(questions):

            selected = st.session_state.get(f"answer_{i}")

            st.markdown(f"**Question {i + 1}: {q['question']}**")

            if selected == q["answer"]:
                st.success(f"Your answer: {selected}")
            else:
                st.error(f"Your answer: {selected}")
                st.info(f"Correct answer: {q['answer']}")

            st.caption(f"Explanation: {q['explanation']}")

            st.divider()

        # --------------------------------
        # 10. RESTART QUIZ
        # --------------------------------

        if st.button("🔄 Generate Another Quiz", use_container_width=True):

            for key in list(st.session_state.keys()):
                del st.session_state[key]

            st.rerun()


# ---------------------------------------
# 11. FOOTER
# ---------------------------------------

st.divider()

st.caption("MCQ Quiz Generator | Powered by Gemini AI")