import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp

# Konfiguracja strony
st.set_page_config(page_title="Zadanie 5 - Przeciwobraz", layout="wide")

st.title("Zadanie 5: Przeciwobraz funkcji $f^{-1}(A)$")
st.markdown("Aplikacja orzeka, czy dany punkt należy do przeciwobrazu oraz wykonuje rysunek z uwzględnieniem topologii przedziału (linie ciągłe dla zbiorów domkniętych, przerywane dla otwartych).")

# --- PANEL BOCZNY (INTERFEJS) ---
st.sidebar.header("Parametry wejściowe")

# 1. Definicja funkcji
st.sidebar.subheader("1. Jawny wzór funkcji $f(x, y)$")
func_str = st.sidebar.text_input("Podaj wzór (np. x**2 + y**2, sin(x)*y):", value="x**2 + y**2")

# 2. Zbiór A
st.sidebar.subheader("2. Zbiór $A \subseteq \mathbb{R}$")
a = st.sidebar.number_input("Początek przedziału (a)", value=1.0, step=0.5)
b = st.sidebar.number_input("Koniec przedziału (b)", value=4.0, step=0.5)

interval_type = st.sidebar.selectbox(
    "Typ przedziału:", 
    options=[
        "Otwarty (a, b)", 
        "Domknięty [a, b]", 
        "Lewostronnie domknięty [a, b)", 
        "Prawostronnie domknięty (a, b]"
    ]
)

# 3. Punkt do sprawdzenia
st.sidebar.subheader("3. Punkt $(x, y) \in \mathbb{R}^2$")
p_x = st.sidebar.number_input("Współrzędna x", value=0.0, step=0.1)
p_y = st.sidebar.number_input("Współrzędna y", value=1.5, step=0.1)

# --- MATEMATYKA I LOGIKA ---
x, y = sp.symbols('x y')
try:
    # Bezpieczne parsowanie funkcji wpisanej przez użytkownika
    f_expr = sp.sympify(func_str)
    # Zamiana funkcji symbolicznej na bardzo szybką funkcję numeryczną (eliminuje lagi!)
    f_lambdified = sp.lambdify((x, y), f_expr, "numpy")
    
    # Obliczenie wartości w podanym punkcie
    val_at_point = f_lambdified(p_x, p_y)
    
    # Ustalenie właściwości topologicznych brzegów przedziału
    left_closed = interval_type in ["Domknięty [a, b]", "Lewostronnie domknięty [a, b)"]
    right_closed = interval_type in ["Domknięty [a, b]", "Prawostronnie domknięty (a, b]"]
    
    # Orzekanie o przynależności do przeciwobrazu
    in_A_left = (val_at_point >= a) if left_closed else (val_at_point > a)
    in_A_right = (val_at_point <= b) if right_closed else (val_at_point < b)
    is_in_preimage = in_A_left and in_A_right
    
    # --- WYNIKI ---
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Część 1: Orzeczenie")
        st.write(f"Obliczona wartość funkcji w punkcie $({p_x}, {p_y})$ wynosi: **{val_at_point:.4f}**")
        
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
        
        # Generowanie gęstej siatki (600x600 rozwiązuje problem poszarpanych krawędzi)
        grid_size = 600
        x_vals = np.linspace(-5, 5, grid_size)
        y_vals = np.linspace(-5, 5, grid_size)
        X, Y = np.meshgrid(x_vals, y_vals)
        Z = f_lambdified(X, Y)
        
        fig, ax = plt.subplots(figsize=(7, 7))
        
        # Wypełnienie obszaru przeciwobrazu
        ax.contourf(X, Y, Z, levels=[a, b], colors=['#a0c4ff'], alpha=0.5)
        
        # Rysowanie lewego brzegu (a)
        if left_closed:
            ax.contour(X, Y, Z, levels=[a], colors='darkblue', linewidths=3, linestyles='solid')
        else:
            ax.contour(X, Y, Z, levels=[a], colors='darkblue', linewidths=2, linestyles='dashed')
            
        # Rysowanie prawego brzegu (b)
        if right_closed:
            ax.contour(X, Y, Z, levels=[b], colors='darkblue', linewidths=3, linestyles='solid')
        else:
            ax.contour(X, Y, Z, levels=[b], colors='darkblue', linewidths=2, linestyles='dashed')
            
        # Zaznaczenie punktu
        ax.plot(p_x, p_y, marker='*', color='red', markersize=15, markeredgecolor='black')
        
        ax.set_aspect('equal')
        ax.set_xlim([-5, 5])
        ax.set_ylim([-5, 5])
        ax.grid(True, linestyle=':', alpha=0.6)
        
        st.pyplot(fig)

except Exception as e:
    st.error("Błąd: Upewnij się, że wpisujesz poprawny wzór funkcji (np. składnia Pythona wymaga użycia `**` dla potęgowania).")
    st.write(f"Szczegóły błędu: {e}")
