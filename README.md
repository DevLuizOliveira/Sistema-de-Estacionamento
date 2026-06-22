# Sistema de Gerenciamento de Estacionamento Inteligente


---

## Sobre o Projeto

Este é um sistema de gerenciamento de estacionamento desenvolvido inteiramente em **Python**, projetado para execução via terminal. Ele simula a operação diária de um pátio de veículos, oferecendo controle automatizado de entrada, saída, visualização de ocupação e configurações dinâmicas de infraestrutura.

O grande diferencial do sistema é a inteligência na **tomada de decisão para alocação de veículos** e a **persistência robusta de dados** utilizando um banco de dados relacional **MySQL**, garantindo integridade, segurança e histórico unificado das operações do pátio.

---

## Funcionalidades Integradas

* **Alocação Automatizada e Inteligente:** O usuário não precisa adivinhar ou escolher a vaga. O sistema calcula e designa automaticamente a melhor vaga disponível com base em critérios de segurança.
* **Geração de Tickets em PDF:** Emissão automática de comprovantes de entrada (com QR Code escaneável) e recibos de saída detalhados.
* **Validação e Unificação de Placas (Regex):** Suporte rigoroso para formatos de placas brasileiras. O sistema traduz e unifica automaticamente o histórico de veículos que transitaram do Padrão Antigo (AAA0000) para o Mercosul (AAA0A00).
* **Gestão de Acessibilidade:** Tratamento exclusivo para vagas PCD (Pessoas com Deficiência), respeitando as regras de negócio e restrições de exclusividade.
* **Menu de Configuração com Trava de Segurança:** Permite alterar o número total de vagas e redefinir as preferências PCD em tempo de execução, bloqueando reduções de pátio caso existam veículos ocupando as vagas a serem excluídas.
* **Mapa Visual do Pátio:** Renderização em tempo real no terminal, indicando de forma clara as vagas livres, ocupadas (com dados do veículo) e reservadas.
* **Simulação de Colisão:** Motor probabilístico que calcula o risco de incidentes durante as manobras com base no adensamento das vagas adjacentes.
* **Auditoria Invisível (Logs):** Registro silencioso e cronológico de todas as operações no arquivo estaciona4.log.

---

## O Algoritmo de Designação de Vagas (Score)

Para mitigar o risco de colisões no pátio, o sistema adota um algoritmo guloso de seleção baseado em **Pontuação de Isolamento (Score)**. Ao solicitar uma entrada, o sistema analisa as vagas livres da categoria escolhida e calcula o nível de segurança de cada uma:

| Pontuação | Cenário de Vagas Vizinhas | Nível de Risco de Colisão |
| :---: | :--- | :--- |
| **Score 3** | Ambos os lados estão vazios (ou é uma parede lateral) | **Mínimo (0%)** |
| **Score 2** | Um dos lados está ocupado por outro veículo | **Médio (15%)** |
| **Score 1** | Ambos os lados já possuem veículos estacionados | **Máximo (35%)** |

> **Regra de Ouro:** O sistema sempre priorizará e entregará ao motorista a vaga de maior Score disponível no momento, reduzindo drasticamente a chance de acidentes nas manobras.

---

## Tecnologias e Bibliotecas Utilizadas

O sistema utiliza bibliotecas externas modernas combinadas com o ecossistema nativo do Python:

**Bibliotecas de Terceiros (Necessário Instalar):**
* mysql-connector-python: Para conexão e manipulação estrutural do banco de dados MySQL.
* fpdf2: Para a criação, formatação e exportação dos tickets e comprovantes em formato PDF.
* qrcode: Para a geração dinâmica de códigos QR embutidos nos tickets de entrada.

**Módulos Nativos:**
* logging: Para rastreamento de eventos e auditoria em segundo plano.
* os: Para checagem e gerenciamento de diretórios locais (pastas de PDFs).
* re: Para validação de integridade de strings via Expressões Regulares.
* random: Para alimentar o motor de simulação probabilística de incidentes.
* datetime: Para marcação de tempo real nos registros e tickets.

---

## Como Executar

### Pré-requisitos
* Python 3.12+ instalado.
* Servidor MySQL local ou remoto rodando.

### Passos para Execução
1. Baixe ou clone os arquivos do projeto para um diretório local.
2. Abra o seu terminal (ou prompt de comando) e instale as dependências executando o comando abaixo:
   pip install mysql-connector-python fpdf2 qrcode

3. Edite o arquivo config.py e insira as credenciais do seu servidor MySQL (usuário, senha e host).
4. Execute o script principal:
   python estacionamento.py

5. Na primeira execução, o sistema criará automaticamente o banco de dados estacionamento, as tabelas necessárias, o arquivo de log e as pastas para os tickets em PDF.

---

## Estrutura de Arquivos

├── estacionamento.py    # Código-fonte principal com a lógica do sistema.
├── config.py            # Arquivo de configuração de credenciais do MySQL.
├── ticketsentrada/      # (Gerado automaticamente) Diretório de PDFs de entrada.
├── ticketssaida/        # (Gerado automaticamente) Diretório de PDFs de saída.
├── estaciona4.log       # (Gerado automaticamente) Histórico de atividades do sistema.
└── README.md            # Documentação do projeto.