from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json
import os

app = Flask(__name__)

# Configuração do Banco de Dados
# Usa SQLite por padrão, mas aceita PostgreSQL se estiver online (Render)
db_url = os.getenv("DATABASE_URL", "sqlite:///sistema_rpg.db")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- TABELA DE ASSOCIAÇÃO (MUITOS-PARA-MUITOS) ---
user_titles = db.Table('user_titles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('title_id', db.Integer, db.ForeignKey('title.id'), primary_key=True)
)

# --- LOJA DIÁRIA ---
class DailyShop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True)
    items_json = db.Column(db.Text) 

# --- JOGADOR (USER) ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    telegram_id = db.Column(db.String(50), unique=True, nullable=True)
    
    # Progresso
    nivel = db.Column(db.Integer, default=1)
    xp_atual = db.Column(db.Integer, default=0)
    xp_next_level = db.Column(db.Integer, default=300)
    rank = db.Column(db.String(10), default="Rank E")
    classe = db.Column(db.String(50), default="Novato")
    gold = db.Column(db.Integer, default=0)
    
    # Atributos Base (Começam em 5)
    pontos_livres = db.Column(db.Integer, default=0)
    base_forca = db.Column(db.Integer, default=5)
    base_agilidade = db.Column(db.Integer, default=5)
    base_vitalidade = db.Column(db.Integer, default=5)
    base_inteligencia = db.Column(db.Integer, default=5)
    
    # Slots de Equipamento (Guardam o ID do Item)
    head_slot = db.Column(db.Integer, db.ForeignKey('shop_item.id'), nullable=True)
    body_slot = db.Column(db.Integer, db.ForeignKey('shop_item.id'), nullable=True)
    legs_slot = db.Column(db.Integer, db.ForeignKey('shop_item.id'), nullable=True)
    weapon_slot = db.Column(db.Integer, db.ForeignKey('shop_item.id'), nullable=True)

    # Relacionamentos
    inventario = db.relationship('Inventory', backref='owner', lazy=True)
    titulos = db.relationship('Title', secondary=user_titles, backref=db.backref('users', lazy=True))

    # --- CÁLCULO DE ATRIBUTOS TOTAIS ---
    @property
    def forca(self): return self.calcular_total('forca')
    @property
    def agilidade(self): return self.calcular_total('agilidade')
    @property
    def vitalidade(self): return self.calcular_total('vitalidade')
    @property
    def inteligencia(self): return self.calcular_total('inteligencia')

    def calcular_total(self, attr):
        # 1. Pega o valor base (ex: 5)
        total = getattr(self, f"base_{attr}")
        
        # 2. Soma Equipamentos
        for slot_id in [self.head_slot, self.body_slot, self.legs_slot, self.weapon_slot]:
            if slot_id:
                item = db.session.get(ShopItem, slot_id)
                # Verifica se item existe e se tem bonus nesse atributo
                if item and item.bonus_attr == attr: 
                    total += (item.bonus_val or 0)
        
        # 3. Soma Títulos
        for t in self.titulos:
            if t.bonus_attr == attr: 
                total += (t.bonus_val or 0)
                
        return total

    def subir_nivel_logica(self):
        self.nivel += 1
        self.xp_atual = 0
        self.xp_next_level = int(self.xp_next_level * 1.5)
        self.pontos_livres += 3
        
        # Atualiza Rank Automaticamente
        if self.nivel < 10: self.rank = "Rank E"
        elif self.nivel < 20: self.rank = "Rank D"
        elif self.nivel < 40: self.rank = "Rank C"
        elif self.nivel < 70: self.rank = "Rank B"
        elif self.nivel < 100: self.rank = "Rank A"
        else: self.rank = "Rank S"

# --- ITENS DA LOJA ---
class ShopItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    preco = db.Column(db.Integer, nullable=False, default=0)
    icon = db.Column(db.String(50))
    tipo = db.Column(db.String(20)) # Head, Body, Weapon, Consumivel
    raridade = db.Column(db.String(20), default="Comum")
    min_rank = db.Column(db.String(5), default="E")
    
    # Bônus
    bonus_attr = db.Column(db.String(20), nullable=True)
    bonus_val = db.Column(db.Integer, default=0) # Default 0 para não quebrar conta

# --- INVENTÁRIO DO JOGADOR ---
class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('shop_item.id'), nullable=False)
    quantidade = db.Column(db.Integer, default=1)
    
    # Relacionamento para acessar dados do item (nome, icon, etc)
    item = db.relationship('ShopItem')

# --- TÍTULOS ---
class Title(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(200))
    bonus_attr = db.Column(db.String(20))
    bonus_val = db.Column(db.Integer, default=0)

# --- QUESTS ---
class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    tasks_json = db.Column(db.Text, default="{}") # Ex: {"Flexão": [0, 10]}
    xp_reward = db.Column(db.Integer, nullable=False)
    gold_reward = db.Column(db.Integer, default=0)
    dificuldade = db.Column(db.String(10))
    concluida = db.Column(db.Boolean, default=False)

# --- LOGS DE TREINO ---
class TrainingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    tipo = db.Column(db.String(50))
    valor = db.Column(db.Float)
    data = db.Column(db.DateTime, default=datetime.utcnow)

# --- CRIAÇÃO DO BANCO ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print(">>> BANCO DE DADOS (SYSTEM V6) CRIADO COM SUCESSO.")