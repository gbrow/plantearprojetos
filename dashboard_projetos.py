# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from collections import Counter
import re

# Configuração da página
st.set_page_config(page_title="Painel de Projetos - PLANTEAR", layout="wide")

# Estilo CSS
st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    div[data-testid="stExpander"] {
        background-color: #f8f9fa;
        border-radius: 10px;
        border-left: 5px solid #0066cc;
    }
</style>
""", unsafe_allow_html=True)

# ===================== DADOS =====================
@st.cache_data
def load_and_process_data():
    """Carrega e processa todos os dados"""
    
    # Dados completos
    projetos_data = {
        "ID": [7, 6, 5, 4, 3, 2],
        "Projeto": [
            "Projeto Atlas dos Territórios Indígenas do Paraná",
            "Projeto Contestado",
            "Projeto Comunidade Graciosa",
            "REURB Sabará",
            "Dona Cida",
            "Nova Esperança"
        ],
        "Descrição": [
            "Co-elaboração de um material didático trilíngue (Guarani Ñandeva, Guarani Mbya e Kaingang) sobre os territórios indígenas do Paraná.",
            "Elaboração de um Plano de Desenvolvimento de Assentamento (PDA).",
            "Estudo Técnico Territorial Socioambiental",
            "Estudos e projetos para a regularização fundiária nas Vilas Sabará, mais especificamente: Vila Esperança, Nova Conquista e Eldorado.",
            "Realização de eventos e formações prévias a REURB.",
            "Projeto em parceria com o Movimento Popular por Moradia (MPM), para auxiliar na regularização fundiária na comunidade Nova Esperança."
        ],
        "Equipe": [
            "Julia Leandro Ribeiro;Desiree Lambert Dias;Gustavo Steinmetz Soares;Katarina Fagundes Aragao;Georgia Fernnanda Baggio de Oliveira;Pedro Henrique Alberti;Savannah Maltaca de Souza;Jorge Ramon Montenegro Gomez",
            "Desiree Lambert Dias;Gustavo Steinmetz Soares;Julia Leandro Ribeiro;Bernardo Donasolo Machado;Joao Matheus de Oliveira Carvalho;Walace Silvares Pereira;Jose Ricardo Vargas de Faria;Jorge Ramon Montenegro Gomez",
            "Maria Luiza Dias Ballarotti;Ingrid da Costa Rosário;Joao Matheus de Oliveira Carvalho;Bernardo Donasolo Machado;Gustavo Steinmetz Soares;Walace Silvares Pereira;Luana Meister Gomes;Sofia Tozzo Bueno de Lima;Gab da Silveira Muller;Carina Yumi Endo",
            "Davi dos Santos Villela Junior;Gabriele Borinelli;Joao Matheus de Oliveira Carvalho;Gab da Silveira Muller;Sandra Rafaela Magalhaes Correa",
            "Davi dos Santos Villela Junior;Gabriele Borinelli;Aline Gomes Holanda;Joao Matheus de Oliveira Carvalho",
            "Aline Gomes Holanda;Bernardo Donasolo Machado;Bruno Fonseca Rocha Leonel Caetano;Gab da Silveira Muller;Gustavo Steinmetz Soares;Joao Matheus de Oliveira Carvalho;Julia Leandro Ribeiro;Pedro Arthur Heitkoeter Melo;Savannah Maltaca de Souza"
        ],
        "Coordenação": [
            "Jorge Ramon Montenegro Gomez",
            "Jorge Ramon Montenegro Gomez;Jose Ricardo Vargas de Faria",
            "Marcelo Caetano Andreoli",
            "Daniele Regina Pontes;Jose Ricardo Vargas de Faria",
            "Jose Ricardo Vargas de Faria",
            "Jose Ricardo Vargas de Faria"
        ],
        "Previsão de início": ["01/04/2025", "13/11/2025", "01/10/2023", "12/02/2026", "01/09/2025", "01/11/2020"],
        "Previsão de término": ["31/07/2027", "12/12/2026", "01/12/2026", "01/05/2027", "", "30/11/2026"],
        "Habilidades": [
            "Tratamento e análise de dados secundários;Elaboração de material teórico;Produção de pranchas e desenhos arquitetônicos;Geoprocessamento;Criação e desenvolvimento de oficinas;Diagramação",
            "Análise socioeconômica;Zoneamento;Análise ambiental;Parcelamento do solo;Produção de pranchas e desenhos arquitetônicos;Geoprocessamento;Aerolevantamento com drone;Pesquisas agronômicas;Topografia;Criação e desenvolvimento de oficinas;Diagramação;Tratamento e análise de dados secundários",
            "Análise socioeconômica;Tratamento e análise de dados secundários;Regularização fundiária;Regularização urbanística;Análise de risco;Análise ambiental;Geoprocessamento;Pesquisas agronômicas;Topografia;Parcelamento do solo;Desenho urbanístico;Diagramação;Criação e desenvolvimento de oficinas;Produção de pranchas e desenhos arquitetônicos",
            "Tratamento e análise de dados secundários;Elaboração de material teórico;Análise ambiental;Criação e desenvolvimento de oficinas;Diagramação;Análise socioeconômica;Parcelamento do solo;Aerolevantamento com drone;Tecnologia da informação;Geoprocessamento;Produção de pranchas e desenhos arquitetônicos",
            "Análise socioeconômica;Tratamento e análise de dados secundários;Elaboração de material teórico;Regularização fundiária;Regularização urbanística;Cadastro;Geoprocessamento;Aerolevantamento com drone;Tecnologia da informação;Criação e desenvolvimento de oficinas;Diagramação",
            "Tratamento e análise de dados secundários;Elaboração de material teórico;Análise ambiental;Parcelamento do solo;Produção de pranchas e desenhos arquitetônicos;Geoprocessamento;Aerolevantamento com drone;Tecnologia da informação;Criação e desenvolvimento de oficinas;Diagramação"
        ],
        "Áreas": [
            "Geografia;Arquitetura e Urbanismo",
            "Arquitetura e Urbanismo;Geografia;Engenharia Agronômica;Engenharia Ambiental",
            "Ciências Sociais;Direito;Arquitetura e Urbanismo;Geografia;Engenharia Ambiental",
            "Arquitetura e Urbanismo;Geografia;Engenharia Ambiental;Engenharia Cartográfica e Ambiental;Engenharia Civil;Direito",
            "Geografia;Arquitetura e Urbanismo;Engenharia Civil;Direito",
            "Arquitetura e Urbanismo;Geografia;Engenharia Ambiental;Engenharia Cartográfica e Ambiental;Engenharia Civil;Design Gráfico"
        ],
        "Qtd_Graduacao": [4, 2, 3, 1, 1, 4],
        "Qtd_Pos": [4, 4, 6, 5, 3, 5],
        "Qtd_Docentes": [1, 2, 3, 0, 1, 0],
        "Atividades": [
            "Oficinas comunitárias;cartografias sociais;geoprocessamento;registro e sistematização;levantamento e sistematização de dados;produção de newsletter;site interativo;realização de eventos estratégicos",
            "10 oficinas;geoprocessamento;registro e sistematização;planejamento de reuniões internas;reuniões com coordenação do assentamento e INCRA;análise das cadeias produtivas;diagnóstico socioeconômicos;revisão e análise das políticas de reforma agrária",
            "Caracterização da biodiversidade;Levantamento de APAs e APPs;Identificação de nascentes;Georrefenciamento;análises socioespaciais;Levantamento de uso e ocupação do solo;análise fundiária;proposta de desenho e reajuste de terras",
            "Oficinas",
            "Formação comunitária sobre REURB;formação de cadastradores;aplicação de questionários;integração de dados a SIG",
            "Oficinas;minicurso"
        ],
        "Fonte_Recurso": ["Recurso da Itaipu", "Emenda parlamentar", "Emenda parlamentar", "Emenda parlamentar", "Emenda parlamentar", "Emenda parlamentar"],
        "Produção": [
            "Livro;Mapa;Materiais digitais",
            "Artigo;Cartilha;Mapa;Maquete;Materiais digitais;Plano;Projeto",
            "Dossiê;Mapa;Plano;Projeto",
            "Artigo;Dossiê;Mapa;Maquete",
            "Cartilha;Materiais digitais",
            "Mapa;Materiais digitais;Dossiê;Artigo"
        ]
    }
    
    df = pd.DataFrame(projetos_data)
    
    # Processar datas
    df["inicio_date"] = pd.to_datetime(df["Previsão de início"], format="%d/%m/%Y", errors="coerce")
    df["termino_date"] = pd.to_datetime(df["Previsão de término"], format="%d/%m/%Y", errors="coerce")
    
    # Converter strings separadas por ; em listas
    df["Habilidades"] = df["Habilidades"].apply(lambda x: [item.strip() for item in x.split(";")])
    df["Áreas"] = df["Áreas"].apply(lambda x: [item.strip() for item in x.split(";")])
    df["Atividades"] = df["Atividades"].apply(lambda x: [item.strip() for item in x.split(";")])
    df["Produção"] = df["Produção"].apply(lambda x: [item.strip() for item in x.split(";")])
    
    return df

# ===================== FUNÇÕES DE VISUALIZAÇÃO =====================

def show_overview(df):
    """Visão geral do dashboard"""
    st.header("📊 Visão Geral dos Projetos")
    
    # Métricas principais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📋 Total de Projetos", len(df))
    
    with col2:
        total_pessoas = df["Qtd_Graduacao"].sum() + df["Qtd_Pos"].sum() + df["Qtd_Docentes"].sum()
        st.metric("👥 Total de Envolvidos", total_pessoas)
    
    with col3:
        # Projetos ativos (sem data de término ou término futuro)
        ativos = df[(df["termino_date"].isna()) | (df["termino_date"] >= pd.Timestamp.now())].shape[0]
        st.metric("✅ Projetos Ativos", ativos)
    
    with col4:
        fontes = df["Fonte_Recurso"].nunique()
        st.metric("💰 Fontes de Recurso", fontes)
    
    with col5:
        total_producoes = sum(len(p) for p in df["Produção"])
        st.metric("📝 Produções Previstas", total_producoes)
    
    st.markdown("---")
    
    # Linha do tempo
    st.subheader("📅 Linha do Tempo dos Projetos")
    
    fig_timeline = go.Figure()
    
    for idx, row in df.iterrows():
        if pd.notna(row["inicio_date"]):
            if pd.notna(row["termino_date"]):
                fig_timeline.add_trace(go.Scatter(
                    x=[row["inicio_date"], row["termino_date"]],
                    y=[row["Projeto"], row["Projeto"]],
                    mode="lines+markers",
                    line=dict(width=4, color="#0066cc"),
                    marker=dict(size=10, color="#ff6600"),
                    name=row["Projeto"],
                    text=f"{row['Projeto']}<br>Início: {row['Previsão de início']}<br>Término: {row['Previsão de término']}",
                    hoverinfo="text"
                ))
            else:
                fig_timeline.add_trace(go.Scatter(
                    x=[row["inicio_date"]],
                    y=[row["Projeto"]],
                    mode="markers",
                    marker=dict(size=15, color="#ff6600", symbol="star"),
                    name=row["Projeto"],
                    text=f"{row['Projeto']}<br>Início: {row['Previsão de início']}<br>Término: Não informado",
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
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Distribuição por Tipo")
        humanos = {
            "Graduação": df["Qtd_Graduacao"].sum(),
            "Pós-Graduação": df["Qtd_Pos"].sum(),
            "Docentes": df["Qtd_Docentes"].sum()
        }
        fig_pie = px.pie(
            values=list(humanos.values()), 
            names=list(humanos.keys()),
            title="Total de Pessoas por Categoria",
            color_discrete_sequence=["#0066cc", "#ff6600", "#66cc66"],
            hole=0.3
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        st.subheader("💰 Distribuição por Fonte")
        fontes_counts = df["Fonte_Recurso"].value_counts().reset_index()
        fontes_counts.columns = ["Fonte", "Quantidade"]
        fig_bar = px.bar(
            fontes_counts, 
            x="Fonte", 
            y="Quantidade",
            title="Projetos por Fonte de Recurso",
            color="Quantidade",
            color_continuous_scale="Blues",
            text="Quantidade"
        )
        fig_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Habilidades mais demandadas
    st.subheader("🛠️ Habilidades Mais Demandadas")
    all_skills = [skill for skills in df["Habilidades"] for skill in skills]
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
    
    # Áreas do conhecimento
    st.subheader("📚 Áreas do Conhecimento")
    all_areas = [area for areas in df["Áreas"] for area in areas]
    area_counts = Counter(all_areas).most_common()
    area_df = pd.DataFrame(area_counts, columns=["Área", "Frequência"])
    fig_areas = px.bar(
        area_df, 
        x="Área", 
        y="Frequência",
        title="Demanda por Áreas do Conhecimento",
        color="Frequência",
        color_continuous_scale="Oranges"
    )
    fig_areas.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig_areas, use_container_width=True)
    
    # Produções
    st.subheader("📝 Produções Técnicas e Acadêmicas")
    all_productions = [prod for prods in df["Produção"] for prod in prods]
    prod_counts = Counter(all_productions).most_common()
    prod_df = pd.DataFrame(prod_counts, columns=["Tipo", "Quantidade"])
    fig_prod = px.bar(
        prod_df, 
        x="Tipo", 
        y="Quantidade",
        title="Tipos de Produção por Projeto",
        color="Quantidade",
        color_continuous_scale="Greens"
    )
    fig_prod.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig_prod, use_container_width=True)

def show_project_detail(df):
    """Detalhamento por projeto"""
    st.header("🔍 Detalhamento por Projeto")
    
    # Seletor
    projetos_list = df["Projeto"].tolist()
    selected_project = st.selectbox("Selecione um projeto para visualizar detalhes:", projetos_list)
    
    project_data = df[df["Projeto"] == selected_project].iloc[0]
    
    # Abas para organizar as informações
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Informações Gerais", "👥 Equipe", "🎯 Atividades", "📦 Produções"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {project_data['Projeto']}")
            st.markdown(f"**📝 Descrição:** {project_data['Descrição']}")
            st.markdown("---")
            st.markdown("**📅 Cronograma**")
            st.write(f"• **Início previsto:** {project_data['Previsão de início']}")
            st.write(f"• **Término previsto:** {project_data['Previsão de término'] if project_data['Previsão de término'] else 'Não informado'}")
        
        with col2:
            st.markdown("**👨‍🎓 Recursos Humanos**")
            st.metric("Graduação", project_data["Qtd_Graduacao"])
            st.metric("Pós-Graduação", project_data["Qtd_Pos"])
            st.metric("Docentes", project_data["Qtd_Docentes"] if project_data["Qtd_Docentes"] > 0 else "Nenhum")
            st.markdown("---")
            st.markdown(f"**💰 Fonte:** {project_data['Fonte_Recurso']}")
        
        st.markdown("---")
        col_skills, col_areas = st.columns(2)
        
        with col_skills:
            st.markdown("**🛠️ Habilidades Indispensáveis**")
            for skill in project_data["Habilidades"]:
                st.markdown(f"- {skill}")
        
        with col_areas:
            st.markdown("**📚 Áreas do Conhecimento**")
            for area in project_data["Áreas"]:
                st.markdown(f"- {area}")
    
    with tab2:
        st.markdown("### 👥 Equipe do Projeto")
        equipe_list = project_data["Equipe"].split(";")
        st.markdown(f"**Total de membros:** {len(equipe_list)}")
        
        # Mostrar em colunas
        cols = st.columns(3)
        for i, membro in enumerate(equipe_list):
            with cols[i % 3]:
                st.markdown(f"- {membro.strip()}")
        
        st.markdown("---")
        st.markdown("### 🎯 Coordenação")
        coord_list = project_data["Coordenação"].split(";")
        for coord in coord_list:
            st.markdown(f"**{coord.strip()}**")
    
    with tab3:
        st.markdown("### 📋 Atividades Previstas")
        for atividade in project_data["Atividades"]:
            st.markdown(f"- {atividade}")
    
    with tab4:
        st.markdown("### 🎯 Produções Técnicas e Acadêmicas")
        producoes = project_data["Produção"]
        cols = st.columns(min(len(producoes), 4))
        for i, prod in enumerate(producoes):
            with cols[i % 4]:
                st.markdown(f"✅ {prod}")

def show_team_analysis(df):
    """Análise de equipe"""
    st.header("👥 Análise de Equipes e Participação")
    
    # Extrair todos os membros
    all_members = []
    for equipe in df["Equipe"]:
        all_members.extend([m.strip() for m in equipe.split(";")])
    
    member_counts = Counter(all_members)
    
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
    
    # Coordenadores
    st.subheader("🎯 Coordenadores de Projetos")
    all_coords = []
    for coord in df["Coordenação"]:
        all_coords.extend([c.strip() for c in coord.split(";")])
    
    coord_counts = Counter(all_coords)
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
    
    # Colaboração
    st.subheader("🤝 Colaboração entre Equipes")
    
    # Matriz de co-ocorrência simplificada
    co_occurrence = {}
    for equipe in df["Equipe"]:
        members = [m.strip() for m in equipe.split(";")]
        for i, m1 in enumerate(members):
            for m2 in members[i+1:]:
                key = tuple(sorted([m1, m2]))
                co_occurrence[key] = co_occurrence.get(key, 0) + 1
    
    top_pairs = sorted(co_occurrence.items(), key=lambda x: x[1], reverse=True)[:10]
    pair_data = []
    for (p1, p2), count in top_pairs:
        nome1 = p1.split()[0] if " " in p1 else p1
        nome2 = p2.split()[0] if " " in p2 else p2
        pair_data.append({"Pessoa 1": nome1, "Pessoa 2": nome2, "Projetos Juntos": count})
    
    if pair_data:
        pair_df = pd.DataFrame(pair_data)
        fig_pairs = px.bar(
            pair_df, 
            x="Projetos Juntos", 
            y="Pessoa 1",
            color="Projetos Juntos",
            orientation='h',
            text="Pessoa 2",
            title="Pares que mais colaboram"
        )
        st.plotly_chart(fig_pairs, use_container_width=True)

def show_resources_analysis(df):
    """Análise de recursos"""
    st.header("📈 Análise de Recursos e Demandas")
    
    # Gráfico de barras empilhadas
    st.subheader("👥 Alocação de Recursos Humanos")
    
    fig_stacked = go.Figure()
    fig_stacked.add_trace(go.Bar(
        name="Graduação",
        x=df["Projeto"],
        y=df["Qtd_Graduacao"],
        marker_color="#0066cc",
        text=df["Qtd_Graduacao"],
        textposition="auto"
    ))
    fig_stacked.add_trace(go.Bar(
        name="Pós-Graduação",
        x=df["Projeto"],
        y=df["Qtd_Pos"],
        marker_color="#ff6600",
        text=df["Qtd_Pos"],
        textposition="auto"
    ))
    fig_stacked.add_trace(go.Bar(
        name="Docentes",
        x=df["Projeto"],
        y=df["Qtd_Docentes"],
        marker_color="#66cc66",
        text=df["Qtd_Docentes"],
        textposition="auto"
    ))
    
    fig_stacked.update_layout(
        barmode="stack",
        title="Distribuição da Equipe por Projeto",
        xaxis_title="",
        yaxis_title="Quantidade de Pessoas",
        xaxis_tickangle=-45,
        height=450,
        legend_title="Categoria"
    )
    st.plotly_chart(fig_stacked, use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚖️ Proporção por Projeto")
        # Calcular proporções
        df_display = df.copy()
        total_people = df_display["Qtd_Graduacao"] + df_display["Qtd_Pos"] + df_display["Qtd_Docentes"]
        df_display["% Graduação"] = (df_display["Qtd_Graduacao"] / total_people * 100).round(1)
        df_display["% Pós-Graduação"] = (df_display["Qtd_Pos"] / total_people * 100).round(1)
        
        # Gráfico de barras 100% empilhado
        fig_prop = go.Figure()
        fig_prop.add_trace(go.Bar(
            name="% Graduação",
            x=df_display["Projeto"],
            y=df_display["% Graduação"],
            marker_color="#0066cc"
        ))
        fig_prop.add_trace(go.Bar(
            name="% Pós-Graduação",
            x=df_display["Projeto"],
            y=df_display["% Pós-Graduação"],
            marker_color="#ff6600"
        ))
        fig_prop.update_layout(
            barmode="stack",
            title="Proporção Graduação vs Pós-Graduação",
            xaxis_tickangle=-45,
            yaxis_title="Percentual (%)"
        )
        st.plotly_chart(fig_prop, use_container_width=True)
    
    with col2:
        st.subheader("📊 Métricas de Complexidade")
        
        # Calcular métricas
        df["num_habilidades"] = df["Habilidades"].apply(len)
        df["num_areas"] = df["Áreas"].apply(len)
        df["num_producoes"] = df["Produção"].apply(len)
        df["num_atividades"] = df["Atividades"].apply(len)
        
        # Gráfico de radar simplificado (usando barras agrupadas)
        complexity_data = []
        for _, row in df.iterrows():
            complexity_data.append({"Projeto": row["Projeto"], "Métrica": "Habilidades", "Valor": row["num_habilidades"]})
            complexity_data.append({"Projeto": row["Projeto"], "Métrica": "Áreas", "Valor": row["num_areas"]})
            complexity_data.append({"Projeto": row["Projeto"], "Métrica": "Produções", "Valor": row["num_producoes"]})
            complexity_data.append({"Projeto": row["Projeto"], "Métrica": "Atividades", "Valor": row["num_atividades"]})
        
        complexity_df = pd.DataFrame(complexity_data)
        
        fig_complex = px.bar(
            complexity_df,
            x="Projeto",
            y="Valor",
            color="Métrica",
            title="Complexidade por Projeto",
            barmode="group",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_complex.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_complex, use_container_width=True)
    
    # Atividades mais comuns
    st.subheader("📋 Atividades Mais Frequentes")
    all_activities = [act.strip().lower() for acts in df["Atividades"] for act in acts]
    activity_counts = Counter(all_activities).most_common(15)
    act_df = pd.DataFrame(activity_counts, columns=["Atividade", "Frequência"])
    fig_act = px.bar(
        act_df,
        x="Atividade",
        y="Frequência",
        title="Atividades mais recorrentes",
        color="Frequência",
        color_continuous_scale="Purples"
    )
    fig_act.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig_act, use_container_width=True)

# ===================== MAIN =====================

def main():
    st.title("🏗️ Painel de Gestão de Projetos - PLANTEAR")
    st.caption("Sistema integrado de visualização e análise de projetos")
    st.markdown("---")
    
    # Carregar dados
    df = load_and_process_data()
    
    # Sidebar
    st.sidebar.header("🎛️ Navegação")
    
    view = st.sidebar.radio(
        "Escolha uma visualização:",
        [
            "📊 Visão Geral",
            "🔍 Detalhe do Projeto",
            "👥 Análise de Equipe",
            "📈 Análise de Recursos"
        ]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Sobre")
    st.sidebar.info(
        "Este dashboard apresenta informações consolidadas "
        "dos projetos do PLANTEAR, permitindo análise de "
        "equipes, recursos e demandas."
    )
    
    # Exibir visualização selecionada
    if view == "📊 Visão Geral":
        show_overview(df)
    elif view == "🔍 Detalhe do Projeto":
        show_project_detail(df)
    elif view == "👥 Análise de Equipe":
        show_team_analysis(df)
    elif view == "📈 Análise de Recursos":
        show_resources_analysis(df)
    
    # Footer
    st.markdown("---")
    st.caption("📅 Dados atualizados em Abril/2026 | PLANTEAR - Planejamento Territorial e Assessoria Popular")

if __name__ == "__main__":
    main()