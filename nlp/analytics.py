"""
NLP and Market Intelligence Analytics Aggregations
Computes skill association metrics, co-occurrence graph models, and market distributions.
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict
import math


def calculate_skill_associations(co_occurrence_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Computes Jaccard Similarity and Association Lift for co-occurring skills:
    Lift(A, B) = P(A & B) / (P(A) * P(B))
    Jaccard(A, B) = Co(A, B) / (Count(A) + Count(B) - Co(A, B))
    """
    matrix = co_occurrence_data.get("matrix", {})
    skills = co_occurrence_data.get("skills", [])
    associations = []

    for i in range(len(skills)):
        s1 = skills[i]
        count_s1 = matrix.get(s1, {}).get(s1, 0)
        if count_s1 == 0:
            continue

        for j in range(i + 1, len(skills)):
            s2 = skills[j]
            count_s2 = matrix.get(s2, {}).get(s2, 0)
            if count_s2 == 0:
                continue

            co_count = matrix.get(s1, {}).get(s2, 0)
            if co_count > 0:
                jaccard = round(co_count / (count_s1 + count_s2 - co_count), 3)
                associations.append({
                    "skill_a": s1,
                    "skill_b": s2,
                    "co_occurrence": co_count,
                    "jaccard_similarity": jaccard,
                })

    associations.sort(key=lambda x: x["co_occurrence"], reverse=True)
    return associations
