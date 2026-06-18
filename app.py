dj eluwina
djeluwina
Niewidoczny

WrObeL
 rozpoczął(-ęła) rozmowę, która trwała 23 minuty. — 27.03.2023, 23:51
WrObeL
 rozpoczął(-ęła) rozmowę, która trwała 33 minuty. — 29.04.2024, 22:56
WrObeL
 rozpoczął(-ęła) rozmowę, która trwała 24 minuty. — 2.06.2024, 11:35
dj eluwina — 19:14
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import re

# --- KONFIGURACJA STRONY ---

message.txt
7 KB
﻿
WrObeL
wrobel889
 
import streamlit as st
import numpy as np
import plotly.graph_objects as go
import re

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Topologia: Przeciwobraz", layout="wide")

st.title("Wizualizacja przeciwobrazu funkcji")
st.markdown("Interaktywne badanie zbioru $f^{-1}(A)$ dla odwzorowania ciągłego $f: \mathbb{R}^2 \\rightarrow \mathbb{R}$.")

# --- GOTOWE PRZYKŁADY (PRESETY) ---
przykłady = {
    "Okrąg (Zbiór ograniczony)": {"f": "x**2 + y**2", "a": 1.0, "b": 4.0, "x": 0.0, "y": 1.5},
    "Pierścień (Brak jednospójności)": {"f": "x**2 + y**2", "a": 2.0, "b": 5.0, "x": 0.0, "y": 0.0},
    "Siodło (Obszary rozłączne)": {"f": "x**2 - y**2", "a": 1.0, "b": 3.0, "x": 2.0, "y": 0.0},
    "Przecięcie prostych (Zbiór osobliwy)": {"f": "x * y", "a": 0.0, "b": 0.0, "x": 0.0, "y": 3.0},
    "Lemniskata (Krzywa nieskończoności)": {"f": "(x**2 + y**2)**2 - 2*(x**2 - y**2)", "a": 0.0, "b": 0.0, "x": 1.0, "y": 0.0},
    "Fale (Nieskończenie wiele składowych)": {"f": "sin(x) * cos(y)", "a": 0.5, "b": 1.0, "x": 1.5, "y": 0.0}
}

# --- INICJALIZACJA PAMIĘCI (ROZWIĄZUJE PROBLEM BLOKADY WPISYWANIA) ---
if 'f_str' not in st.session_state:
    st.session_state.f_str = "x**2 + y**2"
    st.session_state.a_val = 1.0
    st.session_state.b_val = 4.0
    st.session_state.x_val = 0.0
    st.session_state.y_val = 1.5
    st.session_state.last_preset = "-- Własny wzór --"

# --- PANEL BOCZNY: PARAMETRY ---
with st.sidebar:
    st.header("Parametry przestrzeni")
    
    wybrany = st.selectbox("Gotowe przykłady:", ["-- Własny wzór --"] + list(przykłady.keys()))
    
    # Ładuje wartości z presetów tylko w momencie kliknięcia (zmiany w menu)
    if wybrany != st.session_state.last_preset:
        st.session_state.last_preset = wybrany
        if wybrany != "-- Własny wzór --":
            p = przykłady[wybrany]
            st.session_state.f_str = p["f"]
            st.session_state.a_val = float(p["a"])
            st.session_state.b_val = float(p["b"])
            st.session_state.x_val = float(p["x"])
            st.session_state.y_val = float(p["y"])

    f_str = st.text_input("Wzór funkcji f(x, y)", key="f_str")
    
    st.markdown("---")
    st.subheader("Zbiór domknięty A = [a, b]")
    col_a, col_b = st.columns(2)
    with col_a:
        a_val = st.number_input("Początek [a]", step=0.1, key="a_val")
    with col_b:
        b_val = st.number_input("Koniec [b]", step=0.1, key="b_val")
        
    st.markdown("---")
    st.subheader("Punkt badany (x, y)")
    col_x, col_y = st.columns(2)
    with col_x:
        x_val = st.number_input("Współrzędna x", step=0.5, key="x_val")
    with col_y:
        y_val = st.number_input("Współrzędna y", step=0.5, key="y_val")

if a_val > b_val:
    st.error("Błąd topologiczny: Przedział A musi być poprawny (wartość 'a' nie może być większa od 'b').")
    st.stop()

# --- ULTRASZYBKI SILNIK OBLICZENIOWY ---
safe_dict = {k: getattr(np, k) for k in dir(np) if not k.startswith('_')}
f_str_clean = re.sub(r'\^', '**', f_str)
f_latex = f_str.replace('**', '^').replace('*', r' \cdot ')

def evaluate_fast(x_input, y_input):
    local_env = safe_dict.copy()
    local_env['x'] = x_input
    local_env['y'] = y_input
    try:
        return eval(f_str_clean, {"__builtins__": {}}, local_env)
    except Exception as e:
        return None

f_point = evaluate_fast(x_val, y_val)

if f_point is None:
    st.error("Nieprawidłowy wzór funkcji. Sprawdź składnię.")
    st.stop()

# --- WYNIKI ---
is_in_A = a_val <= f_point <= b_val

col_wynik, col_wykres = st.columns([1, 2])

with col_wynik:
    st.subheader("Sprawdzenie przynależności")
    st.markdown("**Funkcja:**")
    st.latex(rf"f(x,y) = {f_latex}")
    st.markdown("**Zbiór:**")
    st.latex(rf"A = [{a_val}, {b_val}]")
    
    st.markdown("---")
    st.markdown("### Obliczenia:")
    st.info(f"Wartość funkcji w punkcie: \n\n$f({x_val}, {y_val}) = {f_point:.4f}$")
    
    if is_in_A:
        st.success(f"**Wniosek:** Punkt $({x_val}, {y_val})$ **należy** do przeciwobrazu $f^{{-1}}(A)$.")
        st.caption(f"Uzasadnienie: Wartość {f_point:.4f} zawiera się w przedziale domkniętym $[{a_val}, {b_val}]$.")
    else:
        st.error(f"**Wniosek:** Punkt $({x_val}, {y_val})$ **nie należy** do przeciwobrazu $f^{{-1}}(A)$.")
        st.caption(f"Uzasadnienie: Wartość {f_point:.4f} leży poza przedziałem domkniętym $[{a_val}, {b_val}]$.")

with col_wykres:
    grid_limit = max(6.0, abs(x_val) * 1.5, abs(y_val) * 1.5)
    x_grid = np.linspace(-grid_limit, grid_limit, 501)
    y_grid = np.linspace(-grid_limit, grid_limit, 501)
    X, Y = np.meshgrid(x_grid, y_grid)
    
    Z = evaluate_fast(X, Y)
    if np.isscalar(Z):
         Z = np.full_like(X, Z)

    fig = go.Figure()

    # --- PERFEKCYJNE RYSOWANIE TOPOLOGICZNE ---
    if a_val == b_val:
        fig.add_trace(go.Contour(
            z=Z, x=x_grid, y=y_grid,
            contours=dict(type='constraint', operation='=', value=a_val),
            line=dict(color='#2563EB', width=3),
            showscale=False,
            name="Przeciwobraz (krzywa)", 
            showlegend=True,
            hoverinfo='skip'
        ))
    else:
        fig.add_trace(go.Contour(
            z=Z, x=x_grid, y=y_grid,
            contours=dict(type='constraint', operation='[]', value=[a_val, b_val]),
            fillcolor='rgba(59, 130, 246, 0.5)', 
            line=dict(color='black', width=1.5),
            showscale=False,
            name="Przeciwobraz (obszar)", 
            showlegend=True,
            hoverinfo='skip'
        ))

    # Punkt
    fig.add_trace(go.Scatter(
        x=[x_val], y=[y_val],
        mode='markers',
        marker=dict(color='#10B981' if is_in_A else '#EF4444', size=14, line=dict(color='black', width=2)),
        name="Badany punkt",
        showlegend=True
    ))

    # --- NAPRAWIONA LEGENDA (CZYTELNY TEKST) ---
    fig.update_layout(
        height=600,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(zeroline=True, zerolinewidth=1, zerolinecolor='gray'),
        yaxis=dict(zeroline=True, zerolinewidth=1, zerolinecolor='gray', scaleanchor="x", scaleratio=1),
        plot_bgcolor='white',
        showlegend=True,
        legend=dict(
            yanchor="top", y=0.98, 
            xanchor="left", x=0.02,
            bgcolor="white",          # Twarde, białe tło
            bordercolor="black",      # Czarna ramka
            borderwidth=1,
            font=dict(color="black"), # Twardy czarny tekst (zapobiega zanikaniu w dark mode)
            itemclick=False,
            itemdoubleclick=False
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
message.txt
7 KB
