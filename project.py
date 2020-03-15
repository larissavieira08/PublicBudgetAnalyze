import pandas as pd 
import numpy as np

#Leitura do arquivo
f='2019_OrcamentoDespesa.zip.csv'
df=pd.read_csv(f,sep=';',encoding='latin-1')


#Renomeando os cabeçalhos do dataframe 
headers = ["exe","c_os","n_os","c_oss","n_oss", "c_uo","n_uo",
         "c_f","n_f","c_sf", "n_sf","c_po","n_po","c_a","n_a",
         "c_ce", "n_ce","c_gd","n_gd","c_ed","n_ed","o_i",
         "o_a","o_r"]

df.columns = headers

#conversão das colunas com virgula como separador decimal para ponto e conversão de valores
df["o_i"] = df["o_i"].str.replace(',','.').astype(np.float64)/1000000000
df["o_a"] = df["o_a"].str.replace(',','.').astype(np.float64)/1000000000
df["o_r"] = df["o_r"].str.replace(',','.').astype(np.float64)/1000000000


#1.ANÁLISES PARA ORGÃOS SUPERIORES 


#1.1 Número de orçamentos e soma total por cada orgão superior 
orc_total= df[['n_os','o_i','o_a','o_r']].groupby('n_os', as_index = False).agg({'o_i':('sum'),'o_a':('sum'),'o_r':('sum','size')})
orc_total.columns = ['n_os','o_i sum','o_a sum','o_r sum','size']


#1.2 Número de orçamentos com valores negativos por cada orgão superior 
l=[]

for i in df.index:
    if df['o_i'][i]<0 or df['o_a'][i]<0 or df['o_r'][i]<0:
        l.append([df['n_os'][i],df['o_i'][i],df['o_a'][i],df['o_r'][i],1 if df['o_i'][i]<0 else 0,1 if df['o_a'][i]<0 else 0,1 if df['o_r'][i]<0 else 0])
    

COLUNAS = ['Órgão','O_inicial','O_atualizado','O_realizado','validate i','validate_a','validate_r']
orc_negativo=pd.DataFrame(l,columns=COLUNAS)

orc_negativo=orc_negativo.groupby('Órgão', as_index = False).agg({'validate i':('sum'),'validate_a':('sum'),'validate_r':('sum')})


#1.3 Cálculo da razão entre os orçamento 
def ef (x,y):
    aux =[]
 
    for i in orc_total.index:
        aux.append(x[i]/(1 if y[i]==0 else y[i]))
        
    return aux

    
#1.4 Inserção dos dados no dataframe
    
orc_total.insert(5,"or/oi", ef(orc_total['o_r sum'],orc_total['o_i sum']))
orc_total.insert(6,"or/oa", ef(orc_total['o_r sum'],orc_total['o_a sum']))
orc_total.insert(7,"oa/oi",ef(orc_total['o_a sum'],orc_total['o_i sum']))



#1.5 Identificação dos outliers 

std_or=orc_total['o_r sum'].std()
mean_std=orc_total['o_r sum'].mean()

for k in orc_total.index:
    if orc_total['o_r sum'][k]< mean_std-2*std_or or orc_total['o_r sum'][k]> mean_std+2*std_or:
    
        print(orc_total['n_os'][k]  + '  ' 'outlier')
    

orc_atual=orc_total.drop([2,7,20])


import seaborn as sns
import matplotlib.pyplot as plt
sns.set(style="whitegrid")

# Initialize the matplotlib figure
f, ax = plt.subplots(figsize=(6, 15))


# Plot the total crashes
sns.set_color_codes("pastel")
sns.barplot(x="o_r sum", y="n_os", data=orc_atual,
            label="Orçamento Realizado", color="r")

# Add a legend and informative axis label
ax.legend(ncol=2, loc="lower right", frameon=True)
ax.set(xlim=(0, 700), ylabel="Orgão Superior",
       xlabel="Orçamento Realizado(em bilhões)")
sns.despine(left=True, bottom=True)


#Trabalhando com bins ----> linspace(start_value, end_value, numbers_generated )

#identifica que partido do valor mínimp até o valor máximo, em 3 classes 
bins = np.linspace(min([0]), max([1]), 4)
#nome das classes 
group_names = ['Baixo', 'Medio', 'Alto']

#a nova var é um corte na variavel inicial, tomando bins como referência, com os group_name como títulos 
orc_atual['or/oa binned'] = pd.cut(orc_atual['or/oa'], bins, labels=group_names, include_lowest=True )
orc_atual[['or/oa','or/oa']].head(17)
#contagem de valores nas classes 
orc_atual["or/oa binned"].value_counts()


import matplotlib as plt
from matplotlib import pyplot
#plot dos bins com a contagem de acordo com as classes 
pyplot.bar(group_names, orc_atual["or/oa binned"].value_counts())

# set x/y labels and plot title
plt.pyplot.xlabel("Nível")
plt.pyplot.ylabel("N° de ocorrências")
plt.pyplot.title("Razão Orçamento Realizado/Orçamento Atualizado")


#ANÁLISE PARA OS MINISTÉRIOS COM MENOR DESEPENHO ENTRE O ORÇAMENTO ATUALIZADO E O ORÇAMENTO REALIZADO

#1.1 Idenficação de dados correspondentes ao Ministério do Turismo
mt=[]

for k in df.index:
    if df['n_os'][k]=='Ministério do Turismo':
        mt.append([df['n_os'][k],df['n_f'][k],df['n_ce'][k],df['n_gd'][k],df['n_ed'][k],df['o_i'][k],df['o_a'][k],df['o_r'][k]])

COLUNAS = ['Órgão','Função','C_Econômica','G_Despesa','El_Despesa','oi','oa','or']
min_turismo=pd.DataFrame(mt,columns=COLUNAS)


#Agrupamento por função 
mt_ftotal= min_turismo[['Função','oi','oa','or']].groupby('Função', as_index = False).agg({'oi':('sum'),'oa':('sum'),'or':('sum','size')})
mt_ftotal.columns = ['Função','oi','oa','or','size']


#1.3 Cálculo da razão entre os orçamento 
def ef1 (x,y):
    aux1 =[]
 
    for i in mt_ftotal.index:
        aux1.append(x[i]/(1 if y[i]==0 else y[i]))
        
    return aux1

    
    
#1.4 Inserção dos dados no dataframe
    
mt_ftotal.insert(5,"or/oi", ef1(mt_ftotal['or'],mt_ftotal['oi']))
mt_ftotal.insert(6,"or/oa", ef1(mt_ftotal['or'],mt_ftotal['oa']))
mt_ftotal.insert(7,"oa/oi",ef1(mt_ftotal['oa'],mt_ftotal['oi']))



#Agrupamento por categoria econômica
mt_cetotal= min_turismo[['C_Econômica','oi','oa','or']].groupby('C_Econômica', as_index = False).agg({'oi':('sum'),'oa':('sum'),'or':('sum','size')})
mt_cetotal.columns = ['C_Econômica','oi','oa','or','size']


#1.3 Cálculo da razão entre os orçamento 
def ef1 (x,y):
    aux1 =[]
 
    for i in mt_cetotal.index:
        aux1.append(x[i]/(1 if y[i]==0 else y[i]))
        
    return aux1

    
#1.4 Inserção dos dados no dataframe
    
mt_cetotal.insert(5,"or/oi", ef1(mt_cetotal['or'],mt_cetotal['oi']))
mt_cetotal.insert(6,"or/oa", ef1(mt_cetotal['or'],mt_cetotal['oa']))
mt_cetotal.insert(7,"oa/oi",ef1(mt_cetotal['oa'],mt_cetotal['oi']))



