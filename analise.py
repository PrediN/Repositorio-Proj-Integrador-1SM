import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
import plotly.graph_objects as go
from streamlit_tags import st_tags

# Configurações  iniciais
st.set_page_config(page_title="Dashboard de Residuos", page_icon="☢️", layout="wide")

# Carregar dados
df_soma = pd.read_excel('./DF/somas_total_2013_2024.xlsx')
df_tipos = pd.read_excel('./DF/tipo_residuos_total.xlsx')
df_soma_mensal = pd.read_excel('./DF/total_mensal_fixed.xlsx')
df_soma_mensal_estimativa = pd.read_excel('./DF/total_mensal_fixed_ESTIMATIVA.xlsx')
df_previcao = pd.read_excel('./DF/previsoes_modelos.xlsx')
df_mensal = pd.read_excel('./DF/2013-2021.xlsx')

# Criar um filtro para retirar o total_geral para fazer somas
df_filtro = df_tipos[df_tipos['tipo_residuo'] != 'total_geral']

# Style
def aplicar_estilo():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
aplicar_estilo()

# Lista para configuração

meses = [
    'jan', 'fev', 'mar', 'abr', 'mai', 'jun', 'jul', 'ago', 'set', 'out', 'nov', 'dez']
meses_previcao = [
    'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov','dec']
meses_traducao = {
    'jan': 'jan', 'fev': 'feb', 'mar': 'mar', 'abr': 'apr',
    'mai': 'may', 'jun': 'jun', 'jul': 'jul', 'ago': 'aug',
    'set': 'sep', 'out': 'oct', 'nov': 'nov', 'dez': 'dec'
}
cores = {
    'Domiciliar': '#0068C9',          
    'Entulho Mecanizado': '#74B537',  
    'Diversos': '#E15759',            
    'Ecoponto': '#F28E2B',             
    'Piscinões': '#9467BD',            
    'Esgoto': '#FFC20A',               
    'Córregos': '#8C564B',            
    'Varricação Manual': '#E377C2',      
    'Feira Livre': '#7F7F7F',           
    'Coleta Seletiva': '#17BECF',      
}
labels_map = {
    'domiciliar': 'Domiciliar',
    'entulho_mecanizado': 'Entulho Mecanizado',
    'diversos': 'Diversos',
    'ecoponto': 'Ecoponto',
    'piscinoes': 'Piscinões',
    'esgoto': 'Esgoto',
    'corregos': 'Córregos',
    'varricao_manual': 'Varricação Manual',
    'feira_livre': 'Feira Livre',
    'coleta_seletiva': 'Coleta Seletiva',
}

# Replace

df_filtro['tipo_residuo'] = df_filtro['tipo_residuo'].replace(labels_map)
df_tipos['tipo_residuo'] = df_tipos['tipo_residuo'].replace(labels_map)
df_mensal['tipo_residuo'] = df_mensal['tipo_residuo'].replace(labels_map)


# Sidebar
st.sidebar.header("Selecione os Filtros")

# Filtro do tipo de residuo

with st.sidebar.expander("Configurações de Tipos de Resíduo"):
    tipo_residuo = st.multiselect(
        "Tipos de resíduo",
        options=df_filtro.nlargest(10, 'total_anos')['tipo_residuo'],  
        default=df_filtro.nlargest(10, 'total_anos')['tipo_residuo'],  
        help="Selecione um ou mais tipos de resíduos para visualizar no gráfico.",
        key='tipo'
    )


with st.sidebar.expander("Configurações de Faixa de Tempo"):
    ano = st.slider(
        'Faixa de tempo em anos',
        min_value=2013,
        max_value=2025,
        value=(2013,2025),
        help="Arraste para selecionar o intervalo de anos."
    )




# Aplicar filtro do tipo de residuo e do ano entre colunas
colunas_ano = [f'total_{a}' for a in range(ano[0], ano[1] + 1) if a != 2022 and a != 2025]
df_selecao_tipos = df_tipos.query(f"tipo_residuo in @tipo_residuo")[colunas_ano]


df_selecao_tipos_setor = df_tipos.query(f"tipo_residuo in @tipo_residuo")

# Restaurando as colunas perdidas
df_selecao_tipos['total_anos'] = df_selecao_tipos.iloc[:, 1:].select_dtypes(include='number').sum(axis=1)
df_selecao_tipos['tipo_residuo'] = df_tipos['tipo_residuo']

# Filtrar o df da soma pelo o tempo
df_selecao_soma = df_soma.query('@ano[0] <= ano <= @ano[1]')



# Ajustar o df da soma mensal de 2013 - 2024
colunas_meses_anos = [f'{mes}/{ i - 2000}' for i in range(ano[0], ano[1] + 1)  if i != 2022 and i != 2025 for mes in meses ]
df_selecao_soma_mensal = df_soma_mensal[colunas_meses_anos]

df_selecao_soma_mensal_long = pd.melt(
    df_selecao_soma_mensal,
    var_name='meses/ano',   
    value_name='total_geral'    
)



# Ajustar o df da soma mensal de 2013 - 2020
colunas_meses_anos_estimativa = [f'{mes}/{ i - 2000}' for i in range(ano[0], ano[1] + 1)  if i <= 2020 for mes in meses ]
df_selecao_soma_mensal_estimativa = df_soma_mensal_estimativa[colunas_meses_anos_estimativa]

df_selecao_soma_mensal_estimativa_long = pd.melt(
    df_selecao_soma_mensal_estimativa,
    var_name='meses/ano',   
    value_name='total_geral'    
)

df_selecao_soma_mensal_estimativa_long['meses/ano'] = df_selecao_soma_mensal_estimativa_long['meses/ano'].replace(meses_traducao, regex=True)
df_selecao_soma_mensal_estimativa_long['meses/ano'] = pd.to_datetime(df_selecao_soma_mensal_estimativa_long['meses/ano'], format='%b/%y')

df_selecao_soma_mensal_long['meses/ano'] = df_selecao_soma_mensal_long['meses/ano'].replace(meses_traducao, regex=True)
df_selecao_soma_mensal_long['meses/ano'] = pd.to_datetime(df_selecao_soma_mensal_long['meses/ano'], format='%b/%y')

# Filtrar df_previsao 
coluna_ano_previsao = [
    f'{mes}/{i - 2000}' 
    for i in range(ano[0], ano[1] + 1) 
    for mes in meses_previcao 
    if (i == 2020 and mes == 'dec') or 
        (2021 <= i <= 2025 and (i < 2025 or mes in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct']))
]
coluna_ano_previsao_datetime = pd.to_datetime(coluna_ano_previsao, format='%b/%y')
df_selecao_previsao = df_previcao.query('ds in @coluna_ano_previsao_datetime')


# Ajustar df mensal 
colunas_meses_anos_34 = [f'{mes}/{i - 2000}'  for i in range(ano[0], ano[1] + 1)   if i <= 2020  for mes in meses  ]
df_selecao_mensal = df_mensal.query(f"tipo_residuo in @tipo_residuo")[colunas_meses_anos_34]
df_selecao_mensal['tipo_residuo'] = df_mensal['tipo_residuo']

df_selecao_mensal.columns = df_selecao_mensal.columns.str.replace(r'(\w{3})/(\d{2})', lambda m: f'{meses_traducao[m.group(1)]}/{m.group(2)}', regex=True)

df_selecao_mensal_long = pd.melt(
    df_selecao_mensal, 
    id_vars=['tipo_residuo'], 
    var_name='mes_ano',    
    value_name='total'
)      

df_selecao_mensal_long['mes_ano'] = pd.to_datetime(df_selecao_mensal_long['mes_ano'], format='%b/%y')

# Funções para exibir

# Números gerais
def Home():
    st.title('Coletas de lixo de 2013 a 2024')

    total_vendas = df_selecao_soma['soma_total'].sum()

    st.metric('Total coletado', value=f"{total_vendas:.2f}", border=True)

# Graficos do total gerado por mês com previções de 2021 - 2025. Comparando com os dados que já existem
def previsao():

    fig_linha = px.line(
        df_selecao_soma_mensal_long,
        x= 'meses/ano',
        y='total_geral',
        title='Total coletado ao longo dos anos',
        labels={
            'total_geral': 'Total Geral',
            'meses/ano': 'Tempo'
        }
    )
    
    fig_linha.update_layout(
        xaxis=dict(showgrid=True),  # Grade vertical
        yaxis=dict(showgrid=True),  # Grade horizontal
        template='plotly_white'  # Tema claro para destacar as grades
    )

    fig_linha.update_traces(
    hovertemplate=(
        '<b>Data:</b> %{x}<br>'        # Exibe o mês/ano no eixo X
        '<b>Total Geral:</b> %{y}<br>'   # Exibe o total geral no eixo Y
        '<extra></extra>'                # Remove o texto adicional padrão do Plotly
    )
    )
    
    fig_linha_previcao = go.Figure()

    fig_linha_previcao.add_trace(go.Scatter(
        x=df_selecao_soma_mensal_estimativa_long['meses/ano'], 
        y=df_selecao_soma_mensal_estimativa_long['total_geral'], 
        mode='lines', 
        name='Histórico', 
        line=dict(color='#0068C9')
    ))
    
    fig_linha_previcao.add_trace(go.Scatter(
        x=df_selecao_previsao['ds'], 
        y=df_selecao_previsao['Previsao_ARIMA'], 
        mode='lines', 
        name='Previsão',
        line=dict(dash='dot',  color='#FF5733'),  # Define a linha como traçada
    ))
    
    fig_linha_previcao.update_layout(
        title='Total coletado ao longo dos anos com previsão',
        xaxis=dict(
            showgrid=True,
            title='Tempo'  # Rótulo do eixo X
        ),
        yaxis=dict(
            showgrid=True,
            title='Total Geral'  # Rótulo do eixo Y
        ),
        template='plotly_white'  # Tema claro para destacar as grades
)
    fig_linha_previcao.update_traces(
        hovertemplate=(
            '<b>Data:</b> %{x}<br>'        # Exibe o mês/ano no eixo X
            '<b>Total Geral:</b> %{y}<br>'   # Exibe o total geral no eixo Y
            '<extra></extra>'                # Remove o texto adicional padrão do Plotly
        )
    )
    
    st.plotly_chart(fig_linha,  use_container_width=True)

    st.plotly_chart(fig_linha_previcao,  use_container_width=True)

    
    colunas_2013 = [f'{mes}/{i - 2000}'  for i in range(2013,2026)    if i == 2013  for mes in meses ]
    media_2013 = df_soma_mensal_estimativa[colunas_2013].values.mean()

    colunas_2024 = [f'{mes}/{i - 2000}'  for i in range(2013,2026)   if i == 2024  for mes in meses_previcao]
    colunas_2024_datatime = pd.to_datetime(colunas_2024, format='%b/%y')
    filtro_2024 = df_previcao.query('ds in @colunas_2024_datatime')
    media_2024 = filtro_2024['Previsao_ARIMA'].values.mean()

    metric1, metric2 = st.columns(2)
    with metric1:
        st.metric('Média de coleta de 2013', value=f"{media_2013:.0f}", border=True)
    with metric2:
        st.metric('Média de coleta de 2024', value=f"{media_2024:.0f}", border=True)

# Grafico do total gerado por mês separado pelo os tipos de resíduo
def soma_tipo():
    
    df_soma_residuos = df_selecao_mensal_long.groupby('tipo_residuo')['total'].sum().reset_index()

    # Selecionando os 20 tipos de resíduo com os maiores totais
    df_top_20_residuos = df_soma_residuos.nlargest(10, 'total')

    # Filtrando o DataFrame original para incluir apenas os 20 maiores totais
    df_mensal_top_20 = df_selecao_mensal_long[df_selecao_mensal_long['tipo_residuo'].isin(df_top_20_residuos['tipo_residuo'])]

    # Gerando o gráfico de linha para os 20 maiores totais
    fig_linha_residuos = px.line(
        df_mensal_top_20,
        x='mes_ano',
        y='total',
        color='tipo_residuo',  # Cada tipo de resíduo terá uma linha diferente
        title="Top 10 Tipos de Resíduos Coletados de 2013 a 2020",
        labels={
            'mes_ano': 'Tempo',
            'total': 'Total Coletado',
            'tipo_residuo': 'Tipo de Resíduo'
        },
        color_discrete_map=cores  # Usando a paleta de cores que você já definiu
    )

    # Ajustando layout
    fig_linha_residuos.update_layout(
        xaxis=dict(showgrid=True),  # Grade vertical
        yaxis=dict(showgrid=True),  # Grade horizontal
        template='plotly_white',  # Tema claro
    )

    # Exibindo o gráfico
    st.plotly_chart(fig_linha_residuos, use_container_width=True)

# Grafico de barras que mostra os 10 maiores tipos de residuos coletados
def tipo_residuo_graficos():

    fig_barras = px.bar(    
        df_selecao_tipos.sort_values(by='total_anos', ascending=False),
        x="total_anos",
        y="tipo_residuo",
        color="tipo_residuo",
        title="Quantidade de Resíduos de todos os anos",
        color_discrete_map=(cores),
        labels={
            'tipo_residuo': 'Tipos de Resíduo',
            'total_anos': 'Total Geral'
        }
    )


    fig_barras.update_traces(
        hovertemplate=(
            '<b>Tipo de Resíduo:</b> %{y}<br>'  # Nome do tipo de resíduo
            '<b>Total:</b> %{x}<br>'           # Quantidade total
            '<extra></extra>'                  # Remove o texto extra padrão
        )
    )


    st.plotly_chart(fig_barras,  use_container_width=True)

# Gera 2 graficos de setor por um select para comparar proporções entre anos
def proporcao():

    select1, select2 = st.columns(2)
    with select1:
        ano_pie_1 = st.selectbox(
            'Selecione o ano do gráfico abaixo:',
            options=range(2013, 2021),
            index=0,
            key='pie1'
        )
    with select2:
        ano_pie_2 = st.selectbox(
            'Selecione o ano do gráfico abaixo:',
            options=[x for x in range(2013, 2021) if x != ano_pie_1],
            index=6,
            key='pie2',
        )


    setor1, setor2 = st.columns(2)
    with setor1:

        fig_pie1 = px.pie(
            df_selecao_tipos_setor.nlargest(5, f'total_{ano_pie_1}'),
            names='tipo_residuo',
            values=f'total_{ano_pie_1}',
            color='tipo_residuo',
            color_discrete_map=(cores),
            title=f'Divisão de tipos de resíduo no ano de {ano_pie_1}',
        )

        fig_pie1.update_traces(
            hovertemplate=(
                '<b>Tipo de Resíduo:</b> %{label}<br>'   # Nome do tipo de resíduo
                '<b>Total:</b> %{value}<br>'             # Valor total
                '<b>Porcentagem:</b> %{percent}<br>'     # Porcentagem do total
                '<extra></extra>'                        # Remove o texto adicional padrão do Plotly
            )
        )

        total_do_ano_1 = df_soma['soma_total'][df_soma['ano'] == ano_pie_1].iloc[0]

        st.plotly_chart(fig_pie1,  use_container_width=True)
        st.metric(f'Total coletado no ano de {ano_pie_1}', value=f"{total_do_ano_1}", border=True)
        
    with setor2:


        fig_pie2 = px.pie(
            df_selecao_tipos_setor.nlargest(5, f'total_{ano_pie_2}'),
            names='tipo_residuo',
            values=f'total_{ano_pie_2}',
            color='tipo_residuo',
            color_discrete_map=(cores),
            title=f'Divisão de tipos de resíduo no ano de {ano_pie_2}'
        )

        fig_pie2.update_traces(
            hovertemplate=(
                '<b>Tipo de Resíduo:</b> %{label}<br>'   # Nome do tipo de resíduo
                '<b>Total:</b> %{value}<br>'             # Valor total
                '<b>Porcentagem:</b> %{percent}<br>'     # Porcentagem do total
                '<extra></extra>'                        # Remove o texto adicional padrão do Plotly
            )
        )

        total_do_ano_2 = df_soma['soma_total'][df_soma['ano'] == ano_pie_2].iloc[0]
        
        st.plotly_chart(fig_pie2,  use_container_width=True)
        st.metric(f'Total coletado no ano de {ano_pie_2}', value=f"{total_do_ano_2}", border=True)
    

Home()
previsao()
st.markdown('- - -')
proporcao()
st.markdown('- - -')
soma_tipo()
tipo_residuo_graficos()




# python -m streamlit run analise.py



