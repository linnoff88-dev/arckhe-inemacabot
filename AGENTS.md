# AGENTS.md

## Visêo geral

O InemacaBot é um assistente pessoal para Telegram escrito em Python. A
implementaçêo atual:

- aceita somente o usuário definido por `TELEGRAM_ALLOWED_USER_ID`;
- responde mensagens de texto por meio do Codex CLI autenticado localmente;
- transcreve voz e áudio pelo Groq quando `GROQ_API_KEY` está configurada;
- mantém um histórico curto somente em memória;
- divide respostas longas antes de enviá-las ao Telegram;
- oferece apenas os comandos `/start`, `/ajuda` e `/limpar`.

O documento `doc/plano_implementacao.md` descreve uma possível migraçêo para uma
API HTTP compatível com OpenAI e a remoçêo do suporte a áudio. Essa migraçêo
ainda nêo foi implementada. Ao alterar o projeto, trate o código e o `README.md`
como a descriçêo do comportamento atual e nêo confunda o plano futuro com o
estado existente.

## Arquitetura atual

Fluxo de texto:

```text
Telegram -> autorizaçêo -> histórico -> Codex CLI -> histórico -> Telegram
```

Fluxo de áudio:

```text
Telegram -> autorizaçêo -> download -> Groq -> transcriçêo -> Codex CLI
         -> histórico -> Telegram
```

Arquivos principais:

- `bot.py`: ponto de entrada, handlers e composiçêo dos serviços;
- `config.py`: carregamento e validaçêo das variáveis de ambiente;
- `auth.py`: verificaçêo do único usuário autorizado;
- `codex_client.py`: execuçêo assíncrona e efêmera do Codex CLI;
- `transcription_client.py`: integraçêo opcional com a transcriçêo do Groq;
- `history.py`: histórico limitado e nêo persistente;
- `message_utils.py`: divisêo segura de respostas longas;
- `tests/`: testes unitários;
- `README.md`: instalaçêo, configuraçêo, operaçêo e soluçêo de problemas.

## Regras de implementaçêo

- Mantenha a autorizaçêo antes de downloads, transcrições ou chamadas ao Codex.
- Usuários nêo autorizados devem ser ignorados silenciosamente.
- Nunca registre ou versione tokens, chaves de API ou cabeçalhos de autorizaçêo.
- Nêo coloque valores reais no `.env.example`.
- Adicione um par ao histórico somente depois de receber uma resposta válida.
- Preserve a trava assíncrona que mantém mensagens e histórico em ordem.
- O histórico deve continuar limitado, somente em memória e apagável por
  `/limpar`.
- Respostas ao Telegram devem respeitar o limite seguro de 4.000 caracteres.
- Erros enviados ao usuário devem ser curtos e nêo revelar detalhes internos.
- Mantenha o cliente do Codex em sessêo efêmera, diretório temporário vazio e
  sandbox somente leitura.
- Nêo introduza execuçêo de ferramentas, comandos externos pelo modelo,
  múltiplos agentes ou automações sem uma decisêo explícita de produto.
- Atualize o `README.md`, o `.env.example` e os testes quando uma mudança alterar
  configuraçêo ou comportamento observável.

## Configuraçêo

Variáveis principais:

- `TELEGRAM_BOT_TOKEN`: obrigatória;
- `TELEGRAM_ALLOWED_USER_ID`: obrigatória e numérica;
- `CODEX_BINARY`: opcional, padrêo `codex`;
- `CODEX_MODEL`: opcional;
- `CODEX_TIMEOUT_SECONDS`: opcional;
- `HISTORY_MAX_EXCHANGES`: opcional;
- `AI_SYSTEM_PROMPT`: opcional;
- `GROQ_API_KEY`: necessária somente para áudio;
- `GROQ_TRANSCRIPTION_MODEL`: opcional;
- `GROQ_TRANSCRIPTION_LANGUAGE`: opcional;
- `MAX_AUDIO_MB`: opcional.

O processo deve executar com o mesmo usuário do sistema que realizou
`codex login`.

## Ambiente e comandos

Use o ambiente virtual existente quando disponível:

```bash
source .venv/bin/activate
```

Instalaçêo:

```bash
python -m pip install -r requirements.txt
```

Testes:

```bash
.venv/bin/python -m unittest discover -v
```

Execuçêo local:

```bash
.venv/bin/python bot.py
```

Antes de iniciar o bot, confira:

```bash
codex --version
codex login status
```

## Critérios para alterações

Antes de concluir uma mudança:

1. execute toda a suíte de testes;
2. adicione testes para caminhos novos e casos de erro relevantes;
3. confirme que nenhum segredo foi incluído nos arquivos;
4. verifique se usuários nêo autorizados continuam sem acionar serviços;
5. revise se documentaçêo e configuraçêo permanecem coerentes com o código.

O diretório pode nêo estar dentro de um repositório Git. Nêo presuma que
comandos como `git status` estarêo disponíveis.
