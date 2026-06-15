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
ARQUIVO_BD = 'Dados.json' # Define o caminho do arquivo de persistência de dados.
ARQUIVO_CONFIG = 'Config.json' # Define o caminho do arquivo de configuração das vagas

# Configuração do sistema de Log
# Registra eventos silenciosos em 'estaciona4.log' para auditoria futura, sem poluir a tela do usuário.
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
    
    # Verifica se o arquivo de persistência já existe no diretório.
    if os.path.exists(ARQUIVO_BD):
        # Bloco de Tratamento de Exceções (try/except):
        # Previne a interrupção abrupta do programa (crash) caso o arquivo JSON esteja corrompido.
        try:
            # Abre o arquivo em modo de leitura ('r'). O 'with' gerencia o fechamento automático do arquivo.
            with open(ARQUIVO_BD, 'r', encoding='utf-8') as arquivo:
                return json.load(arquivo) # Converte o conteúdo do arquivo para uma estrutura de Dicionário Python.
        except (json.JSONDecodeError, OSError):
            print("Falha ao ler os dados existentes. Inicializando uma nova base de dados...")
    
    # Caso seja a primeira execução ou o arquivo falhe, gera uma estrutura inicial de dados.
    # Cria vagas enumeradas de 1 a 15, atribuindo o valor 'None' (vazio) a todas elas.
    # str() transforma os números em strings para que possam ser usados como chaves no dicionário.
    dados = {str(i): None for i in range(1, config['vagas_totais'] + 1)}
    
    salvar_banco(dados) # Grava essa nova estrutura imediatamente no disco.
    return dados


def salvar_banco(dados):
    """Sincroniza o estado atual da memória com o arquivo físico de persistência."""
    # Abre o arquivo em modo de escrita ('w'), sobrescrevendo os dados anteriores com os atualizados.
    with open(ARQUIVO_BD, 'w', encoding='utf-8') as arquivo:
        # A formatação 'indent=4' garante que o arquivo JSON seja legível para humanos.
        json.dump(dados, arquivo, indent=4, ensure_ascii=False)


def carregar_config():
    """Inicializa o sistema: lê os dados existentes ou cria uma nova base vazia."""
    
    # Verifica se o arquivo de configuração já existe no diretório.
    if os.path.exists(ARQUIVO_CONFIG):
        # Bloco de Tratamento de Exceções (try/except):
        # Previne a interrupção abrupta do programa (crash) caso o arquivo JSON esteja corrompido.
        try:
            # Abre o arquivo em modo de leitura ('r'). O 'with' gerencia o fechamento automático do arquivo.
            with open(ARQUIVO_CONFIG, 'r', encoding='utf-8') as arquivo:
                return json.load(arquivo) # Converte o conteúdo do arquivo para uma estrutura de Dicionário Python.
        except (json.JSONDecodeError, OSError):
            print("Falha ao ler os dados existentes. Inicializando uma nova base de dados...")
    
    # Caso seja a primeira execução ou o arquivo falhe, gera uma estrutura inicial de dados.
    # Cria vagas enumeradas de 1 a 15, atribuindo o valor 'None' (vazio) a todas elas.
    # str() transforma os números em strings para que possam ser usados como chaves no dicionário.
    config = {"vagas_totais": 15, "vagas_pcd": ["1"]}
    
    salvar_config(config) # Grava essa nova estrutura imediatamente no disco.
    return config


def salvar_config(config):
    """Sincroniza o estado atual da memória com o arquivo físico de persistência."""
    # Abre o arquivo em modo de escrita ('w'), sobrescrevendo os dados anteriores com os atualizados.
    with open(ARQUIVO_CONFIG, 'w', encoding='utf-8') as arquivo:
        # A formatação 'indent=4' garante que o arquivo JSON seja legível para humanos.
        json.dump(config, arquivo, indent=4, ensure_ascii=False)


def menu_configuracao(config):
    while True:

        print("\n" + "="*50)
        print("           Configuracao")
        print("="*50)
        print(f"Total de vagas atual: {config['vagas_totais']}")
        print(f"Vagas PCD atuais: {config['vagas_pcd']}")

        opcao = input('1. Alterar Total | 2. Alterar PCD | 3. Voltar: ').strip()
        if opcao == '3':
            break

        elif opcao == '2':
            prefvagas = input("Digite o numero das vagas preferenciais (ex: 1, 2, 3,)")
            listapref =[vaga.strip() for vaga in prefvagas.split(',') if vaga.strip() != ""]

            config["vagas_pcd"] = listapref
            salvar_config(config)
            print("Vagas Preferenciais atualizadas com sucesso")
            logging.info(f"Vagas Preferenciais atualizadas para: {listapref}")

        elif opcao == '1':
            total = input("digite o novo total de vagas")

            if total.isdigit() and int(total) > 0:
                config["vagas_totais"] = int(total)
                salvar_config(config)
                print(f'O novo total de vagas é: {total}')
                logging.info(f"Total de vagas atualizado para: {total}")
            
            else:
                print("digite um numero maior que 0")
        
        else:
            print("opcao invalida")




def contar_ocupadas(estacionamento):
    """Varre a estrutura de dados e contabiliza quantas vagas estão em uso."""
    # Retorna o somatório de todas as chaves cujo valor seja diferente de 'None'.
    # Return sum é uma forma eficiente de contar elementos em uma sequência que atendem a uma condição específica.
    return sum(1 for vaga in estacionamento.values() if vaga is not None)


def validar_placa(placa):
    """Aplica uma validação de formato para garantir a integridade dos dados inseridos."""
    # Expressão Regular que define a regra de negócio para placas no Brasil:
    # Exige 3 letras iniciais, 1 número, 1 caractere alfanumérico e 2 números finais (Cobre formato Antigo e Mercosul).
    padrao = r'^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$'
    
    # Retorna um booleano (True/False) indicando se a placa fornecida atende aos critérios.
    return re.match(padrao, placa) is not None


def placa_ja_existe(estacionamento, placa):
    """Verificação de integridade: previne a duplicidade de um mesmo veículo no pátio."""
    # Itera sobre todas as vagas para verificar se a placa já está registrada.
    for veiculo in estacionamento.values():
        if veiculo is not None:
            # Compatibilidade retroativa (defensiva): Verifica se o dado salvo é um dicionário novo ou uma string antiga.
            # isinstance(veiculo, dict) verifica se o dado salvo é um dicionário
            placa_salva = veiculo.get('placa') if isinstance(veiculo, dict) else veiculo
            if placa_salva == placa:
                return True
    return False


# ==============================================================================
# INTERFACE E EXIBIÇÃO VISUAL
# ==============================================================================

def exibir_painel(estacionamento, config):
    """Renderiza o status atualizado do estacionamento no terminal do usuário."""
    ocupadas = contar_ocupadas(estacionamento) 
    livres = config['vagas_totais'] - ocupadas           

    # formação do mapa
    # '=' * 50 cria uma linha de 50 caracteres iguais a '=' 
    print("\n" + "="*50)
    print("           MAPA DO ESTACIONAMENTO")
    print("="*50)

    # Laço de repetição (for) que itera sobre o limite total de vagas.
    for i in range(1, config['vagas_totais'] + 1):
        chave = str(i) # Converte o índice numérico em string para buscar no dicionário de dados.
        veiculo = estacionamento.get(chave, None) 

        if veiculo is None: # Lógica para vagas disponíveis
            if chave in config['vagas_pcd']:
                status = "Livre (PCD)" # Sinalização visual para regras de exclusividade.
            else:
                status = "Livre"
        else: # Lógica para vagas em uso
            if isinstance(veiculo, dict):
                # Extrai os dados do dicionário e injeta na string (f-string)
                status = f"Ocupada: {veiculo['placa']} | {veiculo['tipo']} | Marca: {veiculo['marca']}"
            else:
                # Fallback caso encontre um dado antigo no arquivo json
                status = f"Ocupada: {veiculo}"

        # Formatação {i:02d} padroniza a exibição visual adicionando zeros à esquerda (ex: 01, 02).
        print(f"Vaga {i:02d}: [ {status} ]")

    print("-"*50)
    print(f"{ocupadas} ocupadas | {livres} livres")
    print("="*50)


# ==============================================================================
# ALGORITMO DE SIMULAÇÃO (Colisão)
# ==============================================================================

def verificar_colisao(vaga, estacionamento):
    """Calcula a probabilidade de incidentes durante a manobra com base no adensamento das vagas."""
    vaga = int(vaga) 
    vizinhos = 0     

    # Verificação de adjacência inferior (vaga anterior).
    if str(vaga - 1) in estacionamento and estacionamento[str(vaga - 1)]:
        vizinhos += 1

    # Verificação de adjacência superior (vaga seguinte).
    if str(vaga + 1) in estacionamento and estacionamento[str(vaga + 1)]:
        vizinhos += 1

    # Regra de negócio da probabilidade:
    # 1 vizinho = 15% de chance de colisão | 2 vizinhos = 35% de chance.
    chance = 0.15 if vizinhos == 1 else 0.35 if vizinhos == 2 else 0

    # Gera um valor probabilístico. Se atender à condição, aciona o evento de colisão.
    if random.random() < chance:
        print("!!! Colisão detectada ao estacionar !!!")
        # O evento é gravado no log do sistema para fins de auditoria, sem bloquear a operação.
        logging.warning(f"Colisão na vaga {vaga}")


# ==============================================================================
# FLUXO PRINCIPAL DE EXECUÇÃO
# ==============================================================================

def main():
    """Função central que gerencia o menu interativo e o direcionamento das ações."""
    
    config = carregar_config()
    # Inicializa a estrutura de dados principal do sistema.
    estacionamento = carregar_banco(config)

    

    # Registra o início da execução do sistema no log de auditoria.
    logging.info("Sistema de Estacionamento iniciado.")

    print("\n--- Sistema de Estacionamento ---")

    # Mantém o sistema operando de forma contínua até que uma condição de parada (break) seja atingida.
    while True:
        # Coleta a entrada do usuário e o método '.strip()' remove espaços acidentais nas extremidades.
        acao_bruta = input("\n(1) Entrada | (2) Saída | (3) Ver vagas | (4) Configuracoes | (#) Sair: ").strip()
        
        # Tratamento de Entrada (UX): Previne falhas se o usuário digitar textos misturados com números.
        if acao_bruta == '#':
            acao = '#'
        else:
            # Extrai estritamente os caracteres numéricos da string recebida.
            acao_limpa = "".join(char for char in acao_bruta if char.isdigit())
            
            # Se a filtragem recuperar números válidos, converte para validação no menu.
            if acao_limpa != "":
                acao = str(int(acao_limpa))
            else:
                acao = acao_bruta # Repassa a entrada original para ser capturada como 'Opção Inválida'.

        # ===================== OPERAÇÃO: ENTRADA =====================
        if acao == '1':
            # Verificação de capacidade máxima.
            if contar_ocupadas(estacionamento) >= config['vagas_totais']:
                print("Estacionamento cheio.")
                continue # Interrompe a execução deste bloco e retorna ao início do menu.

            placa = input("Placa: ").strip().upper()

            # Passa pela camada de validação e integridade.
            if not validar_placa(placa):
                print("Placa inválida. Utilize o formato Padrão ou Mercosul.")
                continue

            if placa_ja_existe(estacionamento, placa):
                print("Esse veículo já possui registro ativo no sistema.")
                continue

            # ================= NOVA REGRA DE NEGÓCIO: TIPO E MARCA =================
            # O sistema assume automaticamente a modalidade definida para a operação atual.
            tipo_veiculo = "Carro"
            
            # .title() formata a palavra deixando apenas a primeira letra maiúscula (Ex: fiat -> Fiat)
            marca_carro = input("Marca do veículo (ex: Honda, Chevrolet): ").strip().title()
            # =======================================================================

            vaga_bruta = input("Escolha a vaga: ").strip()

            # Mecanismo de Prevenção de Erros (UX): Corrige entradas como "Vaga 05" ou "P3" extraindo apenas o número.
            vaga_limpa = "".join(char for char in vaga_bruta if char.isdigit())

            if vaga_limpa != "":
                vaga = str(int(vaga_limpa)) # Converte para Integer para remover zeros à esquerda, e retorna para String.
            else:
                vaga = vaga_bruta 

            # Valida se a chave solicitada existe na base de dados.
            if vaga not in estacionamento:
                print("Vaga inválida. O escopo do sistema é de 1 a 15.")
                continue

            # Previne a sobreposição de dados em uma vaga que já possui valor alocado.
            if estacionamento[vaga] is not None:
                print("Vaga indisponível. Consulte o mapa de ocupação.")
                continue

            # Regras de Negócio Específicas (Acessibilidade)
            if vaga in config['vagas_pcd']: 
                pcd = input("Veículo é PCD? (s/n): ").lower() 
                if pcd != 's': 
                    print("Operação não permitida. Vaga com restrição de exclusividade.")
                    continue 

            # Atualização do Estado: Aloca um DICIONÁRIO com os dados do veículo na vaga.
            estacionamento[vaga] = {
                "placa": placa,
                "tipo": tipo_veiculo,
                "marca": marca_carro
            }
            salvar_banco(estacionamento) # Dispara a persistência de dados.

            # Registra no log a entrada bem-sucedida do veículo, incluindo a marca e o tipo.
            logging.info(f"ENTRADA: {tipo_veiculo} {marca_carro} (Placa {placa}) alocado na vaga {vaga}.")

            print("Registro de entrada processado com sucesso.")
            verificar_colisao(vaga, estacionamento) # Aciona a rotina de simulação probabilística.

        # ===================== OPERAÇÃO: SAÍDA =====================
        elif acao == '2':
            vaga_bruta = input("Informe a vaga: ").strip()

            # Reaproveitamento da rotina de limpeza de entrada de dados (UX).
            vaga_limpa = "".join(char for char in vaga_bruta if char.isdigit())

            if vaga_limpa != "":
                vaga = str(int(vaga_limpa)) 
            else:
                vaga = vaga_bruta 

            if vaga not in estacionamento:
                print("Vaga inválida.")
                continue

            # Verifica inconsistência: Tentativa de dar saída em uma vaga não alocada.
            if estacionamento[vaga] is None:
                print("Inconsistência: Não há veículo registrado neste endereço.")
                continue

            # Recupera os dados. Extrai a placa do dicionário (ou pega direto se for registro antigo).
            veiculo_saindo = estacionamento[vaga]
            placa_saida = veiculo_saindo['placa'] if isinstance(veiculo_saindo, dict) else veiculo_saindo

            print(f"Registro de saída processado para o veículo: {placa_saida}.")
            
            # Registra no log a saída do veículo antes de limpar os dados da vaga.
            logging.info(f"SAÍDA: Veículo placa {placa_saida} desocupou a vaga {vaga}.")
            
            # Atualização do Estado: Libera a vaga redefinindo o valor para 'None'.
            estacionamento[vaga] = None 
            salvar_banco(estacionamento) 

        # ===================== OPERAÇÃO: CONSULTA =====================
        elif acao == '3':
            exibir_painel(estacionamento, config)

        elif acao == '4':
            menu_configuracao(config)
        # ===================== OPERAÇÃO: ENCERRAMENTO =====================
        elif acao == '#':
            print("Processo de encerramento do sistema iniciado...")
            
            # Registra no log que o sistema foi encerrado corretamente pelo usuário.
            logging.info("Sistema de Estacionamento encerrado pelo usuário.")
            
            break # Interrompe a estrutura de repetição principal (while True).

        # ===================== TRATAMENTO DE EXCEÇÃO (MENU) =====================
        else:
            print("Opção de comando não reconhecida.")


# ==============================================================================
# PONTO DE ENTRADA DO SCRIPT
# ==============================================================================
# Esta condicional garante que o bloco principal seja executado apenas se 
# o arquivo for chamado diretamente, prevenindo execuções automáticas durante importações.
if __name__ == "__main__":

    main()
