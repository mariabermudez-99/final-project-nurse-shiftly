# NurseShiftly

Prescriptive analytics app for automated nurse shift scheduling using mixed-integer optimization and Streamlit.

## Problem

Hospitals must staff daily shifts while respecting nurse availability, skills, hour limits, and overtime costs. Manual scheduling is error-prone and slow, making it a strong candidate for prescriptive analytics.

## Optimization Approach

NurseShiftly formulates scheduling as a mixed-integer linear program (MILP) with PuLP (CBC solver):

- Binary assignment variables for nurse–shift decisions  
- Continuous overtime variables (optional)  
- Objective: minimize total overtime cost  
- Constraints: shift coverage, availability, skill matching (ICU vs. General), weekly hour limits, valid overtime

## Project Structure

```
nurse-shiftly/
├─ app.py             # Streamlit UI + workflow
├─ scheduling.py      # MILP model + solve routine
├─ data/              # Sample CSVs (nurses, shifts, availability)
├─ requirements.txt   # Dependencies
└─ README.md          # This file
```

## Data Format

- `nurses.csv`: nurse_id, name, skill_level (GENERAL/ICU), max_hours_per_week  
- `shifts.csv`: shift_id, date, start_time, end_time, hours, demand, required_skill  
- `availability.csv`: nurse_id, shift_id, available (1/0)

Sample CSVs are provided in `data/`.

## Running the App

1) Create/activate a virtual environment  
2) Install dependencies: `pip install -r requirements.txt`  
3) Launch Streamlit: `streamlit run app.py`  
4) In the app sidebar, upload your CSVs or click **Use Sample Data**  
5) Adjust overtime settings and click **Generate Schedule**

Outputs include solver status, assignment table, nurse×shift matrix, overtime summary, and a downloadable CSV.

## Screenshot

_(Insert Streamlit UI screenshot here.)_

## Future Work

- Fairness penalties to balance workloads  
- Preference scoring for nurse-shift matches  
- Shift sequencing/rest constraints  
- Robustness to demand uncertainty  
- Solver warm-starts and scenario comparisons

### Preferences (optional)

You can include a `preferences.csv` with columns: `nurse_id,shift_id,score`. In the app, set a positive **Preference weight** to reward higher scores in the objective; leave it at 0 to ignore preferences. Preferences act as a reward term, while overtime and understaff weights act as penalties.
