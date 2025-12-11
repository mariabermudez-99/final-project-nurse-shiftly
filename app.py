import io
import pandas as pd
import streamlit as st
import altair as alt

from scheduling import optimize_schedule


st.set_page_config(page_title="NurseShiftly", layout="wide")
st.title("🧑‍⚕️ NurseShiftly")
st.caption("Prescriptive analytics for automated nurse shift scheduling")

# Session state to keep sample data selection across reruns
if "use_sample" not in st.session_state:
    st.session_state.use_sample = False

st.markdown(
    """
    ### What this app does
    NurseShiftly builds optimal weekly nurse schedules with a mixed-integer model that enforces demand, availability, skills, and weekly hour limits. It minimizes overtime by default but allows you to tune the penalty.

    ### How to use
    1) In the sidebar, upload `nurses.csv`, `shifts.csv`, and `availability.csv`, or click **Use Sample Data**. Optionally upload `preferences.csv` (nurse_id, shift_id, score).  
    2) Set **Overtime cost weight**: higher values discourage overtime; lower values allow more overtime to cover demand.  
    3) (Optional) Set **Preference weight** to reward higher preference scores.  
    4) Click **Generate Schedule** to see assignments, a nurse×shift matrix, overtime by nurse, coverage chart, unmet demand (if allowed), and download the CSV.

    ### Parameter tips
    - **Overtime cost weight**: penalty per overtime hour. Higher = avoid overtime unless necessary; lower = use overtime more freely. Setting to 0 makes overtime “free” (still limited by availability/skills).
    - **Understaff penalty weight**: penalty per unfilled nurse slot on a shift (when understaffing is allowed). Higher = prioritize covering demand; lower = tolerate gaps if cheaper than overtime. Setting to 0 means the model won’t try to close gaps beyond hard constraints.
    - **Preference weight**: reward per unit of preference score for assigning a nurse to a shift. Higher = favor high-score matches. Set to 0 to ignore preferences.
    """
)


def load_csv(uploaded_file_or_path):
    if uploaded_file_or_path is None:
        return None
    if isinstance(uploaded_file_or_path, str):
        return pd.read_csv(uploaded_file_or_path)
    return pd.read_csv(uploaded_file_or_path)


with st.sidebar:
    st.header("Settings")
    allow_overtime = st.checkbox("Allow overtime", value=True)
    overtime_cost = st.number_input("Overtime cost weight", min_value=0.0, value=10.0, step=1.0)
    allow_understaff = st.checkbox("Allow understaffing (penalized)", value=False)
    understaff_penalty = st.number_input(
        "Understaff penalty weight",
        min_value=0.0,
        value=50.0,
        step=5.0,
        help="Higher values discourage leaving demand unmet; set to 0 to ignore penalty.",
    )
    preference_weight = st.number_input(
        "Preference weight (reward)",
        min_value=0.0,
        value=0.0,
        step=1.0,
        help="Higher values favor assignments with higher preference scores (from preferences.csv).",
    )

    st.header("Data")
    nurses_file = st.file_uploader("nurses.csv", type="csv")
    shifts_file = st.file_uploader("shifts.csv", type="csv")
    availability_file = st.file_uploader("availability.csv", type="csv")
    preferences_file = st.file_uploader("preferences.csv (optional)", type="csv")
    if st.button("Use Sample Data"):
        st.session_state.use_sample = True


# Load data
if st.session_state.use_sample:
    nurses_df = load_csv("data/nurses.csv")
    shifts_df = load_csv("data/shifts.csv")
    availability_df = load_csv("data/availability.csv")
    preferences_df = None
elif nurses_file and shifts_file and availability_file:
    nurses_df = load_csv(nurses_file)
    shifts_df = load_csv(shifts_file)
    availability_df = load_csv(availability_file)
    preferences_df = load_csv(preferences_file) if preferences_file is not None else None
    st.session_state.use_sample = False  # prioritize uploaded data on subsequent runs
else:
    nurses_df = shifts_df = availability_df = preferences_df = None


if nurses_df is None or shifts_df is None or availability_df is None:
    st.info("Upload all three CSVs or click 'Use Sample Data' to begin.")
    st.stop()


st.subheader("Input Data")
st.write("Nurses")
st.dataframe(nurses_df)
st.write("Shifts")
st.dataframe(shifts_df)
st.write("Availability")
st.dataframe(availability_df)


if st.button("Generate Schedule"):
    with st.spinner("Solving optimization..."):
        assignments_df, overtime_dict, unmet_demand, status = optimize_schedule(
            nurses_df,
            shifts_df,
            availability_df,
            allow_overtime=allow_overtime,
            overtime_cost=overtime_cost,
            allow_understaff=allow_understaff,
            understaff_penalty=understaff_penalty,
            preferences_df=preferences_df,
            preference_weight=preference_weight,
        )

    st.success(f"Solver status: {status}")

    st.subheader("Assignments")
    st.dataframe(assignments_df)

    st.subheader("Demand vs. Coverage")
    coverage = assignments_df.groupby("shift_id")["assigned"].sum().reset_index()
    demand = shifts_df[["shift_id", "demand"]]
    cov = demand.merge(coverage, on="shift_id", how="left").fillna(0)
    cov = cov.rename(columns={"assigned": "coverage"})
    cov_melt = cov.melt(id_vars="shift_id", value_vars=["demand", "coverage"], var_name="metric", value_name="value")
    chart = (
        alt.Chart(cov_melt)
        .mark_bar()
        .encode(
            x=alt.X("shift_id:N", title="Shift"),
            y=alt.Y("value:Q", title="Headcount"),
            color=alt.Color("metric:N", title=""),
            column=alt.Column("metric:N", title=""),
        )
        .properties(width=180, height=300)
    )
    st.altair_chart(chart, use_container_width=True)

    if allow_understaff:
        st.subheader("Unmet Demand (if any)")
        unmet_df = pd.DataFrame(
            [{"shift_id": s, "unmet": round(v, 2)} for s, v in unmet_demand.items() if v > 0.0001]
        )
        if unmet_df.empty:
            st.write("No unmet demand.")
        else:
            st.dataframe(unmet_df)

    st.subheader("Assignment Matrix (Nurses × Shifts)")
    pivot_df = assignments_df.pivot(index="nurse_id", columns="shift_id", values="assigned").fillna(0).astype(int)
    st.dataframe(pivot_df)

    st.subheader("Overtime")
    overtime_table = pd.DataFrame(
        [{"nurse_id": n, "overtime_hours": round(hours, 2)} for n, hours in overtime_dict.items()]
    )
    st.dataframe(overtime_table)

    csv_buffer = io.StringIO()
    assignments_df.to_csv(csv_buffer, index=False)
    st.download_button(
        "Download Schedule (CSV)",
        data=csv_buffer.getvalue(),
        file_name="optimized_schedule.csv",
        mime="text/csv",
    )

