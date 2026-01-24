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
# Determinar diretório onde o script está rodando
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo -e "${BLUE}Script executado em: $SCRIPT_DIR${NC}"
echo "Conteúdo de $SCRIPT_DIR:"
ls -F "$SCRIPT_DIR"

# Se o script está dentro de pc_price_tracker, definimos o backend relativo a ele
if [ -d "$SCRIPT_DIR/backend" ]; then
    BACKEND_DIR="$SCRIPT_DIR/backend"
    echo -e "${GREEN}Diretório backend detectado em: $BACKEND_DIR${NC}"
else
    echo -e "${RED}ERRO CRÍTICO: Pasta 'backend' não encontrada dentro de $SCRIPT_DIR${NC}"
    echo "O arquivo vm_setup.sh precisa estar ao lado da pasta 'backend'."
    exit 1
fi

# 3. Setup do Ambiente Python
echo -e "${GREEN}[3/6] Configurando ambiente virtual Python em $BACKEND_DIR...${NC}"
cd "$BACKEND_DIR"

if [ ! -d "venv" ]; then
    echo "Criando venv..."
    python3 -m venv venv
fi

source venv/bin/activate
# Forçar upgrade pip e garantir que requirements existam
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}ERRO: requirements.txt não encontrado em $(pwd)${NC}"
    ls -la
    exit 1
fi

pip install --upgrade pip
pip install -r requirements.txt

# 4. Instalação do Playwright
echo -e "${GREEN}[4/6] Instalando Playwright e Browsers...${NC}"
playwright install chromium
# Se for root, install-deps não precisa de sudo, mas se não for, precisa
if [ "$EUID" -eq 0 ]; then
  playwright install-deps chromium
else
  sudo playwright install-deps chromium
fi

# 5. Criar script de execução para o Cron
echo -e "${GREEN}[5/6] Criando script wrapper para o Cron...${NC}"
# Salvar o run_scraper.sh no mesmo nível do vm_setup.sh para facilitar
RUN_SCRIPT="$SCRIPT_DIR/run_scraper.sh"
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
