import pandas as pd
import streamlit as st
from datetime import datetime
import plotly.graph_objects as go
from dateutil.relativedelta import relativedelta
import plotly.express as px
import pacotes.graficoUtil as graficoutil
import pacotes.indicadorErro as indic
import pacotes.ajustedataframe as ajuste_data_frame
from sklearn.metrics import mean_absolute_error
from statsmodels.tsa.seasonal import seasonal_decompose
import locale
import plotly.subplots as sp


#locale.setlocale(locale.LC_ALL, 'pt_BR')
st.set_page_config(layout='wide')
st.title('Analise de histórico e Previsão')

format_dict = ajuste_data_frame.formatar_visualizacao_coluna_df_pandas()
config = ajuste_data_frame.formatar_coluna_dataframe_streamlit(st)


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
    
    df_item = ajuste_data_frame.ajustar_dataframe_analise(df,['DESC_ITEM','DATA','CATEGORIA','EVENTO','IMPACTO'])
    df_item['PONTO_EVENTO'] = df_item.apply(lambda row: None if row.IMPACTO == '-' else row.QUANTIDADE_VENDA_AJUS, axis=1)
    df_item.sort_values(['QUANTIDADE_VENDA'], ascending=False)
    
    combo_opcoes = df['DESC_ITEM'].unique()

    df_categoria = ajuste_data_frame.ajustar_dataframe_analise(df,['DATA','CATEGORIA'])
    descricao_categoria = df_categoria['CATEGORIA'].unique()[0]
    
    df_vendas_previsao = graficoutil.gerar_ultimos_meses(datetime.now(),36).copy()
    df_controle_periodos_mes_atual = graficoutil.gerar_controle_periodo_mes_atual(datetime.now(),36)
    df_vendas_previsao = pd.merge(df_categoria, df_vendas_previsao, on='DATA', how='inner') 
    
    tab_categoria, tab_item = st.tabs(["📈 Análise da Categoria ", "🔍 Análise de Item"])
        
    with tab_categoria:        
        
        linha1_coluna1_categoria, linha1_coluna2_categoria = st.columns(2)
        with linha1_coluna1_categoria:
            format_dict = ajuste_data_frame.formatar_visualizacao_coluna_df_pandas()
            st.dataframe(df_categoria[['DATA','CATEGORIA','QUANTIDADE_VENDA','QUANTIDADE_VENDA_AJUS','QUANTIDADE_VENDA_AJUS_SO','PREVISAO']].style.format(format_dict), column_config=config)
        
        with linha1_coluna2_categoria:
            eixo_y = []
            eixo_y.append('MÊS')
            qtd_anos = df_vendas_previsao['INDICE_ANO'].unique()
            df_vendas_mes_sobreposto = graficoutil.gerar_ajuste_dataframe_grafico(qtd_anos.size, df_vendas_previsao, 'QUANTIDADE_VENDA', eixo_y, df_controle_periodos_mes_atual)
            df_vendas_mes_sobreposto = df_vendas_mes_sobreposto.sort_values('INDICE_MES')
            st.dataframe(df_vendas_mes_sobreposto[eixo_y], column_config=config)

        
        linha2_coluna1_categoria, linha2_coluna2_categoria = st.columns(2)
        with linha2_coluna1_categoria:
            fig_hist_vendas_categoria = px.line(df_vendas_previsao, x = 'DATA', y = ['QUANTIDADE_VENDA','QUANTIDADE_VENDA_AJUS','QUANTIDADE_VENDA_AJUS_SO','PREVISAO'], markers=True)
            graficoutil.atualiza_eixo_x(fig_hist_vendas_categoria,"%m-%Y",45,"M1", 0.8)
            graficoutil.atualiza_layout(fig_hist_vendas_categoria,f'HISTÓRICO DE VENDAS E PREVISÃO: {descricao_categoria}','Mês','Quantidade')
            st.plotly_chart(fig_hist_vendas_categoria, use_container_width=True, key='fig_hist_vendas_categoria', locale="pt-BR")
        
        with linha2_coluna2_categoria:
            
            df_mape_categoria = indic.criar_relatorio_categoria_mape(df_vendas_previsao)
            fig_mape_categoria = go.Figure()
            fig_mape_categoria.add_trace(go.Bar(x=df_mape_categoria['DATA'], y=df_mape_categoria['QUANTIDADE_VENDA'], name='VENDA'))
            fig_mape_categoria.add_trace(go.Bar(x=df_mape_categoria['DATA'], y=df_mape_categoria['PREVISAO'], name='PREVISAO'))
            fig_mape_categoria.add_trace(go.Scatter(x=df_mape_categoria['DATA'], y=df_mape_categoria['MAPE'], mode='lines+markers+text', name='MAPE CATEGORIA', yaxis='y2'))   
            graficoutil.atualiza_eixo_x(fig_mape_categoria,"%m-%Y",45,"M1", None)
            graficoutil.atualiza_layout_grafico_mape(fig_mape_categoria, f'CATEGORIA: {descricao_categoria}')
            st.plotly_chart(fig_mape_categoria, use_container_width=True, key='grafico_mape_categoria2', locale="pt-BR")
            

        linha3_coluna1_categoria, linha3_coluna2_categoria = st.columns(2)
        with linha3_coluna1_categoria:
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

        with linha3_coluna2_categoria:
            
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
                quantidade_venda =  st.number_input("Média de vendas dos últimos 3 meses:", min_value=1, step=5)

            with linha1_coluna3_item:
                quantidade_faturamento = st.number_input("Faturamento dos últimos 3 meses:", min_value=0, step=1000)
 
    
            filtros = {'quantidade_itens' : quantidade_itens, 'quantidade_venda' : quantidade_venda, 'quantidade_faturamento' : quantidade_faturamento}
            df_mape_item = indic.criar_dataframe_item(df_item)
            df_mape_item_m3 = indic.calcular_mape_3m(df_item, filtros)
            
            
            
            event = st.dataframe(df_mape_item_m3[['FATURAMENTO','MAPE_MEDIO','VENDAS_MEDIA']].style.format({'FATURAMENTO':ajuste_data_frame.moeda_brasileira}),on_select='rerun',selection_mode='single-row', column_config=config)
                
                
            linha3_coluna1_item, linha3_coluna2_item = st.columns(2)
            with linha3_coluna1_item:
                with st.expander("Análise indicador MAPE"):
                    if len(event.selection.rows) > 0:
                        st.subheader("Relatório", divider=True)
                        indice_linha_selecionado = event.selection.rows
                        filtro_item = df_mape_item_m3.iloc[indice_linha_selecionado].index[0]
                        df_datahistorico_filtrado = indic.criar_relatorio_item_mape(df_item, filtro_item)                        
                        st.dataframe(df_datahistorico_filtrado[df_datahistorico_filtrado['DESC_ITEM'].isin([filtro_item])][['DATA','MAPE']],column_config=config)

                        st.subheader("Gráfico", divider=True)
                        fig_mape_item = go.Figure()
                        fig_mape_item.add_trace(go.Bar(x = df_datahistorico_filtrado['DATA'], y = df_datahistorico_filtrado['QUANTIDADE_VENDA'], name='VENDA'))
                        fig_mape_item.add_trace(go.Bar(x = df_datahistorico_filtrado['DATA'], y = df_datahistorico_filtrado['PREVISAO'], name='PREVISAO'))
                        graficoutil.atualiza_eixo_x(fig_mape_item,"%m-%Y",45,"M1", None)
                    
                    
                        fig_mape_item.add_trace(go.Scatter(x=df_datahistorico_filtrado['DATA'], y=df_datahistorico_filtrado['MAPE']/100, mode='lines+markers+text', name='MAPE', yaxis='y2'))   
                        graficoutil.atualiza_layout_grafico_mape(fig_mape_item,f'MAPE ITEM: {filtro_item}')
                        st.plotly_chart(fig_mape_item, use_container_width=True, key='grafico_mape_item2', locale="pt-BR")  
                
                with st.expander("Análise Relatório de Vendas"):
                    if len(event.selection.rows) > 0:
                        st.subheader("Relatório", divider=True)
                        df_item_filtrado = df_item[df_item['DESC_ITEM'].isin([filtro_item])].copy()
                        df_item_filtrado['DATA'] = pd.to_datetime(df_item_filtrado['DATA'], format='%Y%m')
                        df_datahistorico_filtrado = graficoutil.gerar_ultimos_meses(datetime.now(),36).copy()    
                        df_datahistorico_filtrado = pd.merge(df_item_filtrado,df_datahistorico_filtrado, on='DATA', how='inner')
                        st.dataframe(df_item_filtrado[['DATA','DESC_ITEM','QUANTIDADE_VENDA','QUANTIDADE_VENDA_AJUS','QUANTIDADE_VENDA_AJUS_SO','PREVISAO']],column_config=config)
                    

            with linha3_coluna2_item:
                if len(event.selection.rows) > 0:
                    with st.expander("Análise relatório comparação das vendas mensais nos anos (anos sobrepostos)"):
                        st.subheader("Venda Histórica sem ajuste", divider=True)
                        eixo_y = []
                        eixo_y.append('MÊS')
                        qtd_anos = df_datahistorico_filtrado['INDICE_ANO'].unique()
                        df_vendas_mes_sobreposto = graficoutil.gerar_ajuste_dataframe_grafico(qtd_anos.size, df_datahistorico_filtrado, 'QUANTIDADE_VENDA', eixo_y, df_controle_periodos_mes_atual)
                        df_vendas_mes_sobreposto = df_vendas_mes_sobreposto.sort_values('INDICE_MES')
                        st.dataframe(df_vendas_mes_sobreposto[eixo_y].style.format(format_dict))
                        
                        st.subheader("Venda Histórica com ajuste", divider=True)
                        eixo_y = []
                        eixo_y.append('MÊS')
                        qtd_anos = df_datahistorico_filtrado['INDICE_ANO'].unique()
                        df_vendas_mes_sobreposto = graficoutil.gerar_ajuste_dataframe_grafico(qtd_anos.size, df_datahistorico_filtrado, 'QUANTIDADE_VENDA_AJUS_SO', eixo_y, df_controle_periodos_mes_atual)
                        df_vendas_mes_sobreposto = df_vendas_mes_sobreposto.sort_values('INDICE_MES')
                        st.dataframe(df_vendas_mes_sobreposto[eixo_y].style.format(format_dict))

                    with st.expander("Análise gráfica comparação das vendas mensais (anos sobrepostos)"):
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
            
            
            if len(event.selection.rows) > 0:
                with st.expander("Análise Gráfica Histórico de Vendas"):
                    st.subheader("Gráfico Histórico de Vendas", divider=True)
                    eixo_y = []
                    fig_hist_vendas_item = px.line(df_item_filtrado, x = 'DATA', y = ['QUANTIDADE_VENDA', 'QUANTIDADE_VENDA_AJUS', 'QUANTIDADE_VENDA_AJUS_SO', 'PREVISAO'], markers=True)
                    graficoutil.atualiza_eixo_x(fig_hist_vendas_item, "%m-%Y", 45, "M1", 0.8)
                    graficoutil.atualiza_layout(fig_hist_vendas_item,f'{filtro_item}', 'Mês', 'Quantidade') 

                    fig_hist_vendas_item.add_trace(
                        go.Scatter(
                        x=df_item_filtrado['DATA'],
                        y=df_item_filtrado['PONTO_EVENTO'],
                        mode='markers',
                        name='Evento',
                        hovertext=df_item_filtrado['EVENTO'],
                        hoverinfo='text',
                        marker=dict(symbol='star', size=12, color='gold')
                        )
                        )
                    st.plotly_chart(fig_hist_vendas_item, use_container_width=True, key='fig_hist_vendas_item', locale="pt-BR")
            
            with st.expander("Análise Decomposição Clássica"):
                if len(event.selection.rows) > 0:
                    st.subheader("Decomposição Clássica", divider=True)
                    filtro_data_decomposicao = datetime.now()
                    df_item_decomposicao = df_item_filtrado.query('DATA < @filtro_data_decomposicao').copy()
                    df_item_decomposicao = df_item_decomposicao.set_index('DATA')
                    resultado = seasonal_decompose(df_item_decomposicao['QUANTIDADE_VENDA'], model='additive', period=12)
                    resultado1 = seasonal_decompose(df_item_decomposicao['QUANTIDADE_VENDA_AJUS_SO'], model='additive', period=12)
                    

                    # Criando subplots com plotly
                    fig = sp.make_subplots(rows=4, cols=2, shared_xaxes=True, 
                                        subplot_titles=('Histórico Original', 'Histórico limpo Original', 'Tendência', 'Tendência Hist. Limpo', 'Sazonalidade', 'Sazonalidade Hist. Limpo', 'Resíduo', 'Resíduo Hist. Limpo'))

                    fig.add_trace(go.Scatter(x=resultado.observed.index, y=resultado.observed, name='Histórico Original', showlegend=False), row=1, col=1)
                    fig.add_trace(go.Scatter(x=resultado1.observed.index, y=resultado1.observed, name='Histórico limpo Original', showlegend=False), row=1, col=2) 

                    fig.add_trace(go.Scatter(x=resultado.trend.index, y=resultado.trend, name='Tendência', showlegend=False), row=2, col=1)
                    fig.add_trace(go.Scatter(x=resultado1.trend.index, y=resultado1.trend, name='Tendência Hist. Limpo', showlegend=False), row=2, col=2)

                    fig.add_trace(go.Scatter(x=resultado.seasonal.index, y=resultado.seasonal, name='Sazonalidade', showlegend=False), row=3, col=1)
                    fig.add_trace(go.Scatter(x=resultado1.seasonal.index, y=resultado1.seasonal, name='Sazonalidade Hist. Limpo', showlegend=False), row=3, col=2)
                    
                    fig.add_trace(go.Scatter(x=resultado.resid.index, y=resultado.resid, name='Resíduo', showlegend=False), row=4, col=1)
                    fig.add_trace(go.Scatter(x=resultado1.resid.index, y=resultado1.resid, name='Resíduo Hist. Limpo', showlegend=False), row=4, col=2)

                    fig.update_layout(height=900)
                    st.plotly_chart(fig)
