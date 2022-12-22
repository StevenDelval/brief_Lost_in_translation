import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy as db
import folium
import streamlit_folium
import json

engine = db.create_engine("sqlite:///db.sqlite")
connection = engine.connect()

df = pd.read_sql_table(table_name="LostItem",con=engine)
with open("departements.geojson") as mon_fichier:
    geo = json.load(mon_fichier)

sql=""" 
SELECT * FROM LostItem
JOIN Gare ON LostItem.code_uic_gare_origine = Gare.code_uic
JOIN Frequentation on Frequentation.code_uic = LostItem.code_uic_gare_origine

"""

df_join = pd.read_sql(sql,con=engine)
df_join['date'] = pd.to_datetime(df_join['date'])

tab1,tab2,tab3 = st.tabs(["Question n°1","Question n°2","Question n°3"])
st.markdown("<style>#map_div{width:100%;}</style>",unsafe_allow_html=True)


with tab1:


    df['date'] = pd.to_datetime(df['date']) - pd.to_timedelta(7, unit='d')
    df_semaine= pd.DataFrame(df.groupby([pd.Grouper(key='date', freq='W')])["type_objet"].count())

    fig, ax = plt.subplots()
    ax.hist(df_semaine,bins=30,color = "#45d4a1", ec="red",lw=2)


    st.pyplot(fig)
with tab2:
    df_semaine_type= pd.DataFrame(df[['date',"type_objet",'id']].groupby([pd.Grouper(key='date', freq='M'),"type_objet"]).count().reset_index().set_index("date"))
    df_semaine_type.rename(columns = {'id':'count_objet_mois'}, inplace = True)
    mask_objet =st.selectbox("Choisissez un type d'objet",df_semaine_type["type_objet"].unique())
    if st.button("Cree le graphique"):
        
        st.line_chart(df_semaine_type[df_semaine_type["type_objet"]==mask_objet]["count_objet_mois"])



with tab3:

    df_dep= pd.DataFrame(df_join[['code_departement','type_objet',"date",'departement']].groupby(['code_departement',pd.Grouper(key='date', freq='Y'),'type_objet']).count().reset_index())
    
    mask_objet =st.selectbox("Choisissez un type d'objet",df_dep["type_objet"].unique(),key='quest3objet')
    mask_date =st.selectbox("Choisissez une annee",df_dep["date"].dt.year.unique(),key='quest3year')
    
    
    
    france = folium.Map(location = [46.763656, 2.429795], zoom_start = 5)

    folium.Choropleth(
        geo_data=geo,
        name="France departements",
        data=df_dep[(df_dep["date"].dt.year==int(mask_date)) & (df_dep["type_objet"] == mask_objet)],
        columns=["code_departement","departement"],
        key_on="feature.properties.code",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=.1,
        legend_name=f"Nombre d'objet de type {mask_objet} perdue en {mask_date}",
    ).add_to(france)

    streamlit_folium.st_folium(france)

        