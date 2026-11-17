# AGENTS.md

## Visão geral

O InemacaBot é um assistente pessoal para Telegram escrito em Python. A
implementação atual:

- aceita somente o usuário definido por `TELEGRAM_ALLOWED_USER_ID`;
- responde mensagens de texto por meio do Codex CLI autenticado localmente;
- transcreve voz e áudio pelo Groq quando `GROQ_API_KEY` está configurada;
- mantém um histórico curto somente em memória;
- divide respostas longas antes de enviá-las ao Telegram;
- oferece apenas os comandos `/start`, `/ajuda` e `/limpar`.

O documento `doc/plano_implementacao.md` descreve uma possível migração para uma
API HTTP compatível com OpenAI e a remoção do suporte a áudio. Essa migração
ainda não foi implementada. Ao alterar o projeto, trate o código e o `README.md`
como a descrição do comportamento atual e não confunda o plano futuro com o
estado existente.

## Arquitetura atual

Fluxo de texto:

```text
Telegram -> autorização -> histórico -> Codex CLI -> histórico -> Telegram
```

Fluxo de áudio:

```text
Telegram -> autorização -> download -> Groq -> transcrição -> Codex CLI
         -> histórico -> Telegram
```

Arquivos principais:

- `bot.py`: ponto de entrada, handlers e composição dos serviços;
- `config.py`: carregamento e validação das variáveis de ambiente;
- `auth.py`: verificação do único usuário autorizado;
- `codex_client.py`: execução assíncrona e efêmera do Codex CLI;
- `transcription_client.py`: integração opcional com a transcrição do Groq;
- `history.py`: histórico limitado e não persistente;
- `message_utils.py`: divisão segura de respostas longas;
- `tests/`: testes unitários;
- `README.md`: instalação, configuração, operação e solução de problemas.

## Regras de implementação

- Mantenha a autorização antes de downloads, transcrições ou chamadas ao Codex.
- Usuários não autorizados devem ser ignorados silenciosamente.
- Nunca registre ou versione tokens, chaves de API ou cabeçalhos de autorização.
- Não coloque valores reais no `.env.example`.
- Adicione um par ao histórico somente depois de receber uma resposta válida.
- Preserve a trava assíncrona que mantém mensagens e histórico em ordem.
- O histórico deve continuar limitado, somente em memória e apagável por
  `/limpar`.
- Respostas ao Telegram devem respeitar o limite seguro de 4.000 caracteres.
- Erros enviados ao usuário devem ser curtos e não revelar detalhes internos.
- Mantenha o cliente do Codex em sessão efêmera, diretório temporário vazio e
  sandbox somente leitura.
- Não introduza execução de ferramentas, comandos externos pelo modelo,
  múltiplos agentes ou automações sem uma decisão explícita de produto.
- Atualize o `README.md`, o `.env.example` e os testes quando uma mudança alterar
  configuração ou comportamento observável.

## Configuração

Variáveis principais:

- `TELEGRAM_BOT_TOKEN`: obrigatória;
- `TELEGRAM_ALLOWED_USER_ID`: obrigatória e numérica;
- `CODEX_BINARY`: opcional, padrão `codex`;
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

Instalação:

```bash
python -m pip install -r requirements.txt
```

Testes:

```bash
.venv/bin/python -m unittest discover -v
```

Execução local:

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
4. verifique se usuários não autorizados continuam sem acionar serviços;
5. revise se documentação e configuração permanecem coerentes com o código.

O diretório pode não estar dentro de um repositório Git. Não presuma que
comandos como `git status` estarão disponíveis.
