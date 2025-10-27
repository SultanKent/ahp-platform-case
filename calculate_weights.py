import numpy as np

def calculate_ahp_matrix(matrix):
    """
    Рассчитывает веса (главный собственный вектор) и 
    индекс согласованности для матрицы парных сравнений.
    """
    
    # 1. Преобразуем матрицу в numpy array
    A = np.array(matrix)
    n = A.shape[0]

    # 2. Расчет собственных значений и векторов
    eigenvalues, eigenvectors = np.linalg.eig(A)

    # 3. Находим максимальное собственное значение (lambda_max)
    lambda_max = np.max(eigenvalues)
    
    # 4. Находим главный собственный вектор (соответствует lambda_max)
    #    и нормализуем его, чтобы получить веса
    index = np.argmax(eigenvalues)
    principal_eigenvector = eigenvectors[:, index]
    
    # Нормализация (сумма весов должна быть = 1)
    weights = principal_eigenvector / np.sum(principal_eigenvector)
    
    # Отбрасываем мнимую часть (она возникает из-за неточностей вычислений)
    weights = np.real(weights)
    lambda_max = np.real(lambda_max)

    # 5. Расчет Индекса Согласованности (CI)
    CI = (lambda_max - n) / (n - 1)

    # 6. Расчет Отношения Согласованности (CR)
    #    Используем таблицу Случайных Индексов (RI) Саати
    #    RI для n = 1, 2, 3, 4, 5, 6...
    RI_table = {
        1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
        6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49
    }
    
    RI = RI_table.get(n, 1.49) # Берем 1.49 для n > 10
    
    if RI == 0:
        CR = 0 # Для n=1, 2 согласованность всегда идеальна
    else:
        CR = CI / RI

    return weights, CI, CR

# --- Запуск анализа ---

# Матрица парных сравнений КРИТЕРИЕВ (Шаг 2.1)
# (Удобство, Функционал, Стоимость, Поддержка)
criteria_matrix = [
    [1, 1/2, 3, 2],
    [2, 1, 5, 3],
    [1/3, 1/5, 1, 1/2],
    [1/2, 1/3, 2, 1]
]

print("--- Анализ матрицы КРИТЕРИЕВ на Python (numpy) ---")
weights, CI, CR = calculate_ahp_matrix(criteria_matrix)

print(f"Размер матрицы (n): {len(criteria_matrix)}")
print(f"Веса критериев:")
print(f"  Удобство:   {weights[0]:.4f} ({(weights[0]*100):.1f}%)")
print(f"  Функционал: {weights[1]:.4f} ({(weights[1]*100):.1f}%)")
print(f"  Стоимость:  {weights[2]:.4f} ({(weights[2]*100):.1f}%)")
print(f"  Поддержка:  {weights[3]:.4f} ({(weights[3]*100):.1f}%)")
print("-" * 20)
print(f"Индекс Согласованности (CI): {CI:.4f}")
print(f"Отношение Согласованности (CR): {CR:.4f}")

# Проверка согласованности
if CR < 0.10:
    print("-> Согласованность приемлемая (CR < 10%).")
else:
    print("-> Согласованность НИЗКАЯ (CR >= 10%). Экспертам нужно пересмотреть оценки.")