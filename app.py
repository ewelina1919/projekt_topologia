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
 
# --- INICJALIZACJA PAMIĘCI ---
if 'f_str' not in st.session_state:
    st.session_state.f_str = "x**2 + y**2"
    st.session_state.a_val = 1.0
    st.session_state.b_val = 4.0
    st.session_state.x_val = 0.0
    st.session_state.y_val = 1.5
    st.session_state.last_preset = "-- Własny wzór --"
    st.session_state.lb = "["
    st.session_state.rb = "]"
 
# --- PANEL BOCZNY: PARAMETRY ---
with st.sidebar:
    st.header("Parametry przestrzeni")
    wybrany = st.selectbox("Gotowe przykłady:", ["-- Własny wzór --"] + list(przykłady.keys()))
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
    st.subheader("Zbiór A")
    # DODANA OBSŁUGA NIESKOŃCZONOŚCI Z CHECKBOXAMI
    col_lb, col_a, col_b, col_rb = st.columns([1, 2, 2, 1])
    with col_lb:
        lb_ui = st.selectbox("Od", ["[", "("], key="lb")
    with col_a:
        is_inf_a = st.checkbox("-∞", key="inf_a")
        a_val_ui = st.number_input("Początek [a]", step=0.1, key="a_val", disabled=is_inf_a)
    with col_b:
        is_inf_b = st.checkbox("+∞", key="inf_b")
        b_val_ui = st.number_input("Koniec [b]", step=0.1, key="b_val", disabled=is_inf_b)
    with col_rb:
        rb_ui = st.selectbox("Do", ["]", ")"], key="rb")
 
    lb = "(" if is_inf_a else lb_ui
    rb = ")" if is_inf_b else rb_ui
    a_val = -np.inf if is_inf_a else a_val_ui
    b_val = np.inf if is_inf_b else b_val_ui
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
left_cond = (f_point > a_val) if lb == '(' else (f_point >= a_val)
right_cond = (f_point < b_val) if rb == ')' else (f_point <= b_val)
is_in_A = left_cond and right_cond
 
col_wynik, col_wykres = st.columns([1, 2])
 
with col_wynik:
    st.subheader("Sprawdzenie przynależności")
    st.markdown("**Funkcja:**")
    st.latex(rf"f(x,y) = {f_latex}")
    st.markdown("**Zbiór:**")
    # Ładne wyświetlanie nieskończoności w LaTeX
    a_tex = "-\\infty" if is_inf_a else f"{a_val}"
    b_tex = "\\infty" if is_inf_b else f"{b_val}"
    st.latex(rf"A = {lb}{a_tex}, {b_tex}{rb}")
    st.markdown("---")
    st.markdown("### Obliczenia:")
    st.info(f"Wartość funkcji w punkcie: \n\n$f({x_val}, {y_val}) = {f_point:.4f}$")
    if is_in_A:
        st.success(f"**Wniosek:** Punkt $({x_val}, {y_val})$ **należy** do przeciwobrazu $f^{{-1}}(A)$.")
        st.caption(f"Uzasadnienie: Wartość {f_point:.4f} zawiera się w przedziale ${lb}{a_tex}, {b_tex}{rb}$.")
    else:
        st.error(f"**Wniosek:** Punkt $({x_val}, {y_val})$ **nie należy** do przeciwobrazu $f^{{-1}}(A)$.")
        st.caption(f"Uzasadnienie: Wartość {f_point:.4f} leży poza przedziałem ${lb}{a_tex}, {b_tex}{rb}$.")
 
with col_wykres:
    grid_limit = max(6.0, abs(x_val) * 1.5, abs(y_val) * 1.5)
    x_grid = np.linspace(-grid_limit, grid_limit, 501)
    y_grid = np.linspace(-grid_limit, grid_limit, 501)
    X, Y = np.meshgrid(x_grid, y_grid)
    Z = evaluate_fast(X, Y)
    if np.isscalar(Z):
         Z = np.full_like(X, Z)
 
    fig = go.Figure()
 
    # --- PERFEKCYJNE RYSOWANIE TOPOLOGICZNE (BEZ ZEPSUTYCH TŁÓW) ---
    if a_val == b_val and not is_inf_a and not is_inf_b:
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
        # Wycina wszystko, co jest poza przedziałem A, zostawiając czystą figurę
        mask_left = (Z > a_val) if lb == '(' else (Z >= a_val)
        mask_right = (Z < b_val) if rb == ')' else (Z <= b_val)
        Z_masked = np.where(mask_left & mask_right, Z, np.nan)
        fig.add_trace(go.Contour(
            z=Z_masked, x=x_grid, y=y_grid,
            colorscale=[[0, 'rgba(59, 130, 246, 0.5)'], [1, 'rgba(59, 130, 246, 0.5)']],
            showscale=False,
            name="Przeciwobraz (obszar)", 
            showlegend=True,
            hoverinfo='skip',
            contours=dict(showlines=False)
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
            bgcolor="white",
            bordercolor="black",
            borderwidth=1,
            font=dict(color="black"),
            itemclick=False,
            itemdoubleclick=False
        )
    )
    st.plotly_chart(fig, use_container_width=True)
