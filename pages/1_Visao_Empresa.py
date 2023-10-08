
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

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

#-----------------------------------------#
# Funções
#-----------------------------------------#

def country_maps(df):
        
    columns = [
    'City',
    'Road_traffic_density',
    'Delivery_location_latitude',
    'Delivery_location_longitude'
    ]
        
    columns_groupby = ['City', 'Road_traffic_density']
    data_plot = df.loc[:, columns].groupby( columns_groupby ).median().reset_index()
        
    # Desenhar o mapa
    map = folium.Map( zoom_start=11 )
    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
        location_info['Delivery_location_longitude']],
        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
    folium_static(map, width=1024, height = 600)

def order_share_by_week(df):
    # 5. A quantidade de pedidos por entregador por semana.

    df_aux2 = df.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    df_aux1 = df.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()
            
    df_aux = pd.merge( df_aux1, df_aux2, how='inner' )
            
    df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    # gráfico
    fig = px.line( df_aux, x='week_of_year', y='order_by_delivery')
    
    return fig

def order_by_week(df):
            
    # 2. Quantidade de pedidos por semana.
    df['week_of_year'] = df['Order_Date'].dt.strftime('%U')    
    cols = ['ID', 'week_of_year']     
    df_aux = df.loc[:, cols].groupby(['week_of_year']).count().reset_index()
    df_aux.columns = ['week_of_year', 'ID']
    fig = px.line(df_aux, x='week_of_year', y='ID')

    return fig

def traffic_order_city(df):
                
    # 4. Comparação do volume de pedidos por cidade e tipo de tráfego.
    cols = ['ID', 'City', 'Road_traffic_density']
                
    df_aux = (df.loc[:, cols]
                .groupby(['City', 'Road_traffic_density'])
                .count()
                .reset_index())
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size = 'ID', color='City')
    
    return fig

def traffic_order_share(df):
            
# 3. Distribuição dos pedidos por tipo de tráfego.
    cols = ['ID', 'Road_traffic_density']
    df_aux = (df.loc[:, cols]
                .groupby(['Road_traffic_density'])
                .count()
                .reset_index())
    df_aux['perc_ID'] = df_aux['ID'] / df_aux['ID'].sum()
                    
    fig = px.pie(df_aux, values = 'perc_ID', names='Road_traffic_density')
                
    return fig

def order_metric (df):
    
    cols = ['ID', 'Order_Date']
    df_aux = df.loc[:, cols].groupby(['Order_Date']).count().reset_index()
    df_aux.columns = ['order_date', 'qtde_entregas']
                
    fig = px.bar(df_aux, x='order_date', y='qtde_entregas')

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

st.header('Marketplace - Visão Cliente')

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

tab1, tab2, tab3 = st.tabs (['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        
        # 1. Quantidade de pedidos por dia.
        fig = order_metric(df)
        st.markdown('# Orders by Day')
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            fig = traffic_order_share(df)
            st.header("Traffic Order Share")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = traffic_order_city(df)
            st.header("Traffic Order City")
            st.plotly_chart(fig, use_container_width=True)
            
with tab2:
    with st.container():
        st.markdown('# Orders by Week')
        fig = order_by_week(df)
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        st.markdown('# Orders Share by Week')
        fig = order_share_by_week(df)
        st.plotly_chart(fig, use_container_width=True)
         
with tab3:
    st.markdown("Country Maps")
    country_maps(df)

