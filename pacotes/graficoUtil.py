from dateutil.relativedelta import relativedelta
from datetime import datetime
import pandas as pd
import calendar


#Atualiza o eixo x para os gráfico gerados em linha
def atualiza_eixo_x(figure, tickFormat, tickangle, dtick, line_traces):
    figure.update_xaxes(
        tickformat=tickFormat,          # Formato do rótulo de data
        tickangle=tickangle,            # Ângulo dos rótulos para melhor legibilidade
        dtick=dtick                     # Frequência dos rótulos (diariamente)   
    )
    if line_traces is not None:
        figure.update_traces(line=dict(width=line_traces)) # Define a largura das linhas para 1
    return figure

#Atualiza os titulos dos gráficos
def atualiza_layout(figure, title, xaxis_title, yaxis_title):
    figure.update_layout(title=title, xaxis_title=xaxis_title, yaxis_title=yaxis_title)

def atualiza_layout_grafico_mape(figure, label):
    figure.update_layout(title=label, xaxis_title = 'Mês', yaxis_title = 'Quantidade', 
        yaxis2=dict(
            title = 'MAPE',
            overlaying='y',
            side='right',
            tickformat=".2%"
            ),
            barmode='group'
        )

#Gera um dataframe com os últimos 12 meses para trás, iniciando a partir do mês atual
#Essa dataframe será utilizado para gerar o gráficos com os meses de cada ano sobrepostos
def gerar_controle_periodo_mes_atual(data_referencia, num_meses=36):
    dados=[]

    resultado = 12 if num_meses > 12 else num_meses
    #Essa função tem como objetivo criar um controle de período a partir do mês atual para trás
    #Supondo que o mês atual seja Janeiro, então o período será 0 e o período do mês de dezembro será -1
    for i in range(resultado):
        data_historico = data_referencia - relativedelta(months=i)
        dados.append({'INDICE_MES': data_historico.month, 'INDICE_MES0':i*-1, 'MÊS': calendar.month_abbr[data_historico.month]})
        df_controle_periodo_mes_atual = pd.DataFrame(dados)    
    return df_controle_periodo_mes_atual


def gerar_ultimos_meses(data_referencia, num_meses=36, futuro = 6):

    dados=[]
    for i in range(num_meses):
        mes = data_referencia - relativedelta(months=i)
        dados.append({'INDICE': i * -1, 'DATA':mes})
        df = pd.DataFrame(dados)
              
        df['DATA'] = df['DATA'].apply(lambda x: x.replace(day=1, hour=0, minute=0, second=0, microsecond=0))
        df['INDICE_ANO'] = df['DATA'].apply(lambda x: (datetime.now().year - x.year) * -1)
        df['INDICE_MES'] = df['DATA'].apply(lambda x: x.month)
        df['INDICE_MES2'] = df['DATA'].apply(lambda x: x.month - datetime.now().month)
    
    dados=[]
    for i in range(futuro):
        mes = data_referencia + relativedelta(months=i+1)
        dados.append({'INDICE': i+1, 'DATA': mes})
        df_futuro = pd.DataFrame(dados)

        df_futuro['DATA'] = df_futuro['DATA'].apply(lambda x: x.replace(day=1, hour=0, minute=0, second=0, microsecond=0))
        df_futuro['INDICE_ANO'] = df_futuro['DATA'].apply(lambda x: ( x.year - datetime.now().year))
        df_futuro['INDICE_MES'] = df_futuro['DATA'].apply(lambda x: x.month)
        df_futuro['INDICE_MES2'] = df_futuro['DATA'].apply(lambda x: x.month - datetime.now().month)
    
    df = pd.concat([df,df_futuro], ignore_index=False).sort_values(['INDICE'])
    return df




def gerar_ajuste_dataframe_grafico(qtd_anos, df_datahistorico, campo, eixo_y, df_controle_periodo_mes_atual):
        df_final = pd.DataFrame()
        df_final = df_datahistorico.groupby(['INDICE_MES','INDICE_MES2']).agg(CONTADOR=pd.NamedAgg(column='INDICE', aggfunc='count')).reset_index()
        
        data_filtro_prev = datetime.now()
        data_filtro_prev = data_filtro_prev.replace(day=1)

        periodos = len(df_datahistorico.query('DATA >= @data_filtro_prev')['INDICE_ANO'].unique()) 
        df_previsao = df_datahistorico.query('INDICE_ANO >= 0 and INDICE_ANO < @periodos')
       
        for i in range(periodos):
            df_previsao_nv = df_previsao.query('INDICE_ANO == @i').copy()
            
            ano = datetime.now() - relativedelta(years=i)
            eixo_y.append(f'PREVISAO_{ano.year}')
            df_previsao_nv.rename(columns={'PREVISAO': f'PREVISAO_{ano.year}'}, inplace=True)
            df_final = pd.merge(df_final, df_previsao_nv[['INDICE_MES2','INDICE_MES', f'PREVISAO_{ano.year}']], on=['INDICE_MES','INDICE_MES2'], how='inner')
        
        for i in range(qtd_anos):
            df_datahistorico_nv = df_datahistorico.query('INDICE_ANO == @i * -1').copy()
            ano = datetime.now() - relativedelta(years=i)

            df_datahistorico_nv.rename(columns={campo: f'VENDAS_{ano.year}'}, inplace=True)
            
            eixo_y.append(f'VENDAS_{ano.year}')
            df_final = pd.merge(df_final, df_datahistorico_nv[['INDICE_MES2','INDICE_MES', f'VENDAS_{ano.year}']], on=['INDICE_MES','INDICE_MES2'], how='left')
            df_final[f'VENDAS_{ano.year}'] = df_final[f'VENDAS_{ano.year}'].fillna(0)
        
        
                  
        df_final = pd.merge(df_final, df_controle_periodo_mes_atual, on='INDICE_MES', how='inner')
        #df_final = df_final.sort_values(['INDICE_MES0'],ascending=True)
        df_final = df_final.sort_values(['INDICE_MES'],ascending=True)
        return df_final


