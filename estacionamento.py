# ==============================================================================
# IMPORTAÇÃO DE BIBLIOTECAS (Módulos Nativos e Terceiros)
# ==============================================================================
import logging  
import os       
import random   
import re       
import qrcode    
import mysql.connector
from mysql.connector import Error
from config import DB_config  
from fpdf import FPDF 
from fpdf.enums import XPos, YPos 
from datetime import datetime 

# ==============================================================================
# CONFIGURAÇÕES GLOBAIS (Constantes e Parâmetros do Sistema)
# ==============================================================================
# Configuração do sistema de Log
logging.basicConfig(
    filename='estaciona4.log', 
    encoding='utf-8',              
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s', 
)

# ==============================================================================
# FUNÇÕES DE BANCO DE DADOS (Setup e Conexão)
# ==============================================================================

def verificar_exist_banco():
    config_server = DB_config.copy()
    nome_banco = config_server.pop('database', 'estacionamento') 

    try:
        conn = mysql.connector.connect(**config_server)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {nome_banco}")
        print(f"Banco de dados '{nome_banco}' verificado/criado com sucesso.")
        cursor.close()
        conn.close()
    except Error as err:
        print(f"Erro ao verificar/criar o banco de dados: {err}")
        logging.error(f"Erro ao verificar/criar o banco de dados: {err}")
    
def conectar_banco():
    try:
        return mysql.connector.connect(**DB_config)
    except Error as err:
        print(f"Erro ao conectar ao banco de dados: {err}")
        logging.error(f"Erro ao conectar ao banco de dados: {err}")
        return None

def inicializar_tabelas():
    """Garante a existência das 3 tabelas normalizadas e insere os dados iniciais."""
    conn = conectar_banco()
    if conn is None:
        return
    
    cursor = conn.cursor()
    
    try:
        # 1. Tabela de Configurações
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave VARCHAR(50) PRIMARY KEY,
                valor VARCHAR(255)
            )
        ''')
        
        # 2. Tabela de Veículos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS veiculos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                placa VARCHAR(10) UNIQUE NOT NULL,
                marca VARCHAR(50) NOT NULL,
                tipo VARCHAR(20) DEFAULT 'Carro'
            )
        ''')
        
        # 3. Tabela de Vagas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vagas (
                numero_vaga INT PRIMARY KEY,
                tipo_vaga VARCHAR(20) DEFAULT 'comum',
                status ENUM('livre', 'ocupada') DEFAULT 'livre',
                veiculo_id INT NULL,
                FOREIGN KEY (veiculo_id) REFERENCES veiculos(id) ON DELETE SET NULL
            )
        ''')
        
        # Setup Padrão Seguro
        cursor.execute("INSERT IGNORE INTO configuracoes (chave, valor) VALUES (%s, %s)", ('vagas_totais', '15'))
        cursor.execute("INSERT IGNORE INTO configuracoes (chave, valor) VALUES (%s, %s)", ('vagas_pcd', '1'))
        
        cursor.execute("SELECT COUNT(*) FROM vagas")
        if cursor.fetchone()[0] == 0:
            cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'vagas_totais'")
            total_vagas = int(cursor.fetchone()[0])
            
            cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'vagas_pcd'")
            vagas_pcd = [v.strip() for v in cursor.fetchone()[0].split(',')]
            
            for i in range(1, total_vagas + 1):
                tipo = 'pcd' if str(i) in vagas_pcd else 'comum'
                cursor.execute(
                    "INSERT INTO vagas (numero_vaga, tipo_vaga, status) VALUES (%s, %s, %s)", 
                    (i, tipo, 'livre')
                )
                
        conn.commit()
        print("Estrutura de tabelas verificada/criada com sucesso.")
        logging.info("Tabelas do banco de dados inicializadas.")
        
    except Error as err:
        print(f"Erro ao inicializar tabelas: {err}")
        logging.error(f"Erro ao criar tabelas: {err}")
    finally:
        cursor.close()
        conn.close()

# ==============================================================================
# GERAÇÃO DE TICKETS E PDFs
# ==============================================================================

def gerar_ticket_entrada(vaga, placa, marca, tipo_vaga):
    """Gera um ticket térmico (PDF) com um QR Code funcional escaneável."""
    pasta = "ticketsentrada"
    if not os.path.exists(pasta):
        os.makedirs(pasta)

    pdf = FPDF(format=(80, 140))
    pdf.add_page()
    pdf.set_margins(5, 5, 5)
    pdf.set_auto_page_break(auto=True, margin=5)
    
    pdf.set_font("Courier", "B", 14)
    pdf.cell(0, 6, "ESTACIONAMENTO", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    pdf.cell(0, 6, "INTELIGENTE", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.set_font("Courier", "", 10)
    pdf.cell(0, 5, "-" * 32, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.set_font("Courier", "B", 12)
    pdf.cell(0, 6, "TICKET DE ENTRADA", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.set_font("Courier", "", 10)
    pdf.cell(0, 5, "-" * 32, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.set_font("Courier", "B", 10)
    pdf.cell(0, 6, f"Data/Hora: {agora}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, f"Placa:     {placa}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 6, f"Marca:     {marca}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    vaga_str = f"{int(vaga):02d}"
    pdf.cell(0, 6, f"Vaga:      {vaga_str} ({tipo_vaga.upper()})", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    pdf.cell(0, 5, "-" * 32, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    pdf.set_font("Courier", "", 8)
    pdf.multi_cell(0, 4, "Guarde este ticket no painel.\nA perda estara sujeita\na taxa extra de R$ 50,00.", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
    
    dados_qr = f"SISTEMA ESTACIONA4\nPlaca: {placa}\nVaga: {vaga_str}\nEntrada: {agora}"
    img_qr = qrcode.make(dados_qr)
    
    nome_img_temp = f"temp_qr_{placa}.png"
    img_qr.save(nome_img_temp)
    
    pdf.ln(2)
    pdf.image(nome_img_temp, x=20, w=40)
    
    if os.path.exists(nome_img_temp):
        os.remove(nome_img_temp)
        
    nome_arquivo = os.path.join(pasta, f"ticket_{placa}_{vaga_str}.pdf")
    pdf.output(nome_arquivo)
    print(f"Ticket de entrada gerado: {nome_arquivo}")

def gerar_ticket_saida(dados_veiculo):
    """Gera um PDF comprovante de saída do estacionamento sem warnings."""
    pasta = "ticketssaida"
    if not os.path.exists(pasta):
        os.makedirs(pasta)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", 'B', 16)
    
    pdf.cell(200, 10, text="Comprovante de Saída - Estacionamento", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align='C')
    pdf.set_font("Helvetica", size=12)
    pdf.ln(10)
    
    pdf.cell(200, 10, text=f"Veículo: {dados_veiculo['tipo']} {dados_veiculo['marca']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(200, 10, text=f"Placa: {dados_veiculo['placa']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(200, 10, text=f"Vaga Liberada: {dados_veiculo['numero_vaga']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(200, 10, text="Status: Pagamento Processado - Saída Autorizada", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    nome_arquivo = os.path.join(pasta, f"saida_{dados_veiculo['placa']}.pdf")
    pdf.output(nome_arquivo)
    print(f"\n[!] Comprovante de saída gerado com sucesso: {nome_arquivo}")

# ==============================================================================
# LÓGICA DE NEGÓCIOS E VALIDAÇÕES
# ==============================================================================

def contar_ocupadas():
    """Retorna o número atual de vagas ocupadas no pátio."""
    conn = conectar_banco()
    if not conn: return 0
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM vagas WHERE status = 'ocupada'")
    resultado = cursor.fetchone()[0]
    
    cursor.close()
    conn.close()
    return resultado if resultado is not None else 0

def validar_placa(placa):
    """Valida se a placa informada cumpre as regras do padrão Antigo ou Mercosul."""
    padrao = r'^[A-Z]{3}[0-9][A-Z0-9][0-9]{2}$'
    return re.match(padrao, placa) is not None

def traduzir_mercosul_para_antiga(placa):
    """Converte placa Mercosul (AAA0A00) para formato antigo (AAA0000) se aplicável."""
    if re.match(r'^[A-Z]{3}[0-9][A-Z][0-9]{2}$', placa):
        mapa_letras = {
            'A': '0', 'B': '1', 'C': '2', 'D': '3', 'E': '4', 
            'F': '5', 'G': '6', 'H': '7', 'I': '8', 'J': '9'
        }
        letra_conversao = placa[4]
        
        if letra_conversao in mapa_letras:
            return placa[:4] + mapa_letras[letra_conversao] + placa[5:]
    return placa

def placa_ja_existe(placa):
    """Verifica se o veículo já está no pátio (checa placa atual e versão traduzida)."""
    conn = conectar_banco()
    if not conn: return False
    cursor = conn.cursor()
    
    placa_traduzida = traduzir_mercosul_para_antiga(placa)
    
    query = '''
        SELECT COUNT(*) FROM vagas v
        JOIN veiculos c ON v.veiculo_id = c.id
        WHERE v.status = 'ocupada' AND (c.placa = %s OR c.placa = %s)
    '''
    cursor.execute(query, (placa, placa_traduzida))
    resultado = cursor.fetchone()
    
    cursor.close()
    conn.close()
    return resultado[0] > 0

# ==============================================================================
# ALGORITMO DE SELEÇÃO INTELIGENTE E COLISÃO
# ==============================================================================

def verificar_colisao(vaga):
    """Calcula a probabilidade de incidentes consultando a vizinhança no MySQL."""
    conn = conectar_banco()
    if not conn: return
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT numero_vaga, status FROM vagas")
    mapa_vagas = {str(row['numero_vaga']): row['status'] for row in cursor.fetchall()}
    cursor.close()
    conn.close()

    vaga = int(vaga) 
    vizinhos = 0    

    if mapa_vagas.get(str(vaga - 1)) == 'ocupada': vizinhos += 1
    if mapa_vagas.get(str(vaga + 1)) == 'ocupada': vizinhos += 1

    chance = 0.15 if vizinhos == 1 else 0.35 if vizinhos == 2 else 0

    if random.random() < chance:
        print("\n!!! ATENÇÃO: Colisão detectada ao realizar a manobra !!!")
        logging.warning(f"Colisão simulada na vaga {vaga}")

def designar_vaga(tipo):
    """Busca vagas elegíveis no MySQL e escolhe a melhor com base no score de isolamento."""
    conn = conectar_banco()
    if not conn: return None
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT chave, valor FROM configuracoes")
    configs = {row['chave']: row['valor'] for row in cursor.fetchall()}
    total = int(configs.get('vagas_totais', 15))
    vagas_pcd = [v.strip() for v in configs.get('vagas_pcd', '').split(',')] if configs.get('vagas_pcd') else []

    cursor.execute("SELECT numero_vaga, status FROM vagas")
    mapa_vagas = {str(row['numero_vaga']): row['status'] for row in cursor.fetchall()}
    cursor.close()
    conn.close()

    if tipo.upper() == "PCD":
        candidatas = [v for v in range(1, total + 1) if str(v) in vagas_pcd and mapa_vagas.get(str(v)) == 'livre']
    else:
        candidatas = [v for v in range(1, total + 1) if str(v) not in vagas_pcd and mapa_vagas.get(str(v)) == 'livre']

    if not candidatas:
        return None
    
    def lado_vazio(vaga_id, lado):
        vizinho = vaga_id + lado
        if vizinho < 1 or vizinho > total: return True
        return mapa_vagas.get(str(vizinho)) == 'livre'
    
    def calcular_score(vaga_id):
        esq = lado_vazio(vaga_id, -1)
        dir = lado_vazio(vaga_id, 1)
        if esq and dir: return 3
        elif esq or dir: return 2
        else: return 1
    
    melhor_vaga = None
    maior_pontuacao = -1

    for vaga in candidatas:
        pontos = calcular_score(vaga)
        if pontos == 3: return vaga
        if pontos > maior_pontuacao:
            maior_pontuacao = pontos
            melhor_vaga = vaga

    return melhor_vaga

# ==============================================================================
# OPERAÇÕES DE ENTRADA E SAÍDA NO BANCO
# ==============================================================================

def registrar_entrada_bd(vaga, placa, marca, tipo_veiculo):
    """Faz a inserção do veículo no banco, lidando com transição de placas."""
    conn = conectar_banco()
    if not conn: return False
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id FROM veiculos WHERE placa = %s", (placa,))
        veiculo = cursor.fetchone()
        
        if veiculo:
            veiculo_id = veiculo[0]
        else:
            placa_antiga = traduzir_mercosul_para_antiga(placa)
            
            if placa_antiga != placa: 
                cursor.execute("SELECT id FROM veiculos WHERE placa = %s", (placa_antiga,))
                veiculo_antigo = cursor.fetchone()
                
                if veiculo_antigo:
                    veiculo_id = veiculo_antigo[0]
                    cursor.execute("UPDATE veiculos SET placa = %s WHERE id = %s", (placa, veiculo_id))
                    print(f"[*] Histórico unificado: Placa antiga {placa_antiga} atualizada para {placa}.")
                    logging.info(f"Placa atualizada no BD: {placa_antiga} -> {placa}")
                else:
                    cursor.execute("INSERT INTO veiculos (placa, marca, tipo) VALUES (%s, %s, %s)", (placa, marca, tipo_veiculo))
                    veiculo_id = cursor.lastrowid
            else:
                cursor.execute("INSERT INTO veiculos (placa, marca, tipo) VALUES (%s, %s, %s)", (placa, marca, tipo_veiculo))
                veiculo_id = cursor.lastrowid
        
        cursor.execute("UPDATE vagas SET status = 'ocupada', veiculo_id = %s WHERE numero_vaga = %s", (veiculo_id, vaga))
        conn.commit()
        return True
    except Error as err:
        print(f"Erro ao registrar entrada no banco: {err}")
        conn.rollback() 
        return False
    finally:
        cursor.close()
        conn.close()

def processar_saida_bd(placa):
    """Libera a vaga no MySQL e retorna os dados para o recibo."""
    conn = conectar_banco()
    if not conn: return False, None
    cursor = conn.cursor(dictionary=True)
    
    placa_antiga = traduzir_mercosul_para_antiga(placa)
    
    query = '''
        SELECT v.numero_vaga, c.marca, c.tipo, c.placa
        FROM vagas v
        JOIN veiculos c ON v.veiculo_id = c.id
        WHERE v.status = 'ocupada' AND (c.placa = %s OR c.placa = %s)
    '''
    cursor.execute(query, (placa, placa_antiga))
    registro = cursor.fetchone()
    
    if registro:
        numero_vaga = registro['numero_vaga']
        cursor.execute("UPDATE vagas SET status = 'livre', veiculo_id = NULL WHERE numero_vaga = %s", (numero_vaga,))
        conn.commit()
        cursor.close()
        conn.close()
        return True, registro
    else:
        cursor.close()
        conn.close()
        return False, None

def configurar_estacionamento_bd():
    """Atualiza as configurações e redimensiona a tabela de vagas com segurança."""
    conn = conectar_banco()
    if not conn: return
    cursor = conn.cursor()

    try:
        print("\n--- CONFIGURAÇÃO DO ESTACIONAMENTO ---")
        novo_total_str = input("Digite a nova quantidade total de vagas: ").strip()
        if not novo_total_str.isdigit():
            print("Erro: O total de vagas deve ser um número inteiro.")
            return
            
        novo_total = int(novo_total_str)
        vagas_pcd = input("Digite os números das vagas PCD separados por vírgula (ex: 1,2,3): ").strip()

        cursor.execute("SELECT MAX(numero_vaga) FROM vagas")
        resultado_max = cursor.fetchone()
        max_vaga = resultado_max[0] if resultado_max[0] else 0

        # Trava de segurança: impede exclusão de vagas ocupadas se o limite diminuir
        if novo_total < max_vaga:
            cursor.execute("SELECT COUNT(*) FROM vagas WHERE numero_vaga > %s AND status = 'ocupada'", (novo_total,))
            vagas_ocupadas = cursor.fetchone()[0]
            
            if vagas_ocupadas > 0:
                print(f"\n[ERRO] Impossível reduzir o pátio para {novo_total} vagas.")
                print("Existem carros estacionados nas vagas que seriam removidas. Libere-as primeiro.")
                return 
            
            print(f"[*] Ajustando pátio: Removendo vagas de {novo_total + 1} até {max_vaga}...")
            cursor.execute("DELETE FROM vagas WHERE numero_vaga > %s", (novo_total,))

        elif novo_total > max_vaga:
            for i in range(max_vaga + 1, novo_total + 1):
                cursor.execute("INSERT INTO vagas (numero_vaga, status) VALUES (%s, 'livre')", (i,))

        # Atualiza configurações
        cursor.execute("UPDATE configuracoes SET valor = %s WHERE chave = 'vagas_totais'", (str(novo_total),))
        cursor.execute("UPDATE configuracoes SET valor = %s WHERE chave = 'vagas_pcd'", (vagas_pcd,))

        # Atualiza os tipos das vagas (PCD vs comum)
        lista_pcd = [v.strip() for v in vagas_pcd.split(',') if v.strip().isdigit()]
        cursor.execute("UPDATE vagas SET tipo_vaga = 'comum'")

        for pcd in lista_pcd:
            if int(pcd) <= novo_total:
                cursor.execute("UPDATE vagas SET tipo_vaga = 'pcd' WHERE numero_vaga = %s", (int(pcd),))

        conn.commit()
        print("\n[!] Configurações salvas e pátio reestruturado com sucesso!")
        logging.info(f"Configurações alteradas: {novo_total} vagas totais, PCDs: {vagas_pcd}")

    except Error as err:
        print(f"Erro ao configurar banco: {err}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

# ==============================================================================
# INTERFACE E EXIBIÇÃO VISUAL
# ==============================================================================

def exibir_painel():
    conn = conectar_banco()
    if not conn: return

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'vagas_totais'")
    resultado_config = cursor.fetchone()
    vagas_totais = int(resultado_config['valor']) if resultado_config else 0

    ocupadas = contar_ocupadas()
    livres = vagas_totais - ocupadas

    print("\n" + "="*50)
    print("            MAPA DO ESTACIONAMENTO (MySQL)")
    print("="*50)

    query = '''
        SELECT v.numero_vaga, v.tipo_vaga, v.status, c.placa, c.tipo, c.marca
        FROM vagas v
        LEFT JOIN veiculos c ON v.veiculo_id = c.id
        ORDER BY v.numero_vaga
    '''
    cursor.execute(query)
    vagas_bd = cursor.fetchall()

    for vaga in vagas_bd:
        num = vaga['numero_vaga']
        if vaga['status'] == 'livre':
            status_str = "Livre (PCD)" if vaga['tipo_vaga'] == 'pcd' else "Livre"
        else:
            status_str = f"Ocupada: {vaga['placa']} | {vaga['tipo']} | Marca: {vaga['marca']}"
        print(f"Vaga {num:02d}: [ {status_str} ]")

    print("-"*50)
    print(f"{ocupadas} ocupadas | {livres} livres")
    print("="*50)
    
    cursor.close()
    conn.close()

# ==============================================================================
# FLUXO PRINCIPAL DE EXECUÇÃO
# ==============================================================================

def main():
    verificar_exist_banco()
    inicializar_tabelas()

    logging.info("Sistema de Estacionamento iniciado.")
    print("\n--- Sistema de Estacionamento Inteligente ---")

    while True:
        acao_bruta = input("\n(1) Entrada | (2) Saída | (3) Ver vagas | (4) Configurações | (#) Sair: ").strip()
        
        if acao_bruta == '#':
            acao = '#'
        else:
            acao_limpa = "".join(char for char in acao_bruta if char.isdigit())
            acao = str(int(acao_limpa)) if acao_limpa != "" else acao_bruta 

        if acao == '1':
            conn = conectar_banco()
            cursor = conn.cursor()
            cursor.execute("SELECT valor FROM configuracoes WHERE chave = 'vagas_totais'")
            limite_vagas = int(cursor.fetchone()[0])
            cursor.close()
            conn.close()

            if contar_ocupadas() >= limite_vagas:
                print("Estacionamento completamente cheio.")
                continue 

            placa = input("Placa do Veículo: ").strip().upper()

            if not validar_placa(placa):
                print("Placa inválida. Utilize o formato Padrão (AAA0000) ou Mercosul (AAA0A00).")
                continue

            if placa_ja_existe(placa):
                print("Esse veículo já possui um registro ativo no pátio.")
                continue

            tipo_veiculo = "Carro"
            marca_carro = input("Marca do veículo (ex: Honda, Fiat): ").strip().title()
            tipo_vaga = input("Escolha o tipo de vaga desejada (normal/pcd): ").strip().lower()

            vaga_designada = designar_vaga(tipo_vaga)
            
            if vaga_designada is None:
                print(f"Não existem vagas disponíveis ou livres para a categoria: {tipo_vaga}")
                continue
                
            vaga = str(vaga_designada)
            print(f'Sua vaga designada é de número: {vaga}')

            sucesso = registrar_entrada_bd(vaga, placa, marca_carro, tipo_veiculo)
            
            if sucesso:
                gerar_ticket_entrada(vaga, placa, marca_carro, tipo_vaga)
                logging.info(f"ENTRADA: {tipo_veiculo} {marca_carro} (Placa {placa}) alocado na vaga {vaga}.")
                print("Registro de entrada processado com sucesso!")
                verificar_colisao(vaga)

        elif acao == '2':
            if contar_ocupadas() == 0:
                print("O estacionamento está vazio.")
                continue

            placa = input("Placa do Veículo para saída: ").strip().upper()
            sucesso, dados_veiculo = processar_saida_bd(placa)

            if sucesso:
                gerar_ticket_saida(dados_veiculo)
                logging.info(f"SAÍDA: Vaga {dados_veiculo['numero_vaga']} liberada. Placa: {dados_veiculo['placa']}")
            else:
                print("Veículo não encontrado ou placa incorreta.")

        elif acao == '3':
            exibir_painel()

        elif acao == '4':
            configurar_estacionamento_bd()

        elif acao == '#':
            print("Processo de encerramento do sistema iniciado...")
            logging.info("Sistema de Estacionamento encerrado pelo usuário.")
            break 

        else:
            print("Opção de comando não reconhecida no menu principal.")

if __name__ == "__main__":
    main()