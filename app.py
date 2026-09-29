import json
import random
import time
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Page Configuration
st.set_page_config(
    page_title="History of Kazakhstan | Learning Platform",
    page_icon="📚",
    layout="centered"
)

# Load Questions from JSON
def load_questions():
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

questions_data = load_questions()

# Session State Initialization
if "test_started" not in st.session_state:
    st.session_state.test_started = False
if "test_submitted" not in st.session_state:
    st.session_state.test_submitted = False
if "current_q_index" not in st.session_state:
    st.session_state.current_q_index = 0
if "user_answers" not in st.session_state:
    st.session_state.user_answers = {}
if "current_questions" not in st.session_state:
    st.session_state.current_questions = []
if "variant_name" not in st.session_state:
    st.session_state.variant_name = ""
if "start_time" not in st.session_state:
    st.session_state.start_time = None
if "test_duration" not in st.session_state:
    st.session_state.test_duration = 25 * 60
if "min_required_answers" not in st.session_state:
    st.session_state.min_required_answers = 15
if "time_out" not in st.session_state:
    st.session_state.time_out = False
if "submit_error_msg" not in st.session_state:
    st.session_state.submit_error_msg = None

# Dialog for Test Submission Confirmation
@st.dialog("Confirm Test Submission")
def show_confirm_dialog():
    st.write("### Are you sure you want to finish the test?")
    st.write(f"You have answered **{len(st.session_state.user_answers)}** out of **{len(st.session_state.current_questions)}** questions.")
    st.warning("Once submitted, your answers will be graded and cannot be changed.")
    
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("Yes, Submit Now", type="primary", use_container_width=True):
            st.session_state.test_submitted = True
            st.rerun()
    with col_no:
        if st.button("No, Back to Test", use_container_width=True):
            st.rerun()

# Function to Start a New Test Session
def start_new_test(selected_option):
    st.session_state.test_started = True
    st.session_state.test_submitted = False
    st.session_state.current_q_index = 0
    st.session_state.user_answers = {}
    st.session_state.start_time = time.time()
    st.session_state.time_out = False
    st.session_state.submit_error_msg = None

    if isinstance(questions_data, list):
        variants = {
            "Variant 1 (Week 1: Ancient History & Bronze Age)": questions_data[:30],
            "Variant 2 (Week 2: Early Iron Age)": questions_data[30:60],
            "Variant 3 (Week 3: Turkic Era VI–XII centuries)": questions_data[60:90],
            "Variant 4 (Week 4: Mongol Era & Post-Mongol States XIII–XV centuries)": questions_data[90:120]
        }

        if selected_option == "🔥 Ultimate Test (All 120 Questions)":
            st.session_state.variant_name = "🔥 Ultimate Test (All 120 Questions)"
            st.session_state.current_questions = questions_data[:120]
            st.session_state.test_duration = (70 * 60)  # 1 hour 10 minutes
            st.session_state.min_required_answers = 60
        else:
            st.session_state.test_duration = 25 * 60  # 25 minutes
            st.session_state.min_required_answers = 15

            if selected_option == "🎲 Random Variant (30 Questions)" or selected_option not in variants:
                chosen_variant = random.choice(list(variants.keys()))
            else:
                chosen_variant = selected_option

            st.session_state.variant_name = chosen_variant
            st.session_state.current_questions = variants[chosen_variant]

# Live Updating Timer Fragment
@st.fragment(run_every=1)
def render_live_timer():
    if st.session_state.start_time and st.session_state.test_started and not st.session_state.test_submitted:
        elapsed = time.time() - st.session_state.start_time
        remaining = st.session_state.test_duration - elapsed

        if remaining <= 0:
            st.session_state.test_submitted = True
            st.session_state.time_out = True
            st.rerun()

        hours, remaining_secs = divmod(max(0, int(remaining)), 3600)
        mins, secs = divmod(remaining_secs, 60)

        if hours > 0:
            time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
        else:
            time_str = f"{mins:02d}:{secs:02d}"

        st.metric(label="⏳ Time Remaining", value=time_str)

# Main Header
st.title("History of Kazakhstan: Testing and Essay Verification")
st.caption("First Group Project | Testing & Essay Plagiarism Check")

tab_test, tab_essay = st.tabs(["📝 Testing", "📄 Essay Verification"])

# ==========================================
# TAB 1: TESTING MODULE
# ==========================================
with tab_test:
    if not questions_data:
        st.error("The questions.json file was not found or is empty! Please place questions.json in the project directory.")
    else:
        # SCREEN 1: WELCOME & VARIANT SELECTION
        if not st.session_state.test_started:
            st.header("History of Kazakhstan Test")
            st.info("Select a specific test variant, choose 'Random Variant', or challenge yourself with the Ultimate Test containing all 120 questions!")
            
            variant_options = [
                "🎲 Random Variant (30 Questions)",
                "🔥 Ultimate Test (All 120 Questions)",
                "Variant 1 (Week 1: Ancient History & Bronze Age)",
                "Variant 2 (Week 2: Early Iron Age)",
                "Variant 3 (Week 3: Turkic Era VI–XII centuries)",
                "Variant 4 (Week 4: Mongol Era & Post-Mongol States XIII–XV centuries)"
            ]
            
            selected_variant = st.selectbox(
                "📌 Select Test Variant:",
                options=variant_options,
                index=0
            )

            st.write("📌 **Rules:**")
            if selected_variant == "🔥 Ultimate Test (All 120 Questions)":
                st.write("• Time limit: **1 hour and 10 minutes (70 mins)**.")
                st.write("• Minimum required answers to submit: **60 questions**.")
            else:
                st.write("• Time limit: **25 minutes**.")
                st.write("• Minimum required answers to submit: **15 questions**.")

            st.write("• You can freely switch between questions using the navigation buttons.")
            st.write("• Answered questions are marked with a checkmark.")
            st.write("• Unanswered questions will be counted as incorrect upon submission or time expiry.")
            
            if st.button("🚀 Start Test", type="primary", use_container_width=True):
                start_new_test(selected_variant)
                st.rerun()

        # SCREEN 2: TEST IN PROGRESS
        elif st.session_state.test_started and not st.session_state.test_submitted:
            q_list = st.session_state.current_questions
            num_questions = len(q_list)
            curr_i = st.session_state.current_q_index

            col_title, col_timer = st.columns([2, 1])
            with col_title:
                st.subheader(f"📌 {st.session_state.variant_name}")
            with col_timer:
                render_live_timer()

            if num_questions == 0:
                st.error("No questions found in this variant. Make sure questions.json has 120 questions!")
                if st.button("🔄 Try Again"):
                    st.session_state.test_started = False
                    st.rerun()
            else:
                # Question Navigation Bar
                st.write("**Question Navigation:**")
                cols_per_row = 10
                for row_start in range(0, num_questions, cols_per_row):
                    cols = st.columns(cols_per_row)
                    for i in range(cols_per_row):
                        q_idx = row_start + i
                        if q_idx < num_questions:
                            is_answered = q_idx in st.session_state.user_answers
                            is_current = (q_idx == curr_i)
                            
                            label = f"{'▶' if is_current else ''}{q_idx + 1}{'✓' if is_answered else ''}"
                            
                            if cols[i].button(
                                label, 
                                key=f"nav_btn_{q_idx}", 
                                type="primary" if is_current else "secondary",
                                use_container_width=True
                            ):
                                st.session_state.current_q_index = q_idx
                                st.rerun()

                st.markdown("---")

                # Current Question Display
                q_item = q_list[curr_i]
                options_dict = q_item['options']

                st.markdown(f"### Question {curr_i + 1} of {num_questions}")
                st.markdown(f"**{q_item['question']}**")

                previous_answer = st.session_state.user_answers.get(curr_i, None)
                
                selected_option = st.radio(
                    "Select an answer option:",
                    options=list(options_dict.keys()),
                    format_func=lambda k: f"{k}) {options_dict[k]}",
                    index=list(options_dict.keys()).index(previous_answer) if previous_answer in options_dict else None,
                    key=f"radio_q_{curr_i}"
                )

                if selected_option is not None:
                    st.session_state.user_answers[curr_i] = selected_option
                    st.session_state.submit_error_msg = None

                st.markdown("---")

                # Show submission error message if user tried submitting with insufficient answers
                if st.session_state.submit_error_msg:
                    st.warning(st.session_state.submit_error_msg)

                # Navigation Controls
                col_prev, col_next, col_finish = st.columns([1, 1, 1])

                with col_prev:
                    if curr_i > 0:
                        if st.button("⬅️ Previous", use_container_width=True):
                            st.session_state.current_q_index -= 1
                            st.rerun()

                with col_next:
                    if curr_i < num_questions - 1:
                        if st.button("Next ➡️", use_container_width=True):
                            st.session_state.current_q_index += 1
                            st.rerun()

                with col_finish:
                    if st.button("🏁 Submit Test", type="primary", use_container_width=True):
                        answered_count = len(st.session_state.user_answers)
                        min_req = st.session_state.min_required_answers
                        if answered_count < min_req:
                            st.session_state.submit_error_msg = f"⚠️ Please answer at least {min_req} questions before submitting! (Currently answered: {answered_count}/{min_req})"
                            st.rerun()
                        else:
                            st.session_state.submit_error_msg = None
                            show_confirm_dialog()

        # SCREEN 3: RESULTS
        elif st.session_state.test_submitted:
            q_list = st.session_state.current_questions
            total = len(q_list)
            
            score = sum(
                1 for idx, item in enumerate(q_list)
                if st.session_state.user_answers.get(idx) == item['correctAnswer']
            )

            st.header("🎉 Test Results")

            if st.session_state.time_out:
                st.warning("⏰ Time's up! The time limit expired, and your test was submitted automatically.")

            answered_count = len(st.session_state.user_answers)
            unanswered_count = total - answered_count

            st.subheader(f"Your score: **{score} out of {total}** ({round(score/total * 100, 1)}%)")
            st.caption(f"Answered: {answered_count} | Unanswered (Incorrect): {unanswered_count}")

            if total > 0 and score / total >= 0.7:
                st.success("Great job! You have successfully passed the test.")
            else:
                st.error("Some answers were incorrect or left blank. We recommend reviewing the course material.")

            st.write("---")
            if st.button("🔄 Retake Test / Choose Another Variant", type="primary"):
                st.session_state.test_started = False
                st.session_state.test_submitted = False
                st.rerun()

# ==========================================
# TAB 2: PLAGIARISM CHECK MODULE
# ==========================================
with tab_essay:
    st.header("Essay Originality Check")
    st.write("Paste your essay text below for automated comparison against reference sources.")
    
    reference_corpus = [
        "In the middle of the 4th century, Huns reached the borders of the Roman Empire.",
        "The Kazakh Khanate was formed in 1465 by Kerey and Zhanibek.",
        "Kenesary Kasymov led the national liberation uprising from 1837 to 1847."
    ]
    
    essay_text = st.text_area("Enter essay text:", height=200)
    
    if st.button("Check Originality"):
        if len(essay_text.strip()) < 30:
            st.warning("The essay text is too short. Please enter at least 30 characters.")
        else:
            documents = [essay_text] + reference_corpus
            vectorizer = TfidfVectorizer().fit_transform(documents)
            vectors = vectorizer.toarray()
            
            similarity_scores = cosine_similarity([vectors[0]], vectors[1:])[0]
            max_similarity = similarity_scores.max() if len(similarity_scores) > 0 else 0.0
            
            uniqueness = round((1 - max_similarity) * 100, 1)
            
            st.subheader("Analysis Results:")
            st.metric(label="Uniqueness Score", value=f"{uniqueness}%")
            
            if uniqueness < 70:
                st.error("⚠️ High percentage of matches detected. The essay requires revision.")
            else:
                st.success("✅ Essay successfully passed the uniqueness check.")
                