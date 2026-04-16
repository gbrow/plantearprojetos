# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from collections import Counter
import requests
from io import StringIO

# Configuração da página
st.set_page_config(page_title="Painel de Projetos - PLANTEAR", layout="wide")

# ===================== FUNÇÃO PARA CARREGAR CSV DO GITHUB =====================

@st.cache_data(ttl=3600, show_spinner="Carregando dados do GitHub...")
def carregar_csv_github():
    """
    Carrega o arquivo CSV diretamente do GitHub usando Raw URL
    Atualiza automaticamente a cada 1 hora (ttl=3600 segundos)
    """
    
    # URL RAW do seu CSV no GitHub
    # Substitua pela URL do SEU arquivo!
    # Como pegar: Vá no GitHub → Seu arquivo CSV → Botão "Raw" → Copie a URL
    URL_CSV = "https://raw.githubusercontent.com/gbrow/plantearprojetos/refs/heads/main/dados/projetos.csv"
    
    try:
        # Baixar o arquivo
        response = requests.get(URL_CSV)
        response.raise_for_status()  # Verifica se houve erro
        
        # Converter para DataFrame
        content = StringIO(response.text)
        df = pd.read_csv(content, encoding='utf-8')
        
        # Processar os dados (adaptar conforme seu CSV)
        df = processar_dados(df)
        
        st.success("✅ Dados carregados com sucesso do GitHub!")
        return df
        
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Erro ao carregar dados do GitHub: {e}")
        st.info("Usando dados de exemplo para demonstração...")
        
        # Dados de exemplo como fallback
        return criar_dados_exemplo()

def processar_dados(df):
    """
    Processa e limpa os dados do DataFrame
    Adapte esta função conforme a estrutura do seu CSV
    """
    
    # Verificar se as colunas necessárias existem
    colunas_necessarias = ['Projeto', 'Descrição do projeto', 'Equipe', 'Coordenação']
    
    # Se as colunas estiverem em português, renomear
    if 'Descrição do projeto' in df.columns and 'Descrição' not in df.columns:
        df.rename(columns={'Descrição do projeto': 'Descrição'}, inplace=True)
    
    # Verificar se há colunas de quantidades
    if 'Quantidade de pessoas da graduação necessárias' in df.columns:
        df.rename(columns={
            'Quantidade de pessoas da graduação necessárias': 'Qtd_Graduacao',
            'Quantidade de pessoas da pós-graduação necessárias': 'Qtd_Pos',
            'Quantidade de pessoas docentes necessárias': 'Qtd_Docentes'
        }, inplace=True)
    
    # Processar datas
    if 'Previsão de início do projeto' in df.columns:
        df['inicio_date'] = pd.to_datetime(df['Previsão de início do projeto'], 
                                          format='%d/%m/%Y', 
                                          errors='coerce')
    else:
        df['inicio_date'] = pd.NaT
    
    if 'Previsão de término do projeto' in df.columns:
        df['termino_date'] = pd.to_datetime(df['Previsão de término do projeto'], 
                                           format='%d/%m/%Y', 
                                           errors='coerce')
    else:
        df['termino_date'] = pd.NaT
    
    # Converter listas se estiverem como string
    if 'Habilidades indispensáveis ao projeto' in df.columns:
        df['Habilidades'] = df['Habilidades indispensáveis ao projeto'].apply(
            lambda x: [item.strip() for item in str(x).strip('[]').replace('"', '').split(',')] if pd.notna(x) else []
        )
    
    if 'Áreas do conhecimento indispensáveis ao projeto' in df.columns:
        df['Áreas'] = df['Áreas do conhecimento indispensáveis ao projeto'].apply(
            lambda x: [item.strip() for item in str(x).strip('[]').replace('"', '').split(',')] if pd.notna(x) else []
        )
    
    if 'Atividades a serem promovidas no projeto' in df.columns:
        df['Atividades'] = df['Atividades a serem promovidas no projeto'].apply(
            lambda x: [item.strip() for item in str(x).split(',')] if pd.notna(x) else []
        )
    
    if 'Produção técnica e acadêmica prevista no projeto' in df.columns:
        df['Produção'] = df['Produção técnica e acadêmica prevista no projeto'].apply(
            lambda x: [item.strip().strip('[]').replace('"', '') for item in str(x).split(',')] if pd.notna(x) else []
        )
    
    # Garantir que colunas numéricas são números
    for col in ['Qtd_Graduacao', 'Qtd_Pos', 'Qtd_Docentes']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        else:
            df[col] = 0
    
    return df

def criar_dados_exemplo():
    """Cria dados de exemplo quando o CSV não pode ser carregado"""
    
    dados_exemplo = {
        "ID": [1, 2, 3],
        "Projeto": ["Projeto Alpha", "Projeto Beta", "Projeto Gamma"],
        "Descrição": [
            "Descrição do projeto Alpha",
            "Descrição do projeto Beta",
            "Descrição do projeto Gamma"
        ],
        "Equipe": [
            "João Silva;Maria Santos",
            "Pedro Costa;Ana Lima;João Silva",
            "Maria Santos;Carlos Souza"
        ],
        "Coordenação": ["João Silva", "Pedro Costa", "Maria Santos"],
        "Previsão de início": ["01/01/2024", "15/06/2024", "10/10/2024"],
        "Previsão de término": ["31/12/2024", "30/04/2025", ""],
        "Qtd_Graduacao": [3, 2, 4],
        "Qtd_Pos": [2, 3, 1],
        "Qtd_Docentes": [1, 1, 0],
        "Fonte_Recurso": ["FAPESP", "CNPq", "CAPES"],
        "inicio_date": pd.to_datetime(["01/01/2024", "15/06/2024", "10/10/2024"], format='%d/%m/%Y'),
        "termino_date": pd.to_datetime(["31/12/2024", "30/04/2025", None], format='%d/%m/%Y', errors='coerce'),
        "Habilidades": [["Python", "SQL"], ["JavaScript", "React"], ["Python", "Machine Learning"]],
        "Áreas": [["TI", "Dados"], ["Frontend", "UX"], ["IA", "Dados"]],
        "Atividades": [["Desenvolvimento", "Testes"], ["Design", "Implementação"], ["Pesquisa", "Análise"]],
        "Produção": [["Artigo", "Software"], ["Site", "Relatório"], ["Modelo", "Paper"]]
    }
    
    return pd.DataFrame(dados_exemplo)

# ===================== FUNÇÕES DE VISUALIZAÇÃO =====================

def show_overview(df):
    """Visão geral do dashboard"""
    st.header("📊 Visão Geral dos Projetos")
    
    # Métricas principais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📋 Total de Projetos", len(df))
    
    with col2:
        if 'Qtd_Graduacao' in df.columns:
            total_pessoas = df["Qtd_Graduacao"].sum() + df["Qtd_Pos"].sum() + df["Qtd_Docentes"].sum()
            st.metric("👥 Total de Envolvidos", total_pessoas)
        else:
            st.metric("👥 Total de Envolvidos", "N/A")
    
    with col3:
        if 'termino_date' in df.columns:
            ativos = df[(df["termino_date"].isna()) | (df["termino_date"] >= pd.Timestamp.now())].shape[0]
            st.metric("✅ Projetos Ativos", ativos)
        else:
            st.metric("✅ Projetos Ativos", len(df))
    
    with col4:
        if 'Fonte_Recurso' in df.columns:
            fontes = df["Fonte_Recurso"].nunique()
            st.metric("💰 Fontes de Recurso", fontes)
        else:
            st.metric("💰 Fontes de Recurso", "N/A")
    
    with col5:
        if 'Produção' in df.columns:
            total_producoes = sum(len(p) for p in df["Produção"] if isinstance(p, list))
            st.metric("📝 Produções Previstas", total_producoes)
        else:
            st.metric("📝 Produções Previstas", "N/A")
    
    st.markdown("---")
    
    # Linha do tempo
    if 'inicio_date' in df.columns:
        st.subheader("📅 Linha do Tempo dos Projetos")
        
        fig_timeline = go.Figure()
        
        for idx, row in df.iterrows():
            if pd.notna(row["inicio_date"]):
                nome_projeto = row["Projeto"][:30] + "..." if len(row["Projeto"]) > 30 else row["Projeto"]
                
                if pd.notna(row["termino_date"]):
                    fig_timeline.add_trace(go.Scatter(
                        x=[row["inicio_date"], row["termino_date"]],
                        y=[nome_projeto, nome_projeto],
                        mode="lines+markers",
                        line=dict(width=4, color="#0066cc"),
                        marker=dict(size=10, color="#ff6600"),
                        name=nome_projeto,
                        text=f"{row['Projeto']}<br>Início: {row['Previsão de início'] if 'Previsão de início' in row else row['inicio_date']}<br>Término: {row['Previsão de término'] if 'Previsão de término' in row else row['termino_date']}",
                        hoverinfo="text"
                    ))
                else:
                    fig_timeline.add_trace(go.Scatter(
                        x=[row["inicio_date"]],
                        y=[nome_projeto],
                        mode="markers",
                        marker=dict(size=15, color="#ff6600", symbol="star"),
                        name=nome_projeto,
                        text=f"{row['Projeto']}<br>Início: {row['Previsão de início'] if 'Previsão de início' in row else row['inicio_date']}<br>Término: Não informado",
                        hoverinfo="text"
                    ))
        
        fig_timeline.update_layout(
            title="Cronograma dos Projetos",
            xaxis_title="Data",
            yaxis_title="",
            height=400,
            showlegend=False,
            hovermode="closest"
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Gráficos de distribuição
    if 'Qtd_Graduacao' in df.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("👥 Distribuição por Tipo")
            humanos = {
                "Graduação": df["Qtd_Graduacao"].sum(),
                "Pós-Graduação": df["Qtd_Pos"].sum(),
                "Docentes": df["Qtd_Docentes"].sum()
            }
            if sum(humanos.values()) > 0:
                fig_pie = px.pie(
                    values=list(humanos.values()), 
                    names=list(humanos.keys()),
                    title="Total de Pessoas por Categoria",
                    color_discrete_sequence=["#0066cc", "#ff6600", "#66cc66"],
                    hole=0.3
                )
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            st.subheader("👥 Recursos por Projeto")
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(name="Graduação", x=df["Projeto"], y=df["Qtd_Graduacao"], marker_color="#0066cc"))
            fig_bar.add_trace(go.Bar(name="Pós-Graduação", x=df["Projeto"], y=df["Qtd_Pos"], marker_color="#ff6600"))
            fig_bar.add_trace(go.Bar(name="Docentes", x=df["Projeto"], y=df["Qtd_Docentes"], marker_color="#66cc66"))
            fig_bar.update_layout(barmode="group", title="Distribuição por Projeto", xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Fonte de recursos
    if 'Fonte_Recurso' in df.columns:
        st.subheader("💰 Distribuição por Fonte de Recurso")
        fontes_counts = df["Fonte_Recurso"].value_counts().reset_index()
        fontes_counts.columns = ["Fonte", "Quantidade"]
        fig_fontes = px.pie(
            values=fontes_counts["Quantidade"],
            names=fontes_counts["Fonte"],
            title="Projetos por Fonte de Recurso",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_fontes, use_container_width=True)
    
    # Habilidades
    if 'Habilidades' in df.columns:
        st.subheader("🛠️ Habilidades Mais Demandadas")
        all_skills = [skill for skills in df["Habilidades"] for skill in skills if skills]
        if all_skills:
            skill_counts = Counter(all_skills).most_common(10)
            skill_df = pd.DataFrame(skill_counts, columns=["Habilidade", "Frequência"])
            fig_skills = px.bar(
                skill_df, 
                x="Habilidade", 
                y="Frequência",
                title="Top 10 Habilidades Indispensáveis",
                color="Frequência",
                color_continuous_scale="Viridis"
            )
            fig_skills.update_layout(xaxis_tickangle=-45, height=450)
            st.plotly_chart(fig_skills, use_container_width=True)

def show_project_detail(df):
    """Detalhamento por projeto"""
    st.header("🔍 Detalhamento por Projeto")
    
    projetos_list = df["Projeto"].tolist()
    selected_project = st.selectbox("Selecione um projeto:", projetos_list)
    
    project_data = df[df["Projeto"] == selected_project].iloc[0]
    
    # Abas
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Informações Gerais", "👥 Equipe", "🎯 Atividades", "📦 Produções"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {project_data['Projeto']}")
            if 'Descrição' in project_data:
                st.markdown(f"**📝 Descrição:** {project_data['Descrição']}")
            st.markdown("---")
            st.markdown("**📅 Cronograma**")
            if 'Previsão de início' in project_data:
                st.write(f"• **Início previsto:** {project_data['Previsão de início']}")
            elif 'inicio_date' in project_data:
                st.write(f"• **Início previsto:** {project_data['inicio_date'].strftime('%d/%m/%Y') if pd.notna(project_data['inicio_date']) else 'Não informado'}")
            
            if 'Previsão de término' in project_data:
                st.write(f"• **Término previsto:** {project_data['Previsão de término'] if project_data['Previsão de término'] else 'Não informado'}")
        
        with col2:
            if all(col in project_data for col in ['Qtd_Graduacao', 'Qtd_Pos', 'Qtd_Docentes']):
                st.markdown("**👨‍🎓 Recursos Humanos**")
                st.metric("Graduação", project_data["Qtd_Graduacao"])
                st.metric("Pós-Graduação", project_data["Qtd_Pos"])
                st.metric("Docentes", project_data["Qtd_Docentes"] if project_data["Qtd_Docentes"] > 0 else "Nenhum")
            
            if 'Fonte_Recurso' in project_data:
                st.markdown("---")
                st.markdown(f"**💰 Fonte:** {project_data['Fonte_Recurso']}")
    
    with tab2:
        if 'Equipe' in project_data:
            st.markdown("### 👥 Equipe do Projeto")
            equipe_list = str(project_data["Equipe"]).split(";")
            st.markdown(f"**Total de membros:** {len(equipe_list)}")
            
            cols = st.columns(3)
            for i, membro in enumerate(equipe_list):
                with cols[i % 3]:
                    st.markdown(f"- {membro.strip()}")
        
        if 'Coordenação' in project_data:
            st.markdown("---")
            st.markdown("### 🎯 Coordenação")
            coord_list = str(project_data["Coordenação"]).split(";")
            for coord in coord_list:
                st.markdown(f"**{coord.strip()}**")
    
    with tab3:
        if 'Atividades' in project_data and isinstance(project_data["Atividades"], list):
            st.markdown("### 📋 Atividades Previstas")
            for atividade in project_data["Atividades"]:
                st.markdown(f"- {atividade}")
    
    with tab4:
        if 'Produção' in project_data and isinstance(project_data["Produção"], list):
            st.markdown("### 🎯 Produções Técnicas e Acadêmicas")
            producoes = project_data["Produção"]
            cols = st.columns(min(len(producoes), 4))
            for i, prod in enumerate(producoes):
                with cols[i % 4]:
                    st.markdown(f"✅ {prod}")

def show_team_analysis(df):
    """Análise de equipe"""
    st.header("👥 Análise de Equipes e Participação")
    
    if 'Equipe' in df.columns:
        # Extrair membros
        all_members = []
        for equipe in df["Equipe"]:
            members = str(equipe).split(";")
            all_members.extend([m.strip() for m in members if m.strip()])
        
        member_counts = Counter(all_members)
        
        if member_counts:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏆 Pessoas com Mais Projetos")
                top_members = member_counts.most_common(10)
                top_df = pd.DataFrame(top_members, columns=["Nome", "Projetos"])
                fig_top = px.bar(
                    top_df, 
                    x="Nome", 
                    y="Projetos",
                    title="Top 10 - Mais participações",
                    color="Projetos",
                    color_continuous_scale="Viridis"
                )
                fig_top.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_top, use_container_width=True)
            
            with col2:
                st.subheader("📊 Distribuição de Participação")
                participation = {
                    "1 projeto": sum(1 for c in member_counts.values() if c == 1),
                    "2 projetos": sum(1 for c in member_counts.values() if c == 2),
                    "3+ projetos": sum(1 for c in member_counts.values() if c >= 3)
                }
                fig_part = px.pie(
                    values=list(participation.values()),
                    names=list(participation.keys()),
                    title="Frequência de Participação",
                    color_discrete_sequence=px.colors.sequential.Blues_r,
                    hole=0.3
                )
                st.plotly_chart(fig_part, use_container_width=True)
    
    if 'Coordenação' in df.columns:
        st.subheader("🎯 Coordenadores de Projetos")
        all_coords = []
        for coord in df["Coordenação"]:
            all_coords.extend([c.strip() for c in str(coord).split(";")])
        
        coord_counts = Counter(all_coords)
        if coord_counts:
            coord_df = pd.DataFrame(coord_counts.most_common(), columns=["Coordenador(a)", "Projetos"])
            fig_coord = px.bar(
                coord_df, 
                x="Coordenador(a)", 
                y="Projetos",
                title="Projetos por Coordenador(a)",
                color="Projetos",
                color_continuous_scale="Reds"
            )
            fig_coord.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_coord, use_container_width=True)

# ===================== MAIN =====================

def main():
    st.title("🏗️ Painel de Gestão de Projetos - PLANTEAR")
    st.caption("Sistema integrado de visualização e análise de projetos")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.header("🎛️ Navegação")
    
    view = st.sidebar.radio(
        "Escolha uma visualização:",
        [
            "📊 Visão Geral",
            "🔍 Detalhe do Projeto",
            "👥 Análise de Equipe"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Sobre")
    st.sidebar.info(
        "Este dashboard apresenta informações consolidadas "
        "dos projetos, permitindo análise de equipes, "
        "recursos e demandas.\n\n"
        "📁 **Fonte dos dados:** CSV carregado do GitHub\n"
        "🔄 **Atualização:** Automática a cada hora"
    )
    
    # Botão para recarregar
    if st.sidebar.button("🔄 Forçar Recarregamento dos Dados"):
        st.cache_data.clear()
        st.rerun()
    
    # Carregar dados
    with st.spinner("Carregando dados..."):
        df = carregar_csv_github()
    
    # Mostrar estatísticas na sidebar
    if df is not None and len(df) > 0:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📈 Estatísticas Atuais")
        st.sidebar.metric("Projetos Carregados", len(df))
        
        if 'Fonte_Recurso' in df.columns:
            st.sidebar.metric("Fontes de Recurso", df["Fonte_Recurso"].nunique())
    
    # Exibir visualização
    if view == "📊 Visão Geral":
        show_overview(df)
    elif view == "🔍 Detalhe do Projeto":
        show_project_detail(df)
    elif view == "👥 Análise de Equipe":
        show_team_analysis(df)
    
    # Footer
    st.markdown("---")
    st.caption("📅 Dados atualizados via GitHub | 🔄 Atualização automática a cada hora")

if __name__ == "__main__":
    main()