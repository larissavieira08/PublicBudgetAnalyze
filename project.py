import pandas as pd 
import numpy as np

#leitura do arquivo
f='2019_OrcamentoDespesa.zip.csv'
df=pd.read_csv(f,sep=';',encoding='latin-1')

#conversão das colunas com virgula como separador decimal para ponto
df["ORÇAMENTO INICIAL (R$)"] = df["ORÇAMENTO INICIAL (R$)"].str.replace(',','').astype(np.float64)
df["ORÇAMENTO ATUALIZADO (R$)"] = df["ORÇAMENTO ATUALIZADO (R$)"].str.replace(',','').astype(np.float64)
df["ORÇAMENTO REALIZADO (R$)"] = df["ORÇAMENTO REALIZADO (R$)"].str.replace(',','').astype(np.float64)


#Número de orçamentos e soma total de orçamento realizado por orgão superior 
df2= df[['NOME ÓRGÃO SUPERIOR','ORÇAMENTO REALIZADO (R$)']].groupby('NOME ÓRGÃO SUPERIOR', as_index = False).agg({'ORÇAMENTO REALIZADO (R$)':('sum','size')})
df2.columns = ['NOME ÓRGÃO SUPERIOR','ORÇAMENTO REALIZADO (R$) sum','ORÇAMENTO REALIZADO (R$) size']

