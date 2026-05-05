# AI_ORQ_2BRAIN - Intelligent Agent Orchestration + Second Brain

Sistema de orquestração de agentes de IA com Second Brain (base de conhecimento dinâmica) focado em automação de processos de consultoria, contabilidade e serviços profissionais.

## Visão Geral

O AI_ORQ_2BRAIN automatiza a qualificação de leads, validação de conformidade e geração de propostas comerciais usando múltiplos agentes especializados com memória persistente.

## Tecnologias

- **Backend**: Python 3.11+ com FastAPI
- **Servidor**: Uvicorn (ASGI)
- **Base de Conhecimento**: Obsidian (via Local REST API ou acesso direto a arquivos)
- **Frontend**: Dashboard Kanban em JavaScript (single-page)
- **Validação**: Pydantic
- **HTTP**: httpx
- **Configuração**: python-dotenv

## Estrutura do Projeto

```
AI_ORQ_2BRAIN/
├── src/
│   ├── agents/          # Agentes de IA especializados
│   │   ├── guardian.py  # Validação de conformidade (RGPD/LGPD)
│   │   ├── scorer.py    # Pontuação de leads (Hot/Warm/Cold)
│   │   └── generator.py # Geração de propostas
│   ├── orchestrator/    # Coordenação do fluxo de agentes
│   ├── memory/          # Second Brain (integração Obsidian)
│   └── api/             # Endpoints FastAPI
├── second-brain/        # Obsidian vault (base de conhecimento)
│   ├── clients/         # Notas de clientes
│   ├── rules/           # Regras de negócio
│   ├── templates/       # Templates de propostas
│   └── history/         # Logs de eventos
├── frontend/
│   └── index.html       # Dashboard Kanban
├── requirements.txt     # Dependências Python
├── start.bat           # Script de inicialização (Windows)
└── .env                # Configuração da API Obsidian
```

## Funcionalidades

### Agentes Especializados

- **Guardian Agent**: Valida conformidade RGPD/LGPD e sensibilidade de dados
- **Scorer Agent**: Qualifica leads (pontuação 0-100, classificação Hot/Warm/Cold)
- **Generator Agent**: Gera propostas automaticamente para leads Hot

### Second Brain (Obsidian)

- Armazenamento de dados de clientes com metadados (frontmatter)
- Regras e templates pesquisáveis
- Histórico de eventos
- Fallback para acesso direto a arquivos se a API não estiver disponível

### Dashboard Operacional

- Kanban board (leads Hot/Warm/Cold)
- Formulário de cadastro de leads com preview de pontuação
- Interface de busca no Second Brain
- Status em tempo real da API e Obsidian

## API Endpoints

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/lead` | POST | Processa lead através do pipeline completo |
| `/api/leads` | GET | Lista todos os leads do Obsidian |
| `/api/brain/search` | POST | Pesquisa na base de conhecimento |
| `/api/status` | GET | Health check do sistema |

Documentação interativa em `/docs`.

## Instalação e Uso

1. Clone o repositório:
```bash
git clone https://github.com/ugleybson/AI_ORQ_2BRAIN.git
cd AI_ORQ_2BRAIN
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o arquivo `.env` com a URL da API do Obsidian (opcional)

4. Execute o projeto:
```bash
# Windows
start.bat

# Ou manualmente
uvicorn src.api.main:app --reload
```

5. Acesse:
   - Dashboard: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`

## Fluxo de Processamento

1. **Compliance Check** - Guardian valida conformidade
2. **Score Calculation** - Scorer pontua o lead
3. **Save to Obsidian** - Dados salvos no Second Brain
4. **Generate Proposal** - Generator cria proposta (se Hot)

## Status

MVP funcional - pipeline de processamento de leads operacional com integração Obsidian para gestão persistente de conhecimento.
