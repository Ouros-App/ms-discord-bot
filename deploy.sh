#!/bin/bash

# Atualiza pip
python3 -m pip install --upgrade pip

# Instala dependências do requirements.txt
if [ -f "requirements.txt" ]; then
    echo "📦 Instalando dependências do requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️  Arquivo requirements.txt não encontrado!"
fi

# Instala outras dependências comuns (se precisar)
# pip install discord.py
# pip install python-dotenv

echo "✅ Deploy concluído!"