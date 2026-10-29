
import streamlit as st

from app.services.pdf_service import extract_text_from_pdf

from app.services.ai_service import (
    generate_summary,
    ask_question,
    generate_smart_notes,
    generate_important_lines,
)

from app.services.quiz_service import generate_quiz


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AI StudyMate",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==================================================
# SESSION STATE
# ==================================================

defaults = {
    "pdf_text": "",
    "pdf_name": "",
    "summary": "",
    "smart_notes": "",
    "smart_notes_style": "",
    "important_lines": "",
    "quiz": [],
    "quiz_submitted": None,
    "chat_history": [],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==================================================
# SIDEBAR NAVIGATION
# ==================================================

with st.sidebar:

    st.title("📚 AI StudyMate")

    st.caption("Your AI-powered learning assistant")

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "📝 Summary",
            "📒 Smart Notes",
            "🔍 Important Lines Finder",
            "🧠 Quiz",
            "💬 Chat with PDF",
        ],
    )

    st.divider()

    if st.session_state["pdf_text"]:

        st.success("PDF ready")

        st.caption(
            f"File: {st.session_state['pdf_name']}"
        )

        st.caption(
            f"Extracted characters: "
            f"{len(st.session_state['pdf_text']):,}"
        )

    else:

        st.info("Upload a PDF to get started.")

    st.divider()

    st.caption("Built with Python, Streamlit & Groq AI")


# ==================================================
# 1. DASHBOARD
# ==================================================

if page == "🏠 Dashboard":

    st.title("Welcome to AI StudyMate 👋")

    st.write(
        "Upload your study PDF to generate AI summaries, "
        "smart notes, important lines, practice MCQs, "
        "and ask questions about your study material."
    )

    st.divider()

    uploaded_pdf = st.file_uploader(
        "Upload your study PDF",
        type=["pdf"],
        key="pdf_uploader",
    )

    if uploaded_pdf is not None:

        st.info(f"Selected file: {uploaded_pdf.name}")

        if st.button(
            "📄 Extract PDF Text",
            type="primary",
        ):

            try:

                with st.spinner("Extracting PDF text..."):

                    extracted_text = extract_text_from_pdf(
                        uploaded_pdf
                    )

                st.session_state["pdf_text"] = extracted_text
                st.session_state["pdf_name"] = uploaded_pdf.name

                # Reset generated content for the previous PDF
                st.session_state["summary"] = ""
                st.session_state["smart_notes"] = ""
                st.session_state["smart_notes_style"] = ""
                st.session_state["important_lines"] = ""
                st.session_state["quiz"] = []
                st.session_state["quiz_submitted"] = None
                st.session_state["chat_history"] = []

                st.success(
                    "PDF text extracted successfully!"
                )

                st.rerun()

            except Exception as error:

                st.error(
                    f"PDF extraction failed: {error}"
                )

    # Display PDF information
    if st.session_state["pdf_text"]:

        st.divider()

        st.subheader("📊 Your Study Material")

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Characters",
            f"{len(st.session_state['pdf_text']):,}",
        )

        col2.metric(
            "Words",
            f"{len(st.session_state['pdf_text'].split()):,}",
        )

        col3.metric(
            "Quiz Questions",
            len(st.session_state["quiz"]),
        )

        with st.expander("Preview extracted text"):

            st.text_area(
                "PDF content",
                value=st.session_state["pdf_text"][:10000],
                height=300,
                disabled=True,
            )

        st.subheader("🚀 Quick Actions")

        st.write(
            "Choose **Summary**, **Smart Notes**, "
            "**Important Lines Finder**, **Quiz**, or "
            "**Chat with PDF** from the sidebar."
        )


# ==================================================
# 2. AI SUMMARY
# ==================================================

elif page == "📝 Summary":

    st.title("📝 AI Study Summary")

    st.write(
        "Generate an exam-friendly summary of your study material."
    )

    if not st.session_state["pdf_text"]:

        st.warning(
            "Please upload and extract a PDF from the Dashboard."
        )

    else:

        max_words = st.select_slider(
            "Summary length",
            options=[150, 250, 400, 600],
            value=250,
        )

        if st.button(
            "✨ Generate AI Summary",
            type="primary",
        ):

            try:

                with st.spinner(
                    "AI is summarizing your notes..."
                ):

                    summary = generate_summary(
                        st.session_state["pdf_text"],
                        max_words=max_words,
                    )

                st.session_state["summary"] = summary

            except Exception as error:

                st.error(
                    f"Summary generation failed: {error}"
                )

        if st.session_state["summary"]:

            st.divider()

            st.subheader("Your Summary")

            st.markdown(
                st.session_state["summary"]
            )

            st.download_button(
                "⬇️ Download Summary",
                data=st.session_state["summary"],
                file_name="ai_studymate_summary.txt",
                mime="text/plain",
            )


# ==================================================
# 3. SMART NOTES GENERATOR
# ==================================================

elif page == "📒 Smart Notes":

    st.title("📒 Smart Notes Generator")

    st.write(
        "Convert your PDF study material into structured, "
        "easy-to-understand notes using AI."
    )

    st.markdown(
        """
        **What you can generate:**

        - Topic-wise explanations
        - Important definitions
        - Key points for revision
        - Exam-oriented notes
        - Short-answer and long-answer questions
        """
    )

    if not st.session_state["pdf_text"]:

        st.warning(
            "Please upload and extract a PDF from the Dashboard first."
        )

    else:

        st.info(
            f"Study material: {st.session_state['pdf_name']}"
        )

        note_style = st.selectbox(
            "Choose your notes style",
            [
                "Detailed Notes",
                "Quick Revision",
                "Exam Preparation",
            ],
        )

        if st.button(
            "✨ Generate Smart Notes",
            type="primary",
        ):

            try:

                with st.spinner(
                    "AI is preparing your smart notes..."
                ):

                    notes = generate_smart_notes(
                        st.session_state["pdf_text"],
                        note_style=note_style,
                    )

                st.session_state["smart_notes"] = notes
                st.session_state["smart_notes_style"] = note_style

                st.success(
                    "Smart notes generated successfully!"
                )

            except Exception as error:

                st.error(
                    f"Notes generation failed: {error}"
                )

        if st.session_state["smart_notes"]:

            st.divider()

            st.subheader("📚 Your Smart Notes")

            st.caption(
                "Notes style: "
                + (
                    st.session_state["smart_notes_style"]
                    or "Detailed Notes"
                )
            )

            st.markdown(
                st.session_state["smart_notes"]
            )

            st.download_button(
                "⬇️ Download Smart Notes",
                data=st.session_state["smart_notes"],
                file_name="ai_studymate_smart_notes.md",
                mime="text/markdown",
            )


# ==================================================
# 4. AI IMPORTANT LINES FINDER
# ==================================================

elif page == "🔍 Important Lines Finder":

    st.title("🔍 AI Important Lines Finder")

    st.write(
        "Find important definitions, concepts, formulas, "
        "and revision points from your uploaded PDF."
    )

    st.info(
        "AI will analyze your study material and organize "
        "important information into easy-to-revise categories."
    )

    if not st.session_state["pdf_text"]:

        st.warning(
            "Please upload and extract a PDF from the Dashboard first."
        )

    else:

        st.success(
            f"PDF loaded: {st.session_state['pdf_name']}"
        )

        number_of_lines = st.selectbox(
            "How many important items do you want?",
            [5, 10, 15, 20],
            index=2,
        )

        if st.button(
            "🔍 Find Important Lines",
            type="primary",
        ):

            try:

                with st.spinner(
                    "AI is finding important points in your PDF..."
                ):

                    result = generate_important_lines(
                        st.session_state["pdf_text"],
                        number_of_lines=number_of_lines,
                    )

                st.session_state["important_lines"] = result

                st.success(
                    "Important lines found successfully!"
                )

            except Exception as error:

                st.error(
                    f"Could not find important lines: {error}"
                )

        if st.session_state["important_lines"]:

            st.divider()

            st.subheader("📌 Important Study Points")

            st.markdown(
                st.session_state["important_lines"]
            )

            st.download_button(
                "⬇️ Download Important Lines",
                data=st.session_state["important_lines"],
                file_name="ai_studymate_important_lines.md",
                mime="text/markdown",
            )


# ==================================================
# 5. PRACTICE QUIZ
# ==================================================

elif page == "🧠 Quiz":

    st.title("🧠 Practice Quiz")

    st.write(
        "Test your understanding of the uploaded study material."
    )

    if not st.session_state["pdf_text"]:

        st.warning(
            "Please upload and extract a PDF from the Dashboard."
        )

    else:

        number_of_questions = st.selectbox(
            "Number of questions",
            [5, 10, 15],
            index=0,
        )

        if st.button(
            "🎯 Generate MCQ Quiz",
            type="primary",
        ):

            try:

                with st.spinner("Generating your quiz..."):

                    questions = generate_quiz(
                        st.session_state["pdf_text"],
                        number_of_questions=number_of_questions,
                    )

                st.session_state["quiz"] = questions
                st.session_state["quiz_submitted"] = None

                st.success(
                    "Quiz generated successfully!"
                )

            except Exception as error:

                st.error(
                    f"Quiz generation failed: {error}"
                )

        questions = st.session_state["quiz"]

        if questions:

            with st.form("quiz_form"):

                answers = {}

                for i, question in enumerate(questions):

                    st.markdown(
                        f"**Q{i + 1}. {question['question']}**"
                    )

                    options = question["options"]

                    answers[i] = st.radio(
                        f"Select answer for question {i + 1}",
                        options=list(options.keys()),
                        format_func=lambda key, opts=options: (
                            f"{key}. {opts[key]}"
                        ),
                        key=f"quiz_answer_{i}",
                    )

                submitted = st.form_submit_button(
                    "Submit Quiz"
                )

            if submitted:

                score = sum(
                    answers[i] == question["answer"]
                    for i, question in enumerate(questions)
                )

                st.session_state["quiz_submitted"] = {
                    "score": score,
                    "answers": answers,
                }

            result = st.session_state["quiz_submitted"]

            if result is not None:

                st.divider()

                st.subheader("📊 Your Result")

                score = result["score"]
                total = len(questions)

                st.metric(
                    "Your Score",
                    f"{score} / {total}",
                )

                percentage = (
                    (score / total) * 100
                    if total else 0
                )

                st.metric(
                    "Percentage",
                    f"{percentage:.1f}%",
                )

                st.progress(
                    percentage / 100
                )

                for i, question in enumerate(questions):

                    correct = question["answer"]
                    selected = result["answers"][i]
                    options = question["options"]

                    if selected == correct:

                        st.success(
                            f"Q{i + 1}: Correct!"
                        )

                    else:

                        st.error(
                            f"Q{i + 1}: Incorrect. "
                            f"Correct answer: {correct}. "
                            f"{options[correct]}"
                        )

                    if question.get("explanation"):

                        st.caption(
                            f"Explanation: "
                            f"{question['explanation']}"
                        )


# ==================================================
# 6. CHAT WITH PDF
# ==================================================

elif page == "💬 Chat with PDF":

    st.title("💬 Chat with Your PDF")

    st.write(
        "Ask questions about your uploaded study material."
    )

    if not st.session_state["pdf_text"]:

        st.warning(
            "Please upload and extract a PDF from the Dashboard."
        )

    else:

        # Display previous messages
        for message in st.session_state["chat_history"]:

            with st.chat_message(message["role"]):

                st.markdown(
                    message["content"]
                )

        question = st.chat_input(
            "Ask a question about your PDF..."
        )

        if question:

            st.session_state["chat_history"].append(
                {
                    "role": "user",
                    "content": question,
                }
            )

            with st.chat_message("user"):

                st.markdown(question)

            with st.chat_message("assistant"):

                try:

                    with st.spinner(
                        "Preparing your answer..."
                    ):

                        answer = ask_question(
                            st.session_state["pdf_text"],
                            question,
                        )

                    st.markdown(answer)

                    st.session_state["chat_history"].append(
                        {
                            "role": "assistant",
                            "content": answer,
                        }
                    )

                except Exception as error:

                    st.error(
                        f"Could not answer your question: {error}"
                    )

        if st.button("🗑️ Clear Chat"):

            st.session_state["chat_history"] = []

            st.rerun()
