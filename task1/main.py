import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict

def create_logistics_network():
    # Створюємо орієнтований граф
    G = nx.DiGraph()
    
    # Додаємо вершини - термінали, склади та магазини
    terminals = ["Термінал 1", "Термінал 2"]
    warehouses = ["Склад 1", "Склад 2", "Склад 3", "Склад 4"]
    stores = [f"Магазин {i}" for i in range(1, 15)]
    
    # Додаємо всі вершини у граф
    G.add_nodes_from(terminals)
    G.add_nodes_from(warehouses)
    G.add_nodes_from(stores)
    
    # Додаємо ребра від терміналів до складів з відповідними пропускними здатностями
    terminal_to_warehouse = [
        ("Термінал 1", "Склад 1", 25),
        ("Термінал 1", "Склад 2", 20),
        ("Термінал 1", "Склад 3", 15),
        ("Термінал 2", "Склад 3", 15),
        ("Термінал 2", "Склад 4", 30),
        ("Термінал 2", "Склад 2", 10)
    ]
    
    # Додаємо ребра від складів до магазинів з відповідними пропускними здатностями
    warehouse_to_store = [
        ("Склад 1", "Магазин 1", 15),
        ("Склад 1", "Магазин 2", 10),
        ("Склад 1", "Магазин 3", 20),
        ("Склад 2", "Магазин 4", 15),
        ("Склад 2", "Магазин 5", 10),
        ("Склад 2", "Магазин 6", 25),
        ("Склад 3", "Магазин 7", 20),
        ("Склад 3", "Магазин 8", 15),
        ("Склад 3", "Магазин 9", 10),
        ("Склад 4", "Магазин 10", 20),
        ("Склад 4", "Магазин 11", 10),
        ("Склад 4", "Магазин 12", 15),
        ("Склад 4", "Магазин 13", 5),
        ("Склад 4", "Магазин 14", 10)
    ]
    
    # Додаємо всі ребра у граф
    for u, v, capacity in terminal_to_warehouse:
        G.add_edge(u, v, capacity=capacity)
    
    for u, v, capacity in warehouse_to_store:
        G.add_edge(u, v, capacity=capacity)
    
    return G, terminals, warehouses, stores

def calculate_max_flow(G, terminals, stores):
    # Створюємо суперджерело та суперсток
    G.add_node("source")
    G.add_node("sink")
    
    # Додаємо ребра від суперджерела до всіх терміналів з нескінченною пропускною здатністю
    for terminal in terminals:
        G.add_edge("source", terminal, capacity=float('inf'))
    
    # Додаємо ребра від всіх магазинів до суперстоку з нескінченною пропускною здатністю
    for store in stores:
        G.add_edge(store, "sink", capacity=float('inf'))
    
    # Застосовуємо алгоритм Едмондса-Карпа для знаходження максимального потоку
    flow_value, flow_dict = nx.maximum_flow(G, "source", "sink", flow_func=nx.algorithms.flow.edmonds_karp)
    
    return flow_value, flow_dict

def analyze_flow(flow_dict, terminals, warehouses, stores):
    # Таблиця фактичних потоків від терміналів до магазинів
    terminal_to_store_flow = defaultdict(float)
    
    # Для кожного терміналу визначаємо, скільки товарів іде до кожного складу
    terminal_to_warehouse_flow = defaultdict(float)
    for terminal in terminals:
        for warehouse, flow in flow_dict[terminal].items():
            if warehouse != "source" and flow > 0:
                terminal_to_warehouse_flow[(terminal, warehouse)] = flow
    
    # Для кожного складу визначаємо, скільки товарів іде до кожного магазину
    warehouse_to_store_flow = defaultdict(float)
    for warehouse in warehouses:
        for store, flow in flow_dict[warehouse].items():
            if store in stores and flow > 0:
                warehouse_to_store_flow[(warehouse, store)] = flow
    
    # Обчислюємо потоки від терміналів до магазинів
    # Для кожного магазину з'ясовуємо, скільки товарів він отримує і від яких терміналів
    for terminal in terminals:
        for warehouse in warehouses:
            terminal_warehouse_flow = terminal_to_warehouse_flow.get((terminal, warehouse), 0)
            if terminal_warehouse_flow > 0:
                for store in stores:
                    warehouse_store_flow = warehouse_to_store_flow.get((warehouse, store), 0)
                    # Пропорційно розподіляємо потік від терміналу через склад до магазину
                    if warehouse_store_flow > 0:
                        total_outflow = sum(flow_dict[warehouse][s] for s in stores if s in flow_dict[warehouse])
                        if total_outflow > 0:
                            proportion = warehouse_store_flow / total_outflow
                            terminal_to_store_flow[(terminal, store)] += terminal_warehouse_flow * proportion
    
    return terminal_to_store_flow, terminal_to_warehouse_flow, warehouse_to_store_flow

def main():
    # Створюємо логістичну мережу
    G, terminals, warehouses, stores = create_logistics_network()
    
    # Обчислюємо максимальний потік
    flow_value, flow_dict = calculate_max_flow(G, terminals, stores)
    
    # Аналізуємо отримані результати
    terminal_to_store_flow, terminal_to_warehouse_flow, warehouse_to_store_flow = analyze_flow(flow_dict, terminals, warehouses, stores)
    
    # Виводимо таблицю результатів
    print("Результати потоків між терміналами та магазинами:")
    print("-" * 60)
    print(f"{'Термінал':<15} {'Магазин':<15} {'Фактичний Потік (одиниць)':>25}")
    print("-" * 60)
    
    # Сортуємо результати для красивого виводу
    sorted_results = sorted(terminal_to_store_flow.items(), key=lambda x: (x[0][0], int(x[0][1].split()[-1])))
    
    for (terminal, store), flow in sorted_results:
        print(f"{terminal:<15} {store:<15} {flow:>25.2f}")
    
    print("-" * 60)
    print(f"Загальний максимальний потік: {flow_value:.2f} одиниць")
    print()
    
    # Аналіз отриманих результатів
    print("Аналіз результатів:")
    
    # 1. Визначаємо, які термінали забезпечують найбільший потік
    terminal_total_flow = {}
    for terminal in terminals:
        terminal_total_flow[terminal] = sum(flow for (term, _), flow in terminal_to_store_flow.items() if term == terminal)
    
    max_terminal = max(terminal_total_flow.items(), key=lambda x: x[1])
    print(f"1. Термінал з найбільшим потоком товарів: {max_terminal[0]} ({max_terminal[1]:.2f} одиниць)")
    
    # 2. Визначаємо маршрути з найменшою пропускною здатністю
    min_capacity_paths = []
    for u, v, data in G.edges(data=True):
        if 'capacity' in data and data['capacity'] < float('inf') and data['capacity'] <= 10:  # Вибираємо ребра з малою пропускною здатністю
            min_capacity_paths.append((u, v, data['capacity']))
    
    min_capacity_paths.sort(key=lambda x: x[2])
    print("2. Маршрути з найменшою пропускною здатністю:")
    for u, v, capacity in min_capacity_paths[:3]:  # Виводимо 3 найгірші
        print(f"   {u} -> {v}: {capacity} одиниць")
    
    # 3. Визначаємо магазини з найменшим потоком
    store_total_flow = {}
    for store in stores:
        store_total_flow[store] = sum(flow for (_, st), flow in terminal_to_store_flow.items() if st == store)
    
    min_stores = sorted(store_total_flow.items(), key=lambda x: x[1])[:3]
    print("3. Магазини з найменшим отриманим потоком:")
    for store, flow in min_stores:
        print(f"   {store}: {flow:.2f} одиниць")
    
    # 4. Визначаємо вузькі місця мережі
    bottlenecks = []
    for u, v, data in G.edges(data=True):
        if 'capacity' in data and data['capacity'] < float('inf'):
            flow = flow_dict[u][v]
            if flow == data['capacity'] and data['capacity'] < 20:  # Вибираємо насичені ребра з малою пропускною здатністю
                bottlenecks.append((u, v, data['capacity']))
    
    print("4. Вузькі місця логістичної мережі (насичені ребра з малою пропускною здатністю):")
    for u, v, capacity in bottlenecks:
        print(f"   {u} -> {v}: пропускна здатність {capacity} одиниць (100% використання)")
    
    print()
    print("Рекомендації для покращення ефективності:")
    for u, v, capacity in bottlenecks[:3]:  # Надаємо рекомендації для найгірших вузьких місць
        print(f"   Збільшіть пропускну здатність маршруту {u} -> {v} з {capacity} до {capacity * 1.5:.1f} одиниць")

if __name__ == "__main__":
    main()