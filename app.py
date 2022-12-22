import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy as db
import folium
import streamlit_folium
import json

engine = db.create_engine("sqlite:///db.sqlite")
connection = engine.connect()

df = pd.read_csv("df_table_lositem.csv")
with open("departements.geojson") as mon_fichier:
    geo = json.load(mon_fichier)



df_join = pd.read_csv("df_join.csv")
df_join['date'] = pd.to_datetime(df_join['date'])
df_dep_voy = pd.read_csv("df_dep_voy.csv")


tab1,tab2,tab3 = st.tabs(["Question n°1","Question n°2","Question n°3"])





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
    df_dep.rename(columns = {'departement':'nombre_objet_perdue'}, inplace = True)
    mask_objet =st.selectbox("Choisissez un type d'objet",df_dep["type_objet"].unique(),key='quest3objet')
    mask_date =st.selectbox("Choisissez une annee",df_dep["date"].dt.year.unique(),key='quest3year')
    
    def chose_year(year):
        if year == 2016:
            return "SUM(total_voyageurs_2016)"
        if year == 2017:
            return "SUM(total_voyageurs_2017)"
        if year == 2018:
            return "SUM(total_voyageurs_2018)"
        if year == 2019:
            return "SUM(total_voyageurs_2019)"
        if year == 2020:
            return "SUM(total_voyageurs_2020)"
        if year == 2021:
            return "SUM(total_voyageurs_2021)"

    
    new_df=df_dep[(df_dep["date"].dt.year==int(mask_date)) & (df_dep["type_objet"] == mask_objet)]
    merge = pd.merge(new_df, df_dep_voy,on="code_departement")
    merge["nombre_objet_perdue"] = round(merge["nombre_objet_perdue"] / (merge[chose_year(mask_date)]/1000000),6)
    
    
    france = folium.Map(location = [46.763656, 2.429795], zoom_start = 5)

    folium.Choropleth(
        geo_data=geo,
        name="France departements",
        data=merge,
        columns=["code_departement","nombre_objet_perdue"],
        key_on="feature.properties.code",
        fill_color="YlGn",
        fill_opacity=0.7,
        line_opacity=.1,
        legend_name=f"Nombre d'objet de type {mask_objet} perdue en {mask_date} par million de voyageurs",
    ).add_to(france)

    streamlit_folium.st_folium(france)

        