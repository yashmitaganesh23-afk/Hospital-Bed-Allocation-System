from flask import Flask, render_template, request
import numpy as np

app = Flask(__name__)

ICU_BEDS = 3
WARD_BEDS = 5

def calculate_risk_score(hr, o2, temp):
    w1, w2, w3 = 0.4, 0.4, 0.2
    score = (w1 * (hr / 100)) + \
            (w2 * ((100 - o2) / 100)) + \
            (w3 * (temp / 100))
    return round(score, 2)

def classify_risk(score):
    if score >= 0.7:
        return "High Risk"
    elif score >= 0.4:
        return "Medium Risk"
    else:
        return "Low Risk"

def markov_prediction(current_state):
    P = np.array([
        [0.6, 0.3, 0.1],
        [0.2, 0.6, 0.2],
        [0.0, 0.0, 1.0]
    ])

    states = {"ICU": 0, "Ward": 1, "Discharge": 2}
    reverse = {0: "ICU", 1: "Ward", 2: "Discharge"}

    index = states[current_state]
    next_index = np.argmax(P[index])
    return reverse[next_index]

def expected_stay(lam):
    return round(1 / lam, 2)

def allocate_bed(risk, predicted):
    global ICU_BEDS, WARD_BEDS

    if risk == "High Risk" and ICU_BEDS > 0:
        ICU_BEDS -= 1
        return "ICU Bed Allocated"
    elif predicted == "Ward" and WARD_BEDS > 0:
        WARD_BEDS -= 1
        return "Ward Bed Allocated"
    else:
        return "No Bed Available"

@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        hr = float(request.form["heart_rate"])
        o2 = float(request.form["oxygen"])
        temp = float(request.form["temperature"])

        score = calculate_risk_score(hr, o2, temp)
        risk = classify_risk(score)

        current_state = "ICU" if risk == "High Risk" else "Ward"
        predicted = markov_prediction(current_state)

        stay = expected_stay(0.5)
        allocation = allocate_bed(risk, predicted)

        result = {
            "score": score,
            "risk": risk,
            "predicted": predicted,
            "stay": stay,
            "allocation": allocation,
            "icu": ICU_BEDS,
            "ward": WARD_BEDS
        }

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run()
