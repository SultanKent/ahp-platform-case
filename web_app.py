import streamlit as st
import ahpy
import pandas as pd
import itertools
import json
import time
import numpy as np 
import plotly.graph_objects as go 

# --- 1. Настройка страницы ---
st.set_page_config(layout="wide", page_title="AHP: Платформа для Коллаборации")
st.title("🚀 Level 7+6: Финальная AHP-Платформа")
st.write("Создавайте проекты, сохраняйте/загружайте сессии, получайте AI-анализ, экспортируйте опросники и загружайте ответы для группового решения.")

# --- 2. "Память" Streamlit (st.session_state) ---
if 'criteria_input' not in st.session_state:
    st.session_state.criteria_input = "Удобство\nФункционал\nСтоимость\nПоддержка"
if 'alternatives_input' not in st.session_state:
    st.session_state.alternatives_input = "Platform A\nPlatform B\nPlatform C"

# --- 3. Шкала Саати ---
saaty_scale_labels = [
    "B в 9 раз важнее", "B в 7 раз важнее", "B в 5 раз важнее", "B в 3 раза важнее",
    "Равная важность",
    "A в 3 раза важнее", "A в 5 раз важнее", "A в 7 раз важнее", "A в 9 раз важнее"
]
saaty_scale_values = {
    "B в 9 раз важнее": 1/9, "B в 7 раз важнее": 1/7, "B в 5 раз важнее": 1/5, "B в 3 раза важнее": 1/3,
    "Равная важность": 1,
    "A в 3 раза важнее": 3, "A в 5 раз важнее": 5, "A в 7 раз важнее": 7, "A в 9 раз важнее": 9
}

# --- 4. Хелпер-функции (ввода, слайдеров, загрузки/выгрузки) ---
def get_lists_from_state():
    criteria = [line.strip() for line in st.session_state.criteria_input.split('\n') if line.strip()]
    alternatives = [line.strip() for line in st.session_state.alternatives_input.split('\n') if line.strip()]
    if len(criteria) != len(set(criteria)) or len(alternatives) != len(set(alternatives)):
        st.error("Ошибка: В критериях или альтернативах есть дубликаты!")
        return None, None
    return criteria, alternatives

def create_comparison(key_prefix, item_a, item_b):
    session_key = f"{key_prefix}_{item_a}_{item_b}"
    if session_key not in st.session_state: st.session_state[session_key] = 1 
    current_val = st.session_state[session_key]
    default_label = min(saaty_scale_values.keys(), key=lambda k: abs(saaty_scale_values[k] - current_val))
    slider_label = f"**{item_a}** (A) vs **{item_b}** (B)"
    selected_label = st.select_slider(slider_label, options=saaty_scale_labels, value=default_label, key=f"slider_{session_key}")
    st.session_state[session_key] = saaty_scale_values[selected_label]

def get_session_data():
    """Собирает ВСЕ данные из session_state в один JSON"""
    return {k: v for k, v in st.session_state.items() if not k.startswith(('slider_', 'last_results'))}

def load_session_data(data):
    """Загружает данные из JSON в session_state"""
    try:
        # Очищаем память перед загрузкой, чтобы не было "хвостов"
        keys_to_clear = [k for k in st.session_state.keys()]
        for k in keys_to_clear:
            del st.session_state[k]
        
        # Загружаем новые данные
        for k, v in data.items():
            st.session_state[k] = v
        st.success("✅ Сессия успешно загружена! Все данные восстановлены.")
        time.sleep(1)
        st.rerun()
    except Exception as e:
        st.error(f"Ошибка чтения файла: {e}")

# --- 5. (Level 7a) Функция Агрегации ---
def aggregate_expert_data(expert_files):
    all_judgments = {}
    
    for file in expert_files:
        file.seek(0)
        data = json.load(file)
        for key, value in data.items():
            if '_' in key and not key.startswith('criteria_') and not key.startswith('alternatives_'):
                if key not in all_judgments: all_judgments[key] = []
                all_judgments[key].append(value)
    
    aggregated_data = {}
    for key, values in all_judgments.items():
        geo_mean = np.prod(values) ** (1/len(values))
        aggregated_data[key] = geo_mean
    
    expert_files[0].seek(0)
    base_data = json.load(expert_files[0])
    aggregated_data['criteria_input'] = base_data['criteria_input']
    aggregated_data['alternatives_input'] = base_data['alternatives_input']
    
    return aggregated_data

# --- 6. (Level 6b) Функция-СИМУЛЯТОР AI ---
def get_ai_analysis(final_weights, criteria_weights, cr_data):
    with st.spinner("🤖 AI-Аналитик изучает ваши данные..."):
        time.sleep(3) # Симуляция работы

    sorted_weights = sorted(final_weights.items(), key=lambda item: item[1], reverse=True)
    winner_name = sorted_weights[0][0]
    best_crit_name = max(criteria_weights, key=criteria_weights.get)

    recommendation = f"**Рекомендация:** Оптимальный выбор — **{winner_name}** (с весом {sorted_weights[0][1]:.1%}).\n\n"
    recommendation += f"**Обоснование:** Этот выбор обусловлен тем, что '{best_crit_name}' был выбран как самый важный критерий (вес {criteria_weights[best_crit_name]:.1%}). {winner_name} показывает сильные результаты по нему (или по совокупности других критериев)."
    
    inconsistent_matrices = [name for name, cr in cr_data.items() if cr > 0.1]
    
    if not inconsistent_matrices:
        consistency_report = "**Согласованность: Идеальная.**\n\nВсе Индексы Согласованности (CR) ниже 0.10. Это означает, что ваши суждения логичны и не противоречат друг другу. Результатам можно полностью доверять."
    else:
        consistency_report = f"**Согласованность: ⚠️ НИЗКАЯ!**\n\nРезультатам **нельзя доверять**. Обнаружены серьезные противоречия в следующих матрицах: **{', '.join(inconsistent_matrices)}**.\n\n"
        consistency_report += "**Пример:** Если CR 'Матрицы \"Стоимость\"' высокий, это значит, что вы, возможно, сказали 'A > B', 'B > C', но при этом 'C > A' при сравнении по стоимости. **Пожалуйста, пересмотрите свои оценки в этих матрицах.**"

    return recommendation, consistency_report

# --- 7. (Level 7b) Функция расчета AHP ---
def calculate_ahp(session_data):
    try:
        criteria = [line.strip() for line in session_data['criteria_input'].split('\n') if line.strip()]
        alternatives = [line.strip() for line in session_data['alternatives_input'].split('\n') if line.strip()]

        criteria_comps, children_comps = {}, {}
        for pair in itertools.combinations(criteria, 2):
            criteria_comps[pair] = session_data.get(f"crit_{pair[0]}_{pair[1]}", 1)
        
        for crit in criteria:
            temp_dict = {}
            for pair in itertools.combinations(alternatives, 2):
                temp_dict[pair] = session_data.get(f"{crit}_{pair[0]}_{pair[1]}", 1)
            children_comps[crit] = temp_dict

        children_nodes = [ahpy.Compare(name, comps, precision=4) for name, comps in children_comps.items()]
        root_node = ahpy.Compare("Goal", criteria_comps, precision=4)
        root_node.add_children(children_nodes)

        final_weights = root_node.target_weights
        criteria_weights = root_node.local_weights
        
        cr_data = {'Матрица "Goal" (Критерии)': root_node.consistency_ratio}
        for child in children_nodes:
            cr_data[f"Матрица '{child.name}'"] = child.consistency_ratio
        
        profiles = {}
        for alt in alternatives:
            profiles[alt] = []
            for child in children_nodes:
                profiles[alt].append(child.local_weights.get(alt, 0))
        
        return final_weights, criteria_weights, cr_data, profiles, criteria

    except Exception as e:
        st.error(f"Ошибка расчета: {e}")
        return None, None, None, None, None

# --- 8. (Level 7c) Функция для Радар-Графика ---
def create_radar_chart(profiles, criteria):
    fig = go.Figure()
    for alt, values in profiles.items():
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=criteria,
            fill='toself',
            name=alt
        ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title="Профиль Альтернатив по Критериям"
    )
    return fig

# --- 9. БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.header("1. Настройка Проекта")
    st.write("Введите критерии и альтернативы. Каждый с новой строки.")
    st.text_area("Критерии", key="criteria_input", height=150)
    st.text_area("Альтернативы", key="alternatives_input", height=100)
    
    st.divider()
    st.header("2. Управление Сессией (L6)")
    
    # (Level 6a) Сохранение
    export_data = get_session_data()
    st.download_button(
        label="💾 Скачать Сессию (.json)",
        data=json.dumps(export_data, indent=2),
        file_name="ahp_project_session.json",
        mime="application/json"
    )
    
    # (Level 6a) Загрузка
    uploaded_file = st.file_uploader("Загрузить Сессию (.json)", type="json")
    if uploaded_file:
        load_session_data(json.load(uploaded_file))

# --- 10. СОЗДАНИЕ ВКЛАДОК ---
tab1, tab2, tab3, tab4 = st.tabs([
    "✍️ Ввод Оценок (Эксперт)", 
    "🤝 Групповой Анализ (L7)", 
    "📊 Результаты и Аналитика (L6/7)", 
    "📖 О Методе"
])

# --- ВКЛАДКА 1: ВВОД ОЦЕНОК ---
with tab1:
    st.header("Ввод Оценок (Единичный Эксперт)")
    st.write("Используйте слайдеры для ввода оценок. Вы можете сохранить эту сессию (в боковой панели) как 'бюллетень' и отправить его администратору.")
    
    criteria_list, alternatives_list = get_lists_from_state()
    if criteria_list and alternatives_list:
        st.subheader("Сравнение Критериев")
        with st.expander("Важность критериев", expanded=True):
            if len(criteria_list) >= 2:
                for pair in itertools.combinations(criteria_list, 2): create_comparison("crit", pair[0], pair[1])
            else: st.info("У вас только один критерий.")

        st.subheader("Сравнение Альтернатив")
        if len(alternatives_list) >= 2:
            for criterion in criteria_list:
                with st.expander(f"Сравнение по '{criterion}'"):
                    for pair in itertools.combinations(alternatives_list, 2): create_comparison(criterion, pair[0], pair[1])
        else: st.info("У вас только одна альтернатива.")

# --- ВКЛАДКА 2: ГРУППОВОЙ АНАЛИЗ ---
with tab2:
    st.header("Агрегация Групповых Решений")
    st.write("Загрузите несколько 'бюллетеней' (.json), заполненных разными экспертами. Система автоматически рассчитает средний (агрегированный) результат.")
    
    expert_files = st.file_uploader(
        "Загрузите 'бюллетени' (.json) от ваших экспертов", 
        type="json", 
        accept_multiple_files=True
    )
    
    if expert_files:
        st.write(f"Загружено файлов от {len(expert_files)} экспертов.")
        if st.button("🚀 Рассчитать Групповой Результат"):
            aggregated_data = aggregate_expert_data(expert_files)
            st.session_state.last_calc_is_group = True
            results = calculate_ahp(aggregated_data)
            st.session_state.last_results = results
            st.success("✅ Групповой результат рассчитан! Перейдите во вкладку 'Результаты'.")
            st.balloons()

# --- ВКЛАДКА 3: РЕЗУЛЬТАТЫ ---
with tab3:
    st.header("Итоговые Результаты и Аналитика")
    
    st.write("Нажмите кнопку, чтобы рассчитать результат на основе данных из вкладки 'Ввод Оценок'.")
    if st.button("🚀 Рассчитать Единичный Результат"):
        session_data = get_session_data()
        st.session_state.last_calc_is_group = False
        results = calculate_ahp(session_data)
        st.session_state.last_results = results
        st.success("✅ Единичный результат рассчитан!")

    st.divider()

    # --- Зона отображения (показывает последние рассчитанные данные) ---
    if 'last_results' in st.session_state and st.session_state.last_results[0] is not None:
        
        final_w, criteria_w, cr_data, profiles, criteria_names = st.session_state.last_results
        
        if st.session_state.get('last_calc_is_group', False):
            st.subheader("Показан 🤝 Групповой Результат (агрегированный)")
        else:
            st.subheader("Показан ✍️ Единичный Результат")

        col1, col2, col3 = st.columns(3)
        sorted_weights = sorted(final_w.items(), key=lambda item: item[1], reverse=True)
        if len(sorted_weights) > 0: col1.metric(label=f"🥇 1-е Место", value=sorted_weights[0][0], delta=f"{sorted_weights[0][1]:.2%}")
        if len(sorted_weights) > 1: col2.metric(label=f"🥈 2-е Место", value=sorted_weights[1][0], delta=f"{sorted_weights[1][1]:.2%}")
        if len(sorted_weights) > 2: col3.metric(label=f"🥉 3-е Место", value=sorted_weights[2][0], delta=f"{sorted_weights[2][1]:.2%}")

        st.divider()
        st.subheader("Продвинутая Визуализация (L7)")
        
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.write("Итоговый Рейтинг")
            df_final = pd.DataFrame.from_dict(final_w, orient='index', columns=['Вес'])
            st.bar_chart(df_final.sort_values(by='Вес', ascending=False))

        with col_chart2:
            st.write("Профили Альтернатив")
            if profiles and criteria_names:
                fig = create_radar_chart(profiles, criteria_names)
                st.plotly_chart(fig, use_container_width=True)
            
        st.divider()
        st.subheader("Детальные таблицы")
        
        col_table1, col_table2 = st.columns(2)
        with col_table1:
            st.write("Важность Критериев")
            criteria_df = pd.DataFrame.from_dict(criteria_w, orient='index', columns=['Вес'])
            st.dataframe(criteria_df.sort_values(by='Вес', ascending=False).style.format({'Вес': '{:.2%}'}), use_container_width=True)
        
        with col_table2:
            st.write("Проверка Согласованности (CR)")
            cr_df = pd.DataFrame.from_dict(cr_data, orient='index', columns=['CR'])
            def color_cr(val): return f'background-color: {"#ffc7ce" if val > 0.1 else "#c7ffce"}'
            st.dataframe(cr_df.style.applymap(color_cr).format({'CR': '{:.4f}'}), use_container_width=True)
        
        st.divider()
        
        # --- (Level 6b) Кнопка AI-Анализа ---
        st.subheader("AI-Аналитик (L6)")
        if st.button("🤖 Попросить ИИ проанализировать результат"):
            rec, cons = get_ai_analysis(final_w, criteria_w, cr_data)
            st.info(f"**AI-Вывод по Рекомендации:**\n\n{rec}")
            if any(cr > 0.1 for cr in cr_data.values()):
                st.error(f"**AI-Вывод по Согласованности:**\n\n{cons}")
            else:
                st.success(f"**AI-Вывод по Согласованности:**\n\n{cons}")
            
    else:
        st.info("Нажмите одну из кнопок 'Рассчитать...' (в этой вкладке или во вкладке 'Групповой Анализ'), чтобы увидеть результаты.")

# --- ВКЛАДКА 4: О МЕТОДЕ ---
with tab4:
    st.header("📖 О Методе (AHP)")
    st.markdown("""
    **Метод Анализа Иерархий (AHP)** — это техника для принятия сложных решений, разработанная Томасом Саати в 1970-х годах. 
    Он помогает структурировать проблему в виде иерархии (Цель -> Критерии -> Альтернативы) и использовать математику для поиска лучшего варианта на основе субъективных суждений экспертов.
    
    ### Как это работает?
    1.  **Попарное Сравнение:** Вместо того чтобы ранжировать 10 критериев, вы сравниваете их попарно ("Что важнее: Цена или Качество?"). Это гораздо проще для человеческого мозга.
    2.  **Шкала Саати:** Для сравнения используется шкала от 1 (равная важность) до 9 (абсолютное превосходство).
    3.  **Расчет Весов:** На основе этих парных сравнений математически вычисляются "веса" (приоритеты).
    
    ### (Level 7) Групповые Решения
    Этот инструмент использует **Метод Агрегирования Индивидуальных Суждений (Aggregation of Individual Judgements, AIJ)**. 
    1.  Каждый эксперт заполняет свой "бюллетень".
    2.  Система собирает все ответы (например, на `Цена vs Качество` эксперт 1 дал `3`, эксперт 2 дал `5`).
    3.  Рассчитывается **геометрическое среднее** (`(3 * 5) ^ (1/2) = 3.87`).
    4.  Итоговый расчет AHP проводится на этой "усредненной" матрице.
    
    ### Что такое Индекс Согласованности (CR)?
    Это **самая важная** метрика. Она показывает, не противоречил ли эксперт (или группа) сам себе.
    * **CR < 0.1 (или 10%)**: Отлично. Суждения логичны.
    * **CR > 0.1 (или 10%)**: Плохо. Суждения противоречивы, результатам доверять нельзя.
    """)
    
