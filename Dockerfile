# Usa o Python 3.10 (compatível com python-telegram-bot)
FROM python:3.10-slim

# Define o diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala dependências
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expõe a porta (opcional, só pra compatibilidade Render)
EXPOSE 10000

# Comando para iniciar o bot
CMD ["python", "main.py"]
