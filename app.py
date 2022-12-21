import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import sqlalchemy as db

engine = db.create_engine("sqlite:///db.sqlite")
connection = engine.connect()

df = pd.read_sql_table(table_name="LostItem",con=engine)
df['date'] = pd.to_datetime(df['date']) - pd.to_timedelta(7, unit='d')
df_semaine= pd.DataFrame(df.groupby([pd.Grouper(key='date', freq='W')])["type_objet"].count())

fig, ax = plt.subplots()
ax.hist(df_semaine,bins=30,color = "#45d4a1", ec="red",lw=2)


st.pyplot(fig)

df_semaine_type= pd.DataFrame(df[['date',"type_objet",'id']].groupby([pd.Grouper(key='date', freq='M'),"type_objet"]).count().reset_index().set_index("date"))
df_semaine_type.rename(columns = {'id':'count_objet_mois'}, inplace = True)
mask_objet =st.selectbox("Choisissez un type d'objet",df_semaine_type["type_objet"].unique())
if st.button("Cree le graphique"):
    
    st.line_chart(df_semaine_type[df_semaine_type["type_objet"]==mask_objet]["count_objet_mois"])
