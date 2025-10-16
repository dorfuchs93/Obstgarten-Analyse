import streamlit as st
import itertools
from fractions import Fraction

def calculate_states():
    states = []
    for rabe in range(6):
        for tree in itertools.product(range(5), repeat=4):
            state = tuple([rabe] + list(tree))
            states.append(state)

    probabilites = {}
    for state in states:
        if state[0] == 0: # Rabe hat den Obstgarten erreicht
            probabilites[state] = (Fraction(0), Fraction(0))
        elif sum(state[1:]) == 0: # Kein Obst mehr auf Bäumen
            probabilites[state] = (Fraction(1), Fraction(1))
        else:
            # n = Anzahl der möglichen Züge sind Rabe, nicht-leere Farben und Obstkorb
            n = sum(1 for x in state if x != 0) + 1
            ps = [0, 0]
            for i in range(2):
                # p = 1/n * p(Rabe im nächsten Zug) + ...
                p = Fraction(probabilites[(state[0]-1, ) + state[1:]][i], n)
                for k in [1, 2, 3, 4]:
                    if state[k] != 0:
                        new_state = state[:k] + (state[k]-1, ) + state[k+1:]
                        # p = ... + 1/n * p(nicht-leere Farbe im nächsten Zug) + ...
                        p += Fraction(probabilites[new_state][i], n)
                # Taktik, wenn Obstkorb gewürfelt wird
                if i == 0:
                    k = state[1:].index(min(x for x in state[1:] if x > 0)) + 1
                else:
                    k = state[1:].index(max(state[1:])) + 1
                new_state = state[:k] + (state[k]-1, ) + state[k+1:]
                # p = ... + 1/n * p(Obstkorb im nächsten Zug)
                p += Fraction(probabilites[new_state][i], n)
                ps[i] = p       
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

rabe = st.number_input(label="🐦‍⬛ Rabe", min_value=0, max_value=5, value=5, step=1)

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

state = (rabe, input1, input2, input3, input4)
p = get_cached_states()

p_min, p_max = p[state]

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

with st.expander("Exakte Wahrscheinlichkeiten"):
    st.write(f"""
             Wählt man beim Würfeln eines Obstkorbes immer den Baum mit den *wenigsten* Früchten, so erhält man die Gewinnwahrscheinlichkeit
             
             $p_\\text{{min}} = {p_min} \\approx {float(p_min)}$.

             Wählt man beim Würfeln eines Obstkorbes immer den Baum mit den *meisten* Früchten, so erhält man die Gewinnwahrscheinlichkeit
             
             $p_\\text{{max}} = {p_max} \\approx {float(p_max)}$.
             """)
