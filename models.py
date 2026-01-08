from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sistema_rpg.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Tabela de Associação (Títulos)
user_titles = db.Table('user_titles',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('title_id', db.Integer, db.ForeignKey('title.id'), primary_key=True)
)

class DailyShop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, unique=True)
    items_json = db.Column(db.Text) 

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    telegram_id = db.Column(db.String(50), unique=True, nullable=True)
    
    nivel = db.Column(db.Integer, default=1)
    xp_atual = db.Column(db.Integer, default=0)
    xp_next_level = db.Column(db.Integer, default=300)
    rank = db.Column(db.String(10), default="Rank E")
    classe = db.Column(db.String(50), default="Novato")
    gold = db.Column(db.Integer, default=0)
    
    # ATRIBUTOS BASE 5
    pontos_livres = db.Column(db.Integer, default=0)
    base_forca = db.Column(db.Integer, default=5)
    base_agilidade = db.Column(db.Integer, default=5)
    base_vitalidade = db.Column(db.Integer, default=5)
    base_inteligencia = db.Column(db.Integer, default=5)
    
    # Slots
    head_slot = db.Column(db.Integer, db.ForeignKey('shop_item.id'), nullable=True)
    body_slot = db.Column(db.Integer, db.ForeignKey('shop_item.id'), nullable=True)
    legs_slot = db.Column(db.Integer, db.ForeignKey('shop_item.id'), nullable=True)
    weapon_slot = db.Column(db.Integer, db.ForeignKey('shop_item.id'), nullable=True)

    inventario = db.relationship('Inventory', backref='owner', lazy=True)
    titulos = db.relationship('Title', secondary=user_titles, backref=db.backref('users', lazy=True))

    @property
    def forca(self): return self.calcular_total('forca')
    @property
    def agilidade(self): return self.calcular_total('agilidade')
    @property
    def vitalidade(self): return self.calcular_total('vitalidade')
    @property
    def inteligencia(self): return self.calcular_total('inteligencia')

    def calcular_total(self, attr):
        total = getattr(self, f"base_{attr}")
        for slot_id in [self.head_slot, self.body_slot, self.legs_slot, self.weapon_slot]:
            if slot_id:
                item = db.session.get(ShopItem, slot_id)
                if item and item.bonus_attr == attr: total += item.bonus_val
        for t in self.titulos:
            if t.bonus_attr == attr: total += t.bonus_val
        return total

    def subir_nivel_logica(self):
        self.nivel += 1
        self.xp_atual = 0
        self.xp_next_level = int(self.xp_next_level * 1.5)
        self.pontos_livres += 3
        if self.nivel < 10: self.rank = "Rank E"
        elif self.nivel < 20: self.rank = "Rank D"
        elif self.nivel < 40: self.rank = "Rank C"
        elif self.nivel < 70: self.rank = "Rank B"
        elif self.nivel < 100: self.rank = "Rank A"
        else: self.rank = "Rank S"

class ShopItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    preco = db.Column(db.Integer, nullable=False)
    icon = db.Column(db.String(50))
    tipo = db.Column(db.String(20)) 
    raridade = db.Column(db.String(20), default="Comum")
    min_rank = db.Column(db.String(5), default="E")
    bonus_attr = db.Column(db.String(20), nullable=True)
    bonus_val = db.Column(db.Integer, default=0)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('shop_item.id'), nullable=False)
    quantidade = db.Column(db.Integer, default=1)
    item = db.relationship('ShopItem')

class Title(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50))
    descricao = db.Column(db.String(200))
    bonus_attr = db.Column(db.String(20))
    bonus_val = db.Column(db.Integer)

class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    tasks_json = db.Column(db.Text, default="{}") 
    xp_reward = db.Column(db.Integer, nullable=False)
    gold_reward = db.Column(db.Integer, default=0)
    dificuldade = db.Column(db.String(10))
    concluida = db.Column(db.Boolean, default=False)

class TrainingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    tipo = db.Column(db.String(50))
    valor = db.Column(db.Float)
    data = db.Column(db.DateTime, default=datetime.utcnow)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print(">>> BANCO DE DADOS CRIADO.")