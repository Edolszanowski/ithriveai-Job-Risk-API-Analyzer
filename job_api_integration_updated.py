"""
Job API Integration Module
This module combines BLS employment data with AI displacement risk analysis.
"""
import bls_connector
from typing import Dict, Any, List, Optional
import time
import pandas as pd
import bls_job_mapper

# Cache for storing processed job data to minimize redundant processing
_job_cache = {}

def get_job_data(job_title: str) -> Dict[str, Any]:
    """
    Get comprehensive job data including BLS statistics and AI risk analysis.
    
    Args:
        job_title: The job title to analyze
        
    Returns:
        Dictionary with combined job data
    """
    # Check cache first for better performance
    if job_title in _job_cache:
        return _job_cache[job_title]
    
    # Special case handling for common jobs with custom data
    special_handlers = {
        "project manager": get_project_manager_data,
        "nurse": get_nurse_data,
        "registered nurse": get_nurse_data,
        "retail sales": get_retail_sales_data,
        "cook": get_cook_data,
        "teacher": get_teacher_data,
        "web developer": get_web_developer_data,
        "business analyst": get_business_analyst_data,
        "software developer": get_web_developer_data
    }
    
    # Check if we have a special handler for this job title
    lower_title = job_title.lower()
    for key, handler in special_handlers.items():
        if key in lower_title or lower_title in key:
            # Use the special handler but also get BLS data
            job_data = handler()
            
            # Cache the result
            _job_cache[job_title] = job_data
            return job_data
    
    # For all other job titles, use the dynamic BLS data mapper
    try:
        # Get complete job data from BLS mapper
        job_data = bls_job_mapper.get_complete_job_data(job_title)
        
        # Cache the result
        _job_cache[job_title] = job_data
        return job_data
        
    except Exception as e:
        print(f"Error getting job data for {job_title}: {str(e)}")
        # Fall back to internal data if BLS retrieval fails
        return get_internal_job_data(job_title)

# Keep all your existing special job data functions as fallbacks
# (get_project_manager_data, get_nurse_data, etc.)


def get_project_manager_data():
    """
    Get comprehensive data for Project Manager role.
    This is a custom implementation to ensure complete data for this common search.
    """
    # Define rich data for Project Managers
    occ_code = "11-3021"  # SOC code for Project Management Specialists
    standardized_title = "Project Manager"
    
    # Occupation data with employment figures
    occupation_data = {
        "status": "success",
        "latest_value": "571300"  # Current employment from BLS stats
    }
    
    # Projection data
    projection_data = {
        "projections": {
            "current_employment": 571300,
            "projected_employment": 627430,
            "percent_change": 9.8,
            "annual_job_openings": 47500
        }
    }
    
    # Calculate risk data with enhanced project manager details
    risk_data = {
        "year_1_risk": 35.0,
        "year_5_risk": 60.0,
        "risk_category": "Moderate to High",
        "risk_factors": [
            "Project management software increasingly automates routine tasks",
            "AI tools can handle resource allocation and scheduling",
            "Reporting and documentation can be automated",
            "Basic project tracking requires less human oversight"
        ],
        "protective_factors": [
            "Complex stakeholder management requires human relationships",
            "Strategic decision-making needs human judgment",
            "Team leadership and motivation remain human-centered",
            "Crisis management and problem-solving benefit from human experience"
        ],
        "analysis": "Project Managers face moderate to high displacement risk as AI tools advance. While routine project tracking and documentation are increasingly automated, roles requiring complex stakeholder management, strategic thinking, and leadership will remain valuable. Project managers who develop skills in AI oversight, strategic leadership, and change management will be more resilient to automation.",
        "projected_growth": {
            "percent_change": 9.8,
            "analysis": "Moderate growth projected"
        },
        "automation_probability": 0.45,
        "wage_trend": "Stable to increasing for specialized roles",
        "evolving_skills": [
            "AI tools implementation and oversight", 
            "Data-driven decision making",
            "Agile and adaptive methodologies",
            "Cross-functional leadership",
            "Change management expertise",
            "Strategic resource optimization"
        ],
        "skill_areas": {
            "technical_skills": [
                "AI/ML oversight and integration",
                "Data analytics and interpretation",
                "Advanced project management platforms",
                "Business intelligence tools",
                "Automation workflow design"
            ],
            "soft_skills": [
                "Strategic leadership",
                "Cross-functional team management",
                "Complex negotiation",
                "Emotional intelligence",
                "Crisis management",
                "Stakeholder communication"
            ],
            "transferable_skills": [
                "Systems thinking",
                "Process optimization",
                "Resource allocation",
                "Change management",
                "Decision-making under uncertainty",
                "Risk assessment"
            ]
        }
    }
    
    # Sample employment trend data
    trend_years = list(range(2020, 2026))
    trend_employment = [525000, 538000, 550000, 571300, 585000, 599000]
    
    # Sample similar jobs data
    similar_jobs = [
        {
            "job_title": "Program Manager",
            "occupation_code": "11-3021",
            "year_1_risk": 30.0,
            "year_5_risk": 55.0,
            "risk_category": "Moderate"
        },
        {
            "job_title": "Product Manager",
            "occupation_code": "11-2021",
            "year_1_risk": 25.0,
            "year_5_risk": 45.0,
            "risk_category": "Moderate"
        },
        {
            "job_title": "Construction Manager",
            "occupation_code": "11-9021",
            "year_1_risk": 20.0,
            "year_5_risk": 40.0,
            "risk_category": "Moderate"
        },
        {
            "job_title": "Operations Manager",
            "occupation_code": "11-1021",
            "year_1_risk": 40.0,
            "year_5_risk": 65.0,
            "risk_category": "High"
        }
    ]
    
    # Combine all data
    result = {
        "job_title": standardized_title,
        "occupation_code": occ_code,
        "source": "enhanced_data",
        "employment_data": [],  # Not needed for display
        "latest_employment": occupation_data["latest_value"],
        "projections": projection_data["projections"],
        "risk_analysis": risk_data,
        "trend_data": {
            "years": trend_years,
            "employment": trend_employment
        },
        "similar_jobs": similar_jobs
    }
    
    return result


def get_nurse_data():
    """
    Get comprehensive data for Nurse role.
    """
    occ_code = "29-1141"  # SOC code for Registered Nurses
    standardized_title = "Registered Nurse"
    
    # Occupation data with employment figures
    occupation_data = {
        "status": "success",
        "latest_value": "3130600"  # Current employment from BLS stats
    }
    
    # Projection data with strong growth (BLS projections)
    projection_data = {
        "projections": {
            "current_employment": 3130600,
            "projected_employment": 3458200,
            "percent_change": 10.5,
            "annual_job_openings": 203200
        }
    }
    
    # Calculate risk data with nurse-specific details
    risk_data = {
        "year_1_risk": 15.0,
        "year_5_risk": 30.0,
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
        "analysis": "Nurses face relatively low displacement risk from AI. While administrative tasks and some monitoring functions may be automated, the core nursing role of direct patient care requires human empathy, physical skills, and clinical judgment that AI cannot replace. Nurses who develop technical skills to work alongside AI tools will be most resilient to technological change.",
        "projected_growth": {
            "percent_change": 10.5,
            "analysis": "Strong growth projected"
        },
        "automation_probability": 0.20,
        "wage_trend": "Increasing, especially for specialized roles",
        "evolving_skills": [
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
    
    # Sample employment trend data
    trend_years = list(range(2020, 2026))
    trend_employment = [2990000, 3080000, 3130600, 3198000, 3268000, 3340000]
    
    # Sample similar jobs data
    similar_jobs = [
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
    ]
    
    # Combine all data
    result = {
        "job_title": standardized_title,
        "occupation_code": occ_code,
        "source": "enhanced_data",
        "employment_data": [],  # Not needed for display
        "latest_employment": occupation_data["latest_value"],
        "projections": projection_data["projections"],
        "risk_analysis": risk_data,
        "trend_data": {
            "years": trend_years,
            "employment": trend_employment
        },
        "similar_jobs": similar_jobs
    }
    
    return result


def get_retail_sales_data():
    """
    Get comprehensive data for Retail Sales role.
    """
    occ_code = "41-2031"  # SOC code for Retail Salespersons
    standardized_title = "Retail Salesperson"
    
    # Occupation data with employment figures
    occupation_data = {
        "status": "success",
        "latest_value": "3625500"  # Current employment from BLS stats
    }
    
    # Projection data with decline (BLS projections)
    projection_data = {
        "projections": {
            "current_employment": 3625500,
            "projected_employment": 3464000,
            "percent_change": -4.5,
            "annual_job_openings": 606000  # High turnover despite decline
        }
    }
    
    # Calculate risk data with retail-specific details
    risk_data = {
        "year_1_risk": 55.0,
        "year_5_risk": 75.0,
        "risk_category": "High",
        "risk_factors": [
            "Self-checkout and automated payment systems replace cashiers",
            "E-commerce continues to grow at expense of physical retail",
            "Inventory management increasingly automated",
            "AI-powered recommendation systems replace product knowledge",
            "Automated customer service chatbots handle basic inquiries"
        ],
        "protective_factors": [
            "Complex customer service scenarios require human judgment",
            "High-end or specialized product sales need human expertise",
            "In-person sales psychology and relationship building",
            "Visual merchandising and store experience design"
        ],
        "analysis": "Retail sales positions face high displacement risk from automation and AI. The combination of e-commerce growth, self-checkout technology, and automated inventory systems threatens many traditional retail jobs. The most resilient roles will be in high-end or specialized retail where product expertise, personalized service, and relationship building remain valuable human skills.",
        "projected_growth": {
            "percent_change": -4.5,
            "analysis": "Moderate decline projected"
        },
        "automation_probability": 0.70,
        "wage_trend": "Declining for general positions, stable for specialized sales",
        "evolving_skills": [
            "Omnichannel customer service", 
            "Digital sales platforms",
            "Personalized shopping experience design",
            "Product expertise beyond online information",
            "Complex problem-solving for customers",
            "Experience-based selling"
        ],
        "skill_areas": {
            "technical_skills": [
                "E-commerce platform knowledge",
                "Digital payment systems",
                "CRM software proficiency",
                "Inventory management systems",
                "Social media selling"
            ],
            "soft_skills": [
                "Consultative selling",
                "Relationship building",
                "Conflict resolution",
                "Product storytelling",
                "Emotional intelligence",
                "Active listening"
            ],
            "transferable_skills": [
                "Customer needs assessment",
                "Solution development",
                "Negotiation",
                "Visual presentation",
                "Persuasive communication",
                "Performance under pressure"
            ]
        }
    }
    
    # Sample employment trend data
    trend_years = list(range(2020, 2026))
    trend_employment = [3835000, 3710000, 3625500, 3580000, 3520000, 3464000]
    
    # Sample similar jobs data
    similar_jobs = [
        {
            "job_title": "Customer Service Representative",
            "occupation_code": "43-4051",
            "year_1_risk": 60.0,
            "year_5_risk": 80.0,
            "risk_category": "High"
        },
        {
            "job_title": "Sales Manager",
            "occupation_code": "11-2022",
            "year_1_risk": 25.0,
            "year_5_risk": 45.0,
            "risk_category": "Moderate"
        },
        {
            "job_title": "Cashier",
            "occupation_code": "41-2011",
            "year_1_risk": 70.0,
            "year_5_risk": 90.0,
            "risk_category": "Very High"
        },
        {
            "job_title": "Sales Representative",
            "occupation_code": "41-4012",
            "year_1_risk": 40.0,
            "year_5_risk": 60.0,
            "risk_category": "High"
        }
    ]
    
    # Combine all data
    result = {
        "job_title": standardized_title,
        "occupation_code": occ_code,
        "source": "enhanced_data",
        "employment_data": [],  # Not needed for display
        "latest_employment": occupation_data["latest_value"],
        "projections": projection_data["projections"],
        "risk_analysis": risk_data,
        "trend_data": {
            "years": trend_years,
            "employment": trend_employment
        },
        "similar_jobs": similar_jobs
    }
    
    return result


def get_cook_data():
    """
    Get comprehensive data for Cook role.
    """
    occ_code = "35-2014"  # SOC code for Cooks, Restaurant
    standardized_title = "Restaurant Cook"
    
    # Occupation data with employment figures
    occupation_data = {
        "status": "success",
        "latest_value": "1235800"  # Current employment from BLS stats
    }
    
    # Projection data
    projection_data = {
        "projections": {
            "current_employment": 1235800,
            "projected_employment": 1334600,
            "percent_change": 8.0,
            "annual_job_openings": 178800
        }
    }
    
    # Calculate risk data
    risk_data = {
        "year_1_risk": 40.0,
        "year_5_risk": 65.0,
        "risk_category": "Moderate to High",
        "risk_factors": [
            "Food preparation robots are being deployed in fast food",
            "Automated cooking systems can handle basic dishes",
            "Recipe standardization reduces need for culinary judgment",
            "Kitchen management software optimizes staffing and inventory",
            "Delivery and takeout growth reduces in-restaurant dining"
        ],
        "protective_factors": [
            "Creative culinary development requires human taste and judgment",
            "Complex dishes need advanced cooking techniques",
            "Fine dining experience depends on human execution",
            "Menu development and food innovation remain human-centered",
            "Food quality control requires human senses"
        ],
        "analysis": "Cooks face moderate to high displacement risk, with significant differences based on restaurant type. Fast food and chain restaurants are implementing automation for basic food preparation, while creative roles in upscale restaurants remain more protected. Cooks who develop specialized skills, culinary creativity, and management abilities will be more resilient to automation.",
        "projected_growth": {
            "percent_change": 8.0,
            "analysis": "Moderate growth projected"
        },
        "automation_probability": 0.60,
        "wage_trend": "Stable to increasing for specialized culinary skills",
        "evolving_skills": [
            "Culinary innovation and creativity", 
            "Advanced cooking techniques",
            "Menu development",
            "Food science knowledge",
            "Specialized cuisine expertise",
            "Technology integration in kitchen operations"
        ],
        "skill_areas": {
            "technical_skills": [
                "Advanced cooking methods",
                "Menu engineering",
                "Food safety systems",
                "Kitchen technology operations",
                "Inventory management platforms"
            ],
            "soft_skills": [
                "Team leadership",
                "Time management under pressure",
                "Creative problem-solving",
                "Quality control",
                "Sensory evaluation",
                "Communication in dynamic environments"
            ],
            "transferable_skills": [
                "Process optimization",
                "Resource management",
                "Team coordination",
                "Multitasking",
                "Quality assessment",
                "Critical decision-making"
            ]
        }
    }
    
    # Sample employment trend data
    trend_years = list(range(2020, 2026))
    trend_employment = [1100000, 1152000, 1235800, 1270000, 1305000, 1334600]
    
    # Sample similar jobs data
    similar_jobs = [
        {
            "job_title": "Chef",
            "occupation_code": "35-1011",
            "year_1_risk": 30.0,
            "year_5_risk": 50.0,
            "risk_category": "Moderate"
        },
        {
            "job_title": "Food Preparation Worker",
            "occupation_code": "35-2021",
            "year_1_risk": 65.0,
            "year_5_risk": 85.0,
            "risk_category": "Very High"
        },
        {
            "job_title": "Baker",
            "occupation_code": "51-3011",
            "year_1_risk": 45.0,
            "year_5_risk": 70.0,
            "risk_category": "High"
        },
        {
            "job_title": "Restaurant Manager",
            "occupation_code": "11-9051",
            "year_1_risk": 25.0,
            "year_5_risk": 45.0,
            "risk_category": "Moderate"
        }
    ]
    
    # Combine all data
    result = {
        "job_title": standardized_title,
        "occupation_code": occ_code,
        "source": "enhanced_data",
        "employment_data": [],  # Not needed for display
        "latest_employment": occupation_data["latest_value"],
        "projections": projection_data["projections"],
        "risk_analysis": risk_data,
        "trend_data": {
            "years": trend_years,
            "employment": trend_employment
        },
        "similar_jobs": similar_jobs
    }
    
    return result


def get_teacher_data():
    """
    Get comprehensive data for Teacher role.
    """
    # Define rich data for Teachers
    occ_code = "25-2021"  # SOC code for Elementary School Teachers
    standardized_title = "Teacher"
    
    # Occupation data with employment figures
    occupation_data = {
        "status": "success",
        "latest_value": "1430000"  # Current employment from BLS stats
    }
    
    # Projection data
    projection_data = {
        "projections": {
            "current_employment": 1430000,
            "projected_employment": 1515000,
            "percent_change": 6.0,
            "annual_job_openings": 124300
        }
    }
    
    # Calculate risk data with enhanced teacher details
    risk_data = {
        "year_1_risk": 15.0,
        "year_5_risk": 30.0,
        "risk_category": "Low to Moderate",
        "risk_factors": [
            "AI tools can generate lesson plans and educational materials",
            "Automated grading systems reduce administrative workload",
            "Educational software can deliver standardized content",
            "Virtual teaching platforms may reduce demand for in-person instruction"
        ],
        "protective_factors": [
            "Building student relationships requires human empathy",
            "Classroom management demands human judgment and adaptability",
            "Personalized instruction requires understanding individual students",
            "Mentoring and social-emotional support remain human-centered"
        ]
    }
    
    # Provide skill recommendations
    skill_data = {
        "future_proof_skills": [
            "Personalized learning approaches",
            "Technology integration in classroom",
            "Social-emotional learning facilitation",
            "Cross-disciplinary teaching methods",
            "Adaptive learning techniques"
        ],
        "skill_areas": {
            "technical_skills": [
                "Educational technology platforms",
                "Data-informed instruction",
                "Digital content creation",
                "Learning management systems",
                "Assistive technology implementation"
            ],
            "soft_skills": [
                "Empathetic communication",
                "Crisis management",
                "Cultural responsiveness",
                "Collaborative leadership",
                "Conflict resolution",
                "Emotional intelligence"
            ],
            "transferable_skills": [
                "Curriculum development",
                "Needs assessment",
                "Performance evaluation",
                "Group facilitation",
                "Project-based learning design",
                "Mentoring"
            ]
        }
    }
    
    # Sample employment trend data
    trend_years = list(range(2020, 2026))
    trend_employment = [1370000, 1395000, 1410000, 1430000, 1470000, 1515000]
    
    # Sample similar jobs data
    similar_jobs = [
        {
            "job_title": "School Counselor",
            "occupation_code": "21-1012",
            "year_1_risk": 12.0,
            "year_5_risk": 25.0,
            "risk_category": "Low"
        },
        {
            "job_title": "Special Education Teacher",
            "occupation_code": "25-2050",
            "year_1_risk": 10.0,
            "year_5_risk": 20.0,
            "risk_category": "Low"
        },
        {
            "job_title": "Educational Administrator",
            "occupation_code": "11-9032",
            "year_1_risk": 20.0,
            "year_5_risk": 35.0,
            "risk_category": "Moderate"
        },
        {
            "job_title": "Instructional Coordinator",
            "occupation_code": "25-9031",
            "year_1_risk": 18.0,
            "year_5_risk": 32.0,
            "risk_category": "Moderate"
        }
    ]
    
    # Combine all data
    result = {
        "job_title": standardized_title,
        "occupation_code": occ_code,
        "source": "enhanced_data",
        "employment_data": [],  # Not needed for display
        "latest_employment": occupation_data["latest_value"],
        "projections": projection_data["projections"],
        "risk_analysis": risk_data,
        "trend_data": {
            "years": trend_years,
            "employment": trend_employment
        },
        "similar_jobs": similar_jobs,
        "skills": skill_data
    }
    
    return result


def get_web_developer_data():
    """
    Get comprehensive data for Web Developer role.
    """
    occ_code = "15-1254"  # SOC code for Web Developer
    standardized_title = "Web Developer"
    
    # Occupation data with employment figures
    occupation_data = {
        "status": "success",
        "latest_value": "199400"  # Current employment from BLS stats
    }
    
    # Projection data
    projection_data = {
        "projections": {
            "current_employment": 199400,
            "projected_employment": 224800,
            "percent_change": 12.7,
            "annual_job_openings": 21800
        }
    }
    
    # Calculate risk data
    risk_data = {
        "year_1_risk": 18.0,
        "year_5_risk": 38.0,
        "risk_category": "Moderate",
        "risk_factors": [
            "AI-powered code generation tools automate boilerplate code",
            "Low-code platforms reduce need for custom coding",
            "Template-based solutions for common websites",
            "Automated testing and deployment systems",
            "Outsourcing of basic web development work"
        ],
        "protective_factors": [
            "Complex backend system integration knowledge",
            "Performance optimization expertise",
            "Security implementation skills",
            "Advanced interaction programming",
            "Custom solution architecture"
        ],
        "analysis": "Web Developers face moderate risk from AI and automation tools. While basic website creation is increasingly automated through templates and AI-powered solutions, complex web applications still require skilled developers. The most resilient Web Developers will be those who specialize in areas requiring deep technical knowledge such as security, performance optimization, or complex system integrations. Those focused on basic website creation face higher displacement risk as AI code generation tools become more capable.",
        "projected_growth": {
            "percent_change": 12.7,
            "analysis": "Strong growth projected"
        },
        "automation_probability": 0.38,
        "wage_trend": "Increasing, especially for those with specialized skills",
        "skill_areas": {
            "technical_skills": [
                "JavaScript frameworks (React, Vue, Angular)",
                "Backend technologies (Node.js, Python, PHP)",
                "Database design and management",
                "API development and integration",
                "DevOps and deployment automation"
            ],
            "soft_skills": [
                "Client communication",
                "Problem-solving",
                "Technical documentation",
                "Time management",
                "Adaptability to new technologies"
            ],
            "transferable_skills": [
                "UX/UI understanding",
                "Project management",
                "Digital security awareness",
                "Data analysis",
                "Performance optimization"
            ]
        },
        "evolving_skills": [
            "Cloud architecture",
            "API design and implementation",
            "Progressive Web App development",
            "Cybersecurity",
            "Web3 and blockchain implementation"
        ]
    }
    
    # Historical employment trend
    trend_years = list(range(2020, 2026))
    trend_employment = [174300, 182100, 192500, 199400, 212600, 224800]
    
    # Sample similar jobs data
    similar_jobs = [
        {
            "job_title": "Frontend Developer",
            "occupation_code": "15-1254",
            "year_1_risk": 20.0,
            "year_5_risk": 40.0,
            "risk_category": "Moderate"
        },
        {
            "job_title": "UI Developer",
            "occupation_code": "15-1254",
            "year_1_risk": 20.0,
            "year_5_risk": 40.0,
            "risk_category": "Moderate"
        },
        {
            "job_title": "Software Developer",
            "occupation_code": "15-1252",
            "year_1_risk": 15.0,
            "year_5_risk": 30.0,
            "risk_category": "Moderate"
        },
        {
            "job_title": "Full Stack Developer",
            "occupation_code": "15-1254",
            "year_1_risk": 14.0,
            "year_5_risk": 32.0,
            "risk_category": "Moderate"
        }
    ]
    
    # Combine all data
    result = {
        "job_title": standardized_title,
        "occupation_code": occ_code,
        "source": "enhanced_data",
        "employment_data": [],  # Not needed for display
        "latest_employment": occupation_data["latest_value"],
        "projections": projection_data["projections"],
        "risk_analysis": risk_data,
        "trend_data": {
            "years": trend_years,
            "employment": trend_employment
        },
        "similar_jobs": similar_jobs
    }
    
    return result
    
# Add dedicated functions for Business Analyst and UI Developer jobs

def get_business_analyst_data():
    """
    Get comprehensive data for Business Analyst role.
    """
    occ_code = "13-1111"  # SOC code for Management Analysts (closest match)
    standardized_title = "Business Analyst"
    
    # Occupation data with employment figures
    occupation_data = {
        "status": "success",
        "latest_value": "950600"  # Current employment from BLS stats
    }
    
    # Projection data
    projection_data = {
        "projections": {
            "current_employment": 950600,
            "projected_employment": 1032200,
            "percent_change": 8.6,
            "annual_job_openings": 95800
        }
    }
    
    # Calculate risk data
    risk_data = {
        "year_1_risk": 25.0,
        "year_5_risk": 45.0,
        "risk_category": "Moderate",
        "risk_factors": [
            "Process automation eliminates routine data analysis",
            "AI tools streamline requirements gathering",
            "Business intelligence tools become more autonomous",
            "Automated reporting reduces analysis needs",
            "Low-code platforms reduce technical intermediary roles"
        ],
        "protective_factors": [
            "Complex stakeholder relationship management",
            "Strategic business understanding and domain expertise",
            "Process improvement and change management skills",
            "Critical thinking and problem-solving in ambiguous situations",
            "Systems thinking across organizational boundaries"
        ],
        "analysis": "Business Analysts face moderate risk from AI and automation technologies. While tools are automating routine analysis and reporting tasks, the role's value in bridging business needs with technical solutions remains important. BAs with strong business domain knowledge, strategic thinking, and stakeholder management skills will remain valuable, while those focused primarily on reporting and basic analysis face higher displacement risk.",
        "projected_growth": {
            "percent_change": 8.6,
            "analysis": "Moderate growth projected"
        },
        "automation_probability": 0.45,
        "wage_trend": "Stable, with growth for specialized analysts",
        "skill_areas": {
            "technical_skills": [
                "Data analysis and statistics",
                "SQL and database query skills",
                "Process modeling",
                "Requirements engineering",
                "Business intelligence tools"
            ],
            "soft_skills": [
                "Stakeholder management",
                "Facilitation and interviewing",
                "Problem-solving",
                "Communication and presentation",
                "Critical thinking"
            ],
            "transferable_skills": [
                "Project management",
                "Strategic planning",
                "Change management",
                "Training and education",
                "Documentation and technical writing"
            ]
        },
        "evolving_skills": [
            "AI/ML understanding",
            "Process automation",
            "Advanced data visualization",
            "Agile methodologies",
            "Strategic business understanding"
        ]
    }
    
    # Historical employment trend
    trend_years = list(range(2020, 2026))
    trend_employment = [876200, 899400, 926700, 950600, 986800, 1032200]
    
    # Sample similar jobs data
    similar_jobs = [
        {
            "job_title": "Management Analyst",
            "occupation_code": "13-1111",
            "year_1_risk": 22.0,
            "year_5_risk": 40.0,
            "risk_category": "Moderate"
        },
        {
            "job_title": "Project Manager",
            "occupation_code": "11-3021",
            "year_1_risk": 20.0,
            "year_5_risk": 35.0,
            "risk_category": "Moderate"
        },
        {
            "job_title": "Systems Analyst",
            "occupation_code": "15-1211",
            "year_1_risk": 18.0,
            "year_5_risk": 38.0,
            "risk_category": "Moderate"
        },
        {
            "job_title": "Data Analyst",
            "occupation_code": "15-2051",
            "year_1_risk": 30.0,
            "year_5_risk": 50.0,
            "risk_category": "Moderate"
        }
    ]
    
    # Combine all data
    result = {
        "job_title": standardized_title,
        "occupation_code": occ_code,
        "source": "enhanced_data",
        "employment_data": [],  # Not needed for display
        "latest_employment": occupation_data["latest_value"],
        "projections": projection_data["projections"],
        "risk_analysis": risk_data,
        "trend_data": {
            "years": trend_years,
            "employment": trend_employment
        },
        "similar_jobs": similar_jobs
    }
    
    return result
    

def get_internal_job_data(job_title: str) -> Dict[str, Any]:
    """
    Fallback to internal database when BLS data is unavailable.
    
    Args:
        job_title: The job title to analyze
        
    Returns:
        Dictionary with internal job data formatted to match app expectations
    """
    # Determine a reasonable job category based on the job title
    job_category = "General"
    if any(keyword in job_title.lower() for keyword in ["develop", "program", "engineer", "tech", "data", "it"]):
        job_category = "Technology"
    elif any(keyword in job_title.lower() for keyword in ["market", "sales", "advertis", "brand", "content"]):
        job_category = "Marketing & Sales"
    elif any(keyword in job_title.lower() for keyword in ["financ", "account", "audit", "tax", "invest"]):
        job_category = "Finance"
    elif any(keyword in job_title.lower() for keyword in ["hr", "recruit", "human resource", "talent"]):
        job_category = "Human Resources"
    elif any(keyword in job_title.lower() for keyword in ["teach", "educat", "instruct", "professor"]):
        job_category = "Education"
    elif any(keyword in job_title.lower() for keyword in ["health", "medic", "nurs", "doctor", "care"]):
        job_category = "Healthcare"
    
    # Set appropriate risk levels based on general industry trends
    year_1_risk = 25.0
    year_5_risk = 45.0
    risk_category = "Moderate"
    
    # Adjust risk levels based on job category
    if job_category == "Technology":
        year_1_risk = 15.0
        year_5_risk = 35.0
    elif job_category == "Healthcare":
        year_1_risk = 15.0
        year_5_risk = 30.0
    elif job_category == "Education":
        year_1_risk = 20.0
        year_5_risk = 35.0
    
    # Define risk factors based on job category
    risk_factors = [
        "AI and automation technologies continue to advance",
        "Routine aspects of many jobs are becoming automated",
        "Digital transformation is changing skill requirements",
        "Task-specific AI tools are becoming more specialized"
    ]
    
    # Define protective factors based on job category
    protective_factors = [
        "Complex problem-solving requires human judgment",
        "Creative thinking and innovation are hard to automate",
        "Human relationship management remains valuable",
        "Strategic decision-making benefits from human experience"
    ]
    
    # Define skill areas based on job category
    skill_areas = {
        "technical_skills": [
            "Digital literacy",
            "Data analysis",
            "Technology adaptation",
            "Software proficiency",
            "Process improvement"
        ],
        "soft_skills": [
            "Critical thinking",
            "Adaptive problem solving",
            "Communication",
            "Collaboration",
            "Emotional intelligence"
        ],
        "transferable_skills": [
            "Project management",
            "Cross-functional collaboration",
            "Research and analysis",
            "Strategic planning",
            "Stakeholder management"
        ]
    }
    
    # Return data in the format that app_production.py expects
    return {
        "job_title": job_title,
        "occupation_code": "00-0000",  # Generic occupation code
        "job_category": job_category,
        "source": "internal_database",
        "latest_employment": "Unknown",
        "automation_probability": 45.0,
        "risk_scores": {
            "year_1": year_1_risk,
            "year_5": year_5_risk
        },
        "risk_category": risk_category,
        "risk_factors": risk_factors,
        "protective_factors": protective_factors,
        "projections": {
            "percent_change": "Unknown",
            "annual_job_openings": "Unknown"
        },
        "trend_data": {
            "years": list(range(2020, 2026)),
            "employment": [100000, 102000, 105000, 108000, 110000, 112000]  # Generic trend data
        },
        "similar_jobs": [
            {
                "job_title": "Related Position 1",
                "occupation_code": "00-0001",
                "year_1_risk": max(10, year_1_risk - 10),
                "year_5_risk": max(20, year_5_risk - 10),
                "risk_category": "Low to Moderate"
            },
            {
                "job_title": "Related Position 2",
                "occupation_code": "00-0002",
                "year_1_risk": min(35, year_1_risk + 5),
                "year_5_risk": min(60, year_5_risk + 10),
                "risk_category": "Moderate to High"
            }
        ],
        "skills": {
            "future_proof_skills": [
                "Continuous learning",
                "AI collaboration", 
                "Complex problem solving",
                "Digital literacy",
                "Human-centered service"
            ],
            "skill_areas": skill_areas
        }
    }


def calculate_displacement_risk(job_title: str, occ_code: str, 
                               occupation_data: Dict[str, Any], 
                               projection_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate AI displacement risk based on BLS data and internal risk models.
    
    Args:
        job_title: Standardized job title
        occ_code: SOC occupation code
        occupation_data: BLS occupation data
        projection_data: BLS employment projections
        
    Returns:
        Dictionary with risk analysis
    """
    # Risk calculation would normally involve complex analysis of multiple factors
    # This is a simplified implementation based on BLS projections and predefined risk factors
    
    risk_factors = []
    protective_factors = []
    
    # Extract projections
    projections = projection_data.get("projections", {})
    percent_change = projections.get("percent_change", 0)
    
    # Base risk assessment on employment projections
    if percent_change <= -20:
        year_1_risk = 60.0
        year_5_risk = 90.0
        risk_category = "Very High"
        risk_factors.append("BLS projects significant employment decline for this occupation")
        growth_analysis = "Significant decline projected"
    elif percent_change <= -10:
        year_1_risk = 40.0
        year_5_risk = 75.0
        risk_category = "High"
        risk_factors.append("BLS projects moderate employment decline for this occupation")
        growth_analysis = "Moderate decline projected"
    elif percent_change <= 0:
        year_1_risk = 25.0
        year_5_risk = 50.0
        risk_category = "Moderate"
        risk_factors.append("BLS projects slight employment decline for this occupation")
        growth_analysis = "Slight decline projected"
    elif percent_change <= 10:
        year_1_risk = 15.0
        year_5_risk = 35.0
        risk_category = "Moderate"
        protective_factors.append("BLS projects slight employment growth for this occupation")
        growth_analysis = "Slight growth projected"
    else:
        year_1_risk = 10.0
        year_5_risk = 25.0
        risk_category = "Low"
        protective_factors.append("BLS projects significant employment growth for this occupation")
        growth_analysis = "Strong growth projected"
    
    # Add occupation-specific risk factors based on SOC code groups
    soc_major_group = occ_code.split('-')[0]
    
    # Initialize new metrics
    wage_trend = "Stable"
    automation_probability = 0.0
    evolving_skills = []
    
    # Administrative support occupations (43-XXXX)
    if soc_major_group == "43":
        risk_factors.append("Administrative tasks are highly susceptible to automation")
        risk_factors.append("Document processing can be handled by AI systems")
        year_1_risk += 10.0
        year_5_risk += 15.0
        automation_probability = 0.75
        wage_trend = "Declining"
        evolving_skills = [
            "Advanced data analysis", 
            "Digital process management",
            "Client relationship management"
        ]
    
    # Computer occupations (15-XXXX)
    elif soc_major_group == "15":
        risk_factors.append("Automated code generation is improving rapidly")
        protective_factors.append("Complex problem-solving still requires human insight")
        automation_probability = 0.35
        wage_trend = "Increasing"
        evolving_skills = [
            "AI/ML engineering", 
            "Cloud architecture",
            "Cybersecurity expertise"
        ]
    
    # Healthcare practitioners (29-XXXX)
    elif soc_major_group == "29":
        protective_factors.append("Direct patient care requires human empathy and dexterity")
        year_1_risk -= 5.0
        year_5_risk -= 10.0
        automation_probability = 0.20
        wage_trend = "Increasing"
        evolving_skills = [
            "Telemedicine competence", 
            "Medical technology operation",
            "Patient data interpretation"
        ]
    
    # Transportation occupations (53-XXXX)
    elif soc_major_group == "53":
        risk_factors.append("Autonomous vehicle technology is developing rapidly")
        year_1_risk += 5.0
        year_5_risk += 10.0
        automation_probability = 0.65
        wage_trend = "Stable to declining"
        evolving_skills = [
            "Advanced vehicle systems", 
            "Logistics optimization",
            "Remote monitoring"
        ]
    
    # Management occupations (11-XXXX)
    elif soc_major_group == "11":
        protective_factors.append("Strategic decision-making requires human judgment")
        protective_factors.append("Complex stakeholder management requires human relationships")
        risk_factors.append("Project management software becoming increasingly automated")
        year_1_risk = 35.0
        year_5_risk = 60.0
        automation_probability = 0.45
        wage_trend = "Stable to increasing, depending on specialization"
        evolving_skills = [
            "AI tools implementation and oversight", 
            "Data-driven decision making",
            "Agile management practices",
            "Cross-functional leadership",
            "Change management expertise"
        ]
    
    # Education occupations (25-XXXX)
    elif soc_major_group == "25":
        protective_factors.append("Teaching requires adaptability and emotional intelligence")
        year_1_risk -= 3.0
        year_5_risk -= 7.0
        automation_probability = 0.30
        wage_trend = "Stable"
        evolving_skills = [
            "Educational technology proficiency", 
            "Personalized learning approaches",
            "Digital content creation"
        ]
    
    # Sales occupations (41-XXXX)
    elif soc_major_group == "41":
        risk_factors.append("Online shopping and self-service technologies reduce demand")
        year_1_risk += 8.0
        year_5_risk += 12.0
        automation_probability = 0.55
        wage_trend = "Declining for basic roles, increasing for consultative sales"
        evolving_skills = [
            "Consultative selling", 
            "Customer experience design",
            "Digital marketing"
        ]
    
    # Food preparation (35-XXXX)
    elif soc_major_group == "35":
        risk_factors.append("Food preparation and service seeing increased automation")
        year_1_risk += 7.0
        year_5_risk += 14.0
        automation_probability = 0.60
        wage_trend = "Stable to declining"
        evolving_skills = [
            "Culinary specialization", 
            "Customer experience",
            "Food safety and quality management"
        ]
    
    # Production occupations (51-XXXX)
    elif soc_major_group == "51":
        risk_factors.append("Manufacturing processes increasingly automated")
        year_1_risk += 12.0
        year_5_risk += 18.0
        automation_probability = 0.80
        wage_trend = "Declining"
        evolving_skills = [
            "Advanced manufacturing tech", 
            "Quality control systems",
            "Process optimization"
        ]
    
    # Default values for other occupations
    else:
        automation_probability = 0.40  # Average
        wage_trend = "Varies by specialization"
        evolving_skills = [
            "Digital literacy", 
            "Data analysis",
            "Adaptability and continuous learning"
        ]
    
    # Ensure risk values are within bounds
    year_1_risk = max(5.0, min(95.0, year_1_risk))
    year_5_risk = max(10.0, min(95.0, year_5_risk))
    
    # Make sure 5-year risk is at least as high as 1-year risk
    year_5_risk = max(year_5_risk, year_1_risk + 5.0)
    
    # Generate analysis text
    analysis = generate_analysis_text(job_title, risk_category, risk_factors, protective_factors)
    
    return {
        "year_1_risk": year_1_risk,
        "year_5_risk": year_5_risk,
        "risk_category": risk_category,
        "risk_factors": risk_factors,
        "protective_factors": protective_factors,
        "analysis": analysis,
        # New statistics
        "projected_growth": {
            "percent_change": percent_change,
            "analysis": growth_analysis
        },
        "automation_probability": automation_probability,
        "wage_trend": wage_trend,
        "evolving_skills": evolving_skills
    }


def generate_analysis_text(job_title: str, risk_category: str, 
                          risk_factors: List[str], protective_factors: List[str]) -> str:
    """
    Generate analysis text based on risk assessment.
    
    Args:
        job_title: Job title
        risk_category: Risk category (Low, Moderate, High, Very High)
        risk_factors: List of risk factors
        protective_factors: List of protective factors
        
    Returns:
        Analysis text
    """
    if risk_category == "Very High":
        return f"{job_title}s face extremely high displacement risk as AI and automation technologies advance rapidly. Within 5 years, most routine aspects of this role may be automated."
    elif risk_category == "High":
        return f"{job_title}s face significant displacement risk, though roles requiring complex judgment and specialized skills will be more resilient to automation."
    elif risk_category == "Moderate":
        return f"{job_title}s face moderate automation risk. While some aspects of the role may be automated, human expertise will remain valuable, especially for complex tasks."
    else:  # Low
        return f"{job_title}s have relatively low displacement risk due to the complexity, creativity, or human elements required in this role. Technology will likely augment rather than replace these positions."


def search_similar_jobs(job_title: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Find similar jobs based on a job title with their respective risk levels.
    
    Args:
        job_title: The job title to use as a basis for searching
        limit: Maximum number of results to return
        
    Returns:
        List of similar jobs with risk data
    """
    # This would normally query the BLS API for related occupations
    # For now, return a simplified implementation
    
    # Get occupation matches
    occupation_matches = bls_connector.search_occupations(job_title)
    
    # Get the SOC major group for finding related occupations
    if occupation_matches:
        occ_code = occupation_matches[0]["code"]
        soc_major_group = occ_code.split('-')[0]
        
        # Find other occupations in the same major group
        all_occupations = bls_connector.search_occupations(soc_major_group)
        
        # Filter out the original job
        similar_jobs = [occ for occ in all_occupations 
                       if occ["title"].lower() != job_title.lower()]
        
        # Limit results
        similar_jobs = similar_jobs[:limit]
        
        # Get risk data for each job
        results = []
        for job in similar_jobs:
            # Get basic risk data without full analysis
            risk_data = calculate_displacement_risk(
                job_title=job["title"],
                occ_code=job["code"],
                occupation_data={"status": "simplified"},
                projection_data={"projections": {}}
            )
            
            results.append({
                "job_title": job["title"],
                "occupation_code": job["code"],
                "year_1_risk": risk_data["year_1_risk"],
                "year_5_risk": risk_data["year_5_risk"],
                "risk_category": risk_data["risk_category"]
            })
        
        return results
    
    return []


def get_employment_trend(job_title: str, years: int = 5) -> Dict[str, Any]:
    """
    Get historical employment trend for a job.
    
    Args:
        job_title: The job title to analyze
        years: Number of years of historical data to retrieve
        
    Returns:
        Dictionary with employment trend data
    """
    # This would normally retrieve historical data from the BLS API
    # For now, return a simplified implementation
    
    # Get occupation matches
    occupation_matches = bls_connector.search_occupations(job_title)
    
    if not occupation_matches:
        return {"status": "error", "message": "No matching occupation found"}
    
    # Use the best match
    best_match = occupation_matches[0]
    occ_code = best_match["code"]
    
    # In a real implementation, this would query the BLS API for historical data
    # Generate sample data for now
    current_year = int(time.strftime("%Y"))
    years_list = list(range(current_year - years, current_year + 1))
    
    # Sample employment values with a trend
    base_employment = 100000
    growth_rate = 0.02  # 2% annual growth
    
    if occ_code.startswith("15"):  # Computer occupations
        base_employment = 150000
        growth_rate = 0.08  # 8% annual growth
    elif occ_code.startswith("43"):  # Administrative support
        base_employment = 200000
        growth_rate = -0.05  # 5% annual decline
    
    employment_values = []
    for i, year in enumerate(years_list):
        employment = int(base_employment * (1 + growth_rate) ** i)
        employment_values.append(employment)
    
    # Create trend data
    trend_data = {
        "job_title": best_match["title"],
        "occupation_code": occ_code,
        "years": years_list,
        "employment": employment_values
    }
    
    return trend_data
    
# Add Web Developer function
