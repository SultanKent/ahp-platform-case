import ahpy
import sys

# --- 1. Определение данных ---
# Пакет 'ahpy' использует словари {('a', 'b'): 5}, а не матрицы.
# Я уже преобразовал все наши матрицы в этот формат.
# Python сам вычислит дроби (1/2, 1/3 и т.д.)

try:
    # --- Матрица КРИТЕРИЕВ ---
    criteria_comparisons = {
        ('Удобство', 'Функционал'): 1/2, ('Удобство', 'Стоимость'): 3, ('Удобство', 'Поддержка'): 2,
        ('Функционал', 'Стоимость'): 5, ('Функционал', 'Поддержка'): 3,
        ('Стоимость', 'Поддержка'): 1/2
    }

    # --- Матрицы АЛЬТЕРНАТИВ ---
    # По 'Удобству'
    udobstvo_comps = {
        ('Platform A', 'Platform B'): 1/5, ('Platform A', 'Platform C'): 1/2,
        ('Platform B', 'Platform C'): 3
    }
    
    # По 'Функционалу'
    func_comps = {
        ('Platform A', 'Platform B'): 3, ('Platform A', 'Platform C'): 1/2,
        ('Platform B', 'Platform C'): 1/5
    }

    # По 'Стоимости'
    stoimost_comps = {
        ('Platform A', 'Platform B'): 1/5, ('Platform A', 'Platform C'): 3,
        ('Platform B', 'Platform C'): 7
    }

    # По 'Поддержке'
    podderzhka_comps = {
        ('Platform A', 'Platform B'): 3, ('Platform A', 'Platform C'): 1/3,
        ('Platform B', 'Platform C'): 1/5
    }

    # --- 2. Создание модели AHP ---

    # Создаем "листья" (матрицы альтернатив)
    udobstvo = ahpy.Compare('Удобство', udobstvo_comps)
    func = ahpy.Compare('Функционал', func_comps)
    stoimost = ahpy.Compare('Стоимость', stoimost_comps)
    podderzhka = ahpy.Compare('Поддержка', podderzhka_comps)

    # Создаем "корень" (матрицу критериев)
    criteria = ahpy.Compare('Критерии', criteria_comparisons)
    
    # Собираем иерархию: добавляем листья к корню
    criteria.add_children([udobstvo, func, stoimost, podderzhka])

    # --- 3. Вывод результатов ---

    print("\n--- ИТОГОВЫЙ РЕЙТИНГ АЛЬТЕРНАТИВ ---")
    # .target_weights - это итоговый результат
    # Выводим, округляя до 4 знаков
    for name, weight in criteria.target_weights.items():
        print(f"  {name}: {weight:.4f} ({(weight*100):.1f}%)")

    print("\n--- Веса Критериев ---")
    # .local_weights - веса на текущем уровне
    for name, weight in criteria.local_weights.items():
        print(f"  {name}: {weight:.4f} ({(weight*100):.1f}%)")
    
    print("\n--- Проверка согласованности (CR) ---")
    # .consistency_ratio - CR
    print(f"  Матрица 'Критерии': CR = {criteria.consistency_ratio:.4f}")
    print(f"  Матрица 'Удобство': CR = {udobstvo.consistency_ratio:.4f}")
    print(f"  Матрица 'Функционал': CR = {func.consistency_ratio:.4f}")
    print(f"  Матрица 'Стоимость': CR = {stoimost.consistency_ratio:.4f}")
    print(f"  Матрица 'Поддержка': CR = {podderzhka.consistency_ratio:.4f}")
    
    # ahpy сам проверяет согласованность
    if criteria.consistency_ratio > 0.1:
        print("\n(ВНИМАНИЕ: Согласованность матрицы 'Критерии' НИЗКАЯ!)")

except Exception as e:
    print(f"ОШИБКА: {e}")
    print("Проверь, правильно ли установлен 'ahpy'")