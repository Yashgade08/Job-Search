"""
Unit Tests for Content Fingerprinting and Deduplication
"""

import pytest
from crawler.deduplication import generate_content_fingerprint, compute_jaccard_similarity


def test_fingerprint_deterministic():
    fp1 = generate_content_fingerprint(
        title="Software Engineer",
        company="Acme Corp",
        location="Remote",
        description_snippet="Building microservices in Go and Kubernetes."
    )
    fp2 = generate_content_fingerprint(
        title="Software Engineer",
        company="Acme Corp",
        location="Remote",
        description_snippet="Building microservices in Go and Kubernetes."
    )
    assert fp1 == fp2
    assert len(fp1) == 64  # SHA256 length


def test_fingerprint_differs_for_different_jobs():
    fp1 = generate_content_fingerprint("Software Engineer", "Acme Corp", "Remote", "desc 1")
    fp2 = generate_content_fingerprint("Data Scientist", "Beta Corp", "NY", "desc 2")
    assert fp1 != fp2


def test_compute_jaccard_similarity():
    sim = compute_jaccard_similarity("Python Docker Kubernetes", "Python Docker AWS")
    assert 0.0 < sim < 1.0

    sim_identical = compute_jaccard_similarity("Python Docker", "Python Docker")
    assert sim_identical == 1.0


def test_deduplication_filter():
    from crawler.deduplication import DeduplicationFilter, generate_url_fingerprint
    f = DeduplicationFilter()
    fp = "abc123"
    url = "https://example.com/job/1"
    assert f.is_duplicate(fp, url) is False
    f.mark_seen(fp, url)
    assert f.is_duplicate(fp, url) is True
    assert f.count() == 1
