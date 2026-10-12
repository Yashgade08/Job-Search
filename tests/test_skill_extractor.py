"""
Unit Tests for NLP Skill Extractor & Taxonomy Matching
"""

import pytest
from nlp.skill_extractor import skill_extractor


def test_extract_technical_skills():
    text = """
    We are seeking a Backend Engineer with 5+ years of experience in Python and Go.
    Must have hands-on experience with FastAPI, PostgreSQL, Docker, and Kubernetes.
    Experience with AWS and Redis is required.
    """
    skills = skill_extractor.extract_skills_from_text(text)
    skill_names = {s["name"] for s in skills}

    assert "Python" in skill_names
    assert "FastAPI" in skill_names
    assert "PostgreSQL" in skill_names
    assert "Docker" in skill_names
    assert "Kubernetes" in skill_names
    assert "AWS" in skill_names
    assert "Redis" in skill_names


def test_required_vs_preferred_classification():
    text = """
    Requirements:
    - Proficient in Python, SQL, and Docker.
    
    Nice to have / Preferred:
    - Exposure to Rust and GraphQL.
    """
    skills = skill_extractor.extract_skills_from_text(text)
    skill_map = {s["name"]: s["is_required"] for s in skills}

    assert skill_map.get("Python") is True
    assert skill_map.get("SQL") is True
    assert skill_map.get("Docker") is True
    assert skill_map.get("Rust") is False
    assert skill_map.get("GraphQL") is False


def test_clean_html_text():
    html_input = "<div><h1>Senior Dev</h1><p>Experience with <b>Python</b> &amp; <i>Docker</i>.</p></div>"
    cleaned = skill_extractor.clean_text(html_input)

    assert "Senior Dev" in cleaned
    assert "Python" in cleaned
    assert "Docker" in cleaned
    assert "<div" not in cleaned
    assert "<p>" not in cleaned


def test_salary_fallback_extraction():
    text = "We offer a competitive compensation between $140,000 to $180,000 per year."
    sal_min, sal_max, currency = skill_extractor.extract_salary_fallback(text)

    assert sal_min == 140000.0
    assert sal_max == 180000.0
    assert currency == "USD"
