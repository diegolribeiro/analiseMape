import pandas as pd
import numpy as np
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pacotes.indicadorErro import mape
pd.set_option('future.no_silent_downcasting', True)

# O import dos dados do DRP vem com o valor - nas colunas que possuem valor nulo
# essa função tem comom objetivo trocar o - pelo valor null
def ajustar_colunas_nula(df):
    df['QUANTIDADE_VENDA'] = df['QUANTIDADE_VENDA'].replace('-', np.nan)
    df['QUANTIDADE_VENDA_AJUS'] = df['QUANTIDADE_VENDA_AJUS'].replace('-', np.nan)
    df['QUANTIDADE_VENDA_AJUS_SO'] = df['QUANTIDADE_VENDA_AJUS_SO'].replace('-', np.nan)
    df['PV_CONFIRMADA'] = df['PV_CONFIRMADA'].replace('-', np.nan)
    df['FATURAMENTO'] = df['FATURAMENTO'].replace('-', np.nan)
    
    
    

def ajustar_dataframe_analise(df,groupby):
    df_retorno = df.groupby(groupby).agg(QUANTIDADE_VENDA = pd.NamedAgg(column='QUANTIDADE_VENDA', aggfunc='sum'), 
                                                                                    QUANTIDADE_VENDA_AJUS = pd.NamedAgg(column='QUANTIDADE_VENDA_AJUS', aggfunc='sum'), 
                                                                                    QUANTIDADE_VENDA_AJUS_SO = pd.NamedAgg(column='QUANTIDADE_VENDA_AJUS_SO', aggfunc='sum'),
                                                                                    PREVISAO = pd.NamedAgg(column='PV_CONFIRMADA', aggfunc='sum'),
                                                                                    FATURAMENTO = pd.NamedAgg(column='FATURAMENTO', aggfunc='sum')).reset_index().copy()
    df_retorno['DATA'] = pd.to_datetime(df_retorno['DATA'], format='%Y%m')
    return df_retorno

def ajustar_dataframe_analise_categoria(df):
    df['QUANTIDADE_VENDA'] = df['QUANTIDADE_VENDA'].replace('-', np.nan)
    df['QUANTIDADE_VENDA_AJUS'] = df['QUANTIDADE_VENDA_AJUS'].replace('-', np.nan)
    df['QUANTIDADE_VENDA_AJUS_SO'] = df['QUANTIDADE_VENDA_AJUS_SO'].replace('-', np.nan)
    df['PV_CONFIRMADA'] = df['PV_CONFIRMADA'].replace('-', np.nan)
    df['FATURAMENTO'] = df['FATURAMENTO'].replace('-', np.nan)


def formatar_coluna_dataframe_streamlit(st):
   return {'MAPE_MEDIO': st.column_config.NumberColumn("MAPE MÉDIO ULT. 3M", format="%.0f%%")
                          , 'DESC_ITEM': st.column_config.TextColumn("DESC. DO ITEM")
                          , 'VENDAS_MEDIA': st.column_config.NumberColumn("VENDAS MÉDIA ULT. 3M", format="%.2f")
                          , 'QUANTIDADE_VENDA': st.column_config.NumberColumn("VENDAS", format="%.2f")
                          , 'QUANTIDADE_VENDA_AJUS': st.column_config.NumberColumn("VENDAS AJUST. EVENTO", format="%.2f")
                          , 'QUANTIDADE_VENDA_AJUS_SO': st.column_config.NumberColumn("VENDAS AJUST. S/ OUTLIER", format="%.2f")
                          , 'DATA' : st.column_config.DateColumn("Data", format="MM/YYYY")
                          , 'MAPE' : st.column_config.NumberColumn("MAPE", format="%.0f%%")
                          , 'FATURAMENTO_FMT': st.column_config.NumberColumn("FATURAMENTO ULT. 3M")
                          , 'PREVISAO': st.column_config.NumberColumn("PREVISÃO", format="%.0f")
                          , 'PREVISAO_2026': st.column_config.NumberColumn("PREVISÃO 2026", format="%.0f")
                          , 'PREVISAO_2025': st.column_config.NumberColumn("PREVISÃO 2025", format="%.0f")
                          , 'PREVISÃO_2024': st.column_config.NumberColumn("PREVISÃO 2024", format="%.0f")
                          , 'PREVISÃO_2023': st.column_config.NumberColumn("PREVISÃO 2023", format="%.0f")
                          , 'VENDAS_2022': st.column_config.NumberColumn("VENDAS 2022", format="%.0f")
                          , 'VENDAS_2023': st.column_config.NumberColumn("VENDAS 2023", format="%.0f")
                          , 'VENDAS_2024': st.column_config.NumberColumn("VENDAS 2024", format="%.0f")
                          , 'VENDAS_2025': st.column_config.NumberColumn("VENDAS 2025", format="%.0f")
                          , 'VENDAS_2026': st.column_config.NumberColumn("VENDAS 2026", format="%.0f")}

def formatar_visualizacao_coluna_df_pandas():
   return {'PREVISAO' : '{:.0f}', 'PREVISAO_2025' : '{:.0f}', 'QUANTIDADE_VENDA_AJUS' : '{:.0f}', 'QUANTIDADE_VENDA_AJUS_SO' : '{:.0f}', 'FATURAMENTO ULT. 3M' : '{:.2f}'.replace(',', 'x').replace('.', ',').replace('x', '.')}


def moeda_brasileira(x):
    return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
