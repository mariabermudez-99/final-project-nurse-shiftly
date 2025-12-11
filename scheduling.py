import pandas as pd
import pulp


def optimize_schedule(
    nurses_df: pd.DataFrame,
    shifts_df: pd.DataFrame,
    availability_df: pd.DataFrame,
    allow_overtime: bool = True,
    overtime_cost: float = 10.0,
    allow_understaff: bool = False,
    understaff_penalty: float = 50.0,
    preferences_df: pd.DataFrame | None = None,
    preference_weight: float = 0.0,
):
    """
    Build and solve the nurse scheduling MILP.

    Returns
    -------
    assignments_df : pd.DataFrame
        Columns: nurse_id, shift_id, assigned (0/1)
    overtime_dict : dict
        Mapping of nurse_id -> overtime hours (float)
    status : str
        PuLP solver status string
    """
    nurses = nurses_df["nurse_id"].unique()
    shifts = shifts_df["shift_id"].unique()

    # Lookups for parameters
    shift_hours = dict(zip(shifts_df["shift_id"], shifts_df["hours"]))
    shift_demand = dict(zip(shifts_df["shift_id"], shifts_df["demand"]))
    shift_skill = dict(zip(shifts_df["shift_id"], shifts_df["required_skill"]))
    nurse_max_hours = dict(zip(nurses_df["nurse_id"], nurses_df["max_hours_per_week"]))
    nurse_skill = dict(zip(nurses_df["nurse_id"], nurses_df["skill_level"]))

    availability_lookup = {}
    for _, row in availability_df.iterrows():
        availability_lookup[(row["nurse_id"], row["shift_id"])] = int(row["available"])

    preference_lookup = {}
    if preferences_df is not None and not preferences_df.empty and preference_weight != 0:
        for _, row in preferences_df.iterrows():
            preference_lookup[(row["nurse_id"], row["shift_id"])] = float(row["score"])

    # Model
    model = pulp.LpProblem("NurseShiftly", pulp.LpMinimize)

    # Decision variables
    x = pulp.LpVariable.dicts("assign", (nurses, shifts), lowBound=0, upBound=1, cat="Binary")
    o = pulp.LpVariable.dicts("overtime", nurses, lowBound=0, cat="Continuous")
    u = pulp.LpVariable.dicts("unmet", shifts, lowBound=0, cat="Continuous")  # understaffing slack

    # Objective: minimize total overtime + understaff penalty
    # Preference scores act as a reward (subtracted from the objective).
    model += (
        pulp.lpSum(overtime_cost * o[n] for n in nurses)
        + pulp.lpSum(understaff_penalty * u[s] for s in shifts)
        - pulp.lpSum(
            preference_weight * preference_lookup.get((n, s), 0.0) * x[n][s]
            for n in nurses
            for s in shifts
        )
    )

    # Constraints
    # Shift coverage
    for s in shifts:
        model += pulp.lpSum(x[n][s] for n in nurses) + u[s] >= shift_demand[s], f"coverage_{s}"
        if not allow_understaff:
            model += u[s] == 0, f"no_understaff_{s}"

    # Availability and skill
    for n in nurses:
        for s in shifts:
            avail = availability_lookup.get((n, s), 0)
            model += x[n][s] <= avail, f"availability_{n}_{s}"
            if shift_skill[s].upper() == "ICU" and nurse_skill[n].upper() != "ICU":
                model += x[n][s] == 0, f"skill_{n}_{s}"

    # Hour limits
    for n in nurses:
        max_hours = nurse_max_hours[n]
        model += (
            pulp.lpSum(shift_hours[s] * x[n][s] for s in shifts) <= max_hours + o[n],
            f"hour_limit_{n}",
        )
        if not allow_overtime:
            model += o[n] == 0, f"no_overtime_{n}"

    # Solve with CBC
    solver = pulp.PULP_CBC_CMD(msg=False)
    model.solve(solver)
    status = pulp.LpStatus[model.status]

    # Extract results
    assignment_rows = []
    for n in nurses:
        for s in shifts:
            assignment_rows.append(
                {"nurse_id": n, "shift_id": s, "assigned": int(pulp.value(x[n][s]))}
            )

    assignments_df = pd.DataFrame(assignment_rows)
    overtime_dict = {n: float(pulp.value(o[n])) for n in nurses}
    unmet_demand = {s: float(pulp.value(u[s])) for s in shifts}

    return assignments_df, overtime_dict, unmet_demand, status


