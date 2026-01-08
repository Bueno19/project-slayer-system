import logging
import random
from datetime import time
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from models import app, db, User, TrainingLog, Quest
import quest_system  # Importante: Usa a lógica de treino inteligente

# --- CONFIGURAÇÃO ---
TOKEN = "7948877311:AAE-tFj9XAD2xyB77V3LOMv4hEHPOxpoux8"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- FUNÇÕES DE SISTEMA ---

def get_or_create_user(tg_user):
    """Busca o utilizador na BD ou cria um novo"""
    tg_id = str(tg_user.id)
    username = tg_user.username or tg_user.first_name
    
    with app.app_context():
        user = User.query.filter_by(telegram_id=tg_id).first()
        if not user:
            user = User(username=username, telegram_id=tg_id)
            db.session.add(user)
            db.session.commit()
            return user, True 
        return user, False

# --- TAREFAS AUTOMÁTICAS (JOBS) ---

async def enviar_daily_quest(context: ContextTypes.DEFAULT_TYPE):
    """Gera e envia a missão diária obrigatória"""
    with app.app_context():
        usuarios = User.query.all()
        for user in usuarios:
            # GERA UMA NOVA QUEST INTELIGENTE
            dados = quest_system.gerar_missao_inteligente(user.rank)
            
            nova_quest = Quest(
                titulo="[DAILY] " + dados['titulo'], # Marca como Daily
                descricao=dados['descricao'],
                xp_reward=int(dados['xp'] * 1.5), # Daily dá mais XP
                gold_reward=int(dados['xp'] * 0.8),
                dificuldade=dados['rank'],
                stat_bonus="Misto"
            )
            db.session.add(nova_quest)
            db.session.commit()
            
            msg = (
                f"🌞 **QUEST DIÁRIA DO SISTEMA**\n"
                f"📜 **{nova_quest.titulo}**\n"
                f"ℹ️ {nova_quest.descricao}\n"
                f"⚡ {nova_quest.xp_reward} XP | 💰 {nova_quest.gold_reward} G\n\n"
                f"⚠️ Complete hoje para manter o combo!"
            )
            try:
                await context.bot.send_message(chat_id=user.telegram_id, text=msg, parse_mode='Markdown')
            except Exception as e:
                print(f"Erro ao enviar para {user.username}: {e}")

async def check_random_quest(context: ContextTypes.DEFAULT_TYPE):
    """Roda a cada 30min e tem chance de gerar quest surpresa"""
    CHANCE = 0.20 # 20% de chance a cada 30 min
    
    if random.random() < CHANCE:
        with app.app_context():
            usuarios = User.query.all()
            for user in usuarios:
                # Gera treino baseado no Rank
                dados = quest_system.gerar_missao_inteligente(user.rank)
                
                nova_quest = Quest(
                    titulo=dados['titulo'], 
                    descricao=dados['descricao'],
                    xp_reward=dados['xp'], 
                    gold_reward=int(dados['xp'] * 0.5),
                    dificuldade=dados['rank'],
                    stat_bonus="Misto"
                )
                db.session.add(nova_quest)
                db.session.commit()
                
                msg = (
                    f"🚨 **QUEST DE EMERGÊNCIA!** 🚨\n"
                    f"O Sistema detectou uma oportunidade de evolução.\n\n"
                    f"📜 **{nova_quest.titulo}**\n"
                    f"💀 {nova_quest.descricao}\n"
                    f"⚡ {nova_quest.xp_reward} XP | 💰 {nova_quest.gold_reward} G"
                )
                try:
                    await context.bot.send_message(chat_id=user.telegram_id, text=msg, parse_mode='Markdown')
                except:
                    pass

# --- COMANDOS DO BOT ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, is_new = get_or_create_user(update.effective_user)
    
    if is_new:
        msg = "⚠️ **SISTEMA SOLO LEVELING INICIADO** ⚠️\n\nBem-vindo, Caçador. A sua evolução começa agora."
    else:
        msg = f"Bem-vindo de volta, {user.username}."

    await update.message.reply_text(msg, parse_mode='Markdown')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = str(update.effective_user.id)
    with app.app_context():
        user = User.query.filter_by(telegram_id=tg_id).first()
        if user:
            texto = f"""
📊 **STATUS** | {user.rank}
👤 {user.username} | Nível {user.nivel}
⚡ XP: {user.xp_atual}/{user.xp_next_level}
💰 Gold: {user.gold}

💪 FOR: {user.forca} | 🏃 AGI: {user.agilidade}
❤️ VIT: {user.vitalidade} | 🧠 INT: {user.inteligencia}
            """
            await update.message.reply_text(texto, parse_mode='Markdown')

async def registrar_treino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando manual de backup: /treino flexao 10"""
    try:
        args = context.args
        if len(args) < 2:
            await update.message.reply_text("⚠️ Uso: `/treino [tipo] [qtd]`")
            return

        tipo = args[0].lower()
        qtd = float(args[1])
        tg_id = str(update.effective_user.id)

        with app.app_context():
            user = User.query.filter_by(telegram_id=tg_id).first()
            if user:
                xp = int(qtd * 2)
                user.xp_atual += xp
                
                if user.xp_atual >= user.xp_next_level:
                    user.subir_nivel_logica()
                    await update.message.reply_text(f"🎉 **LEVEL UP!** Nível {user.nivel}")

                # Salvar Log
                log = TrainingLog(user_id=user.id, tipo=tipo, valor=qtd)
                db.session.add(log)
                db.session.commit()
                
                await update.message.reply_text(f"✅ Treino manual registrado! +{xp} XP")
    except:
        await update.message.reply_text("Erro ao processar.")

async def forcar_quest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando de teste para gerar uma quest na hora"""
    await check_random_quest(context) # Chama a função de random (pode não vir nada se cair nos 80%)
    # Ou forçamos a daily para garantir que vem algo:
    await enviar_daily_quest(context)

# --- INICIALIZAÇÃO ---
if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Comandos
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('treino', registrar_treino))
    application.add_handler(CommandHandler('quest', forcar_quest))

    # --- AGENDADOR ---
    job_queue = application.job_queue
    
    # 1. Quest Diária (08:00 da manhã)
    job_queue.run_daily(enviar_daily_quest, time(hour=8, minute=00))
    
    # 2. Quests Aleatórias (Verifica a cada 30 minutos)
    job_queue.run_repeating(check_random_quest, interval=1800, first=10)

    print(">>> SISTEMA ONLINE: Agendador Ativo...")
    application.run_polling()