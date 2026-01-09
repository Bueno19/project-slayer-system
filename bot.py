import logging
import random
import os
import pytz # Necessário para o horário das tarefas
from datetime import time
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
from models import app, db, User, TrainingLog, Quest
import quest_system 

# --- CONFIGURAÇÃO ---
# Token: Tenta pegar do ambiente (Render), se não der, usa o fixo.
TOKEN = os.getenv("TELEGRAM_TOKEN", "7948877311:AAE-tFj9XAD2xyB77V3LOMv4hEHPOxpoux8")

# Configuração de Logs (Para veres erros no Render)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- FUNÇÕES DE BANCO DE DADOS ---

def get_or_create_user(tg_user):
    """Busca o utilizador na BD ou cria um novo"""
    tg_id = str(tg_user.id)
    # Se não tiver username, usa o primeiro nome
    username = tg_user.username if tg_user.username else tg_user.first_name
    
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
    print(">>> EXECUTANDO DAILY QUEST JOB")
    with app.app_context():
        usuarios = User.query.all()
        for user in usuarios:
            try:
                # GERA UMA NOVA QUEST INTELIGENTE
                dados = quest_system.gerar_daily_quest(user.rank) # Confirme se a função chama 'gerar_daily_quest' ou 'gerar_missao_inteligente' no seu quest_system.py
                
                nova_quest = Quest(
                    titulo="[DAILY] " + dados.get('titulo', 'Treino Diário'),
                    tasks_json=dados.get('tasks_json', '{}'), # Adapte conforme seu modelo
                    xp_reward=int(dados.get('xp', 100) * 1.5),
                    gold_reward=int(dados.get('gold', 50) * 1.2),
                    dificuldade=dados.get('rank', 'E')
                )
                db.session.add(nova_quest)
                db.session.commit()
                
                msg = (
                    f"🌞 **QUEST DIÁRIA DO SISTEMA**\n"
                    f"📜 **{nova_quest.titulo}**\n"
                    f"⚡ {nova_quest.xp_reward} XP | 💰 {nova_quest.gold_reward} G\n"
                    f"⚠️ Verifique o painel para ver os objetivos!"
                )
                
                # Envia mensagem pro usuário
                if user.telegram_id:
                    await context.bot.send_message(chat_id=user.telegram_id, text=msg, parse_mode='Markdown')
            except Exception as e:
                logging.error(f"Erro ao enviar Daily para {user.username}: {e}")

async def check_random_quest(context: ContextTypes.DEFAULT_TYPE):
    """Roda periodicamente e tem chance de gerar quest surpresa"""
    CHANCE = 0.20 # 20% de chance
    
    if random.random() < CHANCE:
        print(">>> EVENTO DE QUEST ALEATÓRIA ATIVADO!")
        with app.app_context():
            usuarios = User.query.all()
            for user in usuarios:
                try:
                    dados = quest_system.gerar_daily_quest(user.rank)
                    
                    nova_quest = Quest(
                        titulo="[SUDDEN QUEST] " + dados.get('titulo'), 
                        tasks_json=dados.get('tasks_json'),
                        xp_reward=dados.get('xp'), 
                        gold_reward=dados.get('gold'),
                        dificuldade=dados.get('rank')
                    )
                    db.session.add(nova_quest)
                    db.session.commit()
                    
                    msg = (
                        f"🚨 **QUEST DE EMERGÊNCIA!** 🚨\n"
                        f"O Sistema detectou uma oportunidade de evolução.\n\n"
                        f"📜 **{nova_quest.titulo}**\n"
                        f"⚡ {nova_quest.xp_reward} XP | 💰 {nova_quest.gold_reward} G"
                    )
                    if user.telegram_id:
                        await context.bot.send_message(chat_id=user.telegram_id, text=msg, parse_mode='Markdown')
                except Exception as e:
                    logging.error(f"Erro na Random Quest: {e}")

# --- COMANDOS DO BOT ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user, is_new = get_or_create_user(update.effective_user)
    
    if is_new:
        msg = f"⚠️ **SISTEMA SOLO LEVELING INICIADO** ⚠️\n\nBem-vindo, {user.username}. A sua evolução começa agora."
    else:
        msg = f"Bem-vindo de volta, {user.username}.\nO seu status atual é: **{user.rank}**"

    await update.message.reply_text(msg, parse_mode='Markdown')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_id = str(update.effective_user.id)
    with app.app_context():
        user = User.query.filter_by(telegram_id=tg_id).first()
        if user:
            # Pega valores com segurança (use 0 se for None)
            f = user.base_forca or 0
            a = user.base_agilidade or 0
            v = user.base_vitalidade or 0
            i = user.base_inteligencia or 0
            
            texto = (
                f"📊 **STATUS** | {user.rank}\n"
                f"👤 {user.username} | Nível {user.nivel}\n"
                f"⚡ XP: {user.xp_atual}/{user.xp_next_level}\n"
                f"💰 Gold: {user.gold}\n\n"
                f"💪 FOR: {f} | 🏃 AGI: {a}\n"
                f"❤️ VIT: {v} | 🧠 INT: {i}"
            )
            await update.message.reply_text(texto, parse_mode='Markdown')
        else:
            await update.message.reply_text("Erro: Utilizador não encontrado. Digite /start.")

async def registrar_treino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando: /treino flexao 10"""
    try:
        if not context.args or len(context.args) < 2:
            await update.message.reply_text("⚠️ Uso correto: `/treino [tipo] [qtd]`\nEx: `/treino flexao 10`", parse_mode='Markdown')
            return

        tipo = context.args[0].lower()
        # Verifica se qtd é número
        try:
            qtd = float(context.args[1])
        except ValueError:
            await update.message.reply_text("⚠️ A quantidade deve ser um número.")
            return

        tg_id = str(update.effective_user.id)

        with app.app_context():
            user = User.query.filter_by(telegram_id=tg_id).first()
            if user:
                # Lógica simples de XP manual
                xp = int(qtd * 2)
                user.xp_atual += xp
                user.gold += int(qtd) # Ganha 1 gold por repetição no treino manual
                
                msg_level_up = ""
                # Verifica Level Up
                if user.xp_atual >= user.xp_next_level:
                    user.subir_nivel_logica()
                    msg_level_up = f"\n🎉 **LEVEL UP!** Agora és Nível {user.nivel}!"

                # Salvar Log
                log = TrainingLog(user_id=user.id, tipo=tipo, valor=qtd)
                db.session.add(log)
                db.session.commit()
                
                await update.message.reply_text(f"✅ Treino registrado!\n+{xp} XP | +{int(qtd)} Gold{msg_level_up}", parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Erro no treino: {e}")
        await update.message.reply_text("Ocorreu um erro ao processar o treino.")

async def forcar_quest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando admin para forçar o envio da Daily (Teste)"""
    await update.message.reply_text("⚙️ Forçando rotina de Quests...")
    await enviar_daily_quest(context)

# --- INICIALIZAÇÃO ---
if __name__ == '__main__':
    print(">>> INICIANDO O BOT...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Adicionar Comandos
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('treino', registrar_treino))
    application.add_handler(CommandHandler('quest', forcar_quest))

    # --- AGENDADOR DE TAREFAS ---
    job_queue = application.job_queue
    
    # Define Fuso Horário (Importante para não dar erro)
    tz = pytz.timezone('America/Sao_Paulo') 
    
    # 1. Quest Diária (08:00 da manhã)
    job_queue.run_daily(enviar_daily_quest, time(hour=8, minute=0, tzinfo=tz))
    
    # 2. Quests Aleatórias (A cada 30 min)
    job_queue.run_repeating(check_random_quest, interval=1800, first=60)

    print(">>> SISTEMA ONLINE: Agendador Ativo. Bot Rodando...")
    application.run_polling()