import streamlit as st
import numpy as np
import plotly.graph_objects as go

# Konfiguracja strony
st.set_page_config(page_title="Topologia - Projekt", layout="wide")

st.title("Wizualizacja Powierzchni Topologicznych")
st.markdown("Projekt z Topologii | Matematyka Stosowana")

# --- SEKCJA MATEMATYCZNA (Z PAMIĘCIĄ PODRĘCZNĄ) ---
# Dekorator @st.cache_data sprawia, że jeśli parametry się nie zmienią, 
# Streamlit nie przelicza tego od nowa, co eliminuje zacinanie!

@st.cache_data
def generate_torus(R, r, resolution):
    u = np.linspace(0, 2 * np.pi, resolution)
    v = np.linspace(0, 2 * np.pi, resolution)
    U, V = np.meshgrid(u, v)
    
    X = (R + r * np.cos(V)) * np.cos(U)
    Y = (R + r * np.cos(V)) * np.sin(U)
    Z = r * np.sin(V)
    return X, Y, Z

@st.cache_data
def generate_mobius(radius, width, resolution):
    u = np.linspace(0, 2 * np.pi, resolution)
    v = np.linspace(-width/2, width/2, resolution)
    U, V = np.meshgrid(u, v)
    
    X = (radius + V * np.cos(U / 2)) * np.cos(U)
    Y = (radius + V * np.cos(U / 2)) * np.sin(U)
    Z = V * np.sin(U / 2)
    return X, Y, Z

# --- PANEL BOCZNY (INTERFEJS) ---
st.sidebar.header("Parametry")
shape = st.sidebar.selectbox("Wybierz powierzchnię:", ["Torus", "Wstęga Möbiusa"])

# Rozdzielczość: wyższa = gładszy (nieposzarpany) wykres, niższa = szybsze ładowanie
resolution = st.sidebar.slider("Rozdzielczość siatki (gładkość)", min_value=30, max_value=150, value=80, step=10)

# --- GENEROWANIE DANYCH W ZALEŻNOŚCI OD WYBORU ---
if shape == "Torus":
    st.sidebar.subheader("Parametry Torusa")
    R = st.sidebar.slider("Promień główny (R)", 1.0, 5.0, 3.0, 0.1)
    r = st.sidebar.slider("Promień rury (r)", 0.1, 2.0, 1.0, 0.1)
    X, Y, Z = generate_torus(R, r, resolution)
    colorscale = 'Viridis'

elif shape == "Wstęga Möbiusa":
    st.sidebar.subheader("Parametry Wstęgi")
    radius = st.sidebar.slider("Promień główny", 1.0, 5.0, 2.0, 0.1)
    width = st.sidebar.slider("Szerokość wstęgi", 0.5, 3.0, 1.0, 0.1)
    X, Y, Z = generate_mobius(radius, width, resolution)
    colorscale = 'Plasma'

# --- WIZUALIZACJA PLOTLY (SZYBKA I PŁYNNA) ---
fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale=colorscale)])

fig.update_layout(
    scene=dict(
        xaxis=dict(visible=False), # Ukrywamy osie dla lepszego efektu wizualnego
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        aspectmode='data' # Zachowuje proporcje matematyczne, żeby torus nie był spłaszczony
    ),
    margin=dict(l=0, r=0, b=0, t=0),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

# Wyświetlenie wykresu na całą szerokość kontenera
st.plotly_chart(fig, use_container_width=True)
