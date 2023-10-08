
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
import numpy as np

st.set_page_config(page_title='Visão Restaurantes', page_icon='🧆', layout='wide')

#-----------------------------------------#
# Funções
#-----------------------------------------#

def avg_std_time_on_traffic(df):
            
    df_aux = (df.loc[:,['City', 'Time_taken(min)', 'Road_traffic_density']]
                .groupby(['City', 'Road_traffic_density'])
                .agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                      color='std_time', color_continuous_scale='RdBu',
                      color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

def avg_std_time_graph (df):
             
    df_aux = (df.loc[:,['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
        
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',
                                         x=df_aux['City'],
                                         y=df_aux['avg_time'],
                                         error_y=dict( type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_delivery(df, festival, op):
    """
    Esta função calcula o tempo médio e o desvio padrão do tempo de entrega.
    Parâmetros:
    Input:
        - df: Dataframe com os dados necessários para o cálculo
        - festival: Yes (com festival) ou No (sem festival)
        - op: Tipo de operação que precisa ser calculada
            'avg_time': calcula o tempo médio
            'std_time': calcula o desvio padrão do tempo.
    Output:
        - df: Dataframe com 2 colunas e 2 linha
    """
    df_aux = (df.loc[:,['Time_taken(min)', 'Festival']]
                .groupby('Festival')
                .agg({'Time_taken(min)':['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op],2)
    return df_aux

def distance(df, fig):

    if fig == False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        
        df['distance'] = (df.loc[:,cols]
                            .apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                         (x['Delivery_location_latitude'], x['Delivery_location_longitude'] )),
                                    axis = 1))
        
        avg_distance = np.round(df['distance'].mean(), 2)
        return avg_distance
    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        
        df['distance'] = df.loc[:,cols].apply( lambda x:
                                        haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                   (x['Delivery_location_latitude'],x['Delivery_location_longitude'] )), axis = 1)

        avg_distance = df.loc[:,['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data=[go.Pie(labels = avg_distance['City'], values=avg_distance['distance'],pull=[0,0.1,0])])
        return fig

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

st.header('Marketplace - Visão Restaurantes')

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
    st.title("Overall Metrics")
    
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        delivery_unique = df['Delivery_person_ID'].nunique()
        col1.metric('Entregadores', delivery_unique)
        
    with col2:
        avg_distance = distance(df,fig = False)
        col2.metric('Distância Média', avg_distance)
                
    with col3:
        df_aux = avg_std_time_delivery(df, 'Yes', 'avg_time')
        col3.metric('Tempo Médio', df_aux)
        
    with col4:
        df_aux = avg_std_time_delivery(df, 'Yes', 'std_time')
        col4.metric('Desvio Padrão', df_aux)

    with col5:
        df_aux = avg_std_time_delivery(df, 'No', 'avg_time')
        col5.metric('Tempo Médio', df_aux)
        
    with col6:
        df_aux = avg_std_time_delivery(df, 'No', 'std_time')
        col6.metric('Desvio Padrão', df_aux)
    
with st.container():
    st.markdown("""---""")
    st.title("Tempo Médio de entrega por cidade")

    col1, col2 = st.columns(2)
    
    with col1:     
        fig = avg_std_time_graph (df)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        #4. O tempo médio e o desvio padrão de entrega por cidade e tipo de pedido.
        df_avg_std_delivery_time_city_type_of_order = (df.loc[:,['Time_taken(min)', 'City', 'Type_of_order']]
                                                     .groupby(['City','Type_of_order'])
                                                     .agg({'Time_taken(min)' : ['mean', 'std']}))
    
        #mudando o nome das colunas
        df_avg_std_delivery_time_city_type_of_order.columns = ['mean', 'std']
        #resetando o index
        df_avg_std_delivery_time_city_type_of_order = df_avg_std_delivery_time_city_type_of_order.reset_index()
        st.dataframe(df_avg_std_delivery_time_city_type_of_order)

with st.container():
    st.markdown("""---""")
    st.title("Distribuição do Tempo")

    col1, col2 = st.columns(2)
    with col1:
        fig = distance(df, fig=True)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = avg_std_time_on_traffic(df)
        st.plotly_chart(fig, use_container_width=True)
        
        


    