#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Iniciando Setup do PC Price Tracker na VM ===${NC}"

# 1. Update e Upgrade do Sistema
echo -e "${GREEN}[1/6] Atualizando pacotes do sistema...${NC}"
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3-pip python3-venv git htop cron

# 2. Clone do Repositório (Se não existir) ou Pull
REPO_DIR="$HOME/webapp"
REPO_URL="https://github.com/SelmoCastro/webapp.git"

if [ -d "$REPO_DIR" ]; then
    echo -e "${GREEN}[2/6] Atualizando repositório existente...${NC}"
    cd "$REPO_DIR"
    git pull
else
    echo -e "${GREEN}[2/6] Clonando repositório...${NC}"
    git clone "$REPO_URL" "$REPO_DIR"
    cd "$REPO_DIR"
fi

# 3. Setup do Ambiente Python
echo -e "${GREEN}[3/6] Configurando ambiente virtual Python...${NC}"
BACKEND_DIR="$REPO_DIR/pc_price_tracker/backend"
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 4. Instalação do Playwright
echo -e "${GREEN}[4/6] Instalando Playwright e Browsers...${NC}"
playwright install chromium
sudo playwright install-deps chromium

# 5. Criar script de execução para o Cron
echo -e "${GREEN}[5/6] Criando script wrapper para o Cron...${NC}"
RUN_SCRIPT="$HOME/run_scraper.sh"
cat > "$RUN_SCRIPT" << EOL
#!/bin/bash
cd "$BACKEND_DIR"
source venv/bin/activate
# Carregar env vars do arquivo .env se existir lá
if [ -f .env ]; then
    export \$(grep -v '^#' .env | xargs)
fi

echo "[\$(date)] Iniciando scraper..." >> "$HOME/scraper.log"
python src/main_scraper.py >> "$HOME/scraper.log" 2>&1
echo "[\$(date)] Finalizado." >> "$HOME/scraper.log"
EOL

chmod +x "$RUN_SCRIPT"

# 6. Instruções Finais
echo -e "${BLUE}=== Setup Finalizado com Sucesso! ===${NC}"
echo -e "Próximos passos manuais:"
echo -e "1. Crie o arquivo .env em: ${RED}$BACKEND_DIR/.env${NC}"
echo -e "   Conteúdo necessário:"
echo -e "   SUPABASE_URL=sua_url"
echo -e "   SUPABASE_KEY=sua_chave"
echo -e ""
echo -e "2. Configure o Crontab para rodar a cada 3 horas:"
echo -e "   Digite: ${GREEN}crontab -e${NC}"
echo -e "   Adicione a linha: ${GREEN}0 */3 * * * $RUN_SCRIPT${NC}"
echo -e ""
echo -e "Para testar agora, rode: ${GREEN}$RUN_SCRIPT${NC}"
