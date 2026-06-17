# ==============================================================================
# IMPORTAÇÃO DE BIBLIOTECAS (Módulos Nativos do Python)
# ==============================================================================
import logging  # Utilizado para registrar eventos do sistema em segundo plano (arquivos de log).
import json     # Utilizado para manipulação e persistência de dados em formato de texto.
import os       # Permite interação com o Sistema Operacional (ex: verificação da existência de arquivos).
import random   # Utilizado para geração de valores aleatórios no algoritmo de probabilidade de colisão.
import re       # Biblioteca de Expressões Regulares, utilizada para validação de padrões textuais (formato de placa).

# ==============================================================================
# CONFIGURAÇÕES GLOBAIS (Constantes e Parâmetros do Sistema)
# ==============================================================================
ARQUIVO_BD = 'Dados.json'       # Define o caminho do arquivo de persistência de dados.
ARQUIVO_CONFIG = 'Config.json' # Define o caminho do arquivo de configuração das vagas

# Configuração do sistema de Log
logging.basicConfig(
    filename='estaciona4.log', 
    encoding='utf-8',              
    level=logging.INFO, # Define a severidade mínima dos registros gravados.
    format='%(asctime)s - %(levelname)s - %(message)s', 
)

# ==============================================================================
# FUNÇÕES DE APOIO (Manipulação de Dados e Validações)
# ==============================================================================

def carregar_banco(config):
    """Inicializa o sistema: lê os dados existentes ou cria uma nova base vazia."""
    if os.path.exists(ARQUIVO_BD):
        try:
            with open(ARQUIVO_BD, 'r', encoding='utf-8') as arquivo:
                return json.load(arquivo) 
        except (json.JSONDecodeError, OSError):
            print("Falha ao ler os dados existentes. Inicializando uma nova base de dados...")
    
    # Cria vagas enumeradas de 1 até o total configurado, como chaves de texto (String)
    dados = {str(i): None for i in range(1, config['vagas_totais'] + 1)}
    salvar_banco(dados) 
    return dados


def salvar_banco(dados):
    """Sincroniza o estado atual da memória com o arquivo físico de persistência."""
    with open(ARQUIVO_BD, 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)


def carregar_config():
    """Inicializa as configurações do sistema ou cria o arquivo padrão."""
    if os.path.exists(ARQUIVO_CONFIG):
        try:
            with open(ARQUIVO_CONFIG, 'r', encoding='utf-8') as arquivo:
                return json.load(arquivo) 
        except (json.JSONDecodeError, OSError):
            print("Falha ao ler as configurações. Inicializando valores padrão...")
    
    config = {"vagas_totais": 15, "vagas_pcd": ["1"]}
    salvar_config(config) 
    return config


def salvar_config(config):
    """Sincroniza as configurações com o arquivo físico."""
    with open(ARQUIVO_CONFIG, 'w', encoding='utf-8') as arquivo:
        json.dump(config, arquivo, indent=4, ensure_ascii=False)


def menu_configuracao(config):
    """Interface de gerenciamento das configurações de vagas do pátio."""
    while True:
        print("\n" + "="*50)
        print("            CONFIGURAÇÃO DO SISTEMA")
        print("="*50)
        print(f"Total de vagas atual: {config['vagas_totais']}")
        print(f"Vagas PCD atuais: {config['vagas_pcd']}")

        opcao = input('1. Alterar Total | 2. Alterar PCD | 3. Voltar: ').strip()
        if opcao == '3':
            break

        elif opcao == '2':
            prefvagas = input("Digite o número das vagas preferenciais separadas por vírgula (ex: 1, 2, 3): ")
            listapref = [vaga.strip() for vaga in prefvagas.split(',') if vaga.strip() != ""]
            config["vagas_pcd"] = listapref
            salvar_config(config)
            print("Vagas Preferenciais atualizadas com sucesso!")
            logging.info(f"Vagas Preferenciais atualizadas para: {listapref}")

        elif opcao == '1':
            total = input("Digite o novo total de vagas do estacionamento: ")
            if total.isdigit() and int(total) > 0:
                config["vagas_totais"] = int(total)
                salvar_config(config)
                print(f'O novo total de vagas é: {total}')
                logging.info(f"Total de vagas atualizado para: {total}")
            else:
                print("Por favor, digite um número inteiro maior que 0.")
        else:
            print("Opção inválida.")


def contar_ocupadas(estacionamento):
    """Varre a estrutura de dados e contabiliza quantas vagas estão em uso."""
    return sum(1 for vaga in estacionamento.values() if vaga is not None)


def validar_placa(placa):
    """Valida se a placa informada cumpre as regras do padrão Antigo ou Mercosul."""
    padrao = r'^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$'
    return re.match(padrao, placa) is not None


def placa_ja_existe(estacionamento, placa):
    """Garante que um veículo com a mesma placa não entre duas vezes no pátio."""
    for veiculo in estacionamento.values():
        if veiculo is not None:
            placa_salva = veiculo.get('placa') if isinstance(veiculo, dict) else veiculo
            if placa_salva == placa:
                return True
    return False


# ==============================================================================
# INTERFACE E EXIBIÇÃO VISUAL
# ==============================================================================

def exibir_painel(estacionamento, config):
    """Renderiza o status atualizado do mapa de vagas no terminal."""
    ocupadas = contar_ocupadas(estacionamento) 
    livres = config['vagas_totais'] - ocupadas           

    print("\n" + "="*50)
    print("            MAPA DO ESTACIONAMENTO")
    print("="*50)

    for i in range(1, config['vagas_totais'] + 1):
        chave = str(i) 
        veiculo = estacionamento.get(chave, None) 

        if veiculo is None: 
            if chave in config['vagas_pcd']:
                status = "Livre (PCD)" 
            else:
                status = "Livre"
        else: 
            if isinstance(veiculo, dict):
                status = f"Ocupada: {veiculo['placa']} | {veiculo['tipo']} | Marca: {veiculo['marca']}"
            else:
                status = f"Ocupada: {veiculo}"

        print(f"Vaga {i:02d}: [ {status} ]")

    print("-"*50)
    print(f"{ocupadas} ocupadas | {livres} livres")
    print("="*50)


# ==============================================================================
# ALGORITMO DE SELEÇÃO INTELIGENTE E COLISÃO
# ==============================================================================

def verificar_colisao(vaga, estacionamento):
    """Calcula a probabilidade de incidentes com base no adensamento vizinho."""
    vaga = int(vaga) 
    vizinhos = 0     

    if str(vaga - 1) in estacionamento and estacionamento[str(vaga - 1)]:
        vizinhos += 1

    if str(vaga + 1) in estacionamento and estacionamento[str(vaga + 1)]:
        vizinhos += 1

    chance = 0.15 if vizinhos == 1 else 0.35 if vizinhos == 2 else 0

    if random.random() < chance:
        print("\n!!! ATENÇÃO: Colisão detectada ao realizar a manobra !!!")
        logging.warning(f"Colisão simulada na vaga {vaga}")


def designar_vaga(estacionamento, tipo, config):
    """Busca vagas elegíveis e escolhe a melhor com base no score de isolamento."""
    total = config["vagas_totais"]
    vagas_pcd = set(config["vagas_pcd"]) if config["vagas_pcd"] else set()

    # Filtra as candidatas corretas baseando-se no tipo do veículo
    if tipo.upper() == "PCD":
        candidatas = [v for v in range(1, total + 1) if str(v) in vagas_pcd and estacionamento.get(str(v)) is None]
    else:
        candidatas = [v for v in range(1, total + 1) if str(v) not in vagas_pcd and estacionamento.get(str(v)) is None]

    if not candidatas:
        return None
    
    def lado_vazio(vaga_id, lado):
        vizinho = vaga_id + lado
        if vizinho < 1 or vizinho > total:
            return True  # Paredes laterais são consideradas seguras
        return estacionamento.get(str(vizinho)) is None
    
    def calcular_score(vaga_id):
        esq = lado_vazio(vaga_id, -1)
        dir = lado_vazio(vaga_id, 1)
        if esq and dir:
            return 3  # Excelente: Ambos os lados vazios
        elif esq or dir:
            return 2  # Bom: Um lado vazio
        else:
            return 1  # Apertado: Ambos ocupados
    
    melhor_vaga = None
    maior_pontuacao = -1

    for vaga in candidatas:
        pontos = calcular_score(vaga)
        
        # Se achar uma vaga perfeita (isolada), aloca imediatamente
        if pontos == 3:
            return vaga
            
        if pontos > maior_pontuacao:
            maior_pontuacao = pontos
            melhor_vaga = vaga

    return melhor_vaga


# ==============================================================================
# FLUXO PRINCIPAL DE EXECUÇÃO
# ==============================================================================

def main():
    """Função central que gerencia o menu interativo e o fluxo do sistema."""
    config = carregar_config()
    estacionamento = carregar_banco(config)

    logging.info("Sistema de Estacionamento iniciado.")
    print("\n--- Sistema de Estacionamento Inteligente ---")

    while True:
        acao_bruta = input("\n(1) Entrada | (2) Saída | (3) Ver vagas | (4) Configurações | (#) Sair: ").strip()
        
        if acao_bruta == '#':
            acao = '#'
        else:
            acao_limpa = "".join(char for char in acao_bruta if char.isdigit())
            if acao_limpa != "":
                acao = str(int(acao_limpa))
            else:
                acao = acao_bruta 

        # ===================== OPERAÇÃO: ENTRADA =====================
        if acao == '1':
            if contar_ocupadas(estacionamento) >= config['vagas_totais']:
                print("Estacionamento completamente cheio.")
                continue 

            placa = input("Placa do Veículo: ").strip().upper()

            if not validar_placa(placa):
                print("Placa inválida. Utilize o formato Padrão (AAA0000) ou Mercosul (AAA0A00).")
                continue

            if placa_ja_existe(estacionamento, placa):
                print("Esse veículo já possui um registro ativo no pátio.")
                continue

            tipo_veiculo = "Carro"
            marca_carro = input("Marca do veículo (ex: Honda, Fiat): ").strip().title()
            tipo_vaga = input("Escolha o tipo de vaga desejada (normal/pcd): ").strip().lower()

            # Algoritmo determina a melhor vaga disponível
            vaga_designada = designar_vaga(estacionamento, tipo_vaga, config)
            
            if vaga_designada is None:
                print(f"Não existem vagas disponíveis ou livres para a categoria: {tipo_vaga}")
                continue
                
            vaga = str(vaga_designada)
            print(f'Sua vaga designada é de número: {vaga}')

            # Registra as informações do veículo na vaga no formato de dicionário
            estacionamento[vaga] = {
                "placa": placa,
                "tipo": tipo_veiculo,
                "marca": marca_carro
            }
            salvar_banco(estacionamento) 

            logging.info(f"ENTRADA: {tipo_veiculo} {marca_carro} (Placa {placa}) alocado na vaga {vaga}.")
            print("Registro de entrada processado com sucesso!")
            
            # Executa a simulação de colisões
            verificar_colisao(vaga, estacionamento)

        # ===================== OPERAÇÃO: SAÍDA =====================
        elif acao == '2':
            vaga_bruta = input("Informe o número da vaga para saída: ").strip()
            vaga_limpa = "".join(char for char in vaga_bruta if char.isdigit())

            if vaga_limpa != "":
                vaga = str(int(vaga_limpa)) 
            else:
                vaga = vaga_bruta 

            if vaga not in estacionamento:
                print("Vaga inválida no escopo do sistema.")
                continue

            if estacionamento[vaga] is None:
                print("Inconsistência: Não há nenhum veículo registrado nesta vaga.")
                continue

            veiculo_saindo = estacionamento[vaga]
            placa_saida = veiculo_saindo['placa'] if isinstance(veiculo_saindo, dict) else veiculo_saindo

            print(f"Registro de saída processado para o veículo de placa: {placa_saida}.")
            logging.info(f"SAÍDA: Veículo placa {placa_saida} desocupou a vaga {vaga}.")
            
            # Libera o espaço limpando a chave para None
            estacionamento[vaga] = None 
            salvar_banco(estacionamento) 

        # ===================== OPERAÇÃO: CONSULTA =====================
        elif acao == '3':
            exibir_painel(estacionamento, config)

        # ===================== OPERAÇÃO: CONFIGURAÇÕES =====================
        elif acao == '4':
            menu_configuracao(config)
            # Sincroniza o banco caso o número total de vagas tenha aumentado
            estacionamento = carregar_banco(config)

        # ===================== OPERAÇÃO: ENCERRAMENTO =====================
        elif acao == '#':
            print("Processo de encerramento do sistema iniciado...")
            logging.info("Sistema de Estacionamento encerrado pelo usuário.")
            break 

        else:
            print("Opção de comando não reconhecida no menu principal.")

# ==============================================================================
# PONTO DE ENTRADA DO SCRIPT
# ==============================================================================
if __name__ == "__main__":
    main()