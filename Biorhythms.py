import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import plotly.graph_objs as go 

st.set_page_config(page_title="📈 Biorhythm Calculator", layout="wide")
st.title("🌀 Biorhythm Forecast")

# --- Stored people (name: birthdate) ---
people = {
    "Scott": "1957-04-11",
    "Patty": "1963-04-30",
    "Marina": "1989-01-19",
    "Drake": "1991-06-06",
    "Custom": None  # Placeholder for manual input
}

# --- Sidebar: Person and Dates ---
with st.sidebar:
    st.header("Person Setup")

    selected_person = st.selectbox("Choose a person", list(people.keys()))

    if people[selected_person]:
        birthdate = pd.to_datetime(people[selected_person]).date()
    else:
        custom_name = st.text_input("Name", value="New Person")
        birthdate = st.date_input("Birthdate", value=datetime(1990, 1, 1))

    start_date = st.date_input("Start Date", value=datetime.today() - + pd.Timedelta(days=15))
    end_date = st.date_input("End Date", value=datetime.today() + pd.Timedelta(days=30))

    if start_date >= end_date:
        st.error("End date must be after start date.")
        st.stop()

# --- Biorhythm Functions ---
def calculate_biorhythm(birthdate, target_date):
    birthdate = pd.Timestamp(birthdate)
    target_date = pd.Timestamp(target_date)
    days_lived = (target_date - birthdate).days
    physical = np.sin(2 * np.pi * days_lived / 23)
    emotional = np.sin(2 * np.pi * days_lived / 28)
    intellectual = np.sin(2 * np.pi * days_lived / 33)
    return physical, emotional, intellectual

def generate_biorhythm_data(birthdate, start_date, end_date):
    date_range = pd.date_range(start=start_date, end=end_date)
    data = []
    for date in date_range:
        p, e, i = calculate_biorhythm(birthdate, date)
        avg = (p + e + i) / 3
        data.append({
            "Date": date,
            "Physical": p,
            "Emotional": e,
            "Intellectual": i,
            "Average": avg
        })
    return pd.DataFrame(data)

# --- Generate Data ---
df = generate_biorhythm_data(birthdate, start_date, end_date)

# --- Plotly Chart ---
fig = go.Figure()

for column, color in zip(["Physical", "Emotional", "Intellectual", "Average"],
                         [None, None, None, "black"]):
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df[column],
        mode='lines+markers',
        name=column,
        line=dict(dash='dot') if column == "Average" else None,
        marker=dict(size=4, opacity=0),
        hoverinfo="none"
    ))

# --- Vertical line for today ---
today = pd.Timestamp.today().normalize().to_pydatetime()
fig.add_vline(
    x=today,
    line_dash="dash",
    line_color="red"
)

fig.add_annotation(
    x=today,
    y=1.05,
    text="Today",
    showarrow=False,
    yanchor="bottom",
    font=dict(color="red")
)

# --- Final Layout ---
fig.update_layout(
    title=f"Biorhythm Chart for {selected_person if selected_person != 'Custom' else custom_name}",
    xaxis_title="Date",
    yaxis_title="Cycle Value",
    yaxis=dict(range=[-1.1, 1.1]),
    hovermode="x unified",  # Vertical guide, minimal hover
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)