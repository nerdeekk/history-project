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

# Session State Initialization for Language and App State
if "lang" not in st.session_state:
    st.session_state.lang = "EN"
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

# Dictionary for Multilingual Support (EN / RU)
translations = {
    "EN": {
        "main_title": "History of Kazakhstan: Testing and Essay Verification",
        "main_caption": "First Group Project | Testing & Essay Plagiarism Check",
        "tab_test": "📝 Testing",
        "tab_essay": "📄 Essay Verification",
        "select_lang": "Language / Язык",
        "test_header": "History of Kazakhstan Test",
        "test_info": "Select a specific test variant, choose 'Random Variant', or challenge yourself with the Ultimate Test containing all 120 questions!",
        "select_variant": "📌 Select Test Variant:",
        "rules_header": "📌 **Rules:**",
        "rules_ultimate": "• Time limit: **1 hour and 10 minutes (70 mins)**.\n• Minimum required answers to submit: **60 questions**.",
        "rules_standard": "• Time limit: **25 minutes**.\n• Minimum required answers to submit: **15 questions**.",
        "rules_general": "• You can freely switch between questions using the navigation buttons.\n• Answered questions are marked with a checkmark.\n• Unanswered questions will be counted as incorrect upon submission or time expiry.",
        "start_btn": "🚀 Start Test",
        "q_nav": "**Question Navigation:**",
        "q_title": "Question",
        "of": "of",
        "select_ans": "Select an answer option:",
        "prev_btn": "⬅️ Previous",
        "next_btn": "Next ➡️",
        "submit_test_btn": "🏁 Submit Test",
        "time_remaining": "⏳ Time Remaining",
        "results_header": "🎉 Test Results",
        "time_out_msg": "⏰ Time's up! The time limit expired, and your test was submitted automatically.",
        "score_label": "Your score:",
        "answered_label": "Answered:",
        "unanswered_label": "Unanswered (Incorrect):",
        "success_pass": "Great job! You have successfully passed the test.",
        "fail_pass": "Some answers were incorrect or left blank. We recommend reviewing the course material.",
        "retake_btn": "🔄 Retake Test / Choose Another Variant",
        "essay_header": "Essay Originality Check",
        "essay_info": "Paste your essay text below for automated comparison against reference sources.",
        "essay_textarea": "Enter essay text:",
        "check_orig_btn": "Check Originality",
        "essay_too_short": "The essay text is too short. Please enter at least 30 characters.",
        "analysis_results": "Analysis Results:",
        "uniqueness_score": "Uniqueness Score",
        "essay_fail": "⚠️ High percentage of matches detected. The essay requires revision.",
        "essay_success": "✅ Essay successfully passed the uniqueness check.",
        "dialog_title": "Confirm Test Submission",
        "dialog_q1": "Are you sure you want to finish the test?",
        "dialog_q2": "You have answered",
        "dialog_q3": "out of",
        "dialog_warning": "Once submitted, your answers will be graded and cannot be changed.",
        "dialog_yes": "Yes, Submit Now",
        "dialog_no": "No, Back to Test",
        "v_random": "🎲 Random Variant (30 Questions)",
        "v_ultimate": "🔥 Ultimate Test (All 120 Questions)",
        "v_1": "Variant 1 (Week 1: Ancient History & Bronze Age)",
        "v_2": "Variant 2 (Week 2: Early Iron Age)",
        "v_3": "Variant 3 (Week 3: Turkic Era VI–XII centuries)",
        "v_4": "Variant 4 (Week 4: Mongol Era & Post-Mongol States XIII–XV centuries)",
        "err_no_json": "The questions.json file was not found or is empty! Please place questions.json in the project directory.",
        "err_no_q": "No questions found in this variant. Make sure questions.json has 120 questions!",
        "try_again": "🔄 Try Again"
    },
    "RU": {
        "main_title": "История Казахстана: Тестирование и проверка эссе",
        "main_caption": "Первый командный проект | Тестирование и проверка на плагиат",
        "tab_test": "📝 Тестирование",
        "tab_essay": "📄 Проверка эссе",
        "select_lang": "Язык / Language",
        "test_header": "Тест по истории Казахстана",
        "test_info": "Выберите конкретный вариант теста, случайный вариант или пройдите Ultimate-тест из всех 120 вопросов!",
        "select_variant": "📌 Выберите вариант теста:",
        "rules_header": "📌 **Правила:**",
        "rules_ultimate": "• Лимит времени: **1 час 10 минут (70 мин)**.\n• Минимальное количество ответов для сдачи: **60 вопросов**.",
        "rules_standard": "• Лимит времени: **25 минут**.\n• Минимальное количество ответов для сдачи: **15 вопросов**.",
        "rules_general": "• Вы можете свободно переключаться между вопросами с помощью кнопок навигации.\n• Отвеченные вопросы отмечены галочкой.\n• Неотвеченные вопросы при сдаче или истечении времени засчитываются как неверные.",
        "start_btn": "🚀 Начать тест",
        "q_nav": "**Навигация по вопросам:**",
        "q_title": "Вопрос",
        "of": "из",
        "select_ans": "Выберите вариант ответа:",
        "prev_btn": "⬅️ Назад",
        "next_btn": "Вперед ➡️",
        "submit_test_btn": "🏁 Завершить тест",
        "time_remaining": "⏳ Осталось времени",
        "results_header": "🎉 Результаты теста",
        "time_out_msg": "⏰ Время вышло! Лимит времени исчерпан, тест был отправлен автоматически.",
        "score_label": "Ваш результат:",
        "answered_label": "Отвечено:",
        "unanswered_label": "Не отвечено (ошибки):",
        "success_pass": "Отличная работа! Вы успешно прошли тест.",
        "fail_pass": "Некоторые ответы оказались неверными или остались пустыми. Рекомендуем повторить материал курса.",
        "retake_btn": "🔄 Пересдать тест / Выбрать другой вариант",
        "essay_header": "Проверка оригинальности эссе",
        "essay_info": "Вставьте текст вашего эссе ниже для автоматического сравнения с эталонными источниками.",
        "essay_textarea": "Введите текст эссе:",
        "check_orig_btn": "Проверить оригинальность",
        "essay_too_short": "Текст эссе слишком короткий. Пожалуйста, введите не менее 30 символов.",
        "analysis_results": "Результаты анализа:",
        "uniqueness_score": "Показатель уникальности",
        "essay_fail": "⚠️ Обнаружен высокий процент совпадений. Эссе требует доработки.",
        "essay_success": "✅ Эссе успешно прошло проверку на уникальность.",
        "dialog_title": "Подтверждение отправки теста",
        "dialog_q1": "Вы уверены, что хотите завершить тест?",
        "dialog_q2": "Вы ответили на",
        "dialog_q3": "из",
        "dialog_warning": "После отправки ваши ответы будут оценены, и их нельзя будет изменить.",
        "dialog_yes": "Да, сдать сейчас",
        "dialog_no": "Нет, вернуться к тесту",
        "v_random": "🎲 Случайный вариант (30 вопросов)",
        "v_ultimate": "🔥 Ultimate Тест (Все 120 вопросов)",
        "v_1": "Вариант 1 (Неделя 1: Древняя история и Эпоха бронзы)",
        "v_2": "Вариант 2 (Неделя 2: Ранний железный век)",
        "v_3": "Вариант 3 (Неделя 3: Тюркская эпоха VI–XII вв.)",
        "v_4": "Вариант 4 (Неделя 4: Монгольская эпоха и государства XIII–XV вв.)",
        "err_no_json": "Файл questions.json не найден или пуст! Пожалуйста, добавьте questions.json в директорию проекта.",
        "err_no_q": "В этом варианте не найдено вопросов. Убедитесь, что в questions.json ровно 120 вопросов!",
        "try_again": "🔄 Попробовать снова"
    }
}

def t(key):
    return translations[st.session_state.lang].get(key, key)

# Helper function to extract localized text from questions
def get_localized(item, key):
    val = item.get(key)
    if isinstance(val, dict):
        return val.get(st.session_state.lang, val.get("EN", ""))
    return val if val else ""

# Load Questions from JSON
def load_questions():
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

questions_data = load_questions()

# Top Header Layout with Language Switcher in the Corner
col_header, col_lang = st.columns([4, 1])

with col_header:
    st.title(t("main_title"))
    st.caption(t("main_caption"))

with col_lang:
    st.write("") 
    selected_lang_option = st.selectbox(
        t("select_lang"),
        options=["English", "Русский"],
        index=0 if st.session_state.lang == "EN" else 1,
        key="lang_selector"
    )
    new_lang = "EN" if selected_lang_option == "English" else "RU"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

# Dialog for Test Submission Confirmation
@st.dialog("Confirm Test Submission")
def show_confirm_dialog():
    st.write(f"### {t('dialog_q1')}")
    st.write(f"{t('dialog_q2')} **{len(st.session_state.user_answers)}** {t('dialog_q3')} **{len(st.session_state.current_questions)}** questions.")
    st.warning(t("dialog_warning"))
    
    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button(t("dialog_yes"), type="primary", use_container_width=True):
            st.session_state.test_submitted = True
            st.rerun()
    with col_no:
        if st.button(t("dialog_no"), use_container_width=True):
            st.rerun()

# Function to Start a New Test Session
def start_new_test(selected_option_key):
    st.session_state.test_started = True
    st.session_state.test_submitted = False
    st.session_state.current_q_index = 0
    st.session_state.user_answers = {}
    st.session_state.start_time = time.time()
    st.session_state.time_out = False
    st.session_state.submit_error_msg = None

    if isinstance(questions_data, list):
        variants = {
            t("v_1"): questions_data[:30],
            t("v_2"): questions_data[30:60],
            t("v_3"): questions_data[60:90],
            t("v_4"): questions_data[90:120]
        }

        if selected_option_key == "v_ultimate":
            st.session_state.variant_name = t("v_ultimate")
            st.session_state.current_questions = questions_data[:120]
            st.session_state.test_duration = (70 * 60)
            st.session_state.min_required_answers = 60
        else:
            st.session_state.test_duration = 25 * 60
            st.session_state.min_required_answers = 15

            if selected_option_key == "v_random":
                chosen_key = random.choice(["v_1", "v_2", "v_3", "v_4"])
                chosen_variant = translations[st.session_state.lang][chosen_key]
            else:
                chosen_variant = translations[st.session_state.lang][selected_option_key]

            st.session_state.variant_name = chosen_variant
            st.session_state.current_questions = variants.get(chosen_variant, questions_data[:30])

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

        st.metric(label=t("time_remaining"), value=time_str)

tab_test, tab_essay = st.tabs([t("tab_test"), t("tab_essay")])

# ==========================================
# TAB 1: TESTING MODULE
# ==========================================
with tab_test:
    if not questions_data:
        st.error(t("err_no_json"))
    else:
        if not st.session_state.test_started:
            st.header(t("test_header"))
            st.info(t("test_info"))
            
            variant_mapping = {
                t("v_random"): "v_random",
                t("v_ultimate"): "v_ultimate",
                t("v_1"): "v_1",
                t("v_2"): "v_2",
                t("v_3"): "v_3",
                t("v_4"): "v_4"
            }
            
            selected_variant_label = st.selectbox(
                t("select_variant"),
                options=list(variant_mapping.keys()),
                index=0
            )
            selected_variant_key = variant_mapping[selected_variant_label]

            st.markdown(t("rules_header"))
            if selected_variant_key == "v_ultimate":
                st.markdown(t("rules_ultimate"))
            else:
                st.markdown(t("rules_standard"))

            st.markdown(t("rules_general"))
            
            if st.button(t("start_btn"), type="primary", use_container_width=True):
                start_new_test(selected_variant_key)
                st.rerun()

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
                st.error(t("err_no_q"))
                if st.button(t("try_again")):
                    st.session_state.test_started = False
                    st.rerun()
            else:
                st.markdown(t("q_nav"))
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

                q_item = q_list[curr_i]
                options_dict = q_item['options']

                st.markdown(f"### {t('q_title')} {curr_i + 1} {t('of')} {num_questions}")
                # Отображение вопроса на выбранном языке
                st.markdown(f"**{get_localized(q_item, 'question')}**")

                previous_answer = st.session_state.user_answers.get(curr_i, None)
                
                selected_option = st.radio(
                    t("select_ans"),
                    options=list(options_dict.keys()),
                    # Отображение вариантов ответа на выбранном языке
                    format_func=lambda k: f"{k}) {get_localized(options_dict, k)}",
                    index=list(options_dict.keys()).index(previous_answer) if previous_answer in options_dict else None,
                    key=f"radio_q_{curr_i}"
                )

                if selected_option is not None:
                    st.session_state.user_answers[curr_i] = selected_option
                    st.session_state.submit_error_msg = None

                st.markdown("---")

                if st.session_state.submit_error_msg:
                    st.warning(st.session_state.submit_error_msg)

                col_prev, col_next, col_finish = st.columns([1, 1, 1])

                with col_prev:
                    if curr_i > 0:
                        if st.button(t("prev_btn"), use_container_width=True):
                            st.session_state.current_q_index -= 1
                            st.rerun()

                with col_next:
                    if curr_i < num_questions - 1:
                        if st.button(t("next_btn"), use_container_width=True):
                            st.session_state.current_q_index += 1
                            st.rerun()

                with col_finish:
                    if st.button(t("submit_test_btn"), type="primary", use_container_width=True):
                        answered_count = len(st.session_state.user_answers)
                        min_req = st.session_state.min_required_answers
                        if answered_count < min_req:
                            st.session_state.submit_error_msg = f"⚠️ Please answer at least {min_req} questions before submitting! (Currently answered: {answered_count}/{min_req})" if st.session_state.lang == "EN" else f"⚠️ Пожалуйста, ответьте как минимум на {min_req} вопросов перед сдачей! (Отвечено: {answered_count}/{min_req})"
                            st.rerun()
                        else:
                            st.session_state.submit_error_msg = None
                            show_confirm_dialog()

        elif st.session_state.test_submitted:
            q_list = st.session_state.current_questions
            total = len(q_list)
            
            score = sum(
                1 for idx, item in enumerate(q_list)
                if st.session_state.user_answers.get(idx) == item['correctAnswer']
            )

            st.header(t("results_header"))

            if st.session_state.time_out:
                st.warning(t("time_out_msg"))

            answered_count = len(st.session_state.user_answers)
            unanswered_count = total - answered_count

            st.subheader(f"{t('score_label')} **{score} / {total}** ({round(score/total * 100, 1)}%)")
            st.caption(f"{t('answered_label')} {answered_count} | {t('unanswered_label')} {unanswered_count}")

            if total > 0 and score / total >= 0.7:
                st.success(t("success_pass"))
            else:
                st.error(t("fail_pass"))

            st.write("---")
            if st.button(t("retake_btn"), type="primary"):
                st.session_state.test_started = False
                st.session_state.test_submitted = False
                st.rerun()

# ==========================================
# TAB 2: PLAGIARISM CHECK MODULE
# ==========================================
with tab_essay:
    st.header(t("essay_header"))
    st.write(t("essay_info"))
    
    reference_corpus = [
        "In the middle of the 4th century, Huns reached the borders of the Roman Empire.",
        "The Kazakh Khanate was formed in 1465 by Kerey and Zhanibek.",
        "Kenesary Kasymov led the national liberation uprising from 1837 to 1847."
    ]
    
    essay_text = st.text_area(t("essay_textarea"), height=200)
    
    if st.button(t("check_orig_btn")):
        if len(essay_text.strip()) < 30:
            st.warning(t("essay_too_short"))
        else:
            documents = [essay_text] + reference_corpus
            vectorizer = TfidfVectorizer().fit_transform(documents)
            vectors = vectorizer.toarray()
            
            similarity_scores = cosine_similarity([vectors[0]], vectors[1:])[0]
            max_similarity = similarity_scores.max() if len(similarity_scores) > 0 else 0.0
            
            uniqueness = round((1 - max_similarity) * 100, 1)
            
            st.subheader(t("analysis_results"))
            st.metric(label=t("uniqueness_score"), value=f"{uniqueness}%")
            
            if uniqueness < 70:
                st.error(t("essay_fail"))
            else:
                st.success(t("essay_success"))