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
import json
import ast

# Configuração da página
st.set_page_config(page_title="Painel de Projetos - PLANTEAR", layout="wide")

# ===================== FUNÇÃO PARA CARREGAR CSV DO GITHUB =====================

@st.cache_data(ttl=3600, show_spinner="Carregando dados do GitHub...")
def carregar_csv_github():
    """
    Carrega o arquivo CSV diretamente do GitHub usando Raw URL
    """
    
    # ⚠️ SUBSTITUA ESTA URL PELA URL RAW DO SEU CSV NO GITHUB ⚠️
    URL_CSV = "https://raw.githubusercontent.com/gbrow/plantearprojetos/main/dados/projetos.csv"
    
    try:
        response = requests.get(URL_CSV)
        response.raise_for_status()
        
        content = StringIO(response.text)
        df = pd.read_csv(content, encoding='utf-8')
        
        df = processar_dados(df)
        
        st.success("✅ Dados carregados com sucesso do GitHub!")
        return df
        
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        st.info("Usando dados de exemplo...")
        return criar_dados_exemplo()

def converter_para_lista(valor):
    """
    Converte diferentes formatos de string para lista Python
    """
    if pd.isna(valor) or valor == "" or valor == "[]":
        return []
    
    if isinstance(valor, list):
        return valor
    
    if isinstance(valor, str):
        valor = valor.strip()
        
        # Tenta converter como JSON (formato ["item1", "item2"])
        if valor.startswith('[') and valor.endswith(']'):
            try:
                # Tenta JSON primeiro
                return json.loads(valor)
            except:
                try:
                    # Tenta ast.literal_eval
                    return ast.literal_eval(valor)
                except:
                    # Remove colchetes e aspas manualmente
                    valor_limpo = valor.strip('[]')
                    if valor_limpo:
                        items = [item.strip().strip('"').strip("'") for item in valor_limpo.split(',')]
                        return [item for item in items if item]
                    return []
        
        # Formato com ponto e vírgula "item1;item2;item3"
        if ';' in valor:
            return [item.strip() for item in valor.split(';') if item.strip()]
        
        # Formato com vírgula "item1, item2, item3"
        if ',' in valor:
            return [item.strip() for item in valor.split(',') if item.strip()]
        
        # Valor único
        return [valor] if valor else []
    
    return []

def processar_dados(df):
    """Processa e limpa os dados do DataFrame"""
    
    # Dicionário de mapeamento de colunas (português -> inglês simplificado)
    mapeamento = {
        'ID': 'ID',
        'Projeto': 'Projeto',
        'Descrição do projeto': 'Descrição',
        'Descrição': 'Descrição',
        'Equipe': 'Equipe',
        'Coordenação': 'Coordenação',
        'Previsão de início do projeto': 'Previsão de início',
        'Previsão de início': 'Previsão de início',
        'Previsão de término do projeto': 'Previsão de término',
        'Previsão de término': 'Previsão de término',
        'Quantidade de pessoas da graduação necessárias': 'Qtd_Graduacao',
        'Quantidade de pessoas da pós-graduação necessárias': 'Qtd_Pos',
        'Quantidade de pessoas docentes necessárias': 'Qtd_Docentes',
        'Habilidades indispensáveis ao projeto': 'Habilidades',
        'Áreas do conhecimento indispensáveis ao projeto': 'Áreas',
        'Atividades a serem promovidas no projeto': 'Atividades',
        'Fonte de recursos do projeto': 'Fonte_Recurso',
        'Fonte de recurso': 'Fonte_Recurso',
        'Produção técnica e acadêmica prevista no projeto': 'Produção',
        'Localização': 'Localização'
    }
    
    # Aplicar mapeamento apenas para colunas que existem
    colunas_renomear = {k: v for k, v in mapeamento.items() if k in df.columns}
    df.rename(columns=colunas_renomear, inplace=True)
    
    # Garantir colunas essenciais
    colunas_essenciais = ['Projeto', 'Descrição', 'Equipe', 'Coordenação', 
                          'Previsão de início', 'Previsão de término', 
                          'Qtd_Graduacao', 'Qtd_Pos', 'Qtd_Docentes',
                          'Habilidades', 'Áreas', 'Atividades', 'Fonte_Recurso', 'Produção']
    
    for col in colunas_essenciais:
        if col not in df.columns:
            df[col] = None
    
    # Processar datas
    if 'Previsão de início' in df.columns:
        df['inicio_date'] = pd.to_datetime(df['Previsão de início'], format='%d/%m/%Y', errors='coerce')
    else:
        df['inicio_date'] = pd.NaT
    
    if 'Previsão de término' in df.columns:
        df['termino_date'] = pd.to_datetime(df['Previsão de término'], format='%d/%m/%Y', errors='coerce')
    else:
        df['termino_date'] = pd.NaT
    
    # Converter colunas de lista
    colunas_lista = ['Habilidades', 'Áreas', 'Atividades', 'Produção']
    for col in colunas_lista:
        if col in df.columns:
            df[col] = df[col].apply(converter_para_lista)
        else:
            df[col] = [[] for _ in range(len(df))]
    
    # Garantir que colunas numéricas são números
    for col in ['Qtd_Graduacao', 'Qtd_Pos', 'Qtd_Docentes']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        else:
            df[col] = 0
    
    # Garantir que Equipe e Coordenação são strings
    if 'Equipe' in df.columns:
        df['Equipe'] = df['Equipe'].fillna('').astype(str)
    else:
        df['Equipe'] = ''
    
    if 'Coordenação' in df.columns:
        df['Coordenação'] = df['Coordenação'].fillna('').astype(str)
    else:
        df['Coordenação'] = ''
    
    # Garantir Fonte_Recurso
    if 'Fonte_Recurso' in df.columns:
        df['Fonte_Recurso'] = df['Fonte_Recurso'].fillna('Não informada').astype(str)
    else:
        df['Fonte_Recurso'] = 'Não informada'
    
    # Garantir Descrição
    if 'Descrição' in df.columns:
        df['Descrição'] = df['Descrição'].fillna('').astype(str)
    else:
        df['Descrição'] = ''
    
    return df

def criar_dados_exemplo():
    """Cria dados de exemplo quando o CSV não pode ser carregado"""
    
    dados = {
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
            "Co-elaboração de um material didático trilíngue sobre os territórios indígenas do Paraná.",
            "Elaboração de um Plano de Desenvolvimento de Assentamento (PDA).",
            "Estudo Técnico Territorial Socioambiental",
            "Estudos e projetos para a regularização fundiária nas Vilas Sabará",
            "Realização de eventos e formações prévias a REURB.",
            "Projeto em parceria com o Movimento Popular por Moradia (MPM)"
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
        "Qtd_Graduacao": [4, 2, 3, 1, 1, 4],
        "Qtd_Pos": [4, 4, 6, 5, 3, 5],
        "Qtd_Docentes": [1, 2, 3, 0, 1, 0],
        "Fonte_Recurso": ["Recurso da Itaipu", "Emenda parlamentar", "Emenda parlamentar", "Emenda parlamentar", "Emenda parlamentar", "Emenda parlamentar"],
        "Habilidades": [
            '["Tratamento e análise de dados secundários","Elaboração de material teórico","Produção de pranchas e desenhos arquitetônicos","Geoprocessamento","Criação e desenvolvimento de oficinas","Diagramação"]',
            '["Análise socioeconômica","Zoneamento","Análise ambiental","Parcelamento do solo","Produção de pranchas e desenhos arquitetônicos","Geoprocessamento","Aerolevantamento com drone","Pesquisas agronômicas","Topografia","Criação e desenvolvimento de oficinas","Diagramação","Tratamento e análise de dados secundários"]',
            '["Análise socioeconômica","Tratamento e análise de dados secundários","Regularização fundiária","Regularização urbanística","Análise de risco","Análise ambiental","Geoprocessamento","Pesquisas agronômicas","Topografia","Parcelamento do solo","Desenho urbanístico","Diagramação","Criação e desenvolvimento de oficinas","Produção de pranchas e desenhos arquitetônicos"]',
            '["Tratamento e análise de dados secundários","Elaboração de material teórico","Análise ambiental","Criação e desenvolvimento de oficinas","Diagramação","Análise socioeconômica","Parcelamento do solo","Aerolevantamento com drone","Tecnologia da informação","Geoprocessamento","Produção de pranchas e desenhos arquitetônicos"]',
            '["Análise socioeconômica","Tratamento e análise de dados secundários","Elaboração de material teórico","Regularização fundiária","Regularização urbanística","Cadastro","Geoprocessamento","Aerolevantamento com drone","Tecnologia da informação","Criação e desenvolvimento de oficinas","Diagramação"]',
            '["Tratamento e análise de dados secundários","Elaboração de material teórico","Análise ambiental","Parcelamento do solo","Produção de pranchas e desenhos arquitetônicos","Geoprocessamento","Aerolevantamento com drone","Tecnologia da informação","Criação e desenvolvimento de oficinas","Diagramação"]'
        ],
        "Áreas": [
            '["Geografia","Arquitetura e Urbanismo"]',
            '["Arquitetura e Urbanismo","Geografia","Engenharia Agronômica","Engenharia Ambiental"]',
            '["Ciências Sociais","Direito","Arquitetura e Urbanismo","Geografia","Engenharia Ambiental"]',
            '["Arquitetura e Urbanismo","Geografia","Engenharia Ambiental","Engenharia Cartográfica e Ambiental","Engenharia Civil","Direito"]',
            '["Geografia","Arquitetura e Urbanismo","Engenharia Civil","Direito"]',
            '["Arquitetura e Urbanismo","Geografia","Engenharia Ambiental","Engenharia Cartográfica e Ambiental","Engenharia Civil","Design Gráfico"]'
        ],
        "Atividades": [
            "Oficinas comunitárias;cartografias sociais;geoprocessamento;registro e sistematização;levantamento e sistematização de dados;produção de newsletter;site interativo;realização de eventos estratégicos",
            "10 oficinas;geoprocessamento;registro e sistematização;planejamento de reuniões internas;reuniões com coordenação do assentamento e INCRA;análise das cadeias produtivas;diagnóstico socioeconômicos;revisão e análise das políticas de reforma agrária",
            "Caracterização da biodiversidade;Levantamento de APAs e APPs;Identificação de nascentes;Georrefenciamento;análises socioespaciais;Levantamento de uso e ocupação do solo;análise fundiária;proposta de desenho e reajuste de terras",
            "Oficinas",
            "Formação comunitária sobre REURB;formação de cadastradores;aplicação de questionários;integração de dados a SIG",
            "Oficinas;minicurso"
        ],
        "Produção": [
            '["Livro","Mapa","Materiais digitais"]',
            '["Artigo","Cartilha","Mapa","Maquete","Materiais digitais","Plano","Projeto"]',
            '["Dossiê","Mapa","Plano","Projeto"]',
            '["Artigo","Dossiê","Mapa","Maquete"]',
            '["Cartilha","Materiais digitais"]',
            '["Mapa","Materiais digitais","Dossiê","Artigo"]'
        ]
    }
    
    df = pd.DataFrame(dados)
    
    # Converter listas
    df['Habilidades'] = df['Habilidades'].apply(converter_para_lista)
    df['Áreas'] = df['Áreas'].apply(converter_para_lista)
    df['Atividades'] = df['Atividades'].apply(converter_para_lista)
    df['Produção'] = df['Produção'].apply(converter_para_lista)
    
    # Processar datas
    df['inicio_date'] = pd.to_datetime(df['Previsão de início'], format='%d/%m/%Y', errors='coerce')
    df['termino_date'] = pd.to_datetime(df['Previsão de término'], format='%d/%m/%Y', errors='coerce')
    
    return df

# ===================== FUNÇÕES DE VISUALIZAÇÃO =====================

def show_overview(df):
    """Visão geral do dashboard"""
    st.header("📊 Visão Geral dos Projetos")
    
    # Debug: mostrar estrutura dos dados (remover depois que funcionar)
    with st.expander("🔧 Debug - Verificar estrutura dos dados"):
        st.write("**Colunas disponíveis:**", list(df.columns))
        st.write("**Exemplo de Habilidades:**", df['Habilidades'].iloc[0] if len(df) > 0 else "Vazio")
        st.write("**Tipo da coluna Habilidades:**", type(df['Habilidades'].iloc[0]) if len(df) > 0 else "N/A")
    
    # Métricas principais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📋 Total de Projetos", len(df))
    
    with col2:
        total_pessoas = df["Qtd_Graduacao"].sum() + df["Qtd_Pos"].sum() + df["Qtd_Docentes"].sum()
        st.metric("👥 Total de Envolvidos", total_pessoas)
    
    with col3:
        ativos = df[(df["termino_date"].isna()) | (df["termino_date"] >= pd.Timestamp.now())].shape[0]
        st.metric("✅ Projetos Ativos", ativos)
    
    with col4:
        fontes = df["Fonte_Recurso"].nunique()
        st.metric("💰 Fontes de Recurso", fontes)
    
    with col5:
        total_producoes = sum(len(p) for p in df["Produção"] if isinstance(p, list))
        st.metric("📝 Produções Previstas", total_producoes)
    
    st.markdown("---")
    
    # Linha do tempo
    st.subheader("📅 Linha do Tempo dos Projetos")
    
    fig_timeline = go.Figure()
    
    for idx, row in df.iterrows():
        if pd.notna(row["inicio_date"]):
            nome_projeto = row["Projeto"][:40] + "..." if len(row["Projeto"]) > 40 else row["Projeto"]
            
            if pd.notna(row["termino_date"]):
                fig_timeline.add_trace(go.Scatter(
                    x=[row["inicio_date"], row["termino_date"]],
                    y=[nome_projeto, nome_projeto],
                    mode="lines+markers",
                    line=dict(width=4, color="#0066cc"),
                    marker=dict(size=10, color="#ff6600"),
                    name=nome_projeto,
                    text=f"{row['Projeto']}<br>Início: {row['Previsão de início']}<br>Término: {row['Previsão de término'] if row.get('Previsão de término') else 'Não informado'}",
                    hoverinfo="text"
                ))
            else:
                fig_timeline.add_trace(go.Scatter(
                    x=[row["inicio_date"]],
                    y=[nome_projeto],
                    mode="markers",
                    marker=dict(size=15, color="#ff6600", symbol="star"),
                    name=nome_projeto,
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
    
    # Gráfico de recursos humanos empilhado
    st.subheader("👥 Alocação de Recursos Humanos por Projeto")
    
    fig_stacked = go.Figure()
    fig_stacked.add_trace(go.Bar(name="Graduação", x=df["Projeto"], y=df["Qtd_Graduacao"], marker_color="#0066cc", text=df["Qtd_Graduacao"], textposition="auto"))
    fig_stacked.add_trace(go.Bar(name="Pós-Graduação", x=df["Projeto"], y=df["Qtd_Pos"], marker_color="#ff6600", text=df["Qtd_Pos"], textposition="auto"))
    fig_stacked.add_trace(go.Bar(name="Docentes", x=df["Projeto"], y=df["Qtd_Docentes"], marker_color="#66cc66", text=df["Qtd_Docentes"], textposition="auto"))
    
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
    
    # Distribuição por categoria
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
    
    # Habilidades (agora funcionando corretamente)
    st.subheader("🛠️ Habilidades Mais Demandadas")
    all_skills = []
    for skills in df["Habilidades"]:
        if isinstance(skills, list):
            all_skills.extend(skills)
        elif isinstance(skills, str) and skills:
            all_skills.extend([s.strip() for s in skills.split(';')])
    
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
    else:
        st.warning("Nenhuma habilidade encontrada nos dados")
    
    # Áreas do conhecimento
    st.subheader("📚 Áreas do Conhecimento")
    all_areas = []
    for areas in df["Áreas"]:
        if isinstance(areas, list):
            all_areas.extend(areas)
        elif isinstance(areas, str) and areas:
            all_areas.extend([a.strip() for a in areas.split(';')])
    
    if all_areas:
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
    all_productions = []
    for prods in df["Produção"]:
        if isinstance(prods, list):
            all_productions.extend(prods)
        elif isinstance(prods, str) and prods:
            all_productions.extend([p.strip() for p in prods.split(';')])
    
    if all_productions:
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
    
    # Proporção
    st.subheader("⚖️ Proporção Graduação vs Pós-Graduação")
    
    total_people = df["Qtd_Graduacao"] + df["Qtd_Pos"] + df["Qtd_Docentes"]
    df_display = df.copy()
    df_display["% Graduação"] = (df_display["Qtd_Graduacao"] / total_people * 100).round(1)
    df_display["% Pós-Graduação"] = (df_display["Qtd_Pos"] / total_people * 100).round(1)
    
    fig_prop = go.Figure()
    fig_prop.add_trace(go.Bar(name="% Graduação", x=df_display["Projeto"], y=df_display["% Graduação"], marker_color="#0066cc"))
    fig_prop.add_trace(go.Bar(name="% Pós-Graduação", x=df_display["Projeto"], y=df_display["% Pós-Graduação"], marker_color="#ff6600"))
    fig_prop.update_layout(barmode="stack", title="Proporção por Projeto", xaxis_tickangle=-45, yaxis_title="Percentual (%)")
    st.plotly_chart(fig_prop, use_container_width=True)
    
    # Atividades
    # st.subheader("📋 Atividades Mais Frequentes")
    # all_activities = []
    # for acts in df["Atividades"]:
    #     if isinstance(acts, list):
    #         all_activities.extend(acts)
    #     elif isinstance(acts, str) and acts:
    #         all_activities.extend([a.strip().lower() for a in acts.split(',')])
    
    # if all_activities:
    #     activity_counts = Counter(all_activities).most_common(15)
    #     act_df = pd.DataFrame(activity_counts, columns=["Atividade", "Frequência"])
    #     fig_act = px.bar(
    #         act_df,
    #         x="Atividade",
    #         y="Frequência",
    #         title="Atividades mais recorrentes nos projetos",
    #         color="Frequência",
    #         color_continuous_scale="Purples"
    #     )
    #     fig_act.update_layout(xaxis_tickangle=-45, height=450)
    #     st.plotly_chart(fig_act, use_container_width=True)
    
    # Complexidade
    st.subheader("📊 Métricas de Complexidade por Projeto")
    
    df["num_habilidades"] = df["Habilidades"].apply(lambda x: len(x) if isinstance(x, list) else 0)
    df["num_areas"] = df["Áreas"].apply(lambda x: len(x) if isinstance(x, list) else 0)
    df["num_producoes"] = df["Produção"].apply(lambda x: len(x) if isinstance(x, list) else 0)
    df["num_atividades"] = df["Atividades"].apply(lambda x: len(x) if isinstance(x, list) else 0)
    
    complexity_data = []
    for _, row in df.iterrows():
        nome = row["Projeto"][:30] + "..." if len(row["Projeto"]) > 30 else row["Projeto"]
        complexity_data.append({"Projeto": nome, "Métrica": "Habilidades", "Valor": row["num_habilidades"]})
        complexity_data.append({"Projeto": nome, "Métrica": "Áreas", "Valor": row["num_areas"]})
        complexity_data.append({"Projeto": nome, "Métrica": "Produções", "Valor": row["num_producoes"]})
        complexity_data.append({"Projeto": nome, "Métrica": "Atividades", "Valor": row["num_atividades"]})
    
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
    fig_complex.update_layout(xaxis_tickangle=-45, height=450)
    st.plotly_chart(fig_complex, use_container_width=True)


def show_project_detail(df):
    """Detalhamento por projeto"""
    st.header("🔍 Detalhamento por Projeto")
    
    projetos_list = df["Projeto"].tolist()
    selected_project = st.selectbox("Selecione um projeto:", projetos_list)
    
    project_data = df[df["Projeto"] == selected_project].iloc[0]
    
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Informações Gerais", "👥 Equipe", "🎯 Atividades", "📦 Produções"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {project_data['Projeto']}")
            st.markdown(f"**📝 Descrição:** {project_data['Descrição']}")
            st.markdown("---")
            st.markdown("**📅 Cronograma**")
            st.write(f"• **Início previsto:** {project_data['Previsão de início']}")
            st.write(f"• **Término previsto:** {project_data['Previsão de término'] if project_data.get('Previsão de término') else 'Não informado'}")
        
        with col2:
            st.markdown("**👨‍🎓 Recursos Humanos**")
            st.metric("Graduação", project_data["Qtd_Graduacao"])
            st.metric("Pós-Graduação", project_data["Qtd_Pos"])
            st.metric("Docentes", project_data["Qtd_Docentes"] if project_data["Qtd_Docentes"] > 0 else "Nenhum")
            st.markdown("---")
            st.markdown(f"**💰 Fonte:** {project_data['Fonte_Recurso']}")
    
    with tab2:
        st.markdown("### 👥 Equipe do Projeto")
        equipe_list = str(project_data["Equipe"]).split(";")
        st.markdown(f"**Total de membros:** {len(equipe_list)}")
        for membro in equipe_list:
            st.markdown(f"- {membro.strip()}")
        
        st.markdown("---")
        st.markdown("### 🎯 Coordenação")
        coord_list = str(project_data["Coordenação"]).split(";")
        for coord in coord_list:
            st.markdown(f"**{coord.strip()}**")
    
    with tab3:
        st.markdown("### 🛠️ Habilidades Indispensáveis")
        habilidades = project_data["Habilidades"]
        if isinstance(habilidades, list):
            for skill in habilidades:
                st.markdown(f"- {skill}")
        else:
            st.markdown(f"- {habilidades}")
        
        st.markdown("### 📚 Áreas do Conhecimento")
        areas = project_data["Áreas"]
        if isinstance(areas, list):
            for area in areas:
                st.markdown(f"- {area}")
        else:
            st.markdown(f"- {areas}")
        
        st.markdown("### 📋 Atividades Previstas")
        atividades = project_data["Atividades"]
        if isinstance(atividades, list):
            for atividade in atividades:
                st.markdown(f"- {atividade}")
        else:
            st.markdown(f"- {atividades}")
    
    with tab4:
        st.markdown("### 🎯 Produções Técnicas e Acadêmicas")
        producoes = project_data["Produção"]
        if isinstance(producoes, list):
            cols = st.columns(min(len(producoes), 4))
            for i, prod in enumerate(producoes):
                with cols[i % 4]:
                    st.markdown(f"✅ {prod}")
        else:
            st.markdown(f"✅ {producoes}")


def show_team_analysis(df):
    """Análise de equipe"""
    st.header("👥 Análise de Equipes e Participação")
    
    all_members = []
    for equipe in df["Equipe"]:
        members = str(equipe).split(";")
        all_members.extend([m.strip() for m in members if m.strip()])
    
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
    
    st.subheader("🎯 Coordenadores de Projetos")
    all_coords = []
    for coord in df["Coordenação"]:
        all_coords.extend([c.strip() for c in str(coord).split(";")])
    
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
    
    st.subheader("🤝 Colaboração entre Equipes")
    
    co_occurrence = {}
    for equipe in df["Equipe"]:
        members = [m.strip() for m in str(equipe).split(";")]
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
    
    # Estatísticas
    st.subheader("📈 Estatísticas da Equipe")
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    
    with stats_col1:
        st.metric("Total de Pessoas", len(member_counts))
    with stats_col2:
        st.metric("Total de Participações", sum(member_counts.values()))
    with stats_col3:
        st.metric("Média por Pessoa", f"{sum(member_counts.values()) / len(member_counts):.1f}" if member_counts else "0")
    with stats_col4:
        st.metric("Mais Participações", max(member_counts.values()) if member_counts else "0")


# ===================== MAIN =====================

def main():
    st.title("🏗️ Painel de Gestão de Projetos - PLANTEAR")
    st.caption("Sistema integrado de visualização e análise de projetos")
    st.markdown("---")
    
    st.sidebar.header("🎛️ Navegação")
    
    view = st.sidebar.radio(
        "Escolha uma visualização:",
        ["📊 Visão Geral", "🔍 Detalhe do Projeto", "👥 Análise de Equipe"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Sobre")
    st.sidebar.info(
        "Este dashboard apresenta informações consolidadas "
        "dos projetos, permitindo análise de equipes, "
        "recursos e demandas.\n\n"
        "📁 **Fonte:** CSV do GitHub\n"
        "🔄 **Atualização:** A cada hora"
    )
    
    if st.sidebar.button("🔄 Recarregar Dados"):
        st.cache_data.clear()
        st.rerun()
    
    with st.spinner("Carregando dados..."):
        df = carregar_csv_github()
    
    if df is not None and len(df) > 0:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📈 Estatísticas")
        st.sidebar.metric("Projetos", len(df))
        st.sidebar.metric("Envolvidos", df["Qtd_Graduacao"].sum() + df["Qtd_Pos"].sum() + df["Qtd_Docentes"].sum())
    
    if view == "📊 Visão Geral":
        show_overview(df)
    elif view == "🔍 Detalhe do Projeto":
        show_project_detail(df)
    elif view == "👥 Análise de Equipe":
        show_team_analysis(df)
    
    st.markdown("---")
    st.caption("📅 Dados via GitHub | 🔄 Atualização automática")


if __name__ == "__main__":
    main()