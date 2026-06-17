import streamlit as st
import numpy as np
import sympy as sp
import plotly.graph_objects as go

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Topologia: Przeciwobraz", layout="wide", initial_sidebar_state="expanded")

# --- STYLE I UI ---
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1E3A8A; margin-bottom: 0rem; }
    .sub-header { font-size: 1.2rem; color: #4B5563; margin-bottom: 2rem; }
    .math-box { background-color: #F3F4F6; padding: 1rem; border-radius: 8px; border-left: 5px solid #3B82F6; }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">Topologiczny analizator przeciwobrazów</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Interaktywna wizualizacja zbioru $f^{-1}(A)$ z użyciem SymPy i Plotly.</p>', unsafe_allow_html=True)

# --- INICJALIZACJA ZMIENNYCH SYMBOLICZNYCH ---
x_sym, y_sym = sp.symbols('x y')

# --- PANEL BOCZNY: PARAMETRY ---
with st.sidebar:
    st.header("⚙️ Parametry przestrzeni")
    
    st.markdown("**1. Odwzorowanie ciągłe**")
    f_str = st.text_input("Wzór f(x, y)", value="sin(x) + cos(y)", 
                          help="Używaj naturalnej składni, np. sin(x), exp(y), x**2. Nie dodawaj 'np.'!")
    
    st.markdown("---")
    st.markdown("**2. Zbiór domknięty A**")
    col_a, col_b = st.columns(2)
    with col_a:
        a_val = st.number_input("Początek [a]", value=-0.5, step=0.1)
    with col_b:
        b_val = st.number_input("Koniec [b]", value=0.5, step=0.1)
        
    st.markdown("---")
    st.markdown("**3. Punkt testowy**")
    col_x, col_y = st.columns(2)
    with col_x:
        x_val = st.number_input("Współrzędna x", value=0.0, step=0.5)
    with col_y:
        y_val = st.number_input("Współrzędna y", value=0.0, step=0.5)

# Zabezpieczenie przed błędem logicznym w topologii
if a_val > b_val:
    st.error("Błąd topologiczny: Przedział A=[a, b] jest zdegenerowany. Wartość 'a' musi być mniejsza lub równa 'b'.")
    st.stop()

# --- PARSOWANIE I EWALUACJA MATEMATYCZNA (SYMPY) ---
try:
    # Konwersja stringa na wyrażenie symboliczne (całkowicie bezpieczne)
    expr = sp.sympify(f_str, evaluate=False)
    # Konwersja wyrażenia na szybką funkcję NumPy
    f_num = sp.lambdify((x_sym, y_sym), expr, "numpy")
    
    # Wyliczenie wartości w badanym punkcie
    f_point = float(f_num(x_val, y_val))
    
except Exception as e:
    st.error(f"Nie udało się sparsować wzoru funkcji. Sprawdź poprawność zapisu matematycznego. Szczegóły błędu: {e}")
    st.stop()

# --- LOGIKA TWIERDZENIA ---
is_in_A = a_val <= f_point <= b_val

# --- INTERFEJS GŁÓWNY: WYNIKI ---
col_wynik, col_wykres = st.columns([1, 2])

with col_wynik:
    st.subheader("Orzeczenie analityczne")
    
    # Wyświetlanie sformatowanej matematyki w LaTeX
    latex_expr = sp.latex(expr)
    st.latex(r"f(x,y) = " + latex_expr)
    st.latex(rf"A = [{a_val}, {b_val}]")
    
    st.markdown("### Wynik obliczeń:")
    st.latex(rf"f({x_val}, {y_val}) = {f_point:.4f}")
    
    if is_in_A:
        st.success(f"Prawda! Punkt ({x_val}, {y_val}) należy do przeciwobrazu.")
        st.markdown(f'<div class="math-box">Ponieważ wartość {f_point:.4f} zawiera się w przedziale [{a_val}, {b_val}], orzekamy że <b>$(x,y) \in f^{{-1}}(A)$</b>. Ze względu na ciągłość odwzorowania $f$, przeciwobraz zbioru domkniętego $A$ jest zbiorem domkniętym.</div>', unsafe_allow_html=True)
    else:
        st.error(f"Fałsz! Punkt ({x_val}, {y_val}) leży poza przeciwobrazem.")
        st.markdown(f'<div class="math-box">Ponieważ wartość {f_point:.4f} nie zawiera się w przedziale [{a_val}, {b_val}], orzekamy że <b>$(x,y) \\notin f^{{-1}}(A)$</b>.</div>', unsafe_allow_html=True)

# --- GENEROWANIE INTERAKTYWNEGO WYKRESU (PLOTLY) ---
with col_wykres:
    st.subheader("Wizualizacja płaszczyzny $\mathbb{R}^2$")
    
    # Gęsta siatka dla wyeliminowania artefaktów (600x600 punktów)
    grid_limit = max(10.0, abs(x_val) * 1.5, abs(y_val) * 1.5)
    x_grid = np.linspace(-grid_limit, grid_limit, 600)
    y_grid = np.linspace(-grid_limit, grid_limit, 600)
    X, Y = np.meshgrid(x_grid, y_grid)
    
    # Obliczenie wartości funkcji na siatce (wektoryzacja NumPy)
    Z = f_num(X, Y)
    
    # Zabezpieczenie przed funkcjami stałymi
    if np.isscalar(Z):
        Z = np.full_like(X, Z)

    # Tworzenie wykresu
    fig = go.Figure()

    # Rysowanie przeciwobrazu
    if a_val == b_val:
        # Przeciwobraz punktu - rysujemy poziomicę
        fig.add_trace(go.Contour(
            z=Z, x=x_grid, y=y_grid,
            contours=dict(start=a_val, end=a_val, size=1),
            line_width=3,
            colorscale=[[0, 'blue'], [1, 'blue']],
            showscale=False,
            name="Przeciwobraz $f^{-1}(A)$"
        ))
    else:
        # Przeciwobraz przedziału - maska obszaru
        # Tworzymy dyskretną maskę binarną
        mask = np.logical_and(Z >= a_val, Z <= b_val).astype(float)
        # Zamiana 0 na NaN, aby tło było całkowicie przezroczyste i czyste
        mask[mask == 0] = np.nan 
        
        fig.add_trace(go.Contour(
            z=mask, x=x_grid, y=y_grid,
            contours_coloring='heatmap',
            colorscale=[[0, 'rgba(59, 130, 246, 0.4)'], [1, 'rgba(59, 130, 246, 0.6)']], # Estetyczny niebieski
            showscale=False,
            hoverinfo='skip',
            name="Przeciwobraz $f^{-1}(A)$"
        ))
        # Dodanie ostrych krawędzi ograniczających zbiór
        fig.add_trace(go.Contour(
            z=Z, x=x_grid, y=y_grid,
            contours=dict(start=a_val, end=b_val, size=b_val - a_val),
            contours_coloring='lines',
            line_width=1.5,
            colorscale=[[0, 'black'], [1, 'black']],
            showscale=False,
            hoverinfo='skip'
        ))

    # Nanoszenie punktu testowego
    marker_color = '#10B981' if is_in_A else '#EF4444' # Zielony jeśli prawda, czerwony jeśli fałsz
    fig.add_trace(go.Scatter(
        x=[x_val], y=[y_val],
        mode='markers+text',
        marker=dict(color=marker_color, size=12, line=dict(color='white', width=2)),
        text=[f"P({x_val}, {y_val})"],
        textposition="top right",
        textfont=dict(size=14, color='white' if not is_in_A else 'black'), # kontrast
        name="Badany punkt",
        hovertemplate=f"X: {x_val}<br>Y: {y_val}<br>Wartość f(x,y): {f_point:.4f}<extra></extra>"
    ))

    # Ustawienia układu i osi
    fig.update_layout(
        xaxis_title="Oś X",
        yaxis_title="Oś Y",
        xaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black', gridcolor='#E5E7EB'),
        yaxis=dict(zeroline=True, zerolinewidth=2, zerolinecolor='black', gridcolor='#E5E7EB', scaleanchor="x", scaleratio=1),
        plot_bgcolor='white',
        margin=dict(l=20, r=20, t=30, b=20),
        hovermode="closest",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01, bgcolor="rgba(255, 255, 255, 0.8)")
    )

    # Wyświetlenie interaktywnego wykresu
    st.plotly_chart(fig, use_container_width=True)
    
st.markdown("---")
st.caption("Aplikacja zaliczeniowa | Silnik renderujący: Plotly | Silnik algebraiczny: SymPy")
