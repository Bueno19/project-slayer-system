from models import app, db, ShopItem, Title

def popular_banco_gigante():
    with app.app_context():
        db.session.query(ShopItem).delete()
        db.session.query(Title).delete()
        
        items = []
        
        # --- CONSUMÍVEIS (Sempre úteis) ---
        items.append(ShopItem(nome="Poção de Cura (Descanso)", descricao="Recupera fadiga mental.", preco=100, icon="🧪", tipo="Consumivel", raridade="Comum", min_rank="E"))
        items.append(ShopItem(nome="Elixir de Energia (Café)", descricao="Boost de energia imediato.", preco=200, icon="☕", tipo="Consumivel", raridade="Comum", min_rank="E"))
        items.append(ShopItem(nome="Ticket de Folga", descricao="Pula treino sem punição.", preco=1000, icon="🎟️", tipo="Consumivel", raridade="Raro", min_rank="D"))
        
        # --- EQUIPAMENTOS RANK E (Iniciante) ---
        items.append(ShopItem(nome="Bandana de Treino", descricao="Absorve suor.", preco=300, icon="🤕", tipo="Head", raridade="Comum", min_rank="E", bonus_attr="vitalidade", bonus_val=2))
        items.append(ShopItem(nome="Camiseta Velha", descricao="Confortável.", preco=400, icon="👕", tipo="Body", raridade="Comum", min_rank="E", bonus_attr="vitalidade", bonus_val=3))
        items.append(ShopItem(nome="Tênis Gastos", descricao="Melhor que descalço.", preco=500, icon="👟", tipo="Legs", raridade="Comum", min_rank="E", bonus_attr="agilidade", bonus_val=2))
        
        # --- EQUIPAMENTOS RANK D (Melhores) ---
        items.append(ShopItem(nome="Capacete Tático", descricao="Proteção leve.", preco=1500, icon="⛑️", tipo="Head", raridade="Incomum", min_rank="D", bonus_attr="vitalidade", bonus_val=5))
        items.append(ShopItem(nome="Colete de Peso", descricao="Aumenta dificuldade.", preco=2000, icon="🦺", tipo="Body", raridade="Incomum", min_rank="D", bonus_attr="forca", bonus_val=5))
        items.append(ShopItem(nome="Tênis de Corrida Pro", descricao="Alta performance.", preco=2500, icon="👟", tipo="Legs", raridade="Incomum", min_rank="D", bonus_attr="agilidade", bonus_val=6))
        items.append(ShopItem(nome="Halteres de 5kg", descricao="Peso inicial.", preco=3000, icon="🏋️", tipo="Weapon", raridade="Incomum", min_rank="D", bonus_attr="forca", bonus_val=8))

        # --- EQUIPAMENTOS RANK C (Profissional) ---
        items.append(ShopItem(nome="Máscara de Oxigênio", descricao="Treino de altitude.", preco=5000, icon="😷", tipo="Head", raridade="Raro", min_rank="C", bonus_attr="vitalidade", bonus_val=10))
        items.append(ShopItem(nome="Traje de Compressão", descricao="Recuperação rápida.", preco=6000, icon="🥋", tipo="Body", raridade="Raro", min_rank="C", bonus_attr="agilidade", bonus_val=10))
        items.append(ShopItem(nome="Adaga de Rasaka", descricao="Item Lendário (Réplica).", preco=15000, icon="🗡️", tipo="Weapon", raridade="Epico", min_rank="C", bonus_attr="agilidade", bonus_val=20))

        # --- TÍTULOS ---
        titles = [
            Title(nome="O Despertado", descricao="Iniciou o Sistema.", bonus_attr="vitalidade", bonus_val=1),
            Title(nome="Matador de Lobos", descricao="Correu 50km no total.", bonus_attr="agilidade", bonus_val=5),
            Title(nome="One Punch Man", descricao="Fez 100 flexões num dia.", bonus_attr="forca", bonus_val=10),
            Title(nome="Sábio da Montanha", descricao="Manteve a rotina por 30 dias.", bonus_attr="inteligencia", bonus_val=10)
        ]

        db.session.add_all(items)
        db.session.add_all(titles)
        db.session.commit()
        print(">>> BANCO DE DADOS POPULADO COM SUCESSO.")

if __name__ == "__main__":
    popular_banco_gigante()