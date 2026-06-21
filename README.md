
# 🚗 Sistema de Gerenciamento de Estacionamento Inteligente


**Projeto Acadêmico - 1º Semestre** **Orientador:** Prof. Celso  

---


## 📝 Sobre o Projeto

Este é um sistema de gerenciamento de estacionamento desenvolvido inteiramente em **Python**, projetado para execução via terminal. Ele simula a operação diária de um pátio de veículos, oferecendo controle automatizado de entrada, saída, visualização de ocupação e configurações dinâmicas de infraestrutura.

O grande diferencial do sistema é a inteligência na **tomada de decisão para alocação de veículos** e a **persistência de dados** utilizando arquivos JSON, garantindo que o estado do estacionamento e suas configurações não sejam perdidos ao encerrar o programa.

---

## 🚀 Funcionalidades Cadastradas

* **Alocação Automatizada e Inteligente:** O usuário não precisa adivinhar ou escolher a vaga. O sistema calcula e designa automaticamente a melhor vaga disponível com base em critérios de segurança.
* **Validação de Placas (Regex):** Suporte e verificação rigorosa para formatos de placas brasileiras (Padrão Antigo `AAA0000` e Mercosul `AAA0A00`).
* **Gestão de Acessibilidade:** Tratamento exclusivo para vagas PCD (Pessoas com Deficiência), respeitando as regras de negócio e restrições de exclusividade.
* **Menu de Configuração Dinâmico:** Permite alterar o número total de vagas do pátio e redefinir quais delas são preferenciais em tempo de execução.
* **Mapa Visual do Pátio:** Renderização em tempo real no terminal, indicando de forma clara as vagas livres, ocupadas (com dados do veículo) e reservadas para PCD.
* **Simulação de Colisão:** Motor probabilístico que calcula o risco de incidentes durante as manobras com base no adensamento das vagas adjacentes.
* **Auditoria Invisível (Logs):** Registro silencioso e cronológico de todas as operações (entradas, saídas, alterações de configuração e alertas de colisão) no arquivo `estaciona4.log`.

---

## 🧠 O Algoritmo de Designação de Vagas (Score)

Para mitigar o risco de colisões no pátio, o sistema adota um algoritmo guloso de seleção baseado em **Pontuação de Isolamento (*Score*)**. Ao solicitar uma entrada, o sistema analisa as vagas livres da categoria escolhida e calcula o nível de segurança de cada uma:

| Pontuação | Cenário de Vagas Vizinhas | Nível de Risco de Colisão |
| :---: | :--- | :--- |
| **Score 3** | Ambos os lados estão vazios (ou é uma parede lateral) | **Mínimo (0%)** |
| **Score 2** | Um dos lados está ocupado por outro veículo | **Médio (15%)** |
| **Score 1** | Ambos os lados já possuem veículos estacionados | **Máximo (35%)** |

> 💡 **Regra de Ouro:** O sistema sempre priorizará e entregará ao motorista a vaga de maior *Score* disponível no momento, reduzindo drasticamente a chance de acidentes nas manobras.

---

## 🛠️ Tecnologias e Bibliotecas Utilizadas

O sistema foi construído seguindo preceitos de portabilidade, utilizando apenas módulos nativos do ecossistema Python:
* `json`: Para persistência e manipulação da base de dados e configurações estruturais.
* `logging`: Para rastreamento de eventos e auditoria em segundo plano.
* `os`: Para checagem e gerenciamento do sistema de arquivos.
* `re`: Para validação de integridade de strings via Expressões Regulares.
* `random`: Para alimentar o motor de simulação probabilística de incidentes.

---

## 💻 Como Executar

### Pré-requisitos
* Python 3.12.2 instalado no sistema operacional.

### Passos para Execução
1. Baixe ou clone os arquivos do projeto para um diretório local.
2. Abra o seu terminal (ou prompt de comando) e navegue até a pasta do projeto.
3. Execute o script principal utilizando o comando:

   ```bash
   python estacionamento.py

4. O sistema criará automaticamente os arquivos Dados.json, Config json e estaciona4.log na primeira execução.

##  Estrutura de Arquivos


├── estacionamento.py   # Código-fonte principal com a lógica do sistema.</br>
├── Dados.json          # (Gerado automaticamente) Banco de dados das vagas.</br>
├── Config.json         # (Gerado automaticamente) Parâmetros estruturais do pátio.</br>
├── estaciona4.log      # (Gerado automaticamente) Histórico de atividades do sistema.</br>
└── README.md           # Documentação do projeto.
