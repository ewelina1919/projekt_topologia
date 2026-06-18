import streamlit as st
import numpy as np
import plotly.graph_objects as go
import re
 
# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Topologia: Przeciwobraz", layout="wide")
st.title("Wizualizacja przeciwobrazu funkcji dwóch zmiennych")
 
# --- FUNKCJE POMOCNICZE ---
def parse_function(func_str, x, y):
    """Bezpieczna ewaluacja funkcji podanej jako string dla numpy."""
    # Podstawowe przekształcenia (np. ^ na **)
    func_str = func_str.replace('^', '**')
    # Dozwolone funkcje matematyczne
    allowed_dict = {
        'x': x, 'y': y,
        'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
        'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
        'abs': np.abs, 'pi': np.pi, 'e': np.e
    }
    try:
        # Obliczenie wartości funkcji (działa zarówno dla skalarów jak i macierzy)
        return eval(func_str, {"__builtins__": None}, allowed_dict)
    except Exception as e:
        return None
 
def check_inclusion(z, a, b, left_bracket, right_bracket):
    """Logika analityczna: sprawdza czy wartość Z mieści się w zadanym przedziale."""
    if z is None or np.isnan(z):
        return False
    # Lewy warunek
    if left_bracket == '(':
        left_cond = (z > a)
    else:  # '['
        left_cond = (z >= a)
    # Prawy warunek
    if right_bracket == ')':
        right_cond = (z < b)
    else:  # ']'
        right_cond = (z <= b)
    return left_cond and right_cond
 
# --- INTERFEJS UŻYTKOWNIKA ---
st.sidebar.header("1. Definicja funkcji")
f_str = st.sidebar.text_input("Wzór funkcji f(x, y):", value="x**2 + y**2")
st.sidebar.markdown("*Wskazówka: używaj standardowych notacji, np. `x**2 + y**2`, `sin(x) * y`.*")
 
st.sidebar.header("2. Definicja zbioru A")
col1, col2, col3, col4 = st.sidebar.columns([1, 2, 2, 1])
with col1:
    left_b = st.selectbox("Nawias", ['[', '('], key='lb')
with col2:
    a_val = st.number_input("Wartość a", value=1.0, step=0.5)
with col3:
    b_val = st.number_input("Wartość b", value=4.0, step=0.5)
with col4:
    right_b = st.selectbox("Nawias", [']', ')'], key='rb')
 
if a_val > b_val:
    st.sidebar.error("Błąd: Wartość 'a' nie może być większa niż 'b'!")
 
st.sidebar.header("3. Badany punkt (x, y)")
px_col, py_col = st.sidebar.columns(2)
with px_col:
    p_x = st.number_input("Współrzędna x", value=1.0, step=0.5)
with py_col:
    p_y = st.number_input("Współrzędna y", value=1.0, step=0.5)
 
# --- OBLICZENIA I WYNIKI ---
if a_val <= b_val:
    # 1. Orzekanie analityczne
    z_point = parse_function(f_str, p_x, p_y)
    st.subheader("Wynik analizy topologicznej punktu")
    if z_point is not None:
        is_in_set = check_inclusion(z_point, a_val, b_val, left_b, right_b)
        # Wyświetlenie matematycznego dowodu dla użytkownika
        set_A_str = f"{left_b}{a_val}, {b_val}{right_b}"
        st.write(f"Wartość funkcji w punkcie: $f({p_x}, {p_y}) = {z_point:.4f}$")
        if is_in_set:
            st.success(f"Punkt $({p_x}, {p_y})$ **NALEŻY** do przeciwobrazu $f^{{-1}}(A)$. Wartość ${z_point:.4f}$ zawiera się w zbiorze $A = {set_A_str}$.")
        else:
            st.error(f"Punkt $({p_x}, {p_y})$ **NIE NALEŻY** do przeciwobrazu $f^{{-1}}(A)$. Wartość ${z_point:.4f}$ nie zawiera się w zbiorze $A = {set_A_str}$.")
    else:
        st.error("Błąd w ewaluacji funkcji. Sprawdź poprawność wzoru.")
 
    # 2. Generowanie rysunku (wizualizacja na płaszczyźnie)
    st.subheader(f"Wizualizacja przeciwobrazu $f^{{-1}}(A)$ dla $A = {set_A_str}$")
    with st.spinner("Generowanie przestrzeni topologicznej..."):
        # Dyskretna siatka punktów (nieparzysta, aby trafić w 0,0)
        grid_size = 501
        x_range = np.linspace(-10, 10, grid_size)
        y_range = np.linspace(-10, 10, grid_size)
        X, Y = np.meshgrid(x_range, y_range)
        # Obliczanie wartości dla całej płaszczyzny
        Z = parse_function(f_str, X, Y)
        if Z is not None:
            # Tworzenie masek wektorowych dla widoku
            if left_b == '(':
                mask_left = (Z > a_val)
            else:
                mask_left = (Z >= a_val)
            if right_b == ')':
                mask_right = (Z < b_val)
            else:
                mask_right = (Z <= b_val)
            # Wycinanie odpowiedniego obszaru (resztę wypełniamy NaN, by Plotly zrobiło je przezroczyste)
            Z_masked = np.where(mask_left & mask_right, Z, np.nan)
            # Rysowanie w Plotly
            fig = go.Figure()
            if a_val == b_val:
                # Jeśli to konkretny punkt a=b, rysujemy same poziomice (linie)
                fig.add_trace(go.Contour(
                    z=Z, x=x_range, y=y_range,
                    contours=dict(start=a_val, end=a_val, size=0, coloring='lines'),
                    line_width=2, colorscale='Blues'
                ))
            else:
                # Jeśli to przedział, wypełniamy obszar
                fig.add_trace(go.Contour(
                    z=Z_masked, x=x_range, y=y_range,
                    colorscale='Viridis',
                    showscale=True,
                    connectgaps=False,
                    contours=dict(showlines=False)
                ))
            # Dodanie badanego punktu do wykresu
            fig.add_trace(go.Scatter(
                x=[p_x], y=[p_y],
                mode='markers+text',
                marker=dict(color='red', size=10, symbol='x'),
                name='Badany punkt',
                text=[f"({p_x}, {p_y})"],
                textposition="top right"
            ))
            fig.update_layout(
                xaxis_title="Oś X",
                yaxis_title="Oś Y",
                width=800,
                height=800,
                plot_bgcolor='rgba(0,0,0,0)' # Przezroczyste tło dla lepszego efektu
            )
            st.plotly_chart(fig, use_container_width=True)
            st.info("Pamiętaj: Wykres stanowi dyskretną aproksymację wizualną obszaru. Weryfikacja analityczna na górze strony posiada najwyższy priorytet topologiczny.")
