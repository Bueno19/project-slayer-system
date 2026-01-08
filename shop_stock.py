from models import app, db, ShopItem, Title

def encher_estoque():
    with app.app_context():
        db.session.query(ShopItem).delete()
        db.session.query(Title).delete()
        
        items = []
        
        # --- CONSUMÍVEIS ---
        items.append(ShopItem(nome="Poção de Cura", descricao="Recupera fadiga mental.", preco=100, icon="🧪", tipo="Consumivel", raridade="Comum", min_rank="E"))
        items.append(ShopItem(nome="Bandagem", descricao="Alivia dores musculares.", preco=50, icon="🩹", tipo="Consumivel", raridade="Comum", min_rank="E"))
        items.append(ShopItem(nome="Suco de Laranja", descricao="Boost de energia rápido.", preco=20, icon="🧃", tipo="Consumivel", raridade="Comum", min_rank="E"))
        items.append(ShopItem(nome="Bife Premium", descricao="Refeição completa.", preco=500, icon="🥩", tipo="Consumivel", raridade="Incomum", min_rank="D"))
        items.append(ShopItem(nome="Água Sagrada", descricao="Cura instantânea de stress.", preco=5000, icon="💧", tipo="Consumivel", raridade="Epico", min_rank="B"))

        # --- CABEÇA (HEAD) ---
        items.append(ShopItem(nome="Capuz Simples", descricao="Discrição básica.", preco=200, icon="🧢", tipo="Head", raridade="Comum", min_rank="E", bonus_attr="agilidade", bonus_val=1))
        items.append(ShopItem(nome="Capacete de Ciclismo", descricao="Proteção leve.", preco=600, icon="⛑️", tipo="Head", raridade="Comum", min_rank="E", bonus_attr="vitalidade", bonus_val=3))
        items.append(ShopItem(nome="Máscara de Gás", descricao="Filtra impurezas.", preco=1500, icon="😷", tipo="Head", raridade="Incomum", min_rank="D", bonus_attr="vitalidade", bonus_val=5))
        items.append(ShopItem(nome="Elmo do Cavaleiro", descricao="Ferro maciço.", preco=4000, icon="🗿", tipo="Head", raridade="Raro", min_rank="C", bonus_attr="vitalidade", bonus_val=10))
        items.append(ShopItem(nome="Coroa do Monarca", descricao="Aura dominadora.", preco=50000, icon="👑", tipo="Head", raridade="Lendario", min_rank="S", bonus_attr="inteligencia", bonus_val=50))

        # --- CORPO (BODY) ---
        items.append(ShopItem(nome="Camiseta Branca", descricao="Puro algodão.", preco=100, icon="👕", tipo="Body", raridade="Comum", min_rank="E", bonus_attr="vitalidade", bonus_val=1))
        items.append(ShopItem(nome="Jaqueta de Couro", descricao="Estilo e defesa.", preco=1200, icon="🧥", tipo="Body", raridade="Incomum", min_rank="D", bonus_attr="vitalidade", bonus_val=4))
        items.append(ShopItem(nome="Manto da Furtividade", descricao="Dificulta detecção.", preco=3500, icon="🥋", tipo="Body", raridade="Raro", min_rank="C", bonus_attr="agilidade", bonus_val=8))
        items.append(ShopItem(nome="Armadura de Escamas", descricao="Feita de monstros.", preco=12000, icon="🐉", tipo="Body", raridade="Epico", min_rank="B", bonus_attr="vitalidade", bonus_val=20))

        # --- PERNAS (LEGS) ---
        items.append(ShopItem(nome="Shorts de Corrida", descricao="Liberdade de movimento.", preco=300, icon="🩳", tipo="Legs", raridade="Comum", min_rank="E", bonus_attr="agilidade", bonus_val=2))
        items.append(ShopItem(nome="Calça Cargo", descricao="Muitos bolsos.", preco=800, icon="👖", tipo="Legs", raridade="Comum", min_rank="E", bonus_attr="forca", bonus_val=2))
        items.append(ShopItem(nome="Botas de Trekking", descricao="Aguenta qualquer terreno.", preco=2000, icon="🥾", tipo="Legs", raridade="Incomum", min_rank="D", bonus_attr="vitalidade", bonus_val=5))
        items.append(ShopItem(nome="Grevas Sônicas", descricao="Passos silenciosos.", preco=8000, icon="⚡", tipo="Legs", raridade="Epico", min_rank="B", bonus_attr="agilidade", bonus_val=15))

        # --- ARMAS (WEAPON) ---
        items.append(ShopItem(nome="Punhos Nus", descricao="Suas próprias mãos.", preco=0, icon="✊", tipo="Weapon", raridade="Comum", min_rank="E", bonus_attr="forca", bonus_val=0))
        items.append(ShopItem(nome="Taco de Beisebol", descricao="Clássico urbano.", preco=500, icon="🏏", tipo="Weapon", raridade="Comum", min_rank="E", bonus_attr="forca", bonus_val=3))
        items.append(ShopItem(nome="Faca de Cozinha", descricao="Afiada.", preco=800, icon="🔪", tipo="Weapon", raridade="Comum", min_rank="E", bonus_attr="agilidade", bonus_val=3))
        items.append(ShopItem(nome="Espada Longa", descricao="Aço temperado.", preco=3000, icon="🗡️", tipo="Weapon", raridade="Incomum", min_rank="D", bonus_attr="forca", bonus_val=10))
        items.append(ShopItem(nome="Adaga de Rasaka", descricao="Venenosa e rápida.", preco=15000, icon="🐍", tipo="Weapon", raridade="Epico", min_rank="C", bonus_attr="agilidade", bonus_val=25))
        items.append(ShopItem(nome="Espada Demoníaca", descricao="Sedenta por sangue.", preco=100000, icon="🩸", tipo="Weapon", raridade="Lendario", min_rank="S", bonus_attr="forca", bonus_val=100))

        # --- TÍTULOS ---
        titles = [
            Title(nome="O Mais Fraco", descricao="Sobreviveu ao primeiro dia.", bonus_attr="vitalidade", bonus_val=1),
            Title(nome="Matador de Lobos", descricao="Derrotou a preguiça.", bonus_attr="agilidade", bonus_val=5),
            Title(nome="Monarca das Sombras", descricao="Atingiu o ápice.", bonus_attr="inteligencia", bonus_val=50)
        ]

        db.session.add_all(items)
        db.session.add_all(titles)
        db.session.commit()
        print(">>> LOJA GIGANTE CRIADA COM SUCESSO.")

if __name__ == "__main__":
    encher_estoque()