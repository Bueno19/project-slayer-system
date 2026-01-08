import json
import random

def gerar_daily_quest(rank):
    """Gera a Missão Diária do Sistema (Balanceada)"""
    
    # Multiplicador de Dificuldade
    mult = 1
    if rank == 'Rank E': mult = 0.15  # 15% da dificuldade original (Iniciante)
    elif rank == 'Rank D': mult = 0.30
    elif rank == 'Rank C': mult = 0.60
    elif rank == 'Rank B': mult = 1.0  # Nível Jin-Woo Episódio 1
    elif rank == 'Rank A': mult = 2.0
    elif rank == 'Rank S': mult = 5.0

    # Base: 100 (Original do anime)
    base_reps = 100
    base_km = 10

    tasks = {
        "Flexões": [0, int(base_reps * mult)],
        "Abdominais": [0, int(base_reps * mult)],
        "Agachamentos": [0, int(base_reps * mult)],
        "Corrida (km)": [0, max(1, int(base_km * mult))] # Mínimo 1km
    }
    
    # XP e Gold baseados no esforço
    xp = int(200 * mult) + 20
    gold = int(1000 * mult) + 100
    
    return {
        "titulo": "PREPARAÇÃO FÍSICA DO JOGADOR",
        "tasks_json": json.dumps(tasks),
        "xp": xp,
        "gold": gold,
        "rank": rank
    }