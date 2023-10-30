import streamlit as st
import pandas as pd
import requests
import io
import altair as alt
import seaborn as sns
import geopandas as gpd
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import Viridis256
from bokeh.io import output_notebook
import time 
import numpy as np



# Fonction pour charger les données
@st.cache_data  # Cette annotation permet de mettre en cache les données, afin de ne pas les recharger à chaque
def load_data(url):
    """Charge les données depuis une URL"""
    try:
        data = pd.read_csv(url, delimiter=";")
        
        return data
    except Exception as e:
        st.write("Une erreur est survenue lors du chargement des données.")
        st.write(e)
        return None


# Fonction principale de l'application Streamlit
def main():
    
    
    st.markdown("""
        <div style='text-align:center'>
            <h1>
                <span>Quelle est la situation des logements en France ?</span>
                <img src='https://cdn.pixabay.com/photo/2013/07/12/12/56/home-146585_1280.png' alt='Logo' style='width:50px; vertical-align: middle; margin-left: 10px;'>
            </h1>
        </div>
    """, unsafe_allow_html=True)

  
   

   # Utilisation de la fonction
    url = "https://www.data.gouv.fr/fr/datasets/r/bf82e99f-cb74-48e6-b49f-9a0da726d5dc"
   
    data = load_data(url)
   
#### Mes Infos

    

    st.sidebar.markdown("## Mes Informations")
    st.sidebar.markdown("Anna Meliz")
    st.sidebar.markdown("#datavz2023efrei")
    st.sidebar.markdown("[LinkedIn](https://www.linkedin.com/in/annameliz/)")
    

    
    

    

    st.write("---")
    #################
    import geopandas as gpd
    from bokeh.models import (ColorBar, ColumnDataSource, HoverTool, LinearColorMapper, Slider, GeoJSONDataSource, Select)
    from bokeh.plotting import figure
    from bokeh.layouts import column
    from bokeh.palettes import YlGnBu as palette

    ###########################

#Vis 1 et 2##################""

# Charger les données
    france_map = gpd.read_file("departements.geojson")
    data['departement'] = data['code_departement']

    # Fusionner les données avec la carte
    merged = france_map.set_index('code').join(data.set_index('departement'))

    # Créer une source de données pour Bokeh
    geosource = GeoJSONDataSource(geojson=merged.to_json())

    # Créer une figure
    p = figure(title="Heatmap", x_axis_location=None, y_axis_location=None )
    p.patches('xs', 'ys', source=geosource, fill_alpha=1, line_color="white", line_width=0.5)

    #Préision du département
    hover = HoverTool()
    hover.tooltips = [("Département", "@nom")]
    p.add_tools(hover)

    # Mapper pour la couleur
    mapper = LinearColorMapper(palette=palette[9][::-1])

    # Color bar
    color_bar = ColorBar(color_mapper=mapper, label_standoff=12, location=(0,0), title='Logements')
    p.add_layout(color_bar, 'right')

    #titre 
    st.markdown("<div style='text-align:center'><h3>Choisissez votre Heatmap</h3></div>", unsafe_allow_html=True)

    # Widgets
    option = st.selectbox("Option :", ["Le taux de logements vacants en France", "Le nombre de logements sociaux en France"])  

    if option == 'Le nombre de logements sociaux en France':
        p.patches('xs', 'ys', source=geosource, fill_color={'field':'parc_social_nombre_de_logements', 'transform':mapper}, line_color="white", line_width=0.5)
    else:
        p.patches('xs', 'ys', source=geosource, fill_color={'field':'taux_de_logements_vacants_en', 'transform':mapper}, line_color="white", line_width=0.5)

    st.bokeh_chart(p)


    st.write('---')

#VISU 3##############

    st.markdown("<div style='text-align:center'><h3>Densité de les logements sociaux</h3></div>", unsafe_allow_html=True)
    # Préparation des données pour le KDE interne
    ages = data['parc_social_age_moyen_du_parc_en_annees'].dropna()  # Suppression des valeurs NaN
    hist_values = np.histogram(ages, bins=100, density=True)
    df_age_density = pd.DataFrame({
        'Âge moyen du parc social (en années)': 0.5*(hist_values[1][1:] + hist_values[1][:-1]),
        'Densité': hist_values[0]
    })

    # Affichage du KDE avec Streamlit
    st.area_chart(df_age_density, x='Âge moyen du parc social (en années)', y='Densité', use_container_width=True)
    
##########################
    ####titre avant le menu déroulant
    st.write('---')
    st.markdown("<div style='text-align:center'><h3>Choisissez un département</h3></div>", unsafe_allow_html=True)
    
    # Créer le MENU déroulant pour choisir un département
    departement_choisi = st.selectbox('Option :', data['nom_departement'].unique())

    # Filtrer les données selon le département choisi
    df_filtre = data[data['nom_departement'] == departement_choisi]
    

##############################

#Vis 4#################
    st.write('---')
    st.markdown("<div style='text-align:center'><h3>Le nombre d'habitants en fonction des années</h3></div>", unsafe_allow_html=True)
    chart = alt.Chart(df_filtre).mark_line().encode(
        x=alt.X('annee_publication:O', title='Année de publication', axis=alt.Axis(tickCount=len(data['annee_publication'].unique()))),
        y=alt.Y('nombre_d_habitants:Q', title="Nombre d'habitants", scale=alt.Scale(zero=False))
    ).properties(
        width=600,
        height=400

    )
    

    st.altair_chart(chart)


#############################

#Vis 5 piechart########

    st.write('---')
    st.markdown("<div style='text-align:center'><h3>Répartition des résidences</h3></div>", unsafe_allow_html=True)
    df_filtre = data[data['nom_departement'] == departement_choisi]
    
    # Calculer le nombre total de résidences principales et autres types de logements
    nombre_residences_principales = df_filtre['nombre_de_residences_principales'].sum()
    nombre_autres_logements = df_filtre['nombre_de_logements'].sum() - nombre_residences_principales

    # Préparer les données pour le pie chart
    labels = ['Résidences principales', 'Autres logements']
    sizes = [nombre_residences_principales, nombre_autres_logements]

    # Créer le pie chart
    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, startangle=90, autopct='%1.1f%%')
    ax.axis('equal')  # Pour assurer que le pie est dessiné en cercle.


    # Afficher le pie chart dans Streamlit
    st.pyplot(fig)

####################

####Vis 6
    
    # Convertir les années en entiers
    df_filtre['annee_publication'] = df_filtre['annee_publication'].astype(int)

    # Grouper par année et sommer le nombre de logements construits pour chaque année
    df_construction_annee = df_filtre.groupby('annee_publication')['construction'].sum().reset_index()
    st.write('---')
    # Afficher le titre sur la page Streamlit en utilisant markdown
    st.markdown("<div style='text-align:center'><h3>Nombre de logements construits par année</h3></div>", unsafe_allow_html=True)
    # Utilisation de seaborn pour créer le graphique
    plt.figure(figsize=(10,6))
    sns.lineplot(data=df_construction_annee, x='annee_publication', y='construction')
    plt.xticks(df_construction_annee['annee_publication'].unique())  # Définir les ticks de l'axe x pour montrer uniquement les années présentes dans le dataframe
    plt.xlabel('Années')
    plt.ylabel('Construction')

    plt.tight_layout()

    st.pyplot(plt)


###Visu 7#############
     #Histogramme du nombre moyen annuel de nouvelles constructions sur 10 ans par département
    st.write('---')
    st.markdown("<div style='text-align:center'><h3>Le nombre moyen annuel de nouvelles constructions sur 10 ans par département</h3></div>", unsafe_allow_html=True)
   
    st.bar_chart(data.groupby("nom_departement")["moyenne_annuelle_de_la_construction_neuve_sur_10_ans"].mean())


    










if __name__ == "__main__":
    main()


