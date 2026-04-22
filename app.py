import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

#Miembros Equipo:
# Flores Bustos Karen
# Mexica Contreras Yaretzi
# Configuración de la página
st.set_page_config(page_title="Dashboard NBA", layout="wide")

# Carga de datos
@st.cache_data
def load_data():
    return pd.read_csv("nba_all_elo.csv")

df = load_data()

st.title("Análisis de Temporadas NBA")

st.sidebar.header("Filtros")

years = sorted(df['year_id'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Selecciona un año", years)

teams = sorted(df['fran_id'].unique())
selected_team = st.sidebar.selectbox("Selecciona un equipo", teams)

game_type = st.sidebar.pills(
    "Tipo de juego", 
    ["Todos", "Temporada Regular", "Playoffs"], 
    default="Todos"
)

filtered_df = df[(df['year_id'] == selected_year) & (df['fran_id'] == selected_team)].copy()

if game_type == "Temporada Regular":
    filtered_df = filtered_df[filtered_df['is_playoffs'] == 0]
elif game_type == "Playoffs":
    filtered_df = filtered_df[filtered_df['is_playoffs'] == 1]

filtered_df = filtered_df.sort_values('date_game')

# --- Lógica de cálculo ---
if not filtered_df.empty:
    filtered_df['win'] = (filtered_df['game_result'] == 'W').astype(int)
    filtered_df['loss'] = (filtered_df['game_result'] == 'L').astype(int)
    
    # Acumulados
    filtered_df['cum_wins'] = filtered_df['win'].cumsum()
    filtered_df['cum_losses'] = filtered_df['loss'].cumsum()
    
    # --- Visualización ---
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"Evolución de {selected_team} en {selected_year}")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=filtered_df['date_game'], y=filtered_df['cum_wins'], mode='lines', name='Victorias Acumuladas'))
        fig_line.add_trace(go.Scatter(x=filtered_df['date_game'], y=filtered_df['cum_losses'], mode='lines', name='Derrotas Acumuladas'))
        fig_line.update_layout(xaxis_title="Fecha", yaxis_title="Cantidad de Juegos")
        st.plotly_chart(fig_line, use_container_width=True)
        
    with col2:
        st.subheader("Distribución de Resultados")
        total_wins = filtered_df['win'].sum()
        total_losses = filtered_df['loss'].sum()
        
        fig_pie = px.pie(
            names=['Victorias', 'Derrotas'], 
            values=[total_wins, total_losses],
            color=['Victorias', 'Derrotas'],
            color_discrete_map={'Victorias':'green', 'Derrotas':'red'}
        )
        st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.warning("No hay datos disponibles para la combinación seleccionada.")
