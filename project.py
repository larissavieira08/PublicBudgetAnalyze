#Import das Bibliotecas
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Leitura do arquivo do orçamento de despesa
f = '2019_OrcamentoDespesa.zip.csv'
df = pd.read_csv(f, sep=';', encoding='latin-1')

# Renomeando os cabeçalhos do dataframe
headers = ["exe", "c_os", "n_os", "c_oss", "n_oss", "c_uo", "n_uo",
           "c_f", "n_f", "c_sf", "n_sf", "c_po", "n_po", "c_a", "n_a",
           "c_ce", "n_ce", "c_gd", "n_gd", "c_ed", "n_ed", "o_i",
           "o_a", "o_r"]
df.columns = headers

#Estatísticas Gerais
df.describe()

# conversão das colunas com virgula como separador decimal para ponto e conversão de valores
df["o_i"] = df["o_i"].str.replace(',', '.').astype(np.float64) / 1000000000
df["o_a"] = df["o_a"].str.replace(',', '.').astype(np.float64) / 1000000000
df["o_r"] = df["o_r"].str.replace(',', '.').astype(np.float64) / 1000000000

# 1.ANÁLISES PARA ORGÃOS SUPERIORES
# 1.1 Número de orçamentos e soma total por cada orgão superior
orc_total = df[['n_os', 'o_i', 'o_a', 'o_r']].groupby('n_os', as_index=False).agg(
    {'o_i': ('sum'), 'o_a': ('sum'), 'o_r': ('sum', 'size')})
orc_total.columns = ['n_os', 'o_i sum', 'o_a sum', 'o_r sum', 'size']
oct=list(orc_total)

# 1.2 Caracterização geral dos orgãos superiores
e_des= orc_total.describe()

# 1.3 Cálculo da razão entre os orçamento
def ef(x, y):
    aux = []
    for i in orc_total.index:
        aux.append(x[i] / (1 if y[i] == 0 else y[i]))
    return aux

orc_total.insert(5, "or/oi", ef(orc_total['o_r sum'], orc_total['o_i sum']))
orc_total.insert(6, "or/oa", ef(orc_total['o_r sum'], orc_total['o_a sum']))
orc_total.insert(7, "oa/oi", ef(orc_total['o_a sum'], orc_total['o_i sum']))

#1.4 retirada dos dois ministérios que possuem apena 1 dado
orc_raz = orc_total.drop([2, 20])

# 1.5 Percentual de orçamentos não realizados, cujo nome de despesa é igual a não informado
tst = []
for i in df.index:
    if df['n_ed'][i] == 'Não informado':
        tst.append([df['n_os'][i], df['n_ed'][i], df['o_r'][i],1])
    else:
        tst.append([df['n_os'][i], df['n_ed'][i], 0,0])

COLUNAS = ['Órgão', 'Gdespesa', 'O_realizado','CONTADOR']
orc_desp = pd.DataFrame(tst, columns=COLUNAS)

orc_desp = orc_desp.groupby('Órgão', as_index=False).\
    agg({'O_realizado': ('size'), 'CONTADOR': ('sum')})
orc_desp['razao']=(orc_desp['CONTADOR']/orc_desp['O_realizado'])*100
orc_desp=orc_desp.drop([2,20])

# 1.6 Percentual total gasto dentro da categoria econômica
orc_tc = df.groupby('n_ce', as_index=False).\
    agg({'o_i': ('sum'),'o_a': ('sum'),'o_r': ('sum')})
orc_tc['oa/oi']=orc_tc['o_a']/orc_tc['o_i']
orc_tc['or/oi']=orc_tc['o_r']/orc_tc['o_i']
orc_tc['or/oa']=orc_tc['o_r']/orc_tc['o_a']

# ANÁLISE PARA OS MINISTÉRIOS COM MENOR DESEPENHO ENTRE O ORÇAMENTO ATUALIZADO E O ORÇAMENTO REALIZADO
# 2.1 Idenficação de dados correspondentes ao Ministério do Turismo, Presidência da República
def name(nome_ministerio,df):
    mt = []
    for k in df.index:
        if df['n_os'][k] == nome_ministerio:
            mt.append(
                [df['n_os'][k], df['n_f'][k], df['n_ce'][k], df['n_gd'][k], df['n_ed'][k], df['o_i'][k], df['o_a'][k],
                 df['o_r'][k]])

    COLUNAS = ['Órgão', 'Função', 'C_Econômica', 'G_Despesa', 'El_Despesa', 'oi', 'oa', 'or']
    min_ = pd.DataFrame(mt, columns=COLUNAS)

    #2.2 Avaliação do desempenho dentro das categorias
    # Agrupamento por função
    ftotal = min_[['Função', 'oi', 'oa', 'or']].groupby('Função', as_index=False).agg(
        {'oi': ('sum'), 'oa': ('sum'), 'or': ('sum', 'size')})
    ftotal.columns = [COLUNAS[1], 'oi', 'oa', 'or', 'size']

    #Agrupamento pot categoria econômica
    cetotal = min_[['C_Econômica', 'oi', 'oa', 'or']].groupby('C_Econômica', as_index=False).agg(
        {'oi': ('sum'), 'oa': ('sum'), 'or': ('sum', 'size')})
    cetotal.columns = [COLUNAS[2], 'oi', 'oa', 'or', 'size']

    #Agrupamento por grupo de despesa
    gdtotal = min_[['G_Despesa', 'oi', 'oa', 'or']].groupby('G_Despesa', as_index=False).agg(
        {'oi': ('sum'), 'oa': ('sum'), 'or': ('sum', 'size')})
    gdtotal.columns = [COLUNAS[3], 'oi', 'oa', 'or', 'size']

    #Agrupamento por elemento de despesa
    edtotal = min_[['El_Despesa', 'oi', 'oa', 'or']].groupby('El_Despesa', as_index=False).agg(
        {'oi': ('sum'), 'oa': ('sum'), 'or': ('sum', 'size')})
    edtotal.columns = [COLUNAS[4], 'oi', 'oa', 'or', 'size']

    #função para inserção dos dados no dataframe
    def ef1(dataf, x, y):
        aux1 = []
        for i in dataf.index:
            aux1.append(x[i] / (1 if y[i] == 0 else y[i]))
        return aux1

    ftotal.insert(5, "or/oi", ef1(ftotal, ftotal['or'], ftotal['oi']))
    ftotal.insert(6, "or/oa", ef1(ftotal, ftotal['or'], ftotal['oa']))
    ftotal.insert(7, "oa/oi", ef1(ftotal, ftotal['oa'], ftotal['oi']))

    cetotal.insert(5, "or/oi", ef1(cetotal, cetotal['or'], cetotal['oi']))
    cetotal.insert(6, "or/oa", ef1(cetotal, cetotal['or'], cetotal['oa']))
    cetotal.insert(7, "oa/oi", ef1(cetotal, cetotal['oa'], cetotal['oi']))

    gdtotal.insert(5, "or/oi", ef1(gdtotal, gdtotal['or'], gdtotal['oi']))
    gdtotal.insert(6, "or/oa", ef1(gdtotal, gdtotal['or'], gdtotal['oa']))
    gdtotal.insert(7, "oa/oi", ef1(gdtotal, gdtotal['oa'], gdtotal['oi']))

    edtotal.insert(5, "or/oi", ef1(edtotal, edtotal['or'], edtotal['oi']))
    edtotal.insert(6, "or/oa", ef1(edtotal, edtotal['or'], edtotal['oa']))
    edtotal.insert(7, "oa/oi", ef1(edtotal, edtotal['oa'], edtotal['oi']))

    #Gerar csv
    ftotal.to_csv('funcao_detalhada-'+nome_ministerio+'.csv')
    cetotal.to_csv('c_e_detalhada-'+nome_ministerio+'.csv')
    gdtotal.to_csv('grupo_despesa-'+nome_ministerio+'.csv')
    edtotal.to_csv('elemento_despesa-'+nome_ministerio+'.csv')

    #Plot do subgrupo Função
    sns.set(style="whitegrid")

    g = sns.catplot(y="Função", x="or/oa", data=ftotal,
                    height=6, kind="bar", palette="pastel")
    g.despine(left=True)
    g.set_ylabels("Órgão Superior")
    g.set_xlabels("Eficiência")
    plt.xlim(0, 1)
    plt.show()
    g.savefig('razao_'+ nome_ministerio)

name("Ministério do Turismo", df)
name("Presidência da República", df)

#Dados de saída em csv
orc_total.to_csv('Orcamento_total_o_superiores.csv',sep=';')
e_des.to_csv('estatística_descritiva_o_superiores.csv',sep=';')
orc_total.to_csv('razao_o_superiores.csv',sep=';')
orc_desp.to_csv('el_despesa_n_informado.csv',sep=';')
orc_tc.to_csv('orcamento_ce_o_superiores.csv',sep=';')

#---------------------------------------------Plot dos Gráficos --------------------------------------------------
#Gráfico 1 - Razão entre o orçamento realizado/ orçamento atualizado para cada órgão superior
sns.set(style="whitegrid")
g = sns.catplot(y="n_os", x="or/oa", data=orc_raz,
                height=6, kind="bar", palette="pastel")
g.despine(left=True)
g.set_ylabels("Órgão Superior")
g.set_xlabels("Eficiência")
plt.xlim(0, 1)
plt.show()
g.savefig('razao')

#Gráfico 2 - Razão entre o n de não informados/ n total de orçamennto para cada órgão superior
sns.set(style="whitegrid")
n= sns.catplot(y="Órgão", x="razao", data=orc_desp,
                height=6, kind="bar", palette="deep")
n.despine(left=True)
n.set_ylabels("Órgão Superior")
n.set_xlabels("Porcentagem(%)")
plt.xlim(0, 100)
plt.show()
n.savefig('desp')
#----------------------------------------------------------------------------------------------------------------------
