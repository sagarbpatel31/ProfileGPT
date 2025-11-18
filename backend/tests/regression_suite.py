"""
ProfileGPT Regression Suite
---------------------------------
Seeds multiple tenants with sample documents and exercises the public API
surface (`/ask`, `/skills`, `/documents`, etc.) to ensure behavioural
regressions are caught early.

Usage:
    python3 backend/tests/regression_suite.py

This script requires the FastAPI app to be running locally at
http://127.0.0.1:8000 (use `uvicorn main:app --reload` inside /backend).
It uses only local data and does not scrape or access external profiles.
"""

import json
import textwrap
from dataclasses import dataclass
from typing import List, Dict
import uuid
import requests

API_BASE = "http://127.0.0.1:8000"


@dataclass
class SeedProfile:
    tenant_name: str
    email: str
    password: str
    documents: List[Dict[str, str]]
    queries: List[str]


SAMPLE_PROFILES = [
    SeedProfile(
        tenant_name="Embedded AI Engineer",
        email="embedded.ai@example.com",
        password="regression1!",
        documents=[
            {
                "title": "Embedded_AI_Profile",
                "source_type": "resume",
                "text": textwrap.dedent(
                    """
                    SUMMARY:
                    Embedded systems engineer combining C/C++, Python automation, and AI/ML research.

                    EXPERIENCE:
                    Cisco Systems - Embedded Software Engineer (2021-2023)
                    - Led board bring-up and validation for switching platforms (PHY, FPGA, PoE).
                    - Created Python automation pipelines and diagnostics CLI in C++.

                    R-Tek Labs - IoT Software Developer (2023-Present)
                    - Integrates Raspberry Pi, STM32, ESP32 devices with cloud APIs.
                    - Built ROS nodes and SLAM stack for GPS-less autonomous drones.

                    RESEARCH:
                    Omdena - Marine plastic detection with ResAttUNet models (>80 IoU).

                    SKILLS:
                    Python, C/C++, ROS, PyTorch, pandas, AWS IoT, Docker.
                    """
                ).strip(),
            }
        ],
        queries=[
            "Rate the scale of C++ skill",
            "Describe AI/ML experience",
            "What projects have you built?",
            "Summarize your education"
        ],
    ),
    SeedProfile(
        tenant_name="Healthcare Data Scientist",
        email="health.ds@example.com",
        password="regression2!",
        documents=[
            {
                "title": "Healthcare_DS_Profile",
                "source_type": "resume",
                "text": textwrap.dedent(
                    """
                    SUMMARY:
                    Healthcare data scientist focusing on patient analytics and predictive models.

                    EXPERIENCE:
                    MedInsight Analytics - Senior Data Scientist (2020-Present)
                    - Built ICU readmission models using LightGBM and clinical features.
                    - Collaborated with clinicians to translate AI insights into decision support dashboards.

                    RESEARCH:
                    Published paper on early sepsis detection using multimodal vitals.

                    SKILLS:
                    Python, SQL, scikit-learn, TensorFlow, healthcare interoperability (FHIR/HL7).
                    """
                ).strip(),
            }
        ],
        queries=[
            "What healthcare experience do you have?",
            "Describe a predictive model project",
            "Rate your SQL expertise"
        ],
    ),
]


def post_json(path: str, payload: Dict):
    response = requests.post(f"{API_BASE}{path}", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def post_file(path: str, payload: Dict):
    response = requests.post(f"{API_BASE}{path}", files=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def seed_profile(profile: SeedProfile) -> str:
    print(f"\n🏗️  Creating tenant: {profile.tenant_name}")
    unique_email = profile.email
    if "@" in profile.email:
        local, domain = profile.email.split("@", 1)
        unique_email = f"{local}+{uuid.uuid4().hex[:6]}@{domain}"
    result = post_json(
        "/tenant",
        {
            "name": profile.tenant_name,
            "email": unique_email,
            "password": profile.password,
            "profession": "Regression Test",
            "bio": f"Auto-seeded profile for {profile.tenant_name}",
        },
    )
    tenant_id = result["tenant_id"]
    print(f"   → tenant_id: {tenant_id}")

    for doc in profile.documents:
        print(f"   → ingesting document: {doc['title']}")
        post_json(
            "/ingest/text",
            {
                "tenant_id": tenant_id,
                "source_type": doc["source_type"],
                "title": doc["title"],
                "content": doc["text"],
            },
        )

    return tenant_id


def run_queries(tenant_id: str, queries: List[str]):
    for question in queries:
        print(f"\n💬 {question}")
        result = post_json(
            "/ask",
            {
                "question": question,
                "tenant_id": tenant_id,
                "mode": "detailed",
            },
        )
        print(json.dumps(result, indent=2))


def main():
    print("=== ProfileGPT Regression Suite ===")
    for profile in SAMPLE_PROFILES:
        tenant_id = seed_profile(profile)
        run_queries(tenant_id, profile.queries)

    print("\n✅ Regression suite completed. Review outputs for anomalies.")


if __name__ == "__main__":
    main()
