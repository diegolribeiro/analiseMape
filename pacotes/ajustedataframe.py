

import pandas as pd
import numpy as np

pd.set_option('future.no_silent_downcasting', True)

# O import dos dados do DRP vem com o valor - nas colunas que possuem valor nulo
# essa função tem comom objetivo trocar o - pelo valor null
def ajustar_colunas_nula(df):
    df['QUANTIDADE_VENDA'] = df['QUANTIDADE_VENDA'].replace('-', np.nan)
    df['QUANTIDADE_VENDA_AJUS'] = df['QUANTIDADE_VENDA_AJUS'].replace('-', np.nan)
    df['QUANTIDADE_VENDA_AJUS_SO'] = df['QUANTIDADE_VENDA_AJUS_SO'].replace('-', np.nan)
    df['PV_CONFIRMADA'] = df['PV_CONFIRMADA'].replace('-', np.nan)
    df['FATURAMENTO'] = df['FATURAMENTO'].replace('-', np.nan)

def ajustar_dataframe_analise_item(df,groupby):
    df = df.groupby(groupby).agg(QUANTIDADE_VENDA = pd.NamedAgg(column='QUANTIDADE_VENDA', aggfunc='sum'), 
                                                                                    QUANTIDADE_VENDA_AJUS = pd.NamedAgg(column='QUANTIDADE_VENDA_AJUS', aggfunc='sum'), 
                                                                                    QUANTIDADE_VENDA_AJUS_SO = pd.NamedAgg(column='QUANTIDADE_VENDA_AJUS_SO', aggfunc='sum'),
                                                                                    PREVISAO = pd.NamedAgg(column='PV_CONFIRMADA', aggfunc='sum'),
                                                                                    FATURAMENTO = pd.NamedAgg(column='FATURAMENTO', aggfunc='sum')).reset_index().copy()
    return df

def ajustar_dataframe_analise_categoria(df):
    df['QUANTIDADE_VENDA'] = df['QUANTIDADE_VENDA'].replace('-', np.nan)
    df['QUANTIDADE_VENDA_AJUS'] = df['QUANTIDADE_VENDA_AJUS'].replace('-', np.nan)
    df['QUANTIDADE_VENDA_AJUS_SO'] = df['QUANTIDADE_VENDA_AJUS_SO'].replace('-', np.nan)
    df['PV_CONFIRMADA'] = df['PV_CONFIRMADA'].replace('-', np.nan)
    df['FATURAMENTO'] = df['FATURAMENTO'].replace('-', np.nan)