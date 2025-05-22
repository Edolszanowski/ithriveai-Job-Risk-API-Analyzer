"""
Updated Nurse data function that matches the format expected by app_production.py
"""

def get_updated_nurse_data():
    """
    Get comprehensive data for Nurse role.
    """
    # Define data in the format app_production.py expects
    return {
        "job_title": "Registered Nurse",
        "occupation_code": "29-1141",  # SOC code for Registered Nurses
        "job_category": "Healthcare",
        "source": "enhanced_data",
        "latest_employment": "3130600",
        "projections": {
            "current_employment": 3130600,
            "projected_employment": 3458200,
            "percent_change": 10.5,
            "annual_job_openings": 203200
        },
        "automation_probability": 20.0,  # Convert to percentage
        "risk_scores": {
            "year_1": 15.0,
            "year_5": 30.0
        },
        "risk_category": "Low to Moderate",
        "risk_factors": [
            "Administrative tasks can be automated",
            "AI diagnostic support tools are increasingly sophisticated",
            "Remote monitoring reduces need for some in-person care",
            "Predictive analytics may reduce staffing requirements"
        ],
        "protective_factors": [
            "Direct patient care requires human empathy and dexterity",
            "Complex decision-making in emergency situations",
            "Patient education and emotional support remain human-centered",
            "Physical assessment and intervention skills are difficult to automate"
        ],
        "trend_data": {
            "years": list(range(2020, 2026)),
            "employment": [2990000, 3080000, 3130600, 3198000, 3268000, 3340000]
        },
        "similar_jobs": [
            {
                "job_title": "Nurse Practitioner",
                "occupation_code": "29-1171",
                "year_1_risk": 10.0,
                "year_5_risk": 20.0,
                "risk_category": "Low"
            },
            {
                "job_title": "Licensed Practical Nurse",
                "occupation_code": "29-2061",
                "year_1_risk": 20.0,
                "year_5_risk": 40.0,
                "risk_category": "Moderate"
            },
            {
                "job_title": "Physician Assistant",
                "occupation_code": "29-1071",
                "year_1_risk": 15.0,
                "year_5_risk": 25.0,
                "risk_category": "Low"
            },
            {
                "job_title": "Nursing Assistant",
                "occupation_code": "31-1131",
                "year_1_risk": 25.0,
                "year_5_risk": 45.0,
                "risk_category": "Moderate"
            }
        ],
        "skills": {
            "future_proof_skills": [
                "Digital health technology proficiency", 
                "Data interpretation for patient monitoring",
                "Telehealth service delivery",
                "Advanced clinical assessment",
                "Complex care coordination",
                "AI-assisted diagnostics"
            ],
            "skill_areas": {
                "technical_skills": [
                    "Digital health record systems",
                    "Remote monitoring technology",
                    "Telehealth platforms",
                    "Medical device integration",
                    "Clinical decision support systems"
                ],
                "soft_skills": [
                    "Complex communication",
                    "Empathetic care",
                    "Crisis management",
                    "Interdisciplinary collaboration",
                    "Patient advocacy",
                    "Ethical decision-making"
                ],
                "transferable_skills": [
                    "Assessment and diagnosis",
                    "Critical thinking",
                    "Care coordination",
                    "Patient education",
                    "Resource management",
                    "Quality improvement"
                ]
            }
        }
    }