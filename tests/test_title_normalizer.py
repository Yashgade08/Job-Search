"""
Unit Tests for Job Title Normalizer and Seniority Classification
"""

import pytest
from nlp.title_normalizer import normalize_job_title, extract_experience_years


def test_role_categorization():
    title1 = "Senior Machine Learning Engineer (LLMs)"
    norm1, role1, exp1 = normalize_job_title(title1)
    assert role1 == "Machine Learning Engineer"
    assert exp1 == "Senior"

    title2 = "Staff Backend Engineer"
    norm2, role2, exp2 = normalize_job_title(title2)
    assert role2 == "Backend Developer"
    assert exp2 == "Lead / Staff"

    title3 = "Lead DevOps & SRE Specialist"
    norm3, role3, exp3 = normalize_job_title(title3)
    assert role3 == "DevOps / SRE"
    assert exp3 == "Lead / Staff"

    title4 = "Junior Frontend Developer (React)"
    norm4, role4, exp4 = normalize_job_title(title4)
    assert role4 == "Frontend Developer"
    assert exp4 == "Entry-Level"


def test_experience_years_extraction():
    text1 = "Candidate should have 5+ years of software development experience."
    min_exp, max_exp = extract_experience_years(text1)
    assert min_exp == 5.0

    text2 = "Looking for someone with 3 to 7 years in cloud infrastructure."
    min_exp2, max_exp2 = extract_experience_years(text2)
    assert min_exp2 == 3.0
    assert max_exp2 == 7.0
