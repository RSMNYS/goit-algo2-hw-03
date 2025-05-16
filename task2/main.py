from BTrees.OOBTree import OOBTree
import csv
import timeit
from functools import partial
import time

def load_items_from_csv(filename):
    """Завантажує дані про товари з CSV файлу."""
    items = []
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Конвертуємо ціну в float
                row['Price'] = float(row['Price'])
                items.append(row)
        return items
    except FileNotFoundError:
        print(f"Файл {filename} не знайдено. Створюю тестові дані.")
        # Якщо файл не знайдено, створюємо тестові дані
        return create_test_data()

def create_test_data():
    """Створює тестові дані, якщо файл не знайдено."""
    items = []
    categories = ["Electronics", "Clothes", "Food", "Books", "Toys"]
    
    for i in range(1, 1001):  # Створюємо 1000 тестових товарів
        item = {
            "ID": i,
            "Name": f"Item {i}",
            "Category": categories[i % len(categories)],
            "Price": round(10 + (i % 100) * 1.5, 2)  # Ціни від 10 до 160
        }
        items.append(item)
    
    return items

def add_item_to_tree(tree, item):
    """Додає товар до структури OOBTree."""
    tree[int(item['ID'])] = item

def add_item_to_dict(dictionary, item):
    """Додає товар до стандартного словника."""
    dictionary[int(item['ID'])] = item

def range_query_tree(tree, min_price, max_price):
    """Виконує діапазонний запит для структури OOBTree."""
    results = []
    
    # Оскільки OOBTree індексований за ID, а не за ціною,
    # нам потрібно ітеруватися через усі елементи та перевіряти ціну
    for _, item in tree.items():
        if min_price <= item['Price'] <= max_price:
            results.append(item)
    
    return results

def range_query_dict(dictionary, min_price, max_price):
    """Виконує діапазонний запит для стандартного словника."""
    results = []
    
    # Ітеруємося через усі значення словника та перевіряємо ціну
    for item in dictionary.values():
        if min_price <= item['Price'] <= max_price:
            results.append(item)
    
    return results

def main():
    # Завантажуємо дані про товари
    items = load_items_from_csv("generated_items_data.csv")
    print(f"Завантажено {len(items)} товарів.")
    
    # Ініціалізуємо структури даних
    tree = OOBTree()
    dictionary = {}
    
    # Додаємо товари до обох структур
    for item in items:
        add_item_to_tree(tree, item)
        add_item_to_dict(dictionary, item)
    
    print(f"Додано {len(tree)} товарів до OOBTree.")
    print(f"Додано {len(dictionary)} товарів до Dict.")
    
    # Визначаємо діапазон цін для запиту
    min_price = 50.0
    max_price = 70.0
    
    # Перевіряємо, чи обидві структури повертають однакові результати
    tree_results = range_query_tree(tree, min_price, max_price)
    dict_results = range_query_dict(dictionary, min_price, max_price)
    
    print(f"Кількість товарів у діапазоні цін {min_price}-{max_price}:")
    print(f"OOBTree: {len(tree_results)} товарів")
    print(f"Dict: {len(dict_results)} товарів")
    
    # Вимірюємо час виконання діапазонного запиту для OOBTree
    tree_query = partial(range_query_tree, tree, min_price, max_price)
    tree_time = timeit.timeit(tree_query, number=100)
    
    # Вимірюємо час виконання діапазонного запиту для Dict
    dict_query = partial(range_query_dict, dictionary, min_price, max_price)
    dict_time = timeit.timeit(dict_query, number=100)
    
    # Виводимо результати
    print("\nРезультати вимірювання часу виконання:")
    print(f"Total range_query time for OOBTree: {tree_time:.6f} seconds")
    print(f"Total range_query time for Dict: {dict_time:.6f} seconds")
    
    # Порівнюємо результати
    ratio = dict_time / tree_time if tree_time > 0 else float('inf')
    print(f"\nСловник Dict повільніший за OOBTree у {ratio:.2f} разів.")
    
    if tree_time < dict_time:
        print("OOBTree показує кращу продуктивність для діапазонних запитів, як і очікувалося.")
    else:
        print("Несподівано, Dict показав кращу продуктивність для діапазонних запитів.")
    
    # Аналізуємо, чому OOBTree може бути ефективнішим
    print("\nАналіз ефективності:")
    print("OOBTree має наступні переваги для діапазонних запитів:")
    print("1. Дані зберігаються в відсортованому вигляді (B-дерево)")
    print("2. Ефективний пошук у великих наборах даних")
    print("3. Оптимізована структура для операцій з діапазонами")
    print("\nОднак, у нашому випадку діапазонний запит реалізований за ціною, а індексація - за ID,")
    print("тому перевага OOBTree менш виражена, ніж могла б бути з індексацією за ціною.")

if __name__ == "__main__":
    main()