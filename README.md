# Khi-Edu-Analytics 📊

Karachi education student survey analysis with complete data pipeline and visualization notebooks!

## Quick Start (30 seconds)

```bash
# 1. Activate your environment
G:\MyPythonEnvs\env\Scripts\activate

# 2. Go to project folder
cd "f:\Project 1.0\Khi-Edu-Analytics"

# 3. Start Jupyter
jupyter notebook

# 4. Run notebooks in order: 01 → 02 → 03 → 04 → 05 → 06
```

---

## 📊 Dataset Overview

**366 Cleaned Survey Responses** from Karachi schools
- Raw survey responses: 1,024
- After data cleaning: 366 valid responses
- Removed: 658 incomplete/invalid entries (64% of raw data)
- **Data Quality:** High-quality, validated responses ready for analysis

---

## What's Included

✅ **Real Survey Data** - 366 cleaned student responses from Karachi
✅ **6 Analysis Notebooks** - Demographics, study habits, wellbeing, executive summary, correlations
✅ **Helper Scripts** - Data loading & cleaning utilities
✅ **Organized Structure** - Folders for data, notebooks, outputs
✅ **Complete Setup** - Everything ready to analyze

---

## Project Structure

```
Khi-Edu-Analytics/
├── data/                                    # Data files
│   ├── Karachi Edu Analytics Survey .csv   # Survey data (366 cleaned responses)
│   ├── raw/                                # Raw data backups
│   └── cleaned/                            # Cleaned data exports
├── notebooks/                              # Jupyter analysis notebooks
│   ├── 01_data_loading_cleaning.ipynb      # Load & explore ← START HERE
│   ├── 02_demographics_analysis.ipynb      # Age, gender, grades
│   ├── 03_study_habits_analysis.ipynb      # Study methods & subjects
│   ├── 04_wellbeing_analysis.ipynb         # Marginalization & substance use
│   ├── 05_executive_summary.ipynb          # All findings in one place
│   └── 06_marginalization_substance_analysis.ipynb  # Correlation analysis
├── scripts/                                # Python helper functions
│   └── helpers.py                          # Reusable utilities
├── report/                                 # Export final reports here
├── visuals/                                # Export charts here
├── requirements.txt                        # Python dependencies
└── README.md                               # This file
```

---

## Survey Dataset Explained

**File:** `data/Karachi Edu Analytics Survey .csv`

**What it contains:**
- 366 cleaned student responses from Karachi
- Data cleaned: removed invalid/incomplete entries from 1,024 raw responses
- Age, gender, grade/class level
- Study hours per day, preferred study methods
- Most challenging subjects
- Extracurricular activities
- Marginalization/discrimination experiences
- Substance use information

**Survey Columns:**
```
Timestamp, Age, Grade/Class, Gender,
Average hours spent studying per day, Preferred study method,
Subject(s) you find most challenging, Extra-curricular activities,
Do you feel marginalized or discriminated against,
Have you ever used tobacco, alcohol, or other substances?
```

---

## Analysis Notebooks (Run in Order)

### **01_data_loading_cleaning.ipynb** ← Start Here
**What:** Load survey data and explore structure
- Load the CSV file
- Show data shape and columns
- Check for missing values
- Display sample rows
- Basic statistics

### **02_demographics_analysis.ipynb**
**What:** Student demographics analysis
- Age distribution (histogram, box plot)
- Gender breakdown (pie chart)
- Grade/Class distribution
- Age by gender analysis

### **03_study_habits_analysis.ipynb**
**What:** Study patterns and subjects
- Daily study hours distribution
- Preferred study methods (bar chart)
- Most challenging subjects analysis
- Extracurricular activities breakdown

### **04_wellbeing_analysis.ipynb**
**What:** Student wellbeing concerns
- Marginalization/discrimination experiences
- Substance use prevalence
- Cross-analysis: Gender vs Marginalization
- Study hours vs Substance use patterns

### **05_executive_summary.ipynb**
**What:** Complete analysis summary in one notebook
- Key findings dashboard
- All demographics at a glance
- Study habits overview
- Wellbeing metrics
- Recommendations based on findings

### **06_marginalization_substance_analysis.ipynb**
**What:** Deep correlation analysis
- Statistical tests (Chi-square analysis)
- Marginalization vs Substance Use correlation
- Bar charts and heatmaps
- Risk analysis and insights

---

## Your Python Setup Explained

### Virtual Environment (`G:\MyPythonEnvs\env`)
✓ Isolated Python installation just for this project
✓ Prevents conflicts with other projects
✓ Has its own package versions

### Packages You Have
| Package | Purpose |
|---------|---------|
| `pandas` | Work with data tables |
| `numpy` | Math & numerical operations |
| `matplotlib` | Create charts & plots |
| `seaborn` | Pretty statistical visualizations |
| `jupyter` | Interactive notebooks (what you're using) |
| `geopandas` | Geographic/location data |
| `folium` | Interactive maps |
| `scikit-learn` | Machine learning |
| `ydata-profiling` | Auto-generate data reports |
| Other libs | Excel, PDF, web data support |

### How to Use
```bash
# Activate environment
G:\MyPythonEnvs\env\Scripts\activate

# Once activated, you can run:
python scripts/helpers.py          # Run helper functions
jupyter notebook                   # Start Jupyter (create/edit notebooks)
pip install new_package            # Add more packages
```

---

## Using Helper Functions

The `scripts/helpers.py` file contains reusable functions:

```python
# In your notebook
import sys
sys.path.insert(0, '../scripts')
from helpers import load_survey_data, clean_survey_data, get_demographics_summary

# Load data
df = load_survey_data()
df_clean = clean_survey_data(df)

# Get summaries
get_demographics_summary(df_clean)
get_study_habits_summary(df_clean)
```

---

## Recommended Workflow

### Session 1: Explore
1. Run `01_data_loading_cleaning.ipynb`
2. Understand the survey questions and data
3. Check data quality

### Session 2: Analysis
1. Run `02_demographics_analysis.ipynb`
2. Run `03_study_habits_analysis.ipynb`
3. Run `04_wellbeing_analysis.ipynb`
4. Run `05_executive_summary.ipynb` for overview
5. Run `06_marginalization_substance_analysis.ipynb` for deep insights
6. Note interesting findings

### Session 3: Visualize & Export
1. Save important charts from `visuals/` folder
2. Create a summary report
3. Export key insights to `report/` folder

### Session 4: Share
1. Create presentation with findings
2. Share reports with stakeholders

---

## Adding New Survey Data

1. **Collect survey responses** using Google Forms or similar
2. **Export as CSV** with same column names
3. **Save to** `data/your_survey_name.csv`
4. **Update notebook 01** to load your new file
5. **Run all notebooks** and they'll analyze your new data!

---

## Creating Custom Analysis

Add new notebooks to explore:
- Geographic analysis - Map schools and student locations
- Time series - Track changes over multiple survey waves
- Predictive models - Forecast wellbeing outcomes
- Custom correlations - Explore specific relationships

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "ModuleNotFoundError: pandas" | Activate environment first: `G:\MyPythonEnvs\env\Scripts\activate` |
| "Jupyter not installed" | Run: `pip install jupyter` |
| Import errors in notebooks | Add this to notebook top: `import sys; sys.path.insert(0, '../scripts')` |
| Data won't load | Check file path and column names match exactly |

---

## Next Steps

✓ Start with **01_data_loading_cleaning.ipynb**
✓ Run analysis notebooks 02-04
✓ View executive summary in **05_executive_summary.ipynb**
✓ Deep dive with **06_marginalization_substance_analysis.ipynb**
✓ Create custom visualizations and reports

**Dataset:** 366 cleaned responses | **Status:** Ready for analysis 🎉


