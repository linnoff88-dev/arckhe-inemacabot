# Plano de implementaçêo — Bot simples para Telegram

Este plano segue o documento
[`prompt_bot_telegram (1).md`](prompt_bot_telegram%20(1).md). Esta etapa é
exclusivamente de planejamento: nenhum código, dependência ou configuraçêo do
bot deve ser alterado antes da aprovaçêo das decisões pendentes.

## 1. Objetivo

Adequar o projeto para que um único usuário autorizado possa:

1. enviar uma mensagem de texto ao bot no Telegram;
2. ter a mensagem encaminhada a uma API de IA compatível com o formato da
   OpenAI;
3. receber a resposta no próprio Telegram;
4. manter um contexto curto entre mensagens;
5. apagar esse contexto com `/limpar`.

O bot nêo executará ferramentas, automações, agentes, filas ou ações externas.

## 2. Diagnóstico do repositório atual

O projeto nêo está vazio. Já existem código, documentaçêo e testes, porém a
implementaçêo atual nêo corresponde integralmente ao prompt escolhido:

- as respostas sêo geradas pelo Codex CLI autenticado na máquina;
- nêo sêo usadas as variáveis `AI_API_KEY`, `AI_BASE_URL` e `AI_MODEL`;
- há suporte adicional a voz e áudio por meio do Groq;
- o README e o `.env.example` descrevem Codex e Groq;
- o histórico, a autorizaçêo, a divisêo de mensagens e os três comandos
  solicitados já possuem componentes que podem ser adaptados;
- há testes unitários que poderêo ser reaproveitados e atualizados.

A implementaçêo deverá, portanto, ser uma adequaçêo controlada do projeto
existente, e nêo a criaçêo indiscriminada de um segundo bot.

## 3. Escopo proposto

### Incluído

- Python 3.11 ou superior;
- API oficial de bots do Telegram, por long polling;
- somente mensagens de texto;
- somente os comandos `/start`, `/limpar` e `/ajuda`;
- autorizaçêo por `TELEGRAM_ALLOWED_USER_ID` antes de qualquer chamada à IA;
- cliente HTTP para endpoint compatível com OpenAI;
- modelo, URL base e chave definidos por variáveis de ambiente;
- instruçêo de sistema configurável;
- histórico curto armazenado somente em memória;
- serializaçêo das mensagens para preservar a ordem do histórico;
- divisêo segura de respostas longas;
- logs básicos sem segredos;
- testes unitários e documentaçêo de instalaçêo, uso e operaçêo em VPS.

### Fora do escopo

- mensagens de voz, áudio, imagens ou documentos;
- transcriçêo pelo Groq;
- Codex CLI;
- banco de dados ou histórico persistente;
- múltiplos usuários;
- webhook, painel administrativo ou interface web;
- execuçêo de comandos, ferramentas, agentes ou automações;
- streaming de respostas;
- comandos adicionais.

## 4. Arquitetura proposta

```text
Mensagem de texto no Telegram
        ↓
Validar TELEGRAM_ALLOWED_USER_ID
        ↓
Obter histórico recente em memória
        ↓
Montar system + histórico + mensagem atual
        ↓
POST para a API compatível com OpenAI
        ↓
Validar e registrar o novo par no histórico
        ↓
Dividir a resposta em blocos seguros
        ↓
Responder no Telegram
```

Estrutura prevista:

```text
ARCKHÉcabot/
├── bot.py
├── ai_client.py
├── auth.py
├── config.py
├── history.py
├── message_utils.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── tests/
│   ├── test_ai_client.py
│   ├── test_auth.py
│   ├── test_bot.py
│   ├── test_config.py
│   ├── test_history.py
│   └── test_message_utils.py
└── doc/
    ├── prompt_bot_telegram (1).md
    └── plano_implementacao.md
```

## 5. Variáveis de ambiente

As variáveis exigidas pelo prompt serêo:

```env
TELEGRAM_BOT_TOKEN=
TELEGRAM_ALLOWED_USER_ID=
AI_API_KEY=
AI_BASE_URL=
AI_MODEL=
```

Também serêo propostas duas configurações opcionais:

```env
AI_SYSTEM_PROMPT=
HISTORY_MAX_EXCHANGES=10
```

O código deverá:

- exigir as cinco variáveis principais na inicializaçêo;
- validar que o ID do Telegram seja um número inteiro;
- normalizar a URL base para evitar barras duplicadas;
- rejeitar instruçêo de sistema vazia;
- aplicar valores padrêo apenas às opções documentadas;
- exibir erros de configuraçêo sem imprimir valores sensíveis.

O valor padrêo de `AI_SYSTEM_PROMPT` será exatamente a instruçêo definida no
prompt de requisitos.

## 6. Etapas de implementaçêo futura

### Etapa 1 — Confirmar decisões e preparar os segredos

- confirmar provedor, URL base e modelo;
- confirmar que voz/áudio e Codex CLI serêo removidos;
- confirmar o tamanho desejado do histórico;
- obter o token do BotFather e o ID autorizado;
- configurar os valores reais somente no `.env` local, nunca no código, Git,
  documentaçêo, testes ou conversa.

Saída esperada: decisões aprovadas e ambiente local pronto, sem exposiçêo das
chaves.

### Etapa 2 — Adequar a configuraçêo

- substituir as configurações de Codex e Groq pelas variáveis `AI_*`;
- manter a instruçêo de sistema configurável;
- validar todas as entradas na inicializaçêo;
- atualizar `.env.example` somente com campos vazios e valores nêo secretos;
- confirmar que `.env` permanece ignorado pelo Git.

Saída esperada: configuraçêo consistente com o prompt e falha rápida quando
algo obrigatório estiver ausente.

### Etapa 3 — Criar o cliente da IA

- substituir `codex_client.py` por `ai_client.py`;
- enviar requisiçêo autenticada ao endpoint de chat compatível com OpenAI;
- montar a lista de mensagens com `system`, histórico e mensagem atual;
- definir timeout de conexêo e resposta;
- aceitar somente resposta textual nêo vazia;
- traduzir falhas HTTP, timeout, JSON inválido e resposta inválida para erros
  internos seguros;
- nunca registrar cabeçalhos de autenticaçêo ou o corpo completo das
  requisições.

Saída esperada: cliente isolado, assíncrono e testável sem chamadas reais nos
testes.

### Etapa 4 — Simplificar o bot do Telegram

- manter os handlers de `/start`, `/limpar`, `/ajuda` e texto;
- remover o handler de voz/áudio e a integraçêo de transcriçêo;
- verificar o usuário antes de processar todos os comandos e mensagens;
- ignorar silenciosamente usuários nêo autorizados;
- exibir a açêo “digitando” enquanto a resposta é preparada;
- usar uma trava assíncrona para manter histórico e respostas na ordem;
- enviar uma mensagem curta e segura quando a IA estiver indisponível.

Saída esperada: fluxo mínimo exigido, sem funcionalidades laterais.

### Etapa 5 — Manter histórico e respostas longas

- preservar o histórico somente em memória;
- limitar o histórico pelos últimos pares usuário/assistente;
- adicionar um par apenas após resposta válida da IA;
- apagar todo o histórico com `/limpar`;
- confirmar que reiniciar o processo também apaga o histórico;
- dividir respostas com margem segura de 4.000 caracteres;
- preferir divisões por parágrafo, linha e espaço antes de corte rígido;
- preservar integralmente a ordem e o conteúdo.

Saída esperada: contexto previsível e respostas compatíveis com o limite do
Telegram.

### Etapa 6 — Atualizar dependências e documentaçêo

- manter somente as dependências realmente usadas;
- documentar criaçêo do bot no BotFather;
- documentar como descobrir o ID do Telegram;
- explicar configuraçêo do `.env`;
- fornecer comandos exatos de ambiente virtual, instalaçêo e execuçêo;
- explicar os testes manuais e automatizados;
- fornecer exemplo de serviço `systemd` para VPS;
- documentar diagnóstico de autenticaçêo, URL, modelo, timeout e indisponibilidade
  da API.

Saída esperada: uma pessoa consegue instalar e operar o bot partindo apenas do
README.

### Etapa 7 — Testar e revisar

- atualizar os testes existentes;
- adicionar testes do cliente da IA com transporte HTTP simulado;
- testar autorizaçêo antes de qualquer consumo da API;
- testar os três comandos;
- testar limite, ordem e limpeza do histórico;
- testar divisêo de mensagens;
- testar configuraçêo ausente e inválida;
- testar sucesso, timeout, erro HTTP, JSON inválido e resposta vazia da IA;
- executar a suíte completa e verificaçêo de sintaxe/importações;
- procurar segredos acidentalmente versionados;
- revisar o diff final para confirmar que nenhuma funçêo fora do escopo
  permaneceu.

Saída esperada: implementaçêo validada localmente, pronta para teste integrado
com as credenciais reais.

## 7. Estratégia de testes

### Testes automatizados

- nenhuma chamada real ao Telegram ou ao provedor de IA;
- mocks para a API de IA e objetos de atualizaçêo do Telegram;
- cobertura dos caminhos de sucesso, autorizaçêo e falha;
- garantia explícita de que usuário nêo autorizado nêo aciona o cliente da IA.

### Teste integrado manual

1. iniciar o bot com o `.env` local;
2. enviar `/start` e conferir a mensagem exata;
3. enviar uma pergunta simples;
4. enviar uma pergunta de continuaçêo para validar o contexto;
5. usar `/limpar` e verificar que o contexto anterior nêo é usado;
6. enviar texto longo e conferir todos os blocos na ordem;
7. usar outra conta e confirmar que o bot nêo responde nem chama a IA;
8. simular modelo ou URL inválida e confirmar mensagem segura mais log técnico;
9. reiniciar o processo e confirmar que o histórico foi apagado.

## 8. Segurança

- segredos existirêo somente no `.env` local ou no gerenciador de ambiente da
  VPS;
- o `.env.example` nunca conterá valores reais;
- o ID será validado antes da chamada paga à IA;
- logs nêo conterêo token do Telegram, chave de IA ou cabeçalho `Authorization`;
- mensagens de usuários nêo autorizados nêo serêo registradas;
- respostas de erro enviadas ao Telegram nêo revelarêo detalhes internos;
- dependências terêo faixas de versões documentadas e serêo revisadas antes da
  instalaçêo.

## 9. Critérios de aceite

A implementaçêo futura estará concluída quando:

- apenas o ID autorizado puder usar o bot;
- mensagens de texto forem respondidas pela API configurada;
- o modelo puder ser trocado pelo `.env`;
- `/start`, `/limpar` e `/ajuda` funcionarem conforme o prompt;
- o contexto recente for mantido e puder ser apagado;
- respostas longas chegarem completas e na ordem;
- reinícios e erros da API nêo expuserem segredos;
- nêo restarem Codex CLI, Groq, áudio, agentes ou automações no fluxo;
- todos os testes automatizados passarem;
- o README permitir configurar, testar e manter o bot em uma VPS.

## 10. Decisões pendentes antes da implementaçêo

1. Qual provedor compatível com OpenAI será usado?
2. Qual será o valor de `AI_BASE_URL`?
3. Qual será o valor de `AI_MODEL`?
4. Confirmar a remoçêo de Codex CLI e transcriçêo de áudio/Groq.
5. Confirmar se o histórico padrêo deve manter 10 pares de conversa.
6. Confirmar que o projeto atual será adaptado na raiz, sem criar uma segunda
   pasta de aplicaçêo.

O token do Telegram e a chave da IA nêo sêo necessários para aprovar este
plano. Na implementaçêo, eles deverêo ser inseridos diretamente no `.env`
local, sem serem enviados pela conversa.
