import pandas as pd
import streamlit as st
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
import plotly.express as px
import pacotes.graficoUtil as graficoutil
import pacotes.indicadorErro as indic
import pacotes.ajustedataframe as ajuste_data_frame
from sklearn.metrics import mean_absolute_error

st.set_page_config(layout='wide')
st.title('Analise de histórico e Previsão')

config = {'MAPE_MEDIO': st.column_config.NumberColumn("MAPE", format="%.0f%%")
                          ,'DESC_ITEM': st.column_config.TextColumn("DESC. DO ITEM")
                          ,'VENDAS_MEDIA': st.column_config.NumberColumn("VENDA 3M", format="%.2f")
                          ,'QUANTIDADE_VENDA': st.column_config.NumberColumn("VENDA", format="%.2f")
                          ,'QUANTIDADE_VENDA_AJUS': st.column_config.NumberColumn("VENDA AJUST. EVENTO", format="%.2f")
                          ,'QUANTIDADE_VENDA_AJUS_SO': st.column_config.NumberColumn("VENDA AJUST. S/ OUTLIER", format="%.2f")
                          , 'DATA' : st.column_config.DateColumn("Data", format="MM/YYYY")
                          , 'MAPE' : st.column_config.NumberColumn("MAPE", format="%.0f%%")
                          ,'FATURAMENTO': st.column_config.NumberColumn("FATURAMENTO", format="R$ %.2f")}

coluna1, coluna2 =  st.columns(2)

with coluna1:
    colunha1_upload, colunha2_upload = st.columns(2)
    with colunha1_upload:
        with st.container(height=200):
            uploaded_file = st.file_uploader(label='Importe seus dados', type=['xlsx','csv','xls'])


df_categoria = pd.DataFrame()

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, decimal=',', thousands='.')       
    ajuste_data_frame.ajustar_colunas_nula(df)

    df_item = ajuste_data_frame.ajustar_dataframe_analise_item(df,['DESC_ITEM','DATA','CATEGORIA'])

    df_item.sort_values(['QUANTIDADE_VENDA'], ascending=False)
    combo_opcoes = df['DESC_ITEM'].unique()

    df_categoria = ajuste_data_frame.ajustar_dataframe_analise_item(df,['DATA','CATEGORIA'])
    descricao_categoria = df_categoria['CATEGORIA'].unique()[0]
    

    df_categoria['DATA'] = pd.to_datetime(df_categoria['DATA'], format='%Y%m')
    
    df_vendas_previsao = graficoutil.gerar_ultimos_meses(datetime.now(),36).copy()
    df_controle_periodos_mes_atual = graficoutil.gerar_controle_periodo_mes_atual(datetime.now(),36)
    df_vendas_previsao = pd.merge(df_categoria, df_vendas_previsao, on='DATA', how='inner') 
    
    #"🔍 ITEM",
    tab_categoria, tab_item = st.tabs(["📈 Análise da Categoria ", "🔍 Análise de Item"])
        
    with tab_categoria:
        
        linha1_coluna1_categoria, linha1_coluna2_categoria = st.columns(2)
        with linha1_coluna1_categoria:
            format_dict = {'PREVISAO' : '{:.0f}', 'PREVISAO_2025' : '{:.0f}', 'QUANTIDADE_VENDA_AJUS' : '{:.0f}', 'QUANTIDADE_VENDA_AJUS_SO' : '{:.0f}'}
            st.dataframe(df_categoria[['DATA','CATEGORIA','QUANTIDADE_VENDA','QUANTIDADE_VENDA_AJUS','QUANTIDADE_VENDA_AJUS_SO','PREVISAO']].style.format(format_dict),column_config=config)
        
        with linha1_coluna2_categoria:
            eixo_y = []
            eixo_y.append('MÊS')
            qtd_anos = df_vendas_previsao['INDICE_ANO'].unique()
            df_vendas_mes_sobreposto = graficoutil.gerar_ajuste_dataframe_grafico(qtd_anos.size, df_vendas_previsao, 'QUANTIDADE_VENDA', eixo_y, df_controle_periodos_mes_atual)
            df_vendas_mes_sobreposto = df_vendas_mes_sobreposto.sort_values('INDICE_MES')
            st.dataframe(df_vendas_mes_sobreposto[eixo_y].style.format(format_dict))

        linha2_coluna1_categoria, linha2_coluna2_categoria = st.columns(2)
        with linha2_coluna1_categoria:
            fig_hist_vendas_categoria = px.line(df_vendas_previsao, x = 'DATA', y = ['QUANTIDADE_VENDA','QUANTIDADE_VENDA_AJUS','QUANTIDADE_VENDA_AJUS_SO','PREVISAO'], markers=True)
            graficoutil.atualiza_eixo_x(fig_hist_vendas_categoria,"%m-%Y",45,"M1", 0.8)
            graficoutil.atualiza_layout(fig_hist_vendas_categoria,f'HISTÓRICO DE VENDAS E PREVISÃO: {descricao_categoria}','Mês','Quantidade')
            st.plotly_chart(fig_hist_vendas_categoria, use_container_width=True, key='fig_hist_vendas_categoria', locale="pt-BR")
        
        with linha2_coluna2_categoria:
            data_filtro_mape = datetime.now() - relativedelta(months=12)
            data_filtro_mape2 = datetime.now()
            df_mape_categoria = df_vendas_previsao.copy()
            df_mape_categoria['MAPE'] = df_mape_categoria.apply(indic.mape,axis=1)
            df_mape_categoria = df_mape_categoria.query('DATA >= @data_filtro_mape and DATA <= @data_filtro_mape2')

            fig_mape_categoria = go.Figure()
            fig_mape_categoria.add_trace(go.Bar(x=df_mape_categoria['DATA'], y=df_mape_categoria['QUANTIDADE_VENDA'], name='VENDA'))
            fig_mape_categoria.add_trace(go.Bar(x=df_mape_categoria['DATA'], y=df_mape_categoria['PREVISAO'], name='PREVISAO'))
            fig_mape_categoria.add_trace(go.Scatter(x=df_mape_categoria['DATA'], y=df_mape_categoria['MAPE'], mode='lines+markers+text', name='MAPE CATEGORIA', yaxis='y2'))   
            graficoutil.atualiza_eixo_x(fig_mape_categoria,"%m-%Y",45,"M1", None)
            graficoutil.atualiza_layout_grafico_mape(fig_mape_categoria, f'CATEGORIA: {descricao_categoria}')
            st.plotly_chart(fig_mape_categoria, use_container_width=True, key='grafico_mape_categoria2', locale="pt-BR")
            
        
        

        coluna1, coluna2 = st.columns(2)
        with coluna1:
            eixo_y = []
            qtd_anos = df_vendas_previsao['INDICE_ANO'].unique()
            fig3 = px.line(graficoutil.gerar_ajuste_dataframe_grafico(qtd_anos.size, df_vendas_previsao, 'QUANTIDADE_VENDA', eixo_y, df_controle_periodos_mes_atual),x = 'MÊS', y = eixo_y)
            graficoutil.atualiza_eixo_x(fig3,"%m-%Y",45,"M1", 0.8)
            graficoutil.atualiza_layout(fig3,f'HISTÓRICO DE VENDAS E PREVISÃO (MÊS): {descricao_categoria}','Mês','Quantidade')
            st.plotly_chart(fig3, use_container_width=True, key='fig03', locale="pt-BR")

            eixo_y = []
            fig4 = px.line(graficoutil.gerar_ajuste_dataframe_grafico(qtd_anos.size, df_vendas_previsao, 'QUANTIDADE_VENDA_AJUS_SO', eixo_y, df_controle_periodos_mes_atual), x = 'MÊS', y = eixo_y)
            graficoutil.atualiza_eixo_x(fig4,"%m-%Y",45,"M1", 0.8)
            graficoutil.atualiza_layout(fig4,f'BASELINE (MÊS): {descricao_categoria}','Mês','Quantidade')
            st.plotly_chart(fig4, use_container_width=True, key='fig04', locale="pt-BR")

        with coluna2:
            
            data_filtro_mape = datetime.now() - relativedelta(months=12)
            data_filtro_mape2 = datetime.now()
            df_vendas_previsao['MAPE'] = df_vendas_previsao.apply(indic.mape,axis=1)
            df_vendas_previsao['MAPE'] = df_vendas_previsao['MAPE'] * 100
            df_vendas_previsao = df_vendas_previsao.query('DATA >= @data_filtro_mape and DATA <= @data_filtro_mape2')
            st.dataframe(df_vendas_previsao[['DATA','MAPE']], column_config=config)

        with tab_item:
            
            linha1_coluna1_item, linha1_coluna2_item, linha1_coluna3_item, linha1_coluna4_item, linha1_coluna5_item, linha1_coluna6_item, linha1_coluna7_item, linha1_coluna8_item = st.columns(8)
            with linha1_coluna1_item:
                quantidade_itens = st.slider("Quantidade de itens a ser visualizado:", 0, 300, 20)
            with linha1_coluna2_item:
                quantidade_venda =  st.number_input("Média de vendas relevante", min_value=1, step=5)
            with linha1_coluna3_item:
                quantidade_faturamento = st.number_input("Média de faturamento relevante", min_value=0, step=1000)
    

            linha2_coluna1_item, linha2_coluna2_item, linha2_coluna3_item = st.columns(3)
            
            with linha2_coluna1_item:
                df_mape_item = df_item
                df_mape_item['MAPE'] = df_mape_item.apply(indic.mape, axis=1)
                df_mape_item['DATA'] = pd.to_datetime(df_mape_item['DATA'], format='%Y%m')
                filtro_data_mape = datetime.now() - relativedelta(months=3)
                filtro_data_mape2 = datetime.now()
                filtro_data_mape = filtro_data_mape.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                filtro_data_mape2 = filtro_data_mape2.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                

                df_mape_item = df_mape_item.query('DATA >= @filtro_data_mape and DATA < @filtro_data_mape2')
                df_mape_item_m3 = df_mape_item.groupby(['DESC_ITEM']).agg(MESES=pd.NamedAgg(column='DATA', aggfunc='count'), 
                    MAPE_MEDIO=pd.NamedAgg(column='MAPE', aggfunc='mean'),
                    VENDAS_MEDIA=pd.NamedAgg(column='QUANTIDADE_VENDA', aggfunc='mean'),
                    FATURAMENTO=pd.NamedAgg(column='FATURAMENTO', aggfunc='mean'))
                df_mape_item_m3 = df_mape_item_m3.query('VENDAS_MEDIA >= @quantidade_venda and FATURAMENTO > @quantidade_faturamento').sort_values(['MAPE_MEDIO'],ascending=False).head(quantidade_itens)
                df_mape_item_m3['MAPE_MEDIO'] = df_mape_item_m3['MAPE_MEDIO'] * 100
                event = st.dataframe(df_mape_item_m3,on_select='rerun',selection_mode='single-row', column_config=config)
                
                if len(event.selection.rows) > 0:
                    indice_linha_selecionado = event.selection.rows
                    filtro_item = df_mape_item_m3.iloc[indice_linha_selecionado].index[0]
                    
                    
                    df_item_filtrado = df_item[df_item['DESC_ITEM'].isin([filtro_item])].copy()
                    df_item_filtrado['DATA'] = pd.to_datetime(df_item_filtrado['DATA'], format='%Y%m')
                    df_datahistorico_filtrado = graficoutil.gerar_ultimos_meses(datetime.now(),36).copy()    
                    df_datahistorico_filtrado = pd.merge(df_item_filtrado,df_datahistorico_filtrado, on='DATA', how='inner')

                    df_datahistorico_filtrado['MAPE'] = df_datahistorico_filtrado.apply(indic.mape, axis=1)
                    df_datahistorico_filtrado['MAPE'] = df_datahistorico_filtrado['MAPE']
                    df_datahistorico_filtrado= df_datahistorico_filtrado.query('DATA >= @data_filtro_mape and DATA <= @data_filtro_mape2')
                    df_datahistorico_filtrado[df_datahistorico_filtrado['DESC_ITEM'].isin([filtro_item])][['DATA','MAPE']]

                    fig_mape_item = go.Figure()
                    fig_mape_item.add_trace(go.Bar(x = df_datahistorico_filtrado['DATA'], y = df_datahistorico_filtrado['QUANTIDADE_VENDA'], name='VENDA'))
                    fig_mape_item.add_trace(go.Bar(x = df_datahistorico_filtrado['DATA'], y = df_datahistorico_filtrado['PREVISAO'], name='PREVISAO'))
                    graficoutil.atualiza_eixo_x(fig_mape_categoria,"%m-%Y",45,"M1", None)
                
                
                    fig_mape_item.add_trace(go.Scatter(x=df_datahistorico_filtrado['DATA'], y=df_datahistorico_filtrado['MAPE'], mode='lines+markers+text', name='MAPE', yaxis='y2'))   
                    graficoutil.atualiza_layout_grafico_mape(fig_mape_item,f'MAPE ITEM: {filtro_item}')
                    st.plotly_chart(fig_mape_item, use_container_width=True, key='grafico_mape_item2', locale="pt-BR")  
            
            with linha2_coluna2_item:
                if len(event.selection.rows) > 0:
                    df_item_filtrado = df_item[df_item['DESC_ITEM'].isin([filtro_item])].copy()
                    df_item_filtrado['DATA'] = pd.to_datetime(df_item_filtrado['DATA'], format='%Y%m')
                    df_datahistorico_filtrado = graficoutil.gerar_ultimos_meses(datetime.now(),36).copy()    
                    df_datahistorico_filtrado = pd.merge(df_item_filtrado,df_datahistorico_filtrado, on='DATA', how='inner')
                    st.dataframe(df_item_filtrado[['DATA','DESC_ITEM','QUANTIDADE_VENDA','QUANTIDADE_VENDA_AJUS','QUANTIDADE_VENDA_AJUS_SO','PREVISAO']])
                
                    eixo_y = []
                    fig_hist_vendas_item = px.line(df_item_filtrado, x = 'DATA', y = ['QUANTIDADE_VENDA', 'QUANTIDADE_VENDA_AJUS', 'QUANTIDADE_VENDA_AJUS_SO', 'PREVISAO'], markers=True)
                    graficoutil.atualiza_eixo_x(fig_hist_vendas_item, "%m-%Y", 45, "M1", 0.8)
                    graficoutil.atualiza_layout(fig_hist_vendas_item,f'HISTÓRICO DE VENDAS E PREVISÃO: {filtro_item}', 'Mês', 'Quantidade') 
                    st.plotly_chart(fig_hist_vendas_item, use_container_width=True, key='fig_hist_vendas_item', locale="pt-BR")

            with linha2_coluna3_item:
                if len(event.selection.rows) > 0:
                    eixo_y = []
                    eixo_y.append('MÊS')
                    qtd_anos = df_datahistorico_filtrado['INDICE_ANO'].unique()
                    df_vendas_mes_sobreposto = graficoutil.gerar_ajuste_dataframe_grafico(qtd_anos.size, df_datahistorico_filtrado, 'QUANTIDADE_VENDA', eixo_y, df_controle_periodos_mes_atual)
                    df_vendas_mes_sobreposto = df_vendas_mes_sobreposto.sort_values('INDICE_MES')
                    st.dataframe(df_vendas_mes_sobreposto[eixo_y].style.format(format_dict))

                    eixo_y = []
                    qtd_anos = df_datahistorico_filtrado['INDICE_ANO'].unique()
                    fig3 = px.line(graficoutil.gerar_ajuste_dataframe_grafico(qtd_anos.size, df_datahistorico_filtrado, 'QUANTIDADE_VENDA', eixo_y, df_controle_periodos_mes_atual),x = 'MÊS', y = eixo_y)
                    graficoutil.atualiza_eixo_x(fig3,"%m-%Y",45,"M1", 0.8)
                    graficoutil.atualiza_layout(fig3,f'HISTÓRICO DE VENDAS E PREVISÃO (MÊS): {filtro_item}','Mês','Quantidade')
                    st.plotly_chart(fig3, use_container_width=True, key='fig033', locale="pt-BR")

                    eixo_y = []
                    fig4 = px.line(graficoutil.gerar_ajuste_dataframe_grafico(qtd_anos.size, df_datahistorico_filtrado, 'QUANTIDADE_VENDA_AJUS_SO', eixo_y, df_controle_periodos_mes_atual), x = 'MÊS', y = eixo_y)
                    graficoutil.atualiza_eixo_x(fig4,"%m-%Y",45,"M1", 0.8)
                    graficoutil.atualiza_layout(fig4,f'BASELINE (MÊS): {filtro_item}','Mês','Quantidade')
                    st.plotly_chart(fig4, use_container_width=True, key='fig044', locale="pt-BR")
