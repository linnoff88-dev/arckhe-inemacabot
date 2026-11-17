# InemacaBot

Assistente pessoal para Telegram feito em Python. O bot:

- aceita somente um usuÃ¡rio autorizado;
- responde mensagens de texto usando o Codex CLI autenticado na mÃ¡quina;
- transcreve mensagens de voz e arquivos de Ã¡udio com o Groq;
- mantÃ©m um histÃ³rico curto em memÃ³ria;
- divide respostas maiores que o limite do Telegram;
- oferece apenas os comandos `/start`, `/limpar` e `/ajuda`.

## Como funciona

```text
Texto no Telegram â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                                  â”œâ”€â†’ Codex CLI â”€â†’ resposta no Telegram
Voz/Ã¡udio â”€â†’ Groq â”€â†’ transcriÃ§Ã£o â”˜
```

O bot nÃ£o usa uma chave da API OpenAI. Ele executa `codex exec` com a
autenticaÃ§Ã£o da assinatura do Codex/ChatGPT jÃ¡ ativa no usuÃ¡rio do sistema. Cada
consulta Ã© efÃªmera, usa um diretÃ³rio temporÃ¡rio vazio e deixa as ferramentas do
modelo em sandbox somente leitura.

O Codex continua sujeito aos limites de uso da assinatura. A chave do Groq Ã©
necessÃ¡ria somente para mensagens de voz ou Ã¡udio.

## PrÃ©-requisitos

- Python 3.11 ou superior;
- Codex CLI instalado;
- uma assinatura com acesso ao Codex;
- um bot criado no Telegram;
- uma chave do Groq, se a transcriÃ§Ã£o de Ã¡udio for utilizada.

Confira os comandos:

```bash
python3 --version
codex --version
codex login status
```

Se o Codex ainda nÃ£o estiver autenticado, execute:

```bash
codex login
```

Conclua o acesso usando a mesma conta que possui a assinatura do Codex.

## 1. Criar o bot com o BotFather

1. Abra o Telegram e inicie uma conversa com `@BotFather`.
2. Envie `/newbot`.
3. Escolha o nome visÃ­vel do bot.
4. Escolha um username terminado em `bot`.
5. Guarde o token entregue pelo BotFather.

NÃ£o publique esse token e nÃ£o o coloque diretamente no cÃ³digo.

## 2. Descobrir seu ID do Telegram

Envie qualquer mensagem ao bot recÃ©m-criado. Em seguida, substitua
`SEU_TOKEN` apenas no terminal e consulte as atualizaÃ§Ãµes:

```bash
curl "https://api.telegram.org/botSEU_TOKEN/getUpdates"
```

No resultado, procure por:

```json
{"from":{"id":123456789}}
```

O nÃºmero de `from.id` Ã© o valor de `TELEGRAM_ALLOWED_USER_ID`. Evite salvar o
comando contendo o token no histÃ³rico do terminal; outra opÃ§Ã£o Ã© usar
temporariamente uma variÃ¡vel local:

```bash
read -rsp "Token do Telegram: " TELEGRAM_SETUP_TOKEN
curl "https://api.telegram.org/bot${TELEGRAM_SETUP_TOKEN}/getUpdates"
unset TELEGRAM_SETUP_TOKEN
```

## 3. Instalar o projeto

Na raiz do projeto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 4. Configurar o ambiente

Copie o exemplo:

```bash
cp .env.example .env
chmod 600 .env
```

Edite `.env` e preencha inicialmente:

```env
TELEGRAM_BOT_TOKEN=token_entregue_pelo_botfather
TELEGRAM_ALLOWED_USER_ID=123456789
```

Para aceitar voz e Ã¡udio, preencha depois:

```env
GROQ_API_KEY=sua_chave_do_groq
```

ConfiguraÃ§Ãµes disponÃ­veis:

| VariÃ¡vel | ObrigatÃ³ria | Finalidade |
|---|---:|---|
| `TELEGRAM_BOT_TOKEN` | sim | Token entregue pelo BotFather |
| `TELEGRAM_ALLOWED_USER_ID` | sim | Ãšnico usuÃ¡rio autorizado |
| `CODEX_BINARY` | nÃ£o | ExecutÃ¡vel do Codex; padrÃ£o `codex` |
| `CODEX_MODEL` | nÃ£o | Modelo solicitado ao Codex; vazio usa o padrÃ£o |
| `CODEX_TIMEOUT_SECONDS` | nÃ£o | Tempo mÃ¡ximo de uma resposta |
| `HISTORY_MAX_EXCHANGES` | nÃ£o | Quantidade de pares mantidos em memÃ³ria |
| `AI_SYSTEM_PROMPT` | nÃ£o | Comportamento principal do assistente |
| `GROQ_API_KEY` | para Ã¡udio | Chave usada somente na transcriÃ§Ã£o |
| `GROQ_TRANSCRIPTION_MODEL` | nÃ£o | PadrÃ£o `whisper-large-v3-turbo` |
| `GROQ_TRANSCRIPTION_LANGUAGE` | nÃ£o | Idioma ISO-639-1; padrÃ£o `pt` |
| `MAX_AUDIO_MB` | nÃ£o | Limite local antes do envio ao Groq |

O arquivo `.env` Ã© ignorado pelo Git.

## 5. Iniciar o bot

Com o ambiente virtual ativado:

```bash
python bot.py
```

O processo continuarÃ¡ ativo por long polling. Para encerrar, pressione
`Ctrl+C`.

## 6. Testar a integraÃ§Ã£o

Execute primeiro os testes locais:

```bash
python -m unittest discover -v
```

Depois, no Telegram:

1. envie `/start`;
2. envie uma pergunta curta;
3. faÃ§a uma pergunta relacionada para confirmar o histÃ³rico;
4. envie `/limpar` e confirme que o contexto foi apagado;
5. envie uma mensagem por outra conta e confirme que nÃ£o hÃ¡ resposta;
6. depois de configurar o Groq, envie uma mensagem de voz.

Os erros bÃ¡sicos aparecem no terminal, sem registrar os tokens.

## 7. Manter o bot ativo em uma VPS

Primeiro descubra os caminhos absolutos:

```bash
pwd
command -v codex
```

Coloque o caminho retornado por `command -v codex` em `CODEX_BINARY` no `.env`.
O serviÃ§o precisa executar com o mesmo usuÃ¡rio Linux que realizou `codex login`.

Crie `/etc/systemd/system/inemacabot.service`:

```ini
[Unit]
Description=Assistente pessoal do Telegram
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=SEU_USUARIO
WorkingDirectory=/CAMINHO/ABSOLUTO/inemacabot
EnvironmentFile=/CAMINHO/ABSOLUTO/inemacabot/.env
ExecStart=/CAMINHO/ABSOLUTO/inemacabot/.venv/bin/python bot.py
Restart=on-failure
RestartSec=5
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

Ative o serviÃ§o:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now inemacabot
sudo systemctl status inemacabot
```

Para acompanhar os registros:

```bash
sudo journalctl -u inemacabot -f
```

## SoluÃ§Ã£o de problemas

### O bot nÃ£o inicia

Confira as variÃ¡veis obrigatÃ³rias e o ID numÃ©rico:

```bash
source .venv/bin/activate
python bot.py
```

### O Telegram responde com erro genÃ©rico

Verifique a autenticaÃ§Ã£o do Codex no mesmo usuÃ¡rio que executa o bot:

```bash
codex login status
```

Confira tambÃ©m o caminho configurado em `CODEX_BINARY` e os logs do processo.

### A mensagem de voz nÃ£o funciona

Confirme que `GROQ_API_KEY` foi definida e reinicie o bot. O projeto usa o
endpoint oficial de transcriÃ§Ã£o do Groq e, por padrÃ£o, o modelo
`whisper-large-v3-turbo`.

### O contexto sumiu

O histÃ³rico Ã© intencionalmente pequeno e fica somente na memÃ³ria. Ele Ã© apagado
por `/limpar` e sempre que o processo Ã© reiniciado.

## ReferÃªncias

- [Codex CLI â€” execuÃ§Ã£o nÃ£o interativa](https://developers.openai.com/codex/cli)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Groq Speech to Text](https://console.groq.com/docs/speech-to-text)

---

Projeto adaptado da comunidade INEMA TDS - Marca Arckhe