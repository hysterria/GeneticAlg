import tkinter as tk
from tkinter import ttk
import numpy as np
import random


# Определение целевой функции
def target_function(x, y):
    return (x - 2) ** 4 + (x - 2 * y) ** 2


# Функция для инициализации популяции
def initialize_population(chromosome_count, gene_min, gene_max, encoding):
    if encoding == "Integer":
        return np.random.randint(gene_min, gene_max, (chromosome_count, 2))
    else:
        return np.random.uniform(gene_min, gene_max, (chromosome_count, 2))


# Функция для оценки приспособленности (fitness)
def evaluate_population(population):
    return np.array([target_function(ind[0], ind[1]) for ind in population])


# Функция для выбора родителей - рулетка
def roulette_wheel_selection(population, fitness):
    total_fitness = np.sum(fitness)
    selection_probs = fitness / total_fitness
    selected_idx = np.random.choice(len(population), p=selection_probs)
    return population[selected_idx]


# Функция для выбора родителей - турнир
def tournament_selection(population, fitness, tournament_size=3):
    selected = random.sample(range(len(population)), tournament_size)
    best = min(selected, key=lambda idx: fitness[idx])
    return population[best]


# Кроссовер
def crossover(parent1, parent2, encoding):
    if encoding == "Integer":
        point = np.random.randint(1, 2)
        child = np.concatenate((parent1[:point], parent2[point:]))
        return child.astype(int)
    else:
        alpha = np.random.rand()
        child = alpha * parent1 + (1 - alpha) * parent2
        return child


# Мутация
def mutate(chromosome, mutation_rate, gene_min, gene_max, encoding):
    if np.random.rand() < mutation_rate:
        gene_idx = np.random.randint(2)
        if encoding == "Integer":
            chromosome[gene_idx] = np.random.randint(gene_min, gene_max)
        else:
            chromosome[gene_idx] = np.random.uniform(gene_min, gene_max)
    return chromosome


# Основной генетический алгоритм с обновлением таблицы
def genetic_algorithm(chromosome_count, gene_min, gene_max, generations, mutation_rate, encoding, selection_method,
                      tree):
    population = initialize_population(chromosome_count, gene_min, gene_max, encoding)
    best_solution = None
    best_fitness = float('inf')

    # Очистка таблицы перед началом
    for item in tree.get_children():
        tree.delete(item)

    for generation in range(generations):
        fitness = evaluate_population(population)

        # Находим лучшее решение в текущем поколении
        if fitness.min() < best_fitness:
            best_fitness = fitness.min()
            best_solution = population[fitness.argmin()]

        # Обновление таблицы
        for idx, (ind, fit) in enumerate(zip(population, fitness)):
            tree.insert("", "end", values=(idx + 1, fit, ind[0], ind[1]))

        new_population = []

        for _ in range(chromosome_count):
            # Выбор родителей
            if selection_method == "Roulette":
                parent1 = roulette_wheel_selection(population, fitness)
                parent2 = roulette_wheel_selection(population, fitness)
            else:
                parent1 = tournament_selection(population, fitness)
                parent2 = tournament_selection(population, fitness)

            # Кроссовер
            child = crossover(parent1, parent2, encoding)

            # Мутация
            child = mutate(child, mutation_rate, gene_min, gene_max, encoding)

            new_population.append(child)

        population = np.array(new_population)

    return best_solution, best_fitness


# Интерфейс tkinter
def run_algorithm():
    chromosome_count = int(entry_chromosomes.get())
    gene_min = int(entry_min_gene.get())
    gene_max = int(entry_max_gene.get())
    generations = int(entry_generations.get())
    mutation_rate = float(entry_mutation.get()) / 100
    encoding = encoding_var.get()
    selection_method = selection_var.get()

    best_solution, best_fitness = genetic_algorithm(
        chromosome_count, gene_min, gene_max, generations, mutation_rate, encoding, selection_method, tree
    )

    result_text.set(f"Лучшее решение: x = {best_solution[0]}, y = {best_solution[1]}\nЗначение функции: {best_fitness}")


# Создание окна интерфейса
root = tk.Tk()
root.title("Генетический алгоритм")

# Параметры
tk.Label(root, text="Количество хромосом:").grid(row=0, column=0)
entry_chromosomes = tk.Entry(root)
entry_chromosomes.grid(row=0, column=1)
entry_chromosomes.insert(0, "50")

tk.Label(root, text="Минимальное значение гена:").grid(row=1, column=0)
entry_min_gene = tk.Entry(root)
entry_min_gene.grid(row=1, column=1)
entry_min_gene.insert(0, "-50")

tk.Label(root, text="Максимальное значение гена:").grid(row=2, column=0)
entry_max_gene = tk.Entry(root)
entry_max_gene.grid(row=2, column=1)
entry_max_gene.insert(0, "50")

tk.Label(root, text="Количество поколений:").grid(row=3, column=0)
entry_generations = tk.Entry(root)
entry_generations.grid(row=3, column=1)
entry_generations.insert(0, "100")

tk.Label(root, text="Вероятность мутации (%):").grid(row=4, column=0)
entry_mutation = tk.Entry(root)
entry_mutation.grid(row=4, column=1)
entry_mutation.insert(0, "20")

# Выбор кодировки
tk.Label(root, text="Кодировка генов:").grid(row=5, column=0)
encoding_var = tk.StringVar(value="Integer")
tk.OptionMenu(root, encoding_var, "Integer", "Float").grid(row=5, column=1)

# Выбор метода выбора родителей
tk.Label(root, text="Метод выбора родителей:").grid(row=6, column=0)
selection_var = tk.StringVar(value="Roulette")
tk.OptionMenu(root, selection_var, "Roulette", "Tournament").grid(row=6, column=1)

# Кнопка запуска алгоритма
tk.Button(root, text="Рассчитать", command=run_algorithm).grid(row=7, column=0, columnspan=2)

# Таблица для отображения поколения
columns = ("Номер", "Результат", "Ген 1", "Ген 2")
tree = ttk.Treeview(root, columns=columns, show="headings")
tree.heading("Номер", text="Номер")
tree.heading("Результат", text="Результат")
tree.heading("Ген 1", text="Ген 1")
tree.heading("Ген 2", text="Ген 2")
tree.grid(row=8, column=0, columnspan=2)

# Поле для вывода результатов
result_text = tk.StringVar()
tk.Label(root, textvariable=result_text).grid(row=9, column=0, columnspan=2)

root.mainloop()


