# NurseShiftly

Prescriptive analytics app for automated nurse shift scheduling using mixed-integer optimization and Streamlit.

## The Problem

Hospitals need to assign nurses to daily shifts while meeting staffing requirements, respecting nurse availability, enforcing skill requirements like ICU certification, and staying within weekly hour limits.

This is a challenging problem because these constraints often conflict. For example, night shifts may require ICU-trained nurses, but those nurses also have limited availability and hour caps. As a result, scheduling is often done manually in spreadsheets, which is time-consuming and can lead to understaffing, excessive overtime, or unfair workloads.

## Optimization Approach

NurseShiftly formulates scheduling as a mixed-integer linear program (MILP) with PuLP (CBC solver):

- Binary assignment variables for nurse–shift decisions  
- Continuous overtime variables (optional)  
- Objective: minimize total overtime cost  
- Constraints: shift coverage, availability, skill matching (ICU vs. General), weekly hour limits, valid overtime

## Live Demo
http://10.0.0.188:8501/

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
5) Adjust overtime, understaff, and nurse preference settings.
6) Finish by clicking **Generate Schedule**

Outputs include solver status, assignment table, nurse×shift matrix, overtime summary, and a downloadable CSV.

## About This Project

Built for ISOM 839 (Prescriptive Analytics) at Suffolk University.

**Author:** Marie Bermudez
**Email:** Marie.Bermudez@su.suffolk.com

## Future Work

- Fairness penalties to balance workloads 
- Shift sequencing/rest constraints  
- Robustness to demand uncertainty  
- Solver warm-starts and scenario comparisons


