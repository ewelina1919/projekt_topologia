import streamlit as st
import numpy as np
import plotly.graph_objects as go
import re

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Topologia: Przeciwobraz", layout="wide")

st.title("Wizualizacja przeciwobrazu funkcji")
# Używamy \rightarrow zamiast \to, żeby Streamlit się nie dławił i nie robił "o"
st.markdown("Interaktywne badanie zbioru $f^{-1}(A)$ dla odwzorowania ciągłego $f: \mathbb{R}^2 \\rightarrow \mathbb{R}$.")

# --- GOTOWE PRZYKŁADY (PRESETY) ---
przykłady = {
    "🛠️ Własny wzór...": {"f": "sin(x) + cos(y)", "a": -0.5, "b": 0.5, "x": 0.0, "y": 0.0},
    "🔵 Okrąg (Zbiór ograniczony)": {"f": "x**2 + y**2", "a": 1.0, "b": 4.0, "x": 0.0, "y": 1.5},
    "🐎 Siodło (Obszary rozłączne)": {"f": "x**2 - y**2", "a": 1.0, "b": 3.0, "x": 2.0, "y": 0.0},
    "🌊 Fale (Nieskończenie wiele składowych)": {"f": "sin(x) * cos(y)", "a": 0.5, "b": 1.0, "x": 1.5, "y": 0.0},
    "✖️ Przecięcie prostych (Zbiór osobliwy)": {"f": "x * y", "a": 0.0, "b": 0.0, "x": 0.0, "y": 3.0}
}

# --- PANEL BOCZNY: PARAMETRY ---
with st.sidebar:
    st.header("Parametry przestrzeni")
    
    wybrany_przyklad = st.selectbox("Wybierz gotowy przykład:", list(przykłady.keys()))
    p = przykłady[wybrany_przyklad]
    
    f_str = st.text_input("Wzór funkcji f(x, y)", value=p["f"])
    
    st.markdown("---")
    st.subheader("Zbiór domknięty A = [a, b]")
    col_a, col_b = st.columns(2)
    with col_a:
        a_val = st.number_input("Początek [a]", value=float(p["a"]), step=0.1)
    with col_b:
        b_val = st.number_input("Koniec [b]", value=float(p["b"]), step=0.1)
        
    st.markdown("---")
    st.subheader("Punkt badany (x, y)")
    col_x, col_y = st.columns(2)
    with col_x:
        x_val = st.number_input("Współrzędna x", value=float(p["x"]), step=0.5)
    with col_y:
        y_val = st.number_input("Współrzędna y", value=float(p["y"]), step=0.5)

if a_val > b_val:
    st.error("Błąd topologiczny: Przedział A musi być poprawny (wartość 'a' nie może być większa od 'b').")
    st.stop()

# --- ULTRASZYBKI SILNIK OBLICZENIOWY ---
safe_dict = {k: getattr(np, k) for k in dir(np) if not k.startswith('_')}
f_str_clean = re.sub(r'\^', '**', f_str)

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
    st.markdown(f"**Funkcja:** $f(x,y) = {f_str}$")
    st.markdown(f"**Zbiór:** $A = [{a_val}, {b_val}]$")
    
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
    x_grid = np.linspace(-grid_limit, grid_limit, 400)
    y_grid = np.linspace(-grid_limit, grid_limit, 400)
    X, Y = np.meshgrid(x_grid, y_grid)
    
    Z = evaluate_fast(X, Y)
    if np.isscalar(Z):
         Z = np.full_like(X, Z)

    fig = go.Figure()

    # Zoptymalizowane i wolne od artefaktów rysowanie (jedna warstwa!)
    if a_val == b_val:
        fig.add_trace(go.Contour(
            z=Z, x=x_grid, y=y_grid,
            contours=dict(start=a_val, end=a_val, size=1),
            line_width=3, colorscale=[[0, '#3B82F6'], [1, '#3B82F6']],
            showscale=False, name="Przeciwobraz"
        ))
    else:
        fig.add_trace(go.Contour(
            z=Z, x=x_grid, y=y_grid,
            contours=dict(
                start=a_val, 
                end=b_val, 
                size=b_val - a_val, # Gwarantuje wypełnienie całego przedziału
            ),
            colorscale=[[0, 'rgba(59, 130, 246, 0.4)'], [1, 'rgba(59, 130, 246, 0.4)']],
            line=dict(color='black', width=1.5), # Czarne ostre linie brzegowe bez szczelin
            showscale=False,
            hoverinfo='skip'
        ))

    # Punkt
    fig.add_trace(go.Scatter(
        x=[x_val], y=[y_val],
        mode='markers',
        marker=dict(color='#10B981' if is_in_A else '#EF4444', size=14, line=dict(color='black', width=2)),
        name=f"Punkt ({x_val}, {y_val})"
    ))

    fig.update_layout(
        height=600,
        margin=dict(l=10, r=10, t=30, b=10),
        xaxis=dict(zeroline=True, zerolinewidth=1, zerolinecolor='gray'),
        yaxis=dict(zeroline=True, zerolinewidth=1, zerolinecolor='gray', scaleanchor="x", scaleratio=1),
        plot_bgcolor='white',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
