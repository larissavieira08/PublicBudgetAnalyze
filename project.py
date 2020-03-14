import pandas as pd 
import numpy as np

#leitura do arquivo
f='2019_OrcamentoDespesa.zip.csv'
df=pd.read_csv(f,sep=';',encoding='latin-1')


#Renomeando os cabeçalhos do dataframe 
headers = ["exe","c_os","n_os","c_oss","n_oss", "c_uo","n_uo",
         "c_f","n_f","c_sf", "n_sf","c_po","n_po","c_a","n_a",
         "c_ce", "n_ce","c_gd","n_gd","c_ed","n_ed","o_i",
         "o_a","o_r"]

df.columns = headers

#conversão das colunas com virgula como separador decimal para ponto e conversão de valores
df["o_i"] = df["o_i"].str.replace(',','').astype(np.float64)
df["o_a"] = df["o_a"].str.replace(',','').astype(np.float64)
df["o_r"] = df["o_r"].str.replace(',','').astype(np.float64)


#ANÁLISES PARA ORGÃOS SUPERIORES 


#Número de orçamentos e soma total por cada orgão superior 
orc_total= df[['n_os','o_i','o_a','o_r']].groupby('n_os', as_index = False).agg({'o_i':('sum'),'o_a':('sum'),'o_r':('sum')})
orc_total.columns = ['n_os','o_i sum','o_a sum','o_r sum']


#Número de orçamentos com valores negativos por cada orgão superior 
l=[]

for i in df.index:
    if df['o_i'][i]<0 or df['o_a'][i]<0 or df['o_r'][i]<0:
        l.append([df['n_os'][i],df['o_i'][i],df['o_a'][i],df['o_r'][i],1 if df['o_i'][i]<0 else 0,1 if df['o_a'][i]<0 else 0,1 if df['o_r'][i]<0 else 0])
    

COLUNAS = ['Órgão','O_inicial','O_atualizado','O_realizado','validate i','validate_a','validate_r']
orc_negativo=pd.DataFrame(l,columns=COLUNAS)

orc_negativo=orc_negativo.groupby('Órgão', as_index = False).agg({'validate i':('sum'),'validate_a':('sum'),'validate_r':('sum')})


#cálculo porcentagem que representa cada amplitude em relação ao seu total 

def porcentagem (x,y):
    aux =[]
    for i in orc_total.index:
        soma=x[i]+y[i]
        ampl=(x[i]-y[i])
        if soma ==0: 
            soma=1
        perc=(ampl/soma)*100.0
        aux.append(perc)
    return aux

orc_total.insert(4,"nome1", porcentagem(orc_total['o_r sum'],orc_total['o_i sum']))
orc_total.insert(5,"nome2", porcentagem(orc_total['o_r sum'],orc_total['o_a sum']))
orc_total.insert(6,"nome3" ,porcentagem(orc_total['o_a sum'],orc_total['o_i sum']))



