import json
import random
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Настройка страницы
st.set_page_config(
    page_title="История Казахстана | Учебная платформа",
    page_icon="🇰🇿",
    layout="centered"
)

# Загрузка данных из JSON
@st.cache_data
def load_questions():
    try:
        with open("questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

questions_data = load_questions()

# Инициализация состояния сессии (st.session_state)
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

# Функция запуска нового теста
def start_new_test():
    st.session_state.test_started = True
    st.session_state.test_submitted = False
    st.session_state.current_q_index = 0
    st.session_state.user_answers = {}

    if isinstance(questions_data, dict):
        # Если JSON разбит по ключам: {"Вариант 1": [...], "Вариант 2": [...]}
        variant_key = random.choice(list(questions_data.keys()))
        st.session_state.variant_name = variant_key
        st.session_state.current_questions = questions_data[variant_key]
    elif isinstance(questions_data, list):
        # Если JSON — плоский список вопросов, делим на 3 варианта по 10 вопросов
        total = len(questions_data)
        if total >= 30:
            var_num = random.randint(1, 3)
            chunk_size = total // 3
            start_idx = (var_num - 1) * chunk_size
            end_idx = start_idx + chunk_size if var_num < 3 else total
            st.session_state.variant_name = f"Вариант {var_num}"
            st.session_state.current_questions = questions_data[start_idx:end_idx]
        else:
            st.session_state.variant_name = "Случайный вариант"
            st.session_state.current_questions = questions_data

st.title("🇰🇿 Платформа проверки знаний: История Казахстана")
st.caption("Первый групповой проект | Раздел тестирования и эссе")

tab_test, tab_essay = st.tabs(["📝 Тестирование", "📄 Проверка Эссе"])

# ==========================================
# ВКЛАДКА 1: МОДУЛЬ ТЕСТИРОВАНИЯ (ЕНТ-СТИЛЬ)
# ==========================================
with tab_test:
    if not questions_data:
        st.error("Файл questions.json не найден или пуст! Положите файл questions.json в папку с проектом.")
    else:
        # ЭКРАН 1: ПРИВЕТСТВИЕ И КНОПКА "НАЧАТЬ ТЕСТ"
        if not st.session_state.test_started:
            st.header("Тест по истории Казахстана")
            st.info("Вам будет случайно назначен один из вариантов тестирования. Формат проведения аналогичен ЕНТ.")
            
            st.write("📌 **Правила:**")
            st.write("• Вы можете свободно переключаться между вопросами с помощью кнопок номеров.")
            st.write("• Завершенный ответ подсвечивается галочкой.")
            st.write("• Нажмите **«Завершить тест»** после заполнения всех ответов.")
            
            if st.button("🚀 Начать тест", type="primary", use_container_width=True):
                start_new_test()
                st.rerun()

        # ЭКРАН 2: ТЕСТ ИДЕТ
        elif st.session_state.test_started and not st.session_state.test_submitted:
            q_list = st.session_state.current_questions
            num_questions = len(q_list)
            curr_i = st.session_state.current_q_index

            st.subheader(f"📌 {st.session_state.variant_name}")
            
            # --- ЕНТ Панель навигации по номерам (сетка 10 кнопок в ряд) ---
            st.write("**Навигация по вопросам:**")
            cols_per_row = 10
            for row_start in range(0, num_questions, cols_per_row):
                cols = st.columns(cols_per_row)
                for i in range(cols_per_row):
                    q_idx = row_start + i
                    if q_idx < num_questions:
                        is_answered = q_idx in st.session_state.user_answers
                        is_current = (q_idx == curr_i)
                        
                        # Формируем метку кнопки
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

            # --- Отображение текущего вопроса ---
            q_item = q_list[curr_i]
            options_dict = q_item['options']

            st.markdown(f"### Вопрос {curr_i + 1} из {num_questions}")
            st.markdown(f"**{q_item['question']}**")

            # Значение по умолчанию, если пользователь уже отвечал на этот вопрос
            previous_answer = st.session_state.user_answers.get(curr_i, None)
            
            selected_option = st.radio(
                "Выберите вариант ответа:",
                options=list(options_dict.keys()),
                format_func=lambda k: f"{k}) {options_dict[k]}",
                index=list(options_dict.keys()).index(previous_answer) if previous_answer in options_dict else None,
                key=f"radio_q_{curr_i}"
            )

            # Сохранение ответа в память
            if selected_option is not None:
                st.session_state.user_answers[curr_i] = selected_option

            st.markdown("---")

            # --- Нижная панель навигации ---
            col_prev, col_next, col_finish = st.columns([1, 1, 1])

            with col_prev:
                if curr_i > 0:
                    if st.button("⬅️ Предыдущий", use_container_width=True):
                        st.session_state.current_q_index -= 1
                        st.rerun()

            with col_next:
                if curr_i < num_questions - 1:
                    if st.button("Следующий ➡️", use_container_width=True):
                        st.session_state.current_q_index += 1
                        st.rerun()

            with col_finish:
                if st.button("🏁 Завершить тест", type="primary", use_container_width=True):
                    if len(st.session_state.user_answers) < num_questions:
                        st.warning(f"Вы ответили только на {len(st.session_state.user_answers)} из {num_questions} вопросов!")
                    st.session_state.test_submitted = True
                    st.rerun()

        # ЭКРАН 3: РЕЗУЛЬТАТЫ
        elif st.session_state.test_submitted:
            q_list = st.session_state.current_questions
            total = len(q_list)
            
            score = sum(
                1 for idx, item in enumerate(q_list)
                if st.session_state.user_answers.get(idx) == item['correctAnswer']
            )

            st.header("🎉 Результаты тестирования")
            st.subheader(f"Ваш результат: **{score} из {total}** ({round(score/total * 100, 1)}%)")

            if score / total >= 0.7:
                st.success("Отличный результат! Вы успешно сдали тест.")
            else:
                st.error("Есть ошибки. Рекомендуется повторить материал.")

            st.write("---")
            if st.button("🔄 Пройти другой вариант", type="primary"):
                start_new_test()
                st.rerun()

# ==========================================
# ВКЛАДКА 2: МОДУЛЬ АНТИПЛАГИАТА
# ==========================================
with tab_essay:
    st.header("Проверка эссе на оригинальность")
    st.write("Вставьте текст эссе для автоматической проверки по базе источников.")
    
    reference_corpus = [
        "In the middle of the 4th century, Huns reached the borders of the Roman Empire.",
        "The Kazakh Khanate was formed in 1465 by Kerey and Zhanibek.",
        "Kenesary Kasymov led the national liberation uprising from 1837 to 1847."
    ]
    
    essay_text = st.text_area("Введите текст эссе:", height=200)
    
    if st.button("Проверить уникальность"):
        if len(essay_text.strip()) < 30:
            st.warning("Текст эссе слишком короткий. Введите не менее 30 символов.")
        else:
            documents = [essay_text] + reference_corpus
            vectorizer = TfidfVectorizer().fit_transform(documents)
            vectors = vectorizer.toarray()
            
            similarity_scores = cosine_similarity([vectors[0]], vectors[1:])[0]
            max_similarity = similarity_scores.max() if len(similarity_scores) > 0 else 0.0
            
            uniqueness = round((1 - max_similarity) * 100, 1)
            
            st.subheader("Результат анализа:")
            st.metric(label="Процент уникальности", value=f"{uniqueness}%")
            
            if uniqueness < 70:
                st.error("⚠️ Обнаружен высокий процент заимствований. Эссе требует доработки.")
            else:
                st.success("✅ Эссе успешно прошло проверку на уникальность.")