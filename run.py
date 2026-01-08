import subprocess
import os
import time

# 1. Inicia o Bot em segundo plano
print(">>> INICIANDO O BOT SOLDIER...")
bot_process = subprocess.Popen(["python", "bot.py"])

# 2. Espera 5 segundos para o bot arrancar
time.sleep(5)

# 3. Inicia o Site (Gunicorn) e segura o processo
print(">>> INICIANDO O SISTEMA MONARCA (WEB)...")
# O Render precisa que este processo fique rodando na porta correta
subprocess.run(["gunicorn", "app:app"])