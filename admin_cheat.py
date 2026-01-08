from models import app, db, User

def dar_poderes():
    with app.app_context():
        user = User.query.first()
        if user:
            user.pontos_livres += 10
            user.gold += 1000
            db.session.commit()
            print(f">>> SUCESSO! Jogador {user.username} recebeu 10 Pontos e 1000 Gold.")
            print(">>> Atualize a página do site para ver os botões de evolução.")
        else:
            print(">>> ERRO: Nenhum jogador encontrado. Inicie o bot no Telegram.")

if __name__ == "__main__":
    dar_poderes()