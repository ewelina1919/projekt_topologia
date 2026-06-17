import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- KONFIGURACJA STRONY ---
st.set_page_config(page_title="Topologia: Przeciwobraz", layout="centered")

st.title("Wizualizacja przeciwobrazu funkcji")
st.markdown("""
Aplikacja bada przeciwobraz $f^{-1}(A)$ dla funkcji $f: \mathbb{R}^2 \\to \mathbb{R}$ oraz zbioru $A \\subseteq \mathbb{R}$.
""")

with st.expander("Ograniczenia implementacyjne i format zapisu"):
    st.markdown("""
    * **Zbiór $A$**: Ograniczony do przedziału domkniętego $[a, b]$.
    * **Funkcja $f(x,y)$**: Musi być ciągła i zapisana zgodnie ze składnią Pythona/NumPy. 
      Przykłady: `x**2 + y**2` (okrąg), `np.sin(x) * np.cos(y)`, `x - y`.
    """)

# --- INTERFEJS UŻYTKOWNIKA ---
st.header("Parametry wejściowe")

f_str = st.text_input("Wzór jawny funkcji f(x, y)", value="x**2 + y**2")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Zbiór $A = [a, b]$")
    a_val = st.number_input("Początek przedziału (a)", value=1.0)
    b_val = st.number_input("Koniec przedziału (b)", value=4.0)
with col2:
    st.subheader("Punkt $(x, y)$")
    x_val = st.number_input("Współrzędna x", value=1.0)
    y_val = st.number_input("Współrzędna y", value=1.0)

if a_val > b_val:
    st.error("Błąd: Wartość 'a' nie może być większa niż 'b'.")
    st.stop()

# --- LOGIKA OBLICZENIOWA ---
# Bezpieczne ewaluowanie funkcji przy użyciu NumPy
def evaluate_f(x, y, expression):
    allowed_names = {k: v for k, v in np.__dict__.items() if not k.startswith('_')}
    allowed_names.update({'x': x, 'y': y})
    try:
        # Zabezpieczony eval (bez wbudowanych funkcji systemowych)
        return eval(expression, {"__builtins__": {}}, allowed_names)
    except Exception as e:
        return None

# Ewaluacja dla podanego punktu
f_point = evaluate_f(x_val, y_val, f_str)

if f_point is None:
    st.error("Błąd parsowania wzoru funkcji. Sprawdź składnię (np. używaj `**` do potęgowania).")
    st.stop()

# --- WYNIK TWIERDZENIA ---
st.header("Orzeczenie")
is_in_A = a_val <= f_point <= b_val

if is_in_A:
    st.success(f"Punkt $({x_val}, {y_val})$ **NALEŻY** do przeciwobrazu $f^{{-1}}(A)$.")
    st.info(f"Uzasadnienie: $f({x_val}, {y_val}) = {f_point:.4f}$, co należy do przedziału $[{a_val}, {b_val}]$.")
else:
    st.error(f"Punkt $({x_val}, {y_val})$ **NIE NALEŻY** do przeciwobrazu $f^{{-1}}(A)$.")
    st.info(f"Uzasadnienie: $f({x_val}, {y_val}) = {f_point:.4f}$, co NIE należy do przedziału $[{a_val}, {b_val}]$.")

# --- WIZUALIZACJA ---
st.header("Rysunek przeciwobrazu $f^{-1}(A)$")

# Definiowanie siatki z dynamicznym zakresem, by punkt był zawsze widoczny
limit = max(5.0, abs(x_val) * 1.5, abs(y_val) * 1.5)
x_grid = np.linspace(-limit, limit, 400)
y_grid = np.linspace(-limit, limit, 400)
X, Y = np.meshgrid(x_grid, y_grid)

try:
    Z = evaluate_f(X, Y, f_str)
    if Z is None or np.isscalar(Z):
        st.error("Funkcja nie zwróciła poprawnej tablicy 2D. Może być to funkcja stała bez 'x' i 'y'.")
        st.stop()

    fig, ax = plt.subplots(figsize=(8, 8))

    # Rysowanie przeciwobrazu
    if a_val == b_val:
        # Przeciwobraz to poziomica
        contour = ax.contour(X, Y, Z, levels=[a_val], colors=['blue'])
        ax.clabel(contour, inline=True, fontsize=10)
    else:
        # Przeciwobraz to obszar między poziomicami
        ax.contourf(X, Y, Z, levels=[a_val, b_val], colors=['lightblue'], alpha=0.6)
        ax.contour(X, Y, Z, levels=[a_val, b_val], colors=['blue'], linewidths=1.5)

    # Nanoszenie badanego punktu
    point_color = 'green' if is_in_A else 'red'
    ax.plot(x_val, y_val, marker='o', markersize=8, color=point_color, markeredgecolor='black', label=f"Badany punkt ({x_val}, {y_val})")

    # Ustawienia estetyczne wykresu
    ax.set_aspect('equal', adjustable='box')
    ax.set_xlabel('Oś X')
    ax.set_ylabel('Oś Y')
    ax.set_title(f"Przeciwobraz zbioru A=[{a_val}, {b_val}] dla f(x,y) = {f_str}")
    ax.grid(True, linestyle=':', alpha=0.7)
    ax.axhline(0, color='black', linewidth=0.8)
    ax.axvline(0, color='black', linewidth=0.8)
    ax.legend(loc="upper right")

    st.pyplot(fig)

except Exception as e:
    st.error(f"Wystąpił błąd podczas generowania wykresu: {e}")