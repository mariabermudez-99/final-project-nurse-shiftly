****🧑‍⚕️ NurseShiftly****

Prescriptive analytics application for automated nurse shift scheduling

NurseShiftly is a Streamlit-based prescriptive analytics tool that generates optimal weekly nurse schedules using mixed-integer linear optimization. It supports realistic healthcare staffing decisions by balancing coverage, labor constraints, overtime, understaffing, and nurse preferences.

**The Problem**

Hospitals must decide which nurses to assign to which shifts while satisfying multiple operational constraints:

- Each shift must meet minimum staffing demand

- Some shifts require ICU-trained nurses

- Nurses have limited availability and weekly hour limits

- Overtime is costly and contributes to burnout

- In some cases, full coverage may be infeasible

These constraints often conflict. For example, ICU night shifts may require specialized nurses who are already near their hour limits. As a result, schedules are frequently built manually using spreadsheets, which is time-consuming and can lead to excessive overtime, understaffing, or unfair workloads.

NurseShiftly addresses this challenge by providing data-driven, optimized scheduling recommendations.


**Prescriptive Analytics Approach**

NurseShiftly formulates the scheduling problem as a mixed-integer linear program (MILP) solved using PuLP with the CBC solver.


**Decision Variables**

- Binary variables indicating whether a nurse is assigned to a shift

- Continuous variables representing overtime hours (optional)

- Optional unmet-demand variables when understaffing is allowed


**Objective Function**

The model minimizes a weighted combination of:

- Overtime hours (penalized)

- Understaffed shift demand (penalized, optional)

- Nurse preference scores (rewarded, optional)

This allows decision-makers to explore trade-offs between efficiency, coverage, and staff satisfaction.


**Constraints**

Hard constraints (never violated):

- Nurse availability

- Skill requirements (ICU vs. General)

- Valid assignment structure

- Soft constraints (violated at a cost):

- Weekly hour limits (via overtime)

- Shift coverage (via understaffing, if enabled)

- Nurse preferences (modeled as rewards)


**Application Features**

Interactive parameter controls for:

- Overtime penalties

- Understaffing penalties

- Nurse preference weights

- Upload custom datasets or use built-in sample data

- Solver status reporting (optimal / infeasible)


**Clear output tables:**

- Nurse–shift assignments

- Nurse × shift matrix

- Overtime summary

- Unmet demand (if applicable)

- Downloadable schedule as CSV


**Live Demo**

👉 App URL:
http://10.0.0.188:8501/

Project Structure
nurse-shiftly/
├─ app.py             # Streamlit UI and workflow
├─ scheduling.py      # MILP model and solver
├─ data/              # Sample CSVs
├─ requirements.txt   # Dependencies
└─ README.md

**Data Format**

- nurses.csv
  
    nurse_id, name, skill_level (GENERAL/ICU), max_hours_per_week

- shifts.csv
  
    shift_id, date, start_time, end_time, hours, demand, required_skill

- availability.csv
  
    nurse_id, shift_id, available (1/0)

Sample datasets are included in the data/ directory.


**Running the App**
    
1. Create and activate a virtual environment

2. Install dependencies:

      pip install -r requirements.txt

3. Launch the app:

      streamlit run app.py

5. Upload CSVs or click Use Sample Data

6. Adjust optimization parameters

7. Click Generate Schedule


**About This Project**

Built for ISOM 839 – Prescriptive Analytics
Suffolk University

Author: Marie Bermudez
📧 Marie.Bermudez@su.suffolk.com


**Future Work**

- Fairness objectives to balance workloads

- Rest-time and shift-sequencing constraints

- Robust optimization under demand uncertainty

- Multi-week scheduling horizons

- Scenario comparison and solver warm-starts
