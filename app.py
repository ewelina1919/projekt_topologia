import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

# Konfiguracja strony
st.set_page_config(page_title="Przeciwobraz funkcji", layout="wide")

st.title("Przeciwobraz funkcji $f^{-1}(A)$")
st.markdown("Aplikacja orzeka, czy dany punkt należy do przeciwobrazu oraz wykonuje rysunek.")

# --- PANEL BOCZNY (INTERFEJS) ---
st.sidebar.header("Parametry wejściowe")

# 1. Definicja funkcji
st.sidebar.subheader("1. Jawny wzór funkcji $f(x, y)$")
func_str = st.sidebar.text_input("Podaj wzór (np. x**2 + y**2, sin(x)*y):", value="x**2 + y**2")

# 2. Zbiór A
st.sidebar.subheader("2. Zbiór $A \subseteq \mathbb{R}$")

use_minus_inf = st.sidebar.checkbox("Początek w $-\infty$")
a = st.sidebar.number_input("Początek przedziału (a)", value=1.0, step=0.5, disabled=use_minus_inf)

use_plus_inf = st.sidebar.checkbox("Koniec w $+\infty$")
b = st.sidebar.number_input("Koniec przedziału (b)", value=4.0, step=0.5, disabled=use_plus_inf)

interval_type = st.sidebar.selectbox(
    "Typ przedziału:", 
    options=[
        "Otwarty (a, b)", 
        "Domknięty [a, b]", 
        "Lewostronnie domknięty [a, b)", 
        "Prawostronnie domknięty (a, b]"
    ],
    help="Uwaga: Zaznaczenie nieskończoności matematycznie wymusza nawias otwarty po danej stronie, ignorując ten wybór."
)

# 3. Punkt do sprawdzenia
st.sidebar.subheader("3. Punkt $(x, y) \in \mathbb{R}^2$")
p_x = st.sidebar.number_input("Współrzędna x", value=0.0, step=0.1)
p_y = st.sidebar.number_input("Współrzędna y", value=1.5, step=0.1)

# --- MATEMATYKA I LOGIKA ---
x, y = sp.symbols('x y')
try:
    f_expr = sp.sympify(func_str)
    f_lambdified = sp.lambdify((x, y), f_expr, "numpy")
    
    val_at_point = f_lambdified(p_x, p_y)
    
    # Jeśli strona to nieskończoność, ignorujemy wybór i wymuszamy otwartość matematyczną (False)
    left_closed = False if use_minus_inf else (interval_type in ["Domknięty [a, b]", "Lewostronnie domknięty [a, b)"])
    right_closed = False if use_plus_inf else (interval_type in ["Domknięty [a, b]", "Prawostronnie domknięty (a, b]"])
    
    # Logika przynależności
    in_A_left = True if use_minus_inf else ((val_at_point >= a) if left_closed else (val_at_point > a))
    in_A_right = True if use_plus_inf else ((val_at_point <= b) if right_closed else (val_at_point < b))
    is_in_preimage = in_A_left and in_A_right
    
    # --- WYNIKI ---
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Część 1: Orzeczenie")
        st.write(f"Obliczona wartość funkcji w punkcie $({p_x}, {p_y})$ wynosi: **{val_at_point:.4f}**")
        
        # Zbudowanie matematycznego zapisu przedziału
        str_a = "$-\\infty$" if use_minus_inf else str(a)
        str_b = "$\\infty$" if use_plus_inf else str(b)
        str_bracket_L = "(" if (use_minus_inf or not left_closed) else "["
        str_bracket_R = ")" if (use_plus_inf or not right_closed) else "]"
        
        st.write(f"Badany przedział to $A = {str_bracket_L}{str_a}, {str_b}{str_bracket_R}$")
        
        if is_in_preimage:
            st.success(f"Orzeczenie: Punkt $({p_x}, {p_y})$ **należy** do przeciwobrazu $f^{{-1}}(A)$.")
        else:
            st.error(f"Orzeczenie: Punkt $({p_x}, {p_y})$ **nie należy** do przeciwobrazu $f^{{-1}}(A)$.")
            
        st.markdown("---")
        st.markdown("**Legenda wykresu:**")
        st.markdown("* **Niebieski obszar:** Wnętrze przeciwobrazu")
        st.markdown("* **Gruba linia ciągła:** Brzeg domknięty (punkt należy)")
        st.markdown("* **Linia przerywana:** Brzeg otwarty (punkt nie należy)")
        st.markdown("* **Czerwona gwiazdka:** Badany punkt")

    # --- RYSOWANIE WYKRESU Z ZACHOWANIEM TOPOLOGII ---
    with col2:
        st.markdown("### Część 2: Rysunek przeciwobrazu")
        
        grid_size = 600
        x_vals = np.linspace(-5, 5, grid_size)
        y_vals = np.linspace(-5, 5, grid_size)
        X, Y = np.meshgrid(x_vals, y_vals)
        Z = f_lambdified(X, Y)
        
        fig, ax = plt.subplots(figsize=(7, 7))
        
        # Ekstremalne wartości Z dla bezpiecznego kolorowania obszaru z nieskończonością
        Z_min, Z_max = np.min(Z), np.max(Z)
        plot_a = Z_min - 1.0 if use_minus_inf else a
        plot_b = Z_max + 1.0 if use_plus_inf else b
        
        # Rysowanie tła (obszaru) tylko jeśli przedział ma sens logiczny
        if plot_a < plot_b:
            ax.contourf(X, Y, Z, levels=[plot_a, plot_b], colors=['#a0c4ff'], alpha=0.5)
        
        # Rysowanie lewego brzegu (tylko jeśli to nie -nieskończoność i mieści się w widoku)
        if not use_minus_inf and (Z_min <= a <= Z_max):
            linestyle = 'solid' if left_closed else 'dashed'
            linewidth = 3 if left_closed else 2
            ax.contour(X, Y, Z, levels=[a], colors='darkblue', linewidths=linewidth, linestyles=linestyle)
            
        # Rysowanie prawego brzegu (tylko jeśli to nie +nieskończoność i mieści się w widoku)
        if not use_plus_inf and (Z_min <= b <= Z_max):
            linestyle = 'solid' if right_closed else 'dashed'
            linewidth = 3 if right_closed else 2
            ax.contour(X, Y, Z, levels=[b], colors='darkblue', linewidths=linewidth, linestyles=linestyle)
            
        # Zaznaczenie punktu
        ax.plot(p_x, p_y, marker='*', color='red', markersize=15, markeredgecolor='black')
        
        ax.set_aspect('equal')
        ax.set_xlim([-5, 5])
        ax.set_ylim([-5, 5])
        ax.grid(True, linestyle=':', alpha=0.6)
        
        st.pyplot(fig)

except Exception as e:
    st.error("Błąd: Upewnij się, że wpisujesz poprawny wzór funkcji.")
    st.write(f"Szczegóły błędu: {e}")
