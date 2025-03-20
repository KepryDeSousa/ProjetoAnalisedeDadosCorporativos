import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Business Pro Analytics", page_icon="📈", layout="wide")

# Sidebar - Navegação e Upload
st.sidebar.title("📌 Controles")
page = st.sidebar.radio("Navegação", ["📊 Visão Geral", "📈 Estatísticas", "📉 Visualização", "📅 Tendências"])
uploaded_file = st.sidebar.file_uploader("Carregar Dados", type=["xlsx"])

# Processamento de Dados
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Mapeamento Dinâmico de Colunas
    with st.sidebar.expander("🔧 Configurar Colunas"):
        date_col = st.selectbox("Coluna de Data", df.columns)
        value_col = st.selectbox("Coluna de Valores", df.select_dtypes(include='number').columns)
        product_col = st.selectbox("Coluna de Produtos", df.columns)
        category_col = st.selectbox("Coluna de Categoria", [col for col in df.columns if col not in [date_col, value_col]])
    
    try:
        df[date_col] = pd.to_datetime(df[date_col])
    except Exception as e:
        st.error(f"Erro na coluna de data: {str(e)}")
        st.stop()

    # Filtros Universais
    with st.sidebar.expander("⏳ Filtros Temporais"):
        date_range = st.date_input("Período", 
                                 value=(df[date_col].min().date(), df[date_col].max().date()))
    
    df = df[(df[date_col].dt.date >= date_range[0]) & (df[date_col].dt.date <= date_range[1])]

    # Páginas Principais
    if page == "📊 Visão Geral":
        st.title("📈 Visão Executiva")
        
        # KPIs Dinâmicos
        col1, col2, col3 = st.columns(3)
        col1.metric("Faturamento Total", f"R$ {df[value_col].sum():,.2f}")
        col2.metric("Transações", len(df))
        col3.metric("Ticket Médio", f"R$ {df[value_col].sum()/len(df):,.2f}")

        # Gráficos Principais
        fig1 = px.bar(df.groupby(product_col)[value_col].sum().reset_index(),
                     x=product_col, y=value_col, title="Vendas por Produto")
        st.plotly_chart(fig1, use_container_width=True)

    elif page == "📈 Estatísticas":
        st.title("📊 Análise Estatística")
        
        st.dataframe(df.describe(), use_container_width=True)
        
        fig2 = px.histogram(df, x=value_col, nbins=20, title="Distribuição de Valores")
        st.plotly_chart(fig2, use_container_width=True)

    elif page == "📉 Visualização":
        st.title("🔍 Análise Exploratória")
        
        col_x = st.selectbox("Eixo X", df.columns)
        col_y = st.selectbox("Eixo Y", df.select_dtypes(include='number').columns)
        
        fig3 = px.scatter(df, x=col_x, y=col_y, color=category_col, hover_data=[product_col])
        st.plotly_chart(fig3, use_container_width=True)

    elif page == "📅 Tendências":
        st.title("📅 Análise Temporal")
        
        # Tendência Geral
        df_temp = df.groupby(date_col)[value_col].sum().reset_index()
        fig4 = px.line(df_temp, x=date_col, y=value_col, title="Evolução Temporal")
        st.plotly_chart(fig4, use_container_width=True)
        
        # Tendência por Categoria (Sua Funcionalidade Original)
        if category_col in df.columns:
            st.subheader("📈 Tendência por Categoria")
            df_cat = df.groupby([date_col, category_col])[value_col].sum().reset_index()
            
            # Controle de Categorias
            categorias = st.multiselect("Selecionar Categorias", df_cat[category_col].unique(),
                                      default=df_cat[category_col].unique()[:3])
            
            fig5 = px.line(df_cat[df_cat[category_col].isin(categorias)], 
                          x=date_col, y=value_col, color=category_col,
                          title="Evolução por Categoria")
            st.plotly_chart(fig5, use_container_width=True)

        # Sazonalidade (Versão Aprimorada)
        st.subheader("📅 Padrões Sazonais")
        df['Mês'] = df[date_col].dt.month_name()
        df_saz = df.groupby(['Mês', category_col])[value_col].sum().reset_index()
        
        fig6 = px.bar(df_saz, x='Mês', y=value_col, color=category_col,
                     category_orders={"Mês": ["January", "February", "March", "April", "May", "June",
                                             "July", "August", "September", "October", "November", "December"]},
                     title="Performance Mensal por Categoria")
        st.plotly_chart(fig6, use_container_width=True)

else:
       st.info("⏳ Carregue um arquivo para iniciar a análise", icon="ℹ️")