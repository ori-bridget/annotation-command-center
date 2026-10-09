from __future__ import annotations

import re
from typing import Any


JOBS = [
    {"job_id": "JOB-2048", "batch": "Batch Alpha", "category": "2D Bounding Box", "assignee": "Linh", "status": "Completed", "score": 96, "edits": 1, "age": 2, "hard": False},
    {"job_id": "JOB-2049", "batch": "Batch Alpha", "category": "2D Bounding Box", "assignee": "Minh", "status": "In review", "score": 84, "edits": 3, "age": 4, "hard": True},
    {"job_id": "JOB-2050", "batch": "Batch Alpha", "category": "2D Bounding Box", "assignee": "An", "status": "Completed", "score": 91, "edits": 1, "age": 1, "hard": False},
    {"job_id": "JOB-2051", "batch": "Batch Alpha", "category": "Tracking", "assignee": "Linh", "status": "In progress", "score": 78, "edits": 5, "age": 6, "hard": True},
    {"job_id": "JOB-2052", "batch": "Batch Alpha", "category": "Tracking", "assignee": "Minh", "status": "Blocked", "score": 72, "edits": 4, "age": 8, "hard": True},
    {"job_id": "JOB-2053", "batch": "Batch Alpha", "category": "Tracking", "assignee": "An", "status": "Completed", "score": 94, "edits": 0, "age": 2, "hard": False},
    {"job_id": "JOB-2054", "batch": "Batch Alpha", "category": "3D LiDAR", "assignee": "Linh", "status": "In progress", "score": 88, "edits": 2, "age": 3, "hard": False},
    {"job_id": "JOB-2055", "batch": "Batch Alpha", "category": "3D LiDAR", "assignee": "Minh", "status": "In review", "score": 76, "edits": 4, "age": 5, "hard": True},
]

ISSUES = [
    {"id": "#184", "title": "Occluded object: when should it be labeled?", "label": "annotation-question", "status": "Open", "job_id": "JOB-2051", "category": "Tracking"},
    {"id": "#181", "title": "Track ID changes after full occlusion", "label": "annotation-question", "status": "Open", "job_id": "JOB-2052", "category": "Tracking"},
    {"id": "#176", "title": "Small object threshold clarification", "label": "guideline", "status": "Resolved", "job_id": "JOB-2049", "category": "2D Bounding Box"},
    {"id": "#171", "title": "Add validation sample for truncation", "label": "process", "status": "Resolved", "job_id": "JOB-2048", "category": "2D Bounding Box"},
    {"id": "#188", "title": "Sparse point cloud: minimum evidence for a cuboid", "label": "annotation-question", "status": "Open", "job_id": "JOB-2055", "category": "3D LiDAR"},
]

GUIDELINES = [
    {"doc": "2D Bounding Box Guideline", "version": "v2.1", "week": "Week 41", "category": "2D Bounding Box", "section": "Occlusion", "page": "p. 8", "text": "When an object is partially occluded but enough visual evidence remains to identify its visible extent, annotate the visible bounding box and mark the occlusion attribute as true."},
    {"doc": "2D Bounding Box Guideline", "version": "v2.1", "week": "Week 41", "category": "2D Bounding Box", "section": "Small objects", "page": "p. 11", "text": "Objects smaller than 6 by 6 pixels should not be annotated unless they are part of an already established tracking sequence."},
    {"doc": "Tracking Guideline", "version": "v1.4", "week": "Week 41", "category": "Tracking", "section": "Full occlusion", "page": "p. 14", "text": "Keep the same track ID through a full occlusion when the object can be confidently matched after it reappears. Start a new track only when the identity cannot be determined."},
    {"doc": "Tracking Guideline", "version": "v1.4", "week": "Week 40", "category": "Tracking", "section": "Track creation", "page": "p. 5", "text": "Create a new track when an object first enters the visible scene. Do not reuse a previous ID when identity is uncertain."},
    {"doc": "3D LiDAR Guideline", "version": "v1.0", "week": "Week 41", "category": "3D LiDAR", "section": "Sparse point cloud", "page": "p. 6", "text": "Annotate a 3D cuboid only when the point cloud provides enough evidence to determine the object's center, dimensions, and orientation. Do not infer a cuboid from a few isolated points."},
    {"doc": "3D LiDAR Guideline", "version": "v1.0", "week": "Week 41", "category": "3D LiDAR", "section": "Occlusion", "page": "p. 9", "text": "For a partially occluded object, fit the cuboid to the visible point cloud and use contextual evidence only when the guideline-defined object extent is still identifiable."},
]


def filtered_jobs(batch: str, category: str) -> list[dict[str, Any]]:
    return [job for job in JOBS if (batch == "All batches" or job["batch"] == batch) and (category == "All categories" or job["category"] == category)]


def filtered_issues(category: str) -> list[dict[str, Any]]:
    return [issue for issue in ISSUES if category == "All categories" or issue["category"] == category]


def filtered_guidelines(guidelines: list[dict[str, Any]], week: str, category: str, question: str) -> list[dict[str, Any]]:
    terms = set(re.findall(r"[\wÀ-ỹ]+", question.lower()))
    candidates = []
    for item in guidelines:
        if week != "All weeks" and item["week"] != week:
            continue
        if category != "All categories" and item["category"] != category:
            continue
        corpus = f"{item['section']} {item['text']}".lower()
        score = sum(1 for term in terms if len(term) > 2 and term in corpus)
        if score:
            candidates.append((score, item))
    return [item for _, item in sorted(candidates, key=lambda value: value[0], reverse=True)]
