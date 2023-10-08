
#Libraries
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine

#Bibliotecas necessárias
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='🚚', layout='wide')

#-----------------------------------------#
# Funções
#-----------------------------------------#

def top_delivers(df, top_asc):
                
    df2 = (df.loc[:,['Delivery_person_ID', 'City', 'Time_taken(min)']]
             .groupby(['City', 'Delivery_person_ID'])
             .max()
             .sort_values(['City', 'Time_taken(min)'], ascending = top_asc)
             .reset_index())
                    
                    
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian',:].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban',:].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban',:].head(10)
                    
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop = True)
    return df3

def clean_code (df):
    """ Esta função tem a responsabilidade de limpar o dataframe

        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

        Input: Dataframe
        Output: Dataframe
    """
    
    #Removendo espaços de strings
    df.loc[:,'ID'] = df.loc[:,'ID'].str.strip()
    df.loc[:,'Delivery_person_ID'] = df.loc[:,'Delivery_person_ID'].str.strip()
    df.loc[:,'Road_traffic_density'] = df.loc[:,'Road_traffic_density'].str.strip()
    df.loc[:,'Type_of_order'] = df.loc[:,'Type_of_order'].str.strip()
    df.loc[:,'Type_of_vehicle'] = df.loc[:,'Type_of_vehicle'].str.strip()
    df.loc[:,'City'] = df.loc[:,'City'].str.strip()
    df.loc[:,'Festival'] = df.loc[:,'Festival'].str.strip()
    
    
    #Convertendo datas para datetime
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format = '%d-%m-%Y')
    
    
    #Removendo NaN
    selected_lines = (df['Delivery_person_Age'] != 'NaN ')
    df = df.loc[selected_lines,:]
    
    selected_lines = (df['Delivery_person_Ratings'] != 'NaN')
    df = df.loc[selected_lines,:]
    
    selected_lines = (df['Weatherconditions'] != 'NaN')
    df = df.loc[selected_lines,:]
    
    selected_lines = (df['multiple_deliveries'] != 'NaN')
    df = df.loc[selected_lines,:]
    
    selected_lines = (df['City'] != 'NaN')
    df = df.loc[selected_lines,:]
    
    selected_lines = (df['Road_traffic_density'] != 'NaN')
    df = df.loc[selected_lines,:]
    
    selected_lines = (df['Festival'] != 'NaN ')
    df = df.loc[selected_lines,:]
    
    
    #Convertendo string para int
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    
    
    #Convertendo string para float
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    
    
    #Limpando a coluna de Time Taken
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    return df

#-----------------------------Início da estrutura lógica do código-------------------------#

#-----------------------------
# Import dataset #
#-----------------------------#
df_raw = pd.read_csv('dataset/train.csv')
df = df_raw.copy()

#-----------------------------
# Limpando os dados
#-----------------------------
df = clean_code(df)


#-----------------------------------------#
#Barra Lateral
#-----------------------------------------#

st.header('Marketplace - Visão Entregadores')

#image_path = '/Users/User/Documents/Repos/ftc_programacao_python/images/logo_lr5.png'
image = Image.open('logo_lr5.png')
st.sidebar.image(image,width=250)
st.sidebar.markdown("""---""")

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('Selecione uma data limite')

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value = datetime(2022, 4, 13),
    min_value = datetime(2022, 2, 11),
    max_value = datetime(2022, 4, 6),
    format = 'DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?', 
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Lucas Rocha')


#Data Filter
selected_lines = df['Order_Date'] < date_slider
df = df.loc[selected_lines,:]

#Traffic Filter
selected_lines = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[selected_lines,:]

#-----------------------------------------#
#LAYOUT STREAMLIT#
#-----------------------------------------#

with st.container():
    st.title( 'Overall Metrics')

    col1, col2, col3, col4 = st.columns(4, gap='Large')
    
    with col1:

        
        #A maior idade dos entregadores
        selected_lines = (df['Delivery_person_Age'] != 'NaN ')
        df_age = df.loc[selected_lines,:]
        
        maior_idade = df_age['Delivery_person_Age'].max()
        col1.metric( 'Maior idade', maior_idade)
        
    with col2:
        #A menor idade dos entregadores
        menor_idade = df_age['Delivery_person_Age'].min()
        col2.metric( 'Menor idade', menor_idade)
    
    with col3:
        #Melhor condição
        melhor_condicao = df['Vehicle_condition'].max()
        col3.metric( 'Melhor condição', melhor_condicao)
    
    with col4:
        #Pior condição
        pior_condicao = df['Vehicle_condition'].min()
        col4.metric( 'Pior condição', pior_condicao)

with st.container():
    st.markdown("""---""")
    st.title('Avaliações')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown( '##### Avaliações médias por entregador')
        #3. A avaliação média por entregador.
        df_avg = (df.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                   .groupby('Delivery_person_ID')
                   .mean()
                   .reset_index())
        st.dataframe(df_avg)
    
    with col2:
        st.markdown( '##### Avaliações médias por trânsito')  
        #4. A avaliação média e o desvio padrão por tipo de tráfego.

        df_avg_std_rating_by_traffic = (df.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                          .groupby('Road_traffic_density')
                                          .agg({'Delivery_person_Ratings' : ['mean', 'std']}))
        
        #mudança de nome das colunas
        df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']
        
        #reset do index
        df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
        
        st.dataframe(df_avg_std_rating_by_traffic)

        st.markdown( '##### Avaliações médias por clima')  
        #5. A avaliação média e o desvio padrão por condições climáticas.

        df_avg_std_rating_by_weatherconditions = (df.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                                    .groupby('Weatherconditions')
                                                    .agg({'Delivery_person_Ratings' : ['mean', 'std']}))
        
        #mudança de nome das colunas
        df_avg_std_rating_by_weatherconditions.columns = ['delivery_mean', 'delivery_std']
        
        #reset do index
        df_avg_std_rating_by_weatherconditions = df_avg_std_rating_by_weatherconditions.reset_index()
        
        st.dataframe(df_avg_std_rating_by_weatherconditions)
          
with st.container():
    st.markdown("""---""")
    st.title('Velocidade de Entrega')

    col1, col2 = st.columns(2)
    with col1:
        st.markdown( '##### Top entregadores mais rápidos')
        df3 = top_delivers(df, top_asc=True)
        st.dataframe(df3)
    
    with col2:
        st.markdown( '##### Top entregadores mais lentos')  
        df3 = top_delivers(df, top_asc=False)
        st.dataframe(df3)


        