import streamlit as st
import os
import google.generativeai as genai
from datetime import datetime
import os
import requests
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI  # Importação atualizada para a nova versão
from typing import List, Dict

# Carrega variáveis de ambiente
load_dotenv()

# Configurações
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o"  # Atualize para o modelo correto que você deseja usar
COLLECTION_NAME = os.getenv("ASTRA_DB_COLLECTION")
NAMESPACE = os.getenv("ASTRA_DB_NAMESPACE", "default_keyspace")
EMBEDDING_DIMENSION = 1536
ASTRA_DB_API_BASE = os.getenv("ASTRA_DB_API_ENDPOINT")
ASTRA_DB_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Configura o cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)


class AstraDBClient:
    def __init__(self):
        self.base_url = f"{ASTRA_DB_API_BASE}/api/json/v1/{NAMESPACE}"
        self.headers = {
            "Content-Type": "application/json",
            "x-cassandra-token": ASTRA_DB_TOKEN,
            "Accept": "application/json"
        }
    
    def vector_search(self, collection: str, vector: List[float], limit: int = 3) -> List[Dict]:
        """Realiza busca por similaridade vetorial"""
        url = f"{self.base_url}/{collection}"
        payload = {
            "find": {
                "sort": {"$vector": vector},
                "options": {"limit": limit}
            }
        }
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()["data"]["documents"]
        except Exception as e:
            st.error(f"Erro na busca vetorial: {str(e)}")
            st.error(f"Resposta da API: {response.text if 'response' in locals() else 'N/A'}")
            return []

def get_embedding(text: str) -> List[float]:
    """Obtém embedding do texto usando OpenAI"""
    try:
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding
    except Exception as e:
        st.error(f"Erro ao obter embedding: {str(e)}")
        return []

def generate_response(query: str, context: str) -> str:
    """Gera resposta usando o modelo de chat da OpenAI"""
    if not context:
        return "Não encontrei informações relevantes para responder sua pergunta."
    
    prompt = f"""Responda baseado no contexto abaixo:
    
    Contexto:
    {context}
    
    Pergunta: {query}
    Resposta:"""
    
    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": '''
                Você é um especialista em marketing digital. Com base na sua base de conhecimentos, 
                ajude o usuário a encontrar a melhor estratégia para proceder.
                '''},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"

# Configuração inicial
st.set_page_config(
    layout="wide",
    page_title="Strategic AI Agent",
    page_icon="🚀"
)

# Configura o cliente OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Inicializa o cliente AstraDB
astra_client = AstraDBClient()

# Inicializar Gemini
gemini_api_key = os.getenv("GEM_API_KEY")
genai.configure(api_key=gemini_api_key)
modelo_texto = genai.GenerativeModel("gemini-2.0-flash")

# CSS personalizado
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        flex-wrap: wrap;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        border-radius: 4px;
        white-space: nowrap;
        font-size: 14px;
        transition: all 0.2s;
        background-color: #f0f2f6;
        margin-right: 8px !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50 !important;
        color: white !important;
        font-weight: 600;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .strategy-card {
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background-color: #f9f9f9;
        border-left: 4px solid #4CAF50;
    }
    .insight-badge {
        background-color: #ffeb3b;
        color: #333;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: bold;
        margin-right: 8px;
    }
    .content-pillar {
        background-color: #f0f8ff;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid #4682b4;
    }
    .content-type-badge {
        background-color: #e6e6fa;
        color: #333;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        margin-right: 8px;
        display: inline-block;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.image('https://via.placeholder.com/300x80?text=Strategic+AI+Agent', width=300)
st.title('Strategic AI Agent')
st.caption('Assistente de IA para planejamento estratégico e solução de desafios complexos')

# Abas principais
tabs = st.tabs([
    "🔍 Definição do Problema",
    "📊 Análise de Dados",
    "💡 Geração de Insights",
    "🛠️ Estratégias e Briefings",
    "📝 Estratégia de Conteúdo",  # Nova aba adicionada
    "🏷️ Estratégia de Marca",
    "📡 Comunicação e Canais",
    "📈 Métricas e KPIs",
    "👥 Estrutura de Time",
    "📊 Análises Estratégicas"
])

# 1. Definição do Problema
with tabs[0]:
    st.header("🔍 Definição do Problema Estratégico")
    
    col1, col2 = st.columns(2)
    with col1:
        business_context = st.text_area(
            "Contexto do Negócio*",
            placeholder="Descreva sua organização, mercado e situação atual...",
            height=150
        )
    with col2:
        business_challenge = st.text_area(
            "Desafio Estratégico*",
            placeholder="Qual problema ou oportunidade você está enfrentando?",
            height=150
        )
    
    if st.button("🔍 Formular Tensão Estratégica", key="btn_tensao"):
        if not business_context or not business_challenge:
            st.warning("Preencha todos os campos obrigatórios")
        else:
            with st.spinner('Identificando o cerne do problema...'):
                # Passo 1: Gerar a formulação inicial da tensão estratégica
                prompt = f"""
                Com base nestas informações:
                
                **Contexto:** {business_context}
                **Desafio:** {business_challenge}
                
                Crie uma formulação clara do problema como uma tensão estratégica (paradoxo aparente) usando o formato:
                "[Grupo] quer [objetivo], mas [barreira]"
                
                Inclua:
                1. A tensão principal (1-2 frases)
                2. Explicação breve do conflito (50 palavras)
                3. 3 perguntas-chave que precisam ser respondidas
                
                Saída em markdown com formatação clara.
                """
                initial_response = modelo_texto.generate_content(prompt)
                
                # Passo 2: Gerar pergunta para busca na base de dados
                question_prompt = f'''
                Baseado em {initial_response.text}, crie uma pergunta concisa para consultar 
                uma base de dados de marketing digital e recuperar informações relevantes 
                que possam ajudar a resolver esta tensão estratégica.
                
                A pergunta deve ser direta e focada nos aspectos-chave do problema.
                '''
                search_question = modelo_texto.generate_content(question_prompt)
                
                # Passo 3: Buscar informações relevantes (RAG)
                if search_question.text:
                    embedding = get_embedding(search_question.text)
                    if embedding:
                        rag_results = astra_client.vector_search(COLLECTION_NAME, embedding)
                        rag_context = "\n".join([str(doc) for doc in rag_results])
                    else:
                        rag_context = "Não foi possível recuperar informações adicionais."
                else:
                    rag_context = "Não foi gerada uma pergunta para busca."
                
                # Passo 4: Aprimorar a resposta inicial com o contexto RAG
                refinement_prompt = f'''
                Aqui está a análise inicial da tensão estratégica:
                {initial_response.text}
                
                E aqui estão informações relevantes recuperadas da base de conhecimento:
                {rag_context}
                
                Com base nisso, aprimore a análise inicial:
                1. Mantenha a estrutura original (tensão, explicação, perguntas)
                2. Incorpore insights relevantes das informações recuperadas
                3. Melhore a clareza e precisão onde aplicável
                4. Adicione 1-2 exemplos concretos se relevantes
                5. Mantenha a formatação em markdown
                
                Se as informações recuperadas não forem relevantes, mantenha a análise original.
                '''
                refined_response = modelo_texto.generate_content(refinement_prompt)
                
                # Armazenar e exibir resultados
                st.session_state['strategic_tension'] = refined_response.text
                st.session_state['rag_context'] = rag_context
                
                st.success("Tensão Estratégica Identificada:")
                st.markdown(refined_response.text)
                
                # Opcional: mostrar informações recuperadas (pode ser colapsado)
                with st.expander("Ver informações de apoio utilizadas"):
                    st.markdown(f"**Pergunta de busca:** {search_question.text}")
                    st.markdown("**Informações recuperadas:**")
                    st.write(rag_context)

# 2. Análise de Dados
with tabs[1]:
    st.header("📊 Análise Combinada de Dados")
    
    if 'strategic_tension' not in st.session_state:
        st.info("ℹ️ Defina primeiro o problema na aba 'Definição do Problema'")
    else:
        st.markdown("**Tensão Estratégica Atual:**")
        st.markdown(st.session_state['strategic_tension'])
        
        analysis_type = st.radio(
            "Tipo de Análise:",
            ["📚 Pesquisa Secundária", "📊 Dados Quantitativos", "🗣️ Entrevista Qualitativa"],
            horizontal=True
        )
        
        if analysis_type == "📚 Pesquisa Secundária":
            research_topics = st.text_area(
                "Tópicos para Pesquisa Secundária*",
                placeholder="Ex: tendências de mercado, benchmarks do setor, relatórios relevantes...",
                height=100
            )
            
            if st.button("🔎 Realizar Pesquisa Secundária"):
                with st.spinner('Analisando dados e contextos externos...'):
                    prompt = f"""
                    Com base na tensão estratégica:
                    {st.session_state['strategic_tension']}
                    
                    Realize uma análise de pesquisa secundária sobre:
                    {research_topics}
                    
                    Inclua:
                    1. 3-5 fontes confiáveis relevantes
                    2. Principais achados (bullet points)
                    3. Como esses dados se relacionam com o problema
                    4. 2-3 hipóteses preliminares
                    
                    Formato: markdown com seções claras.
                    """
                    response = modelo_texto.generate_content(prompt)
                    question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                    st.session_state['secondary_research'] = response.text
                    st.markdown(response.text)
                    st.markdown(question.text)
        
        elif analysis_type == "📊 Dados Quantitativos":
            st.file_uploader("Carregar Conjunto de Dados (CSV/Excel)", type=["csv", "xlsx"])
            data_questions = st.text_area(
                "Perguntas para Análise Quantitativa*",
                placeholder="Que hipóteses você quer testar? Que relações investigar?",
                height=100
            )
            
            if st.button("📈 Analisar Dados Quantitativos"):
                with st.spinner('Processando dados e identificando padrões...'):
                    prompt = f"""
                    Com base na tensão estratégica:
                    {st.session_state['strategic_tension']}
                    
                    Sugira uma abordagem para analisar dados quantitativos que responda a:
                    {data_questions}
                    
                    Inclua:
                    1. Métodos estatísticos recomendados
                    2. Visualizações sugeridas
                    3. Possíveis armadilhas
                    4. Como interpretar os resultados
                    
                    Formato: markdown com exemplos.
                    """
                    response = modelo_texto.generate_content(prompt)
                    st.session_state['quantitative_analysis'] = response.text
                    st.markdown(response.text)
                    question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                    st.markdown(question.text)
        
        else:  # Entrevista Qualitativa
            interview_goals = st.text_area(
                "Objetivos da Pesquisa Qualitativa*",
                placeholder="O que você quer entender sobre comportamentos, motivações, barreiras?",
                height=100
            )
            participant_profile = st.text_input(
                "Perfil dos Participantes*",
                placeholder="Ex: consumidores entre 25-40 anos, usuários frequentes do produto..."
            )
            
            if st.button("🗣️ Gerar Roteiro de Entrevista"):
                with st.spinner('Criando guia de pesquisa qualitativa...'):
                    prompt = f"""
                    Com base na tensão estratégica:
                    {st.session_state['strategic_tension']}
                    
                    Crie um roteiro de entrevista qualitativa para:
                    **Objetivo:** {interview_goals}
                    **Participantes:** {participant_profile}
                    
                    Inclua:
                    1. 5-7 perguntas principais (abertas)
                    2. Técnicas de sondagem (ex: "Pode me contar mais sobre...")
                    3. Exercícios projetivos (ex: "Se fosse um carro, qual seria?")
                    4. Como analisar as respostas
                    
                    Formato: markdown com seções lógicas.
                    """
                    response = modelo_texto.generate_content(prompt)
                    st.session_state['qualitative_guide'] = response.text
                    st.markdown(response.text)
                    question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                    st.markdown(question.text)

# 3. Geração de Insights
with tabs[2]:
    st.header("💡 Geração de Insights Estratégicos")
    
    if 'strategic_tension' not in st.session_state:
        st.info("ℹ️ Comece definindo o problema na primeira aba")
    else:
        st.markdown("**Contexto Atual:**")
        st.markdown(st.session_state['strategic_tension'])
        
        research_data = ""
        if 'secondary_research' in st.session_state:
            st.markdown("**Pesquisa Secundária:**")
            st.markdown(st.session_state['secondary_research'][:500] + "...")
            research_data += f"\n\nPesquisa Secundária:\n{st.session_state['secondary_research']}"
        
        if 'quantitative_analysis' in st.session_state:
            st.markdown("**Análise Quantitativa:**")
            st.markdown(st.session_state['quantitative_analysis'][:500] + "...")
            research_data += f"\n\nAnálise Quantitativa:\n{st.session_state['quantitative_analysis']}"
        
        if 'qualitative_guide' in st.session_state:
            st.markdown("**Pesquisa Qualitativa:**")
            st.markdown(st.session_state['qualitative_guide'][:500] + "...")
            research_data += f"\n\nPesquisa Qualitativa:\n{st.session_state['qualitative_guide']}"
        
        if st.button("💡 Gerar Insights Estratégicos"):
            with st.spinner('Sintetizando dados em insights acionáveis...'):
                prompt = f"""
                Com base nestas informações:
                **Tensão Estratégica:** {st.session_state['strategic_tension']}
                **Dados de Pesquisa:** {research_data if research_data else "Nenhum dado adicional fornecido"}
                
                Gere 3-5 insights estratégicos profundos que:
                1. Revelam padrões comportamentais ou culturais
                2. Explicam a raiz do problema
                3. São surpreendentes ou contra-intuitivos
                4. Levam a oportunidades estratégicas
                
                Formato para cada insight:
                ### [Título do Insight]
                <span class='insight-badge'>INSIGHT</span>
                **O que é:** [Descrição clara]
                **Por que importa:** [Impacto no negócio]
                **Como usar:** [Aplicação prática]
                
                Use markdown com formatação rica.
                """
                response = modelo_texto.generate_content(prompt)
                st.session_state['strategic_insights'] = response.text
                st.markdown(response.text, unsafe_allow_html=True)
                
                question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                st.markdown(question.text)

# 4. Estratégias e Briefings
with tabs[3]:
    st.header("🛠️ Desenvolvimento de Estratégias")
    
    if 'strategic_insights' not in st.session_state:
        st.info("ℹ️ Gere insights primeiro na aba anterior")
    else:
        st.markdown("**Insights Atuais:**")
        st.markdown(st.session_state['strategic_insights'], unsafe_allow_html=True)
        
        strategy_tab1, strategy_tab2, strategy_tab3 = st.tabs([
            "📋 Opções Estratégicas",
            "✍️ Briefs Estratégicos",
            "🎯 Frameworks"
        ])
        
        with strategy_tab1:
            if st.button("🔄 Gerar Opções Estratégicas"):
                with st.spinner('Criando alternativas estratégicas...'):
                    prompt = f"""
                    Com base nestes insights:
                    {st.session_state['strategic_insights']}
                    
                    Desenvolva 3 opções estratégicas distintas, cada uma com:
                    ### [Nome da Estratégia]
                    **Ideia Central:** [1-2 frases]
                    **Prós:** [3-5 pontos fortes]
                    **Contras:** [2-3 limitações]
                    **Melhor Para:** [Quando usar esta abordagem]
                    **Exemplo de Implementação:** [Caso concreto]
                    
                    As estratégias devem representar abordagens fundamentalmente diferentes.
                    """
                    response = modelo_texto.generate_content(prompt)
                    st.session_state['strategy_options'] = response.text
                    st.markdown(response.text)
                    question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                    st.markdown(question.text)
        
        with strategy_tab2:
            briefing_type = st.selectbox(
                "Tipo de Briefing",
                ["Client Brief (Negócio)", "Creative Brief (Criatividade)", "Tactical Brief (Execução)"]
            )
            
            if st.button(f"📝 Gerar {briefing_type}"):
                with st.spinner(f'Criando {briefing_type}...'):
                    prompt = f"""
                    Crie um {briefing_type} profissional com base em:
                    **Tensão Estratégica:** {st.session_state['strategic_tension']}
                    **Insights:** {st.session_state['strategic_insights']}
                    
                    Use a estrutura:
                    ### Contexto
                    - Background
                    - Objetivo
                    - Público-alvo
                    
                    ### Desafio
                    - Problema central
                    - Barreiras
                    - Oportunidades
                    
                    ### Direção
                    - Tom
                    - Mensagem-chave
                    - Chamada para ação
                    
                    ### {briefing_type.split(' ')[0]} Específicos
                    {"[Dados de negócio e métricas]" if "Client" in briefing_type else 
                     "[Inspiração criativa e referências]" if "Creative" in briefing_type else 
                     "[Canais, cronograma e recursos]"}
                    
                    Formato: markdown profissional.
                    """
                    response = modelo_texto.generate_content(prompt)
                    st.session_state[f'{briefing_type.lower().split()[0]}_brief'] = response.text
                    st.markdown(response.text)
                    question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                    st.markdown(question.text)
        
        with strategy_tab3:
            framework = st.selectbox(
                "Framework Estratégico",
                ["GET/TO/BY", "Single Minded Proposition", "Tensão-Insight-Ideia"]
            )
            
            if st.button(f"🖇️ Aplicar {framework}"):
                with st.spinner(f'Adaptando {framework}...'):
                    prompt = f"""
                    Aplique o framework {framework} a este cenário:
                    **Tensão:** {st.session_state['strategic_tension']}
                    **Insights:** {st.session_state['strategic_insights']}
                    
                    {"Para GET/TO/BY, preencha:" if framework == "GET/TO/BY" else 
                     "Para SMP, defina:" if framework == "Single Minded Proposition" else 
                     "Desenvolva a narrativa:"}
                    
                    {f"""
                    ### GET/TO/BY
                    **GET** [Audiência]: 
                    **TO** [Mudança desejada]: 
                    **BY** [Meio/Mecanismo]: 
                    """ if framework == "GET/TO/BY" else 
                    f"""
                    ### Single Minded Proposition
                    **Proposição Única:** [1 frase impactante]
                    **Razão para Acreditar:** [3 pontos]
                    """ if framework == "Single Minded Proposition" else 
                    f"""
                    ### Tensão → Insight → Ideia
                    **Tensão:** [Recapitulação]
                    **Insight Chave:** [Do research]
                    **Ideia Central:** [Solução criativa]
                    """}
                    
                    Formato: markdown com exemplos concretos.
                    """
                    response = modelo_texto.generate_content(prompt)
                    st.markdown(response.text)
                    question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                    st.markdown(question.text)

# 5. Estratégia de Conteúdo (NOVA ABA)
with tabs[4]:
    st.header("📝 Estratégia de Conteúdo")
    
    st.markdown("""
    <style>
        .content-pillar {
            background-color: #f0f8ff;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            border-left: 4px solid #4682b4;
        }
        .content-type-badge {
            background-color: #e6e6fa;
            color: #333;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-right: 8px;
            display: inline-block;
            margin-bottom: 4px;
        }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        content_goal = st.selectbox(
            "Objetivo Principal do Conteúdo*",
            ["Educar", "Engajar", "Converter", "Fidelizar", "Humanizar a marca"]
        )
        content_audience = st.text_input(
            "Público-Alvo Principal*",
            placeholder="Ex: Mulheres 25-35, classe AB, interessadas em sustentabilidade..."
        )
    with col2:
        content_channels = st.multiselect(
            "Canais Prioritários*",
            ["Website/Blog", "Redes Sociais", "E-mail", "Vídeo", "Podcast", "Eventos", "Publicações"],
            default=["Website/Blog", "Redes Sociais"]
        )
        content_budget = st.select_slider(
            "Orçamento para Conteúdo",
            options=["Baixo", "Médio", "Alto"]
        )
    
    if st.button("📊 Gerar Estratégia de Conteúdo"):
        with st.spinner('Criando plano de conteúdo personalizado...'):
            prompt = f"""
            Crie uma estratégia de conteúdo completa para:
            **Objetivo:** {content_goal}
            **Público:** {content_audience}
            **Canais:** {', '.join(content_channels)}
            **Orçamento:** {content_budget}
            
            A estratégia deve incluir:
            
            ### 1. Pilares de Conteúdo (3-5 temas centrais)
            Para cada pilar:
            - Justificativa estratégica
            - Ângulos de abordagem
            - Exemplos concretos
            
            ### 2. Tipos de Conteúdo por Canal
            - Formatos recomendados
            - Frequência ideal
            - Recursos necessários
            
            ### 3. Calendário Editorial
            - Estrutura de temas mensais
            - Datas relevantes
            - Balanceamento de formatos
            
            ### 4. Fluxo de Conversão
            - Como o conteúdo leva ao objetivo
            - Chamadas para ação
            - Integração entre canais
            
            Formato: markdown com formatação rica e exemplos.
            """
            response = modelo_texto.generate_content(prompt)
            
            # Armazenar e exibir resultados
            st.session_state['content_strategy'] = response.text
            
            st.success("Estratégia de Conteúdo Gerada:")
            st.markdown(response.text, unsafe_allow_html=True)
            
            # Adiciona análise de perguntas para base de dados
            question = modelo_texto.generate_content(f'''Baseado em {response.text}, crie uma pergunta para consultar uma base de dados de marketing digital e recuperar informações relevantes sobre estratégias de conteúdo''')
            st.markdown("**Pergunta para Base de Dados:**")
            st.markdown(question.text)

# 6. Estratégia de Marca
with tabs[5]:
    st.header("🏷️ Estratégia de Marca")
    
    brand_name = st.text_input("Nome da Marca*")
    brand_category = st.text_input("Categoria/Setor*")
    
    if brand_name and brand_category:
        brand_tab1, brand_tab2, brand_tab3 = st.tabs([
            "🔍 Brand Audit",
            "🪜 Benefit Ladder",
            "🔮 Brand Prism"
        ])
        
        with brand_tab1:
            if st.button("🔄 Realizar Brand Audit"):
                with st.spinner('Analisando identidade da marca...'):
                    prompt = f"""
                    Realize um Brand Audit completo para {brand_name} ({brand_category}) com 14 perguntas críticas:
                    
                    1. **Propósito**: Por que a marca existe além de lucrar?
                    2. **Posicionamento**: Como é única na mente dos consumidores?
                    3. **Arquitetura**: Masterbrand, House of Brands ou Híbrida?
                    4. **Valores**: Quais 3-5 valores fundamentais?
                    5. **Personalidade**: Se fosse uma pessoa, como seria?
                    6. **Visual Identity**: Elementos distintivos?
                    7. **Voz e Tom**: Como comunica?
                    8. **Experiência**: Promessa consistente em todos os pontos?
                    9. **Cultura**: Como é internalizada na organização?
                    10. **Diferenciação**: Vantagens competitivas reais?
                    11. **Consistência**: Coerência ao longo do tempo?
                    12. **Relevância**: Importância para o público-alvo?
                    13. **Flexibilidade**: Capacidade de evoluir?
                    14. **Resiliência**: Como lida com crises?
                    
                    Formato: lista com respostas concisas para cada.
                    """
                    response = modelo_texto.generate_content(prompt)
                    st.markdown(response.text)
                    question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                    st.markdown(question.text)
        
        with brand_tab2:
            if st.button("🪜 Construir Benefit Ladder"):
                with st.spinner('Criando hierarquia de benefícios...'):
                    prompt = f"""
                    Construa uma Benefit Ladder para {brand_name} ({brand_category}) com 4 níveis:
                    
                    1. **Atributos**: Características físicas/funcionais
                    2. **Benefícios Funcionais**: O que faz pelo consumidor
                    3. **Benefícios Emocionais**: Como faz se sentir
                    4. **Propósito**: Impacto maior no mundo
                    
                    Exemplo:
                    | Nível | Conteúdo |
                    |-------|---------|
                    | Atributo | Bebida gaseificada com extrato de cola |
                    | Funcional | Refresca e revigora |
                    | Emocional | Promove momentos de felicidade |
                    | Propósito | Inspira otimismo e conexão humana |
                    """
                    response = modelo_texto.generate_content(prompt)
                    st.markdown(response.text)
                    question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                    st.markdown(question.text)
        
        with brand_tab3:
            if st.button("🔮 Definir Brand Prism"):
                with st.spinner('Desenhando identidade da marca...'):
                    prompt = f"""
                    Defina o Brand Identity Prism para {brand_name} ({brand_category}) com 6 dimensões:
                    
                    1. **Físico**: Características tangíveis
                    2. **Personalidade**: Caráter humano
                    3. **Cultura**: Valores e origens
                    4. **Relacionamento**: Conexão com consumidores
                    5. **Autoimagem**: Como os usuários se veem usando
                    6. **Reflexo**: Como reflete seus consumidores
                    
                    Formato: tabela markdown com exemplos.
                    """
                    response = modelo_texto.generate_content(prompt)
                    st.markdown(response.text)
                    question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                    st.markdown(question.text)

# 7. Comunicação e Canais
with tabs[6]:
    st.header("📡 Planejamento de Comunicação")
    
    campaign_goal = st.selectbox(
        "Objetivo Principal",
        ["Awareness", "Consideração", "Conversão", "Engajamento", "Fidelização"]
    )
    budget_range = st.selectbox(
        "Faixa de Orçamento",
        ["Baixo (até 50k)", "Médio (50-500k)", "Alto (500k+)"]
    )
    
    if st.button("📅 Gerar Plano de Comunicação"):
        with st.spinner('Criando estratégia multicanal...'):
            prompt = f"""
            Crie um plano de comunicação completo para:
            **Objetivo:** {campaign_goal}
            **Orçamento:** {budget_range}
            
            Inclua:
            
            ### 1. Estratégia de Conteúdo
            - Tema central
            - Formatos prioritários
            - Tom de voz
            
            ### 2. Canais Recomendados
            - Distribuição por fase (Awareness → Consideração → Conversão)
            - Mix ideal para o orçamento
            - Canais emergentes a considerar
            
            ### 3. Calendário
            - Fases da campanha (teaser → lançamento → sustentação)
            - Frequência de publicação
            - Momentos-chave
            
            ### 4. Métricas por Canal
            - KPIs primários
            - Benchmarks esperados
            - Ferramentas de medição
            
            Formato: markdown com tabelas quando aplicável.
            """
            response = modelo_texto.generate_content(prompt)
            st.markdown(response.text)
            question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
            st.markdown(question.text)

# 8. Métricas e KPIs
with tabs[7]:
    st.header("📈 Métricas e Performance")
    
    goal_tab1, goal_tab2, goal_tab3 = st.tabs([
        "📊 KPIs por Objetivo",
        "🔄 ESOV Analysis",
        "📍 Entry Points"
    ])
    
    with goal_tab1:
        business_goal = st.selectbox(
            "Selecione o Objetivo de Negócio",
            ["Awareness", "Consideração", "Conversão", "Retenção", "Upsell"],
            key="kpi_goal"
        )
        
        if st.button("🎯 Gerar Recomendações de KPIs"):
            with st.spinner('Selecionando métricas relevantes...'):
                prompt = f"""
                Para o objetivo de {business_goal}, recomende:
                
                ### Métricas Primárias
                - 3-5 KPIs principais
                - Benchmarks do setor
                - Como medir (ferramentas)
                
                ### Métricas Secundárias
                - Indicadores complementares
                - Sinais precoces
                - Métricas de qualidade
                
                ### Armadilhas Comuns
                - Vanity metrics a evitar
                - Problemas de atribuição
                - Viéses comuns
                
                Formato: markdown com tabelas comparativas.
                """
                response = modelo_texto.generate_content(prompt)
                st.markdown(response.text)
                question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                st.markdown(question.text)
    
    with goal_tab2:
        st.info("ESOV = Share of Voice vs. Share of Market")
        market_position = st.selectbox(
            "Posição no Mercado",
            ["Líder", "Desafiante", "Seguidor", "Nicho"]
        )
        
        if st.button("📢 Analisar ESOV"):
            with st.spinner('Calculando relação voz/market share...'):
                prompt = f"""
                Para uma marca na posição de {market_position}, analise:
                
                ### Situação Ideal ESOV
                - % de Share of Voice recomendado
                - Como alocar por canal
                - Estratégias para aumentar SOV
                
                ### Diagnóstico Atual
                - Como calcular SOV atual
                - Fontes de dados
                - Benchmarks do setor
                
                ### Estratégias
                - Táticas para líderes
                - Táticas para desafiantes
                - Táticas para nicho
                
                Formato: markdown com exemplos.
                """
                response = modelo_texto.generate_content(prompt)
                st.markdown(response.text)
                question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                st.markdown(question.text)
    
    with goal_tab3:
        st.info("Category Entry Points = Momentos de decisão")
        product_category = st.text_input("Categoria de Produto", key="cep_category")
        
        if st.button("📍 Mapear Entry Points"):
            with st.spinner('Identificando momentos-chave...'):
                prompt = f"""
                Para a categoria {product_category}, identifique:
                
                ### 5-7 Principais Entry Points
                - Situações
                - Necessidades
                - Gatilhos mentais
                
                ### Estratégias por Ponto
                - Como estar presente
                - Mensagens-chave
                - Canais prioritários
                
                ### Exemplo de Mapeamento
                | Entry Point | Estratégia | Exemplo |
                |------------|------------|---------|
                | [Momento]  | [Tática]   | [Caso]  |
                
                Formato: markdown completo.
                """
                response = modelo_texto.generate_content(prompt)
                st.markdown(response.text)
                question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                st.markdown(question.text)

# 9. Estrutura de Time
with tabs[8]:
    st.header("👥 Planejamento de Equipe")
    
    org_size = st.selectbox(
        "Tamanho da Organização",
        ["Startup (<10)", "Pequena (10-50)", "Média (50-200)", "Grande (200+)"]
    )
    project_scope = st.selectbox(
        "Escopo do Projeto",
        ["Campanha", "Lançamento", "Transformação", "Operação Contínua"]
    )
    
    if st.button("👔 Recomendar Estrutura"):
        with st.spinner('Desenhando equipe ideal...'):
            prompt = f"""
            Para uma organização {org_size} trabalhando em {project_scope}, recomende:
            
            ### Equipe Essencial
            - Funções críticas
            - Alocação (% tempo)
            - Habilidades-chave
            
            ### Modelo de Operação
            - Estrutura (centralizada x descentralizada)
            - Processos de aprovação
            - Ferramentas colaborativas
            
            ### Carga de Trabalho
            - FTE necessário
            - Picos esperados
            - Necessidade de parceiros
            
            ### Cultura Recomendada
            - Valores de equipe
            - Ritmos (sprints, revisões)
            - Métricas internas
            
            Formato: markdown com organograma sugerido.
            """
            response = modelo_texto.generate_content(prompt)
            st.markdown(response.text)
            question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
            st.markdown(question.text)

# 10. Análises Estratégicas
with tabs[9]:
    st.header("📊 Análises Estratégicas")
    
    analysis_type = st.radio(
        "Tipo de Análise",
        ["SWOT", "PESTLE", "Oportunidades/Ameaças"],
        horizontal=True
    )
    
    if analysis_type == "SWOT":
        company_overview = st.text_area("Visão Geral da Empresa", height=100)
        
        if st.button("📋 Gerar Análise SWOT"):
            with st.spinner('Desenvolvendo matriz SWOT...'):
                prompt = f"""
                Crie uma análise SWOT detalhada para:
                {company_overview}
                
                **Forças:**
                - 3-5 vantagens internas
                - Como sustentar
                
                **Fraquezas:**
                - 3-5 limitações internas
                - Como mitigar
                
                **Oportunidades:**
                - 3-5 fatores externos positivos
                - Como capitalizar
                
                **Ameaças:**
                - 3-5 riscos externos
                - Como preparar
                
                **Matriz de Priorização:**
                | Critério | Impacto | Probabilidade | Prioridade |
                |----------|---------|---------------|------------|
                | [Item]   | [Alto/Médio/Baixo] | [Alta/Média/Baixa] | [1-5] |
                
                Formato: markdown completo.
                """
                response = modelo_texto.generate_content(prompt)
                st.markdown(response.text)
                question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                st.markdown(question.text)
    
    elif analysis_type == "PESTLE":
        industry = st.text_input("Setor/Indústria")
        
        if st.button("🌍 Gerar Análise PESTLE"):
            with st.spinner('Analisando fatores macro...'):
                prompt = f"""
                Realize análise PESTLE para o setor {industry}:
                
                **Políticos:**
                - 3-5 fatores
                - Impacto potencial
                
                **Econômicos:**
                - 3-5 fatores
                - Impacto potencial
                
                **Sociais:**
                - 3-5 fatores
                - Impacto potencial
                
                **Tecnológicos:**
                - 3-5 fatores
                - Impacto potencial
                
                **Legais:**
                - 3-5 fatores
                - Impacto potencial
                
                **Ambientais:**
                - 3-5 fatores
                - Impacto potencial
                
                **Recomendações:**
                - Como se preparar
                - Sinais de mudança
                
                Formato: markdown com tabela resumo.
                """
                response = modelo_texto.generate_content(prompt)
                st.markdown(response.text)
                question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                st.markdown(question.text)
    
    else:
        market_trends = st.text_area("Tendências de Mercado", height=100)
        
        if st.button("🔮 Identificar Oportunidades/Ameaças"):
            with st.spinner('Analisando cenário futuro...'):
                prompt = f"""
                Com base nestas tendências:
                {market_trends}
                
                Identifique:
                
                ### 3-5 Oportunidades Estratégicas
                - Descrição
                - Janela de tempo
                - Recursos necessários
                - Casos análogos
                
                ### 3-5 Ameaças Potenciais
                - Natureza do risco
                - Probabilidade
                - Sinais de alerta
                - Planos de contingência
                
                **Matriz de Priorização:**
                | Item | Impacto | Preparação | Ação Recomendada |
                |------|---------|------------|------------------|
                | [O/A] | [1-5] | [1-5] | [Diretriz] |
                
                Formato: markdown completo.
                """
                response = modelo_texto.generate_content(prompt)
                st.markdown(response.text)
                question = modelo_texto.generate_content(f''''Baseado em {response}, crie uma pergunta a uma base de dados de marketing
                digital para recuperar mais informações relevantes''')
                st.markdown(question.text)

# Rodapé
st.markdown("---")
st.caption("Strategic AI Agent v1.0 · Ferramenta para planejamento estratégico avançado")
