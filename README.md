ï»¿# ARCKHÉcaBot

Assistente pessoal para Telegram feito em Python. O bot:

- aceita somente um usuêÂ¡rio autorizado;
- responde mensagens de texto usando o Codex CLI autenticado na mêÂ¡quina;
- transcreve mensagens de voz e arquivos de êÂ¡udio com o Groq;
- mantêÂ©m um histêÂ³rico curto em memêÂ³ria;
- divide respostas maiores que o limite do Telegram;
- oferece apenas os comandos `/start`, `/limpar` e `/ajuda`.

## Como funciona

```text
Texto no Telegram ê¢ââ¬ê¢ââ¬ê¢ââ¬ê¢ââ¬ê¢ââ¬ê¢ââ¬ê¢ââ¬ê¢ââ¬ê¢ââ¬ê¢ââ¬ê¢ââ¬ê¢ââ¬ê¢ââ¬ê¢ââ¬ê¢ââ¬ê¢ââ¬ê¢âÂ
                                  ê¢âÅê¢ââ¬ê¢â â Codex CLI ê¢ââ¬ê¢â â resposta no Telegram
Voz/êÂ¡udio ê¢ââ¬ê¢â â Groq ê¢ââ¬ê¢â â transcriêÂ§êÂ£o ê¢âË
```

O bot nêÂ£o usa uma chave da API OpenAI. Ele executa `codex exec` com a
autenticaêÂ§êÂ£o da assinatura do Codex/ChatGPT jêÂ¡ ativa no usuêÂ¡rio do sistema. Cada
consulta êÂ© efêÂªmera, usa um diretêÂ³rio temporêÂ¡rio vazio e deixa as ferramentas do
modelo em sandbox somente leitura.

O Codex continua sujeito aos limites de uso da assinatura. A chave do Groq êÂ©
necessêÂ¡ria somente para mensagens de voz ou êÂ¡udio.

## PrêÂ©-requisitos

- Python 3.11 ou superior;
- Codex CLI instalado;
- uma assinatura com acesso ao Codex;
- um bot criado no Telegram;
- uma chave do Groq, se a transcriêÂ§êÂ£o de êÂ¡udio for utilizada.

Confira os comandos:

```bash
python3 --version
codex --version
codex login status
```

Se o Codex ainda nêÂ£o estiver autenticado, execute:

```bash
codex login
```

Conclua o acesso usando a mesma conta que possui a assinatura do Codex.

## 1. Criar o bot com o BotFather

1. Abra o Telegram e inicie uma conversa com `@BotFather`.
2. Envie `/newbot`.
3. Escolha o nome visêÂ­vel do bot.
4. Escolha um username terminado em `bot`.
5. Guarde o token entregue pelo BotFather.

NêÂ£o publique esse token e nêÂ£o o coloque diretamente no cêÂ³digo.

## 2. Descobrir seu ID do Telegram

Envie qualquer mensagem ao bot recêÂ©m-criado. Em seguida, substitua
`SEU_TOKEN` apenas no terminal e consulte as atualizaêÂ§êÂµes:

```bash
curl "https://api.telegram.org/botSEU_TOKEN/getUpdates"
```

No resultado, procure por:

```json
{"from":{"id":123456789}}
```

O nêÂºmero de `from.id` êÂ© o valor de `TELEGRAM_ALLOWED_USER_ID`. Evite salvar o
comando contendo o token no histêÂ³rico do terminal; outra opêÂ§êÂ£o êÂ© usar
temporariamente uma variêÂ¡vel local:

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

Para aceitar voz e êÂ¡udio, preencha depois:

```env
GROQ_API_KEY=sua_chave_do_groq
```

ConfiguraêÂ§êÂµes disponêÂ­veis:

| VariêÂ¡vel | ObrigatêÂ³ria | Finalidade |
|---|---:|---|
| `TELEGRAM_BOT_TOKEN` | sim | Token entregue pelo BotFather |
| `TELEGRAM_ALLOWED_USER_ID` | sim | êÅ¡nico usuêÂ¡rio autorizado |
| `CODEX_BINARY` | nêÂ£o | ExecutêÂ¡vel do Codex; padrêÂ£o `codex` |
| `CODEX_MODEL` | nêÂ£o | Modelo solicitado ao Codex; vazio usa o padrêÂ£o |
| `CODEX_TIMEOUT_SECONDS` | nêÂ£o | Tempo mêÂ¡ximo de uma resposta |
| `HISTORY_MAX_EXCHANGES` | nêÂ£o | Quantidade de pares mantidos em memêÂ³ria |
| `AI_SYSTEM_PROMPT` | nêÂ£o | Comportamento principal do assistente |
| `GROQ_API_KEY` | para êÂ¡udio | Chave usada somente na transcriêÂ§êÂ£o |
| `GROQ_TRANSCRIPTION_MODEL` | nêÂ£o | PadrêÂ£o `whisper-large-v3-turbo` |
| `GROQ_TRANSCRIPTION_LANGUAGE` | nêÂ£o | Idioma ISO-639-1; padrêÂ£o `pt` |
| `MAX_AUDIO_MB` | nêÂ£o | Limite local antes do envio ao Groq |

O arquivo `.env` êÂ© ignorado pelo Git.

## 5. Iniciar o bot

Com o ambiente virtual ativado:

```bash
python bot.py
```

O processo continuarêÂ¡ ativo por long polling. Para encerrar, pressione
`Ctrl+C`.

## 6. Testar a integraêÂ§êÂ£o

Execute primeiro os testes locais:

```bash
python -m unittest discover -v
```

Depois, no Telegram:

1. envie `/start`;
2. envie uma pergunta curta;
3. faêÂ§a uma pergunta relacionada para confirmar o histêÂ³rico;
4. envie `/limpar` e confirme que o contexto foi apagado;
5. envie uma mensagem por outra conta e confirme que nêÂ£o hêÂ¡ resposta;
6. depois de configurar o Groq, envie uma mensagem de voz.

Os erros bêÂ¡sicos aparecem no terminal, sem registrar os tokens.

## 7. Manter o bot ativo em uma VPS

Primeiro descubra os caminhos absolutos:

```bash
pwd
command -v codex
```

Coloque o caminho retornado por `command -v codex` em `CODEX_BINARY` no `.env`.
O serviêÂ§o precisa executar com o mesmo usuêÂ¡rio Linux que realizou `codex login`.

Crie `/etc/systemd/system/ARCKHÉcabot.service`:

```ini
[Unit]
Description=Assistente pessoal do Telegram
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=SEU_USUARIO
WorkingDirectory=/CAMINHO/ABSOLUTO/ARCKHÉcabot
EnvironmentFile=/CAMINHO/ABSOLUTO/ARCKHÉcabot/.env
ExecStart=/CAMINHO/ABSOLUTO/ARCKHÉcabot/.venv/bin/python bot.py
Restart=on-failure
RestartSec=5
PrivateTmp=true
NoNewPrivileges=true

[Install]
WantedBy=multi-user.target
```

Ative o serviêÂ§o:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ARCKHÉcabot
sudo systemctl status ARCKHÉcabot
```

Para acompanhar os registros:

```bash
sudo journalctl -u ARCKHÉcabot -f
```

## SoluêÂ§êÂ£o de problemas

### O bot nêÂ£o inicia

Confira as variêÂ¡veis obrigatêÂ³rias e o ID numêÂ©rico:

```bash
source .venv/bin/activate
python bot.py
```

### O Telegram responde com erro genêÂ©rico

Verifique a autenticaêÂ§êÂ£o do Codex no mesmo usuêÂ¡rio que executa o bot:

```bash
codex login status
```

Confira tambêÂ©m o caminho configurado em `CODEX_BINARY` e os logs do processo.

### A mensagem de voz nêÂ£o funciona

Confirme que `GROQ_API_KEY` foi definida e reinicie o bot. O projeto usa o
endpoint oficial de transcriêÂ§êÂ£o do Groq e, por padrêÂ£o, o modelo
`whisper-large-v3-turbo`.

### O contexto sumiu

O histêÂ³rico êÂ© intencionalmente pequeno e fica somente na memêÂ³ria. Ele êÂ© apagado
por `/limpar` e sempre que o processo êÂ© reiniciado.

## ReferêÂªncias

- [Codex CLI ê¢â¬â execuêÂ§êÂ£o nêÂ£o interativa](https://developers.openai.com/codex/cli)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Groq Speech to Text](https://console.groq.com/docs/speech-to-text)

---

Projeto  - ARCKHÉe