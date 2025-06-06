# pip install streamlit
# pip install streamlit-option-menu
# pip install plotly
# python -m streamlit run projeto.py

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# Configuração inicial
st.set_page_config(page_title="Impacto Ambiental", page_icon="🌱", layout="wide")

# Estilo personalizado (opcional)
def aplicar_estilo():
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

aplicar_estilo()

# Carregar os dados
df = pd.read_excel("dataBase.xlsx")

# Traduzir tipos de produto para português (sem alterar o original)
traducao_produtos = {
    "Polyester": "Poliéster",
    "Nylon": "Nylon",
    "Recycled_Poly": "Poliéster Reciclado",
    "Cotton": "Algodão",
    "Synthetic_Blend": "Mistura Sintética",
    "Organic_Cotton": "Algodão Orgânico",
    "Microfiber": "Microfibra",
    "Linen": "Linho",
    "Tencel": "Tencel",
    "Viscose": "Viscose",
    "Wool": "Lã"
}
df["Tipo_Produto_PT"] = df["Product_Type"].map(traducao_produtos)


# Sidebar - Filtros
st.sidebar.header("Filtros")

empresas = st.sidebar.multiselect(
    "Empresas",
    options=df["Company"].unique(),
    default=df["Company"].unique(),
    key="empresa"
)

produtos = st.sidebar.multiselect(
    "Tipos de Produto",
    options=df["Tipo_Produto_PT"].unique(),
    default=df["Tipo_Produto_PT"].unique(),
    key="produto"
)

anos = st.sidebar.multiselect(
    "Ano de Produção",
    options=sorted(df["Production_Year"].unique()),
    default=sorted(df["Production_Year"].unique()),
    key="ano"
)

# Aplicar filtros
df_filtrado = df.query("Company in @empresas and Tipo_Produto_PT in @produtos and Production_Year in @anos")

# Página principal
def Home():
    st.title("🌍 Visão Geral do Impacto Ambiental")

    total_emissoes = df_filtrado["Greenhouse_Gas_Emissions"].sum()
    media_agua = df_filtrado["Water_Consumption"].mean()
    receita_total = df_filtrado["Sales_Revenue"].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🌫️ Emissões Totais (CO₂)", f"{total_emissoes:,} kg")
    with col2:
        st.metric("💧 Média de Consumo de Água", f"{media_agua:,.0f} L")
    with col3:
        st.metric("💵 Receita Total", f"US$ {receita_total:,.2f}")

    st.markdown("---")
    
    st.title("📊 Análises Gráficas")

    col1, col2 = st.columns(2)

    with col1:
        fig_emissoes = px.bar(
            df_filtrado,
            x="Tipo_Produto_PT",
            y="Greenhouse_Gas_Emissions",
            color="Company",
            title="Emissões de CO₂ por Tipo de Produto",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        st.plotly_chart(fig_emissoes, use_container_width=True)


    with col2:
        fig_agua = px.bar(
            df_filtrado,
            x="Tipo_Produto_PT",
            y="Water_Consumption",
            color="Company",
            title="Consumo de Água por Tipo de Produto",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        st.plotly_chart(fig_agua, use_container_width=True)

    col3, col4, col5 = st.columns(3)
    with col3:
        fig_linha = px.line(
            df_filtrado.groupby("Production_Year").sum(numeric_only=True).reset_index(),
            x="Production_Year",
            y="Greenhouse_Gas_Emissions",
            title="Evolução das Emissões ao Longo dos Anos",
            markers=True,
        )
        st.plotly_chart(fig_linha, use_container_width=False)

    with col4:
        fig_rosca = px.pie(
            data_frame= df_filtrado.groupby("Tipo_Produto_PT").size().reset_index(name='quantidade'),
            values= "quantidade",
            hole=0.5,
            names='Tipo_Produto_PT',
            labels={'Materials': 'Tipo_Produto_PT'},
            title="Total de produtos"
        )
        st.plotly_chart(fig_rosca, use_container_width=True)
        
    with col5:
    # Agregar dados por companhia
        df_agg = df_filtrado.groupby("Company").agg({
            "Greenhouse_Gas_Emissions": "sum",
            "Sales_Revenue": "sum"
        }).reset_index()
        
        # Criar gráfico de dispersão com Plotly
        fig = px.scatter(
            df_agg,
            x="Greenhouse_Gas_Emissions",
            y="Sales_Revenue",
            color="Company",
            size= [8] * len(df_agg),
            hover_data=["Company"],  # Mostrar nome da companhia ao passar o mouse
            labels={
                "Greenhouse_Gas_Emissions": "Emissões de Gases de Efeito Estufa (Toneladas CO2e)",
                "Sales_Revenue": "Receita de Vendas (USD)",
                "Company": "Companhia"
            },
            title="Vendas vs Emissões de Gases de Efeito Estufa por Companhia"
        )
        st.plotly_chart(fig, use_container_width=True)

# Gráficos
def Graficos():
    st.title("📊 Análises Gráficas")

    col1, col2 , col3 = st.columns(3)

    with col1:
        fig_emissoes = px.bar(
            df_filtrado,
            x="Tipo_Produto_PT",
            y="Greenhouse_Gas_Emissions",
            color="Company",
            title="Emissões de CO₂ por Tipo de Produto",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        st.plotly_chart(fig_emissoes, use_container_width=True)


    with col2:
        fig_agua = px.bar(
            df_filtrado,
            x="Tipo_Produto_PT",
            y="Water_Consumption",
            color="Company",
            title="Consumo de Água por Tipo de Produto",
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        st.plotly_chart(fig_agua, use_container_width=True)

    fig_linha = px.line(
        df_filtrado.groupby("Production_Year").sum(numeric_only=True).reset_index(),
        x="Production_Year",
        y="Greenhouse_Gas_Emissions",
        title="Evolução das Emissões ao Longo dos Anos",
        markers=True
    )
    st.plotly_chart(fig_linha, use_container_width=False)
    
    with col3:
        # Agregar dados por companhia
        df_agg = df_filtrado.groupby("Company").agg({
            "Greenhouse_Gas_Emissions": "sum",
            "Sales_Revenue": "sum"
        }).reset_index()
        
        # Criar gráfico de dispersão com Plotly
        fig = px.scatter(
            df_agg,
            x="Greenhouse_Gas_Emissions",
            y="Sales_Revenue",
            color="Company",
            size= [8] * len(df_agg),
            hover_data=["Company"],  # Mostrar nome da companhia ao passar o mouse
            labels={
                "Greenhouse_Gas_Emissions": "Emissões de Gases de Efeito Estufa (Toneladas CO2e)",
                "Sales_Revenue": "Receita de Vendas (USD)",
                "Company": "Companhia"
            },
            title="Vendas vs Emissões de Gases de Efeito Estufa por Companhia"
        )
        st.plotly_chart(fig, use_container_width=True)

# Menu lateral
def sideBar():
    with st.sidebar:
        selecionado = option_menu(
            menu_title="Menu",
            options=["Home", "Gráficos"],
            icons=["house", "bar-chart"],
            default_index=0
        )
    if selecionado == "Home":
        Home()
    elif selecionado == "Gráficos":
        Graficos()

sideBar()
