import numpy as np
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from pacotes.graficoUtil import gerar_ultimos_meses


filtro_data_mape = datetime.now() - relativedelta(months=3)
filtro_data_mape2 = datetime.now()
data_filtro_mape = datetime.now() - relativedelta(months=12)
filtro_data_mape = filtro_data_mape.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
filtro_data_mape2 = filtro_data_mape2.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
data_filtro_mape = data_filtro_mape.replace(day=1, hour=0, minute=0, second=0, microsecond=0)



def mape(row: pd.Series):
    if row['QUANTIDADE_VENDA'] > 0 and row['PREVISAO'] > 0:
        mape = np.mean(np.abs((row['QUANTIDADE_VENDA'] - row['PREVISAO']) / row['QUANTIDADE_VENDA']))
        return mape
    elif (row['QUANTIDADE_VENDA'] > 0 and row['PREVISAO'] == 0) or (row['QUANTIDADE_VENDA'] == 0 and row['PREVISAO'] > 0):
        return 1
    else:
        return 0
    
def criar_dataframe_item(df_item):
    df_mape_item = df_item
    df_mape_item['MAPE'] = df_mape_item.apply(mape, axis=1)
    df_mape_item['DATA'] = pd.to_datetime(df_mape_item['DATA'], format='%Y%m')
    return df_mape_item

def calcular_mape_3m(df_mape_item, filtros) :
    quantidade_itens = filtros['quantidade_itens']
    quantidade_venda = filtros['quantidade_venda']
    quantidade_faturamento = filtros['quantidade_faturamento']

    df_mape_item = df_mape_item.query('DATA >= @filtro_data_mape and DATA < @filtro_data_mape2')
    df_mape_item_m3 = df_mape_item.groupby(['DESC_ITEM']).agg(MESES=pd.NamedAgg(column='DATA', aggfunc='count'), 
        MAPE_MEDIO=pd.NamedAgg(column='MAPE', aggfunc='mean'),
        VENDAS_MEDIA=pd.NamedAgg(column='QUANTIDADE_VENDA', aggfunc='mean'),
        FATURAMENTO=pd.NamedAgg(column='FATURAMENTO', aggfunc='sum'))
    df_mape_item_m3 = df_mape_item_m3.query('VENDAS_MEDIA >= @quantidade_venda and FATURAMENTO > @quantidade_faturamento').sort_values(['MAPE_MEDIO'],ascending=False).head(quantidade_itens)
    df_mape_item_m3['MAPE_MEDIO'] = df_mape_item_m3['MAPE_MEDIO'] * 100
    return df_mape_item_m3


def criar_relatorio_item_mape(df_item, filtro_item):
    df_item_filtrado = df_item[df_item['DESC_ITEM'].isin([filtro_item])].copy()
    df_item_filtrado['DATA'] = pd.to_datetime(df_item_filtrado['DATA'], format='%Y%m')
    df_datahistorico_filtrado = gerar_ultimos_meses(datetime.now(),36).copy()    
    df_datahistorico_filtrado = pd.merge(df_item_filtrado,df_datahistorico_filtrado, on='DATA', how='inner')
    df_datahistorico_filtrado['MAPE'] = df_datahistorico_filtrado.apply(mape, axis=1)
    df_datahistorico_filtrado['MAPE'] = df_datahistorico_filtrado['MAPE']
    df_datahistorico_filtrado= df_datahistorico_filtrado.query('DATA >= @data_filtro_mape and DATA <= @filtro_data_mape2')
    df_datahistorico_filtrado['MAPE'] =   df_datahistorico_filtrado['MAPE'] * 100
    return df_datahistorico_filtrado

def criar_relatorio_categoria_mape(df_vendas_previsao):
    df_mape_categoria = df_vendas_previsao.copy()
    df_mape_categoria['MAPE'] = df_mape_categoria.apply(mape,axis=1)
    df_mape_categoria = df_mape_categoria.query('DATA >= @data_filtro_mape and DATA <= @filtro_data_mape2')
    return df_mape_categoria