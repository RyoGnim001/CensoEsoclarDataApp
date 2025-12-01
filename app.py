import pandas as pd

CAMINHO = "microdados_ed_basica_2024.csv"

# 1. Definição do mapeamento (Maiúsculo CSV -> Minúsculo JSON)
colunas_map = {
    'NO_ENTIDADE': 'no_entidade', 
    'CO_ENTIDADE': 'co_entidade',
    'NO_UF': 'no_uf', 
    'SG_UF': 'sg_uf', 
    'CO_UF': 'co_uf',
    'NO_MUNICIPIO': 'no_municipio', 
    'CO_MUNICIPIO': 'co_municipio',
    'NO_MESORREGIAO': 'no_mesorregiao', 
    'CO_MESORREGIAO': 'co_mesorregiao',
    'NO_MICRORREGIAO': 'no_microrregiao', 
    'CO_MICRORREGIAO': 'co_microrregiao',
    'NU_ANO_CENSO': 'nu_ano_censo', 
    'NO_REGIAO': 'no_regiao', 
    'CO_REGIAO': 'co_regiao',
    'QT_MAT_BAS': 'qt_mat_bas', 
    'QT_MAT_INF': 'qt_mat_inf',
    'QT_MAT_FUND': 'qt_mat_fund', 
    'QT_MAT_MED': 'qt_mat_med',
    'QT_MAT_PROF': 'qt_mat_prof', 
    'QT_MAT_EJA': 'qt_mat_eja',
    'QT_MAT_ESP': 'qt_mat_esp'
}

# Lista das colunas originais que queremos carregar
colunas_desejadas = list(colunas_map.keys())

print("Iniciando leitura otimizada...")

# 2. Truque de segurança: Ler apenas o cabeçalho para garantir que as colunas existem
# Isso evita erro se o nome de alguma coluna tiver mudado no CSV
try:
    df_head = pd.read_csv(CAMINHO, sep=";", encoding="latin1", nrows=0)
    # Interseção: Só tenta ler as colunas que realmente existem no arquivo
    usecols_seguro = [c for c in colunas_desejadas if c in df_head.columns]
except Exception as e:
    print(f"Erro ao ler cabeçalho: {e}")
    exit()

# 3. Lê o arquivo em pedaços, MAS trazendo APENAS as colunas necessárias (usecols)
# Isso reduz o uso de memória em 90%
chunks = pd.read_csv(
    CAMINHO,
    sep=";",
    encoding="latin1",
    chunksize=50_000,
    usecols=usecols_seguro, # AQUI ESTÁ O SEGREDO DA PERFORMANCE
    low_memory=False
)

resultado = []

for i, chunk in enumerate(chunks):
    # Converte CO_UF para numérico para evitar erros de comparação
    chunk["CO_UF"] = pd.to_numeric(chunk["CO_UF"], errors="coerce")
    
    # Filtra Paraíba (25)
    pb = chunk[chunk["CO_UF"] == 25]
    
    if not pb.empty:
        resultado.append(pb.copy()) # O .copy() ajuda a liberar memória do chunk original

    # Feedback visual para você saber que não travou
    print(f"Processando lote {i+1}...", end='\r')

print("\nJuntando dados filtrados...")

if resultado:
    # Junta todos os pedaços
    df_final = pd.concat(resultado, ignore_index=True)
    
    # Renomeia as colunas
    df_final.rename(columns=colunas_map, inplace=True)
    
    # Exporta para JSON
    nome_arquivo = "dados_censo_pb.json"
    df_final.to_json(nome_arquivo, orient='records', force_ascii=False, indent=4)
    
    print(f"\nSucesso! Arquivo '{nome_arquivo}' gerado.")
    print(f"Total de escolas encontradas: {len(df_final)}")
else:
    print("\nNenhum dado encontrado para a Paraíba (UF 25). Verifique o filtro.")