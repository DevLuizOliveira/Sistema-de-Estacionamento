#  Sistema de Gerenciamento de Estacionamento

**Projeto Acadêmico - 1º Semestre** **Orientador:** Prof. Celso  

---

##  Sobre o Projeto

Este projeto é um sistema de gerenciamento de estacionamento desenvolvido inteiramente em **Python**, projetado para ser executado via terminal. Ele simula a operação diária de um pátio de veículos, oferecendo controle de entrada, saída, visualização de ocupação e configurações dinâmicas de infraestrutura.

O grande diferencial do sistema é a sua **persistência de dados** utilizando arquivos JSON, garantindo que o estado do estacionamento e suas configurações (como número de vagas e vagas exclusivas) não sejam perdidos ao encerrar o programa.

##  Funcionalidades

* **Controle de Entrada e Saída:** Registro detalhado de veículos contendo placa, tipo e marca.
* **Validação de Placas:** Suporte e verificação para formatos de placas brasileiras (Padrão Antigo e Mercosul) utilizando Expressões Regulares (Regex).
* **Gestão de Acessibilidade:** Tratamento exclusivo para vagas PCD, impedindo a alocação indevida de veículos comuns.
* **Menu de Configuração Dinâmico:** Capacidade de alterar o número total de vagas e designar quais delas são preferenciais em tempo de execução.
* **Mapa Visual:** Renderização do pátio em tempo real no terminal, indicando vagas livres, ocupadas e reservadas.
* **Simulação de Colisão:** Algoritmo probabilístico que calcula o risco de incidentes durante as manobras com base no adensamento das vagas adjacentes.
* **Auditoria Invisível (Logs):** Todos os eventos de entrada, saída e colisões são registrados em um arquivo `estaciona4.log` em segundo plano.

##  Tecnologias e Bibliotecas Utilizadas

O sistema foi construído sem dependências externas, utilizando apenas módulos nativos do Python:
* `json`: Para persistência e manipulação da base de dados e configurações.
* `logging`: Para rastreamento de eventos e auditoria silenciosa.
* `os`: Para interação com o sistema de arquivos.
* `re`: Para validação de integridade dos dados inseridos pelo usuário.
* `random`: Para o motor de simulação probabilística.

##  Como Executar

### Pré-requisitos
* Python 3.x instalado na máquina.

### Passos
1. Clone este repositório ou baixe os arquivos para um diretório local.
2. Abra o terminal e navegue até a pasta do projeto.
3. Execute o script principal:
   ```bash
   python estacionamento.py

4. O sistema criará automaticamente os arquivos Dados.json, Config json e estaciona4.log na primeira execução.

##  Estrutura de Arquivos

/
├── estacionamento.py   # Código-fonte principal com a lógica do sistema.
├── Dados.json          # (Gerado automaticamente) Banco de dados das vagas.
├── Config.json         # (Gerado automaticamente) Parâmetros estruturais do pátio.
├── estaciona4.log      # (Gerado automaticamente) Histórico de atividades do sistema.
└── README.md           # Documentação do projeto.