from flask import Flask, render_template, request, jsonify
from models import app, db, User, ShopItem, Inventory, Quest, DailyShop, Title
import quest_system
import json
import random
from datetime import date
import requests
import os

# CONFIGURAÇÃO DO TOKEN
# Tenta pegar do ambiente (Render), senão usa o teu fixo
TOKEN_SECRETO = "7948877311:AAE-tFj9XAD2xyB77V3LOMv4hEHPOxpoux8"
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", TOKEN_SECRETO)

def notificar(chat_id, msg):
    try: requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
    except: pass

def get_daily_shop():
    hoje = date.today()
    # Tenta pegar a loja de hoje
    try:
        shop = DailyShop.query.filter_by(date=hoje).first()
    except:
        return [] # Se der erro no banco, retorna vazio

    if shop:
        ids = json.loads(shop.items_json)
        return ShopItem.query.filter(ShopItem.id.in_(ids)).all()
    else:
        all_items = ShopItem.query.all()
        if not all_items: return []
        selection = random.sample(all_items, k=min(len(all_items), 6))
        ids = [i.id for i in selection]
        
        # Limpa dias velhos e salva o novo
        DailyShop.query.filter(DailyShop.date != hoje).delete()
        new_shop = DailyShop(date=hoje, items_json=json.dumps(ids))
        
        db.session.add(new_shop)
        db.session.commit()
        return selection

@app.route('/')
def dashboard():
    user = User.query.first()
    if not user: return "<h1>Sistema Online! Inicie o bot no Telegram: /start</h1>"
    
    equipped = {
        'head': db.session.get(ShopItem, user.head_slot) if user.head_slot else None,
        'body': db.session.get(ShopItem, user.body_slot) if user.body_slot else None,
        'legs': db.session.get(ShopItem, user.legs_slot) if user.legs_slot else None,
        'weapon': db.session.get(ShopItem, user.weapon_slot) if user.weapon_slot else None,
    }
    
    quests = []
    for q in Quest.query.filter_by(concluida=False).all():
        q.tasks = json.loads(q.tasks_json)
        quests.append(q)

    loja_dia = get_daily_shop()
    inv = Inventory.query.filter_by(user_id=user.id).all()
    xp_pct = min(100, int((user.xp_atual / user.xp_next_level) * 100)) if user.xp_next_level > 0 else 0
    
    return render_template('index.html', player=user, equipped=equipped, quests=quests, 
                           loja=loja_dia, inventario=inv, xp_pct=xp_pct, titulos=user.titulos)

# --- ROTAS DA API ---
@app.route('/api/create_quest', methods=['POST'])
def create_quest_api():
    user = User.query.first()
    dados = quest_system.gerar_daily_quest(user.rank)
    nova = Quest(titulo=dados['titulo'], tasks_json=dados['tasks_json'], 
                 xp_reward=dados['xp'], gold_reward=dados['gold'], dificuldade=dados['rank'])
    db.session.add(nova)
    db.session.commit()
    notificar(user.telegram_id, f"⚠️ **NOVA MISSÃO**\nVerifique o Painel.")
    return jsonify({'success': True})

@app.route('/api/update_task', methods=['POST'])
def update_task():
    d = request.json
    q = db.session.get(Quest, d['quest_id'])
    tasks = json.loads(q.tasks_json)
    if d['task_name'] in tasks:
        tasks[d['task_name']][0] = int(d['val'])
        q.tasks_json = json.dumps(tasks)
        db.session.commit()
    return jsonify({'success': True})

@app.route('/api/finish_quest/<int:id>', methods=['POST'])
def finish(id):
    u = User.query.first()
    q = db.session.get(Quest, id)
    tasks = json.loads(q.tasks_json)
    if not all(t[0] >= t[1] for t in tasks.values()):
        return jsonify({'success': False, 'msg': 'Complete todas as tarefas!'})
    u.xp_atual += q.xp_reward; u.gold += q.gold_reward; u.subir_nivel_logica()
    q.concluida = True
    db.session.delete(q)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/buy/<int:id>', methods=['POST'])
def buy(id):
    u = User.query.first()
    item = db.session.get(ShopItem, id)
    if u.gold >= item.preco:
        u.gold -= item.preco
        inv = Inventory.query.filter_by(user_id=u.id, item_id=id).first()
        if inv: inv.quantidade += 1
        else: db.session.add(Inventory(user_id=u.id, item_id=id))
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False, 'msg': 'Sem Gold'})

@app.route('/api/equip/<int:id>', methods=['POST'])
def equip(id):
    u = User.query.first()
    inv = db.session.get(Inventory, id)
    tipo = inv.item.tipo
    if tipo == 'Head': u.head_slot = inv.item_id
    elif tipo == 'Body': u.body_slot = inv.item_id
    elif tipo == 'Legs': u.legs_slot = inv.item_id
    elif tipo == 'Weapon': u.weapon_slot = inv.item_id
    elif tipo == 'Consumivel':
        if inv.quantidade > 1: inv.quantidade -= 1
        else: db.session.delete(inv)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/add_stat/<attr>', methods=['POST'])
def add_stat(attr):
    u = User.query.first()
    if u.pontos_livres > 0:
        val = getattr(u, f"base_{attr}")
        setattr(u, f"base_{attr}", val + 1)
        u.pontos_livres -= 1
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'success': False})

# --- FUNÇÃO MÁGICA DE AUTO-INSTALAÇÃO ---
def inicializar_banco():
    """Cria tabelas e popula itens se o banco estiver vazio"""
    with app.app_context():
        db.create_all() # Cria as tabelas no PostgreSQL
        
        # Verifica se já existem itens
        if not ShopItem.query.first():
            print(">>> BANCO VAZIO DETECTADO. INICIANDO POPULAÇÃO AUTOMÁTICA...")
            # Copiamos a lógica do shop_stock.py aqui para garantir
            items = [
                ShopItem(nome="Poção de Cura", descricao="Recupera fadiga.", preco=100, icon="🧪", tipo="Consumivel", raridade="Comum"),
                ShopItem(nome="Elixir de Energia", descricao="Boost de café.", preco=200, icon="⚡", tipo="Consumivel", raridade="Comum"),
                ShopItem(nome="Ticket de Folga", descricao="Pula treino.", preco=800, icon="🎟️", tipo="Consumivel", raridade="Raro"),
                ShopItem(nome="Bandana de Novato", descricao="Foco básico.", preco=300, icon="🤕", tipo="Head", bonus_attr="inteligencia", bonus_val=2, raridade="Comum"),
                ShopItem(nome="Capacete Tático", descricao="Proteção sólida.", preco=1200, icon="⛑️", tipo="Head", bonus_attr="vitalidade", bonus_val=5, raridade="Incomum"),
                ShopItem(nome="Camisa de Treino", descricao="Leve.", preco=400, icon="👕", tipo="Body", bonus_attr="agilidade", bonus_val=2, raridade="Comum"),
                ShopItem(nome="Colete Pesado", descricao="Resistência.", preco=1500, icon="🦺", tipo="Body", bonus_attr="forca", bonus_val=5, raridade="Incomum"),
                ShopItem(nome="Tênis Velhos", descricao="Básico.", preco=300, icon="👟", tipo="Legs", bonus_attr="agilidade", bonus_val=1, raridade="Comum"),
                ShopItem(nome="Luvas de Boxe", descricao="Impacto.", preco=500, icon="🥊", tipo="Weapon", bonus_attr="forca", bonus_val=3, raridade="Comum"),
                ShopItem(nome="Adaga de Rasaka", descricao="Lendário.", preco=5000, icon="🗡️", tipo="Weapon", bonus_attr="agilidade", bonus_val=12, raridade="Epico"),
            ]
            titles = [
                Title(nome="O Despertado", descricao="Iniciou o sistema.", bonus_attr="vitalidade", bonus_val=1),
                Title(nome="Lobo Solitário", descricao="Treino constante.", bonus_attr="agilidade", bonus_val=5),
            ]
            db.session.add_all(items)
            db.session.add_all(titles)
            db.session.commit()
            print(">>> SISTEMA POPULADO COM SUCESSO.")

# Executa a verificação ao iniciar o app
inicializar_banco()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)