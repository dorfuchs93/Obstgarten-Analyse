import streamlit as st
import pandas as pd
import itertools
from fractions import Fraction

st.set_page_config(
    page_title="Erster Obstgarten mathematisch analysiert",
    page_icon="🍎"
)

def basis_vector(n, k):
    vec = [Fraction(0)] * n
    vec[k] = Fraction(1)
    return vec

def linear_combination(vectors, coefficients):
    n = len(vectors[0])
    result = [Fraction(0)] * n
    for vec, coeff in zip(vectors, coefficients):
        for i in range(n):
            result[i] += vec[i] * coeff
    return result

def calculate_states():
    states = []
    for rabe in range(7):
        for tree in itertools.product(range(5), repeat=4):
            state = tuple([rabe] + list(tree))
            states.append(state)

    probabilites = {}
    for state in states:
        if state[0] == 0: # Rabe hat den Obstgarten erreicht
            obst = sum(state[1:])
            probabilites[state] = (Fraction(0), Fraction(0), basis_vector(23, 16-obst), basis_vector(23, 16-obst))
        elif sum(state[1:]) == 0: # Kein Obst mehr auf Bäumen
            probabilites[state] = (Fraction(1), Fraction(1), basis_vector(23, 16+state[0]), basis_vector(23, 16+state[0]))
        else:
            # n = Anzahl der möglichen Züge sind Rabe, nicht-leere Farben und Obstkorb
            n = sum(1 for x in state if x != 0) + 1
            ps = [0, 0, 0, 0]
            for i in range(2):
                vectors = []
                coefficients = []
                # p = 1/n * p(Rabe im nächsten Zug) + ...
                new_state = (state[0]-1, ) + state[1:]
                probability = Fraction(probabilites[new_state][i], n)
                p = probability
                vectors.append(probabilites[new_state][i+2])
                coefficients.append(Fraction(1, n))
                for k in [1, 2, 3, 4]:
                    if state[k] != 0:
                        new_state = state[:k] + (state[k]-1, ) + state[k+1:]
                        # p = ... + 1/n * p(nicht-leere Farbe im nächsten Zug) + ...
                        probability = Fraction(probabilites[new_state][i], n)
                        p += probability
                        vectors.append(probabilites[new_state][i+2])
                        coefficients.append(Fraction(1, n))
                # Taktik, wenn Obstkorb gewürfelt wird
                if i == 0:
                    k = state[1:].index(min(x for x in state[1:] if x > 0)) + 1
                else:
                    k = state[1:].index(max(state[1:])) + 1
                new_state = state[:k] + (state[k]-1, ) + state[k+1:]
                # p = ... + 1/n * p(Obstkorb im nächsten Zug)
                probability = Fraction(probabilites[new_state][i], n)
                p += probability
                vectors.append(probabilites[new_state][i+2])
                coefficients.append(Fraction(1, n))
                histogram = linear_combination(vectors, coefficients)
                ps[i] = p
                ps[i+2] = histogram
                if p != sum(histogram[17:]):
                    print(state, p, histogram)
                    raise ValueError("Histogramm passt nicht zur Wahrscheinlichkeit.")
            probabilites[state] = ps
    return probabilites

@st.cache_data
def get_cached_states():
    return calculate_states()

# Streamlit-App Hauptteil

"""
# Erster Obstgarten mathematisch analysiert
Dieses Tool berechnet die Gewinnwahrscheinlichkeiten für das Spiel **Erster Obstgarten**.

## Aktueller Spielzustand
Gib hier den Zustand des Spiels ein. Voreingestellt ist der Anfangszustand des Spiels, wo der Rabe 5 Felder vom Obstgarten entfernt ist und auf jedem Baum 4 Früchte liegen.
"""

rabe = st.number_input(label="🐦‍⬛ Rabe", min_value=0, max_value=6, value=5, step=1)

col1, col2, col3, col4 = st.columns(4)
min_val = 0
max_val = 4
step_val = 1
default_val = 4

with col1:
    input1 = st.number_input("🍏 grüne Äpfel", 
                             min_value=min_val, 
                             max_value=max_val, 
                             value=default_val, 
                             step=step_val)

with col2:
    input2 = st.number_input("🍎 rote Äpfel", 
                             min_value=min_val, 
                             max_value=max_val, 
                             value=default_val, 
                             step=step_val)

with col3:
    input3 = st.number_input("🔵 Pflaumen", 
                             min_value=min_val, 
                             max_value=max_val, 
                             value=default_val, 
                             step=step_val)

with col4:
    input4 = st.number_input("🟡 Birnen", 
                             min_value=min_val, 
                             max_value=max_val, 
                             value=default_val, 
                             step=step_val)

obst = input1 + input2 + input3 + input4

if obst == 0:
    if rabe == 0:
        st.write("🤔 Dieser Zustand kann nicht erreicht werden.")
    else:
        st.write(f"""
                 ## 🎉 Gewonnen!
                 
                 Du hast gewonnen und das **Ergebnis {rabe}** erzielt, da der Rabe {rabe} {"Felder" if rabe > 1 else "Feld"} vom Obstgarten entfernt ist.
                 
                 Herzlichen Glückwunsch!""")
        st.balloons()
elif rabe == 0:
    st.write(f"""
             ## 😢 Verloren.
             
             Du hast verloren und das **Ergebnis -{obst}** erzielt, da noch {obst} {"Früchte an den Bäumen hängen." if obst > 1 else "Frucht am Baum hängt."}
            """)
else:
    state = (rabe, input1, input2, input3, input4)
    p = get_cached_states()

    p_min, p_max, hist_min, hist_max = p[state]

    df = pd.DataFrame({
        "Ergebnis": list(range(-16, 7)),
        "Min-Strategie": [float(x) for x in hist_min],
        "Max-Strategie": [float(x) for x in hist_max]
    })

    def prob_to_str(x):
        if x >= 0.995:
            return f"{100*x:.1f} %"
        else:
            return f"{100*x:.0f} %"

    if prob_to_str(p_min) == prob_to_str(p_max):
        st.write(f"## Gewinn zu {prob_to_str(p_min)}")
    else:
        st.write(f"## Gewinn zu {prob_to_str(p_min)} bis {prob_to_str(p_max)}")

    # st.write(f"Der Rabe steht {rabe} Felder vor dem Gartenzaun und es hängen noch {obst} Früchte an den Bäumen.")

    st.write(f"Die Gewinnwahrscheinlichkeit beträgt je nach Spieltaktik {float(p_min*100):.2f} % bis {float(p_max*100):.2f} %.")

    st.bar_chart(df, x="Ergebnis", stack=False)

    st.write("""
            Ein positives Ergebnis bedeutet, dass die Spieler gewinnen, indem sie alle Früchte in den Korb legen konnten und zählt, wie viele Felder der Rabe vom Obstgarten am Spielende entfernt ist.

            Ein negatives Ergebnis bedeutet, dass die Spieler verlieren, da der Rabe den Obstgarten erreicht hat und zählt, wie viele Früchte noch an den Bäumen hängen.

            Ein Ergebnis von 0 ist nicht möglich, da es kein Unentschieden geben kann.
            """)

    with st.expander("Exakte Wahrscheinlichkeiten"):
        st.write(f"""
                Wählt man beim Würfeln eines Obstkorbes immer den Baum mit den *wenigsten* Früchten, so erhält man die Gewinnwahrscheinlichkeit
                
                $p_\\text{{min}} = {p_min} \\approx {float(p_min)}$.

                Wählt man beim Würfeln eines Obstkorbes immer den Baum mit den *meisten* Früchten, so erhält man die Gewinnwahrscheinlichkeit
                
                $p_\\text{{max}} = {p_max} \\approx {float(p_max)}$.
                """)