#!/usr/bin/env python3
"""
Comprehensive regression testing suite for ProfileGPT
Tests different professions, skills, and conceptual knowledge scenarios
"""

import requests
import json
import time
import random
import string
from typing import Dict, List, Any
import tempfile
import os
from datetime import datetime

class ProfileGPTTester:
    def __init__(self, base_url="https://profilegpt-production.up.railway.app"):
        self.base_url = base_url
        self.test_results = []
        self.tenants = {}

    def log_result(self, test_name: str, status: str, details: Dict[str, Any] = None):
        """Log test results"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)

        # Color-coded console output
        color = "\033[92m" if status == "PASS" else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{status}: {test_name}{reset}")
        if details and "error" in details:
            print(f"  Error: {details['error']}")
        elif details and "message" in details:
            print(f"  {details['message']}")
        print()

    def create_test_document_content(self, profession: str, person_name: str) -> str:
        """Generate realistic resume content for different professions"""

        profession_data = {
            "software_engineer": {
                "skills": ["Python", "React", "AWS", "Docker", "Kubernetes", "PostgreSQL", "Machine Learning", "REST APIs", "Git", "Agile"],
                "experience": [
                    "Built scalable web applications serving 100K+ users",
                    "Implemented CI/CD pipelines reducing deployment time by 75%",
                    "Led team of 5 developers on microservices architecture project",
                    "Optimized database queries improving performance by 40%"
                ],
                "projects": [
                    "E-commerce platform with real-time inventory management",
                    "Machine learning recommendation system",
                    "Kubernetes cluster management dashboard"
                ]
            },
            "data_scientist": {
                "skills": ["Python", "R", "TensorFlow", "PyTorch", "SQL", "Statistics", "Machine Learning", "Deep Learning", "Tableau", "Jupyter"],
                "experience": [
                    "Developed predictive models improving business forecasting accuracy by 30%",
                    "Analyzed customer behavior data to drive product recommendations",
                    "Built real-time anomaly detection system for fraud prevention",
                    "Created automated reporting dashboards for C-level executives"
                ],
                "projects": [
                    "Customer churn prediction model with 85% accuracy",
                    "Natural language processing system for sentiment analysis",
                    "Computer vision pipeline for quality control"
                ]
            },
            "product_manager": {
                "skills": ["Product Strategy", "User Research", "Agile", "Roadmap Planning", "Analytics", "A/B Testing", "Stakeholder Management", "Market Research"],
                "experience": [
                    "Launched 3 major product features resulting in 25% user engagement increase",
                    "Managed cross-functional teams of 15+ members across engineering and design",
                    "Conducted user interviews and market research to identify new opportunities",
                    "Defined product requirements and specifications for mobile applications"
                ],
                "projects": [
                    "Mobile app redesign increasing user retention by 40%",
                    "API platform serving 50+ enterprise clients",
                    "B2B dashboard with advanced analytics capabilities"
                ]
            },
            "marketing_manager": {
                "skills": ["Digital Marketing", "SEO/SEM", "Social Media Marketing", "Content Strategy", "Google Analytics", "Email Marketing", "Brand Management", "Campaign Management"],
                "experience": [
                    "Increased organic website traffic by 150% through SEO optimization",
                    "Managed $500K annual marketing budget across multiple channels",
                    "Developed content strategy resulting in 300% social media growth",
                    "Led rebranding initiative improving brand awareness by 60%"
                ],
                "projects": [
                    "Multi-channel campaign generating $2M in new revenue",
                    "Influencer marketing program with 50+ partnerships",
                    "Marketing automation system improving lead conversion by 35%"
                ]
            },
            "financial_analyst": {
                "skills": ["Financial Modeling", "Excel", "SQL", "Python", "Bloomberg Terminal", "Risk Analysis", "Valuation", "Financial Reporting", "Tableau", "VBA"],
                "experience": [
                    "Built complex financial models for M&A transactions worth $100M+",
                    "Conducted variance analysis identifying cost savings of $2M annually",
                    "Prepared quarterly financial reports for board presentations",
                    "Analyzed investment opportunities with IRR calculations and scenario modeling"
                ],
                "projects": [
                    "Automated financial reporting system reducing manual work by 70%",
                    "Risk assessment model for credit portfolio management",
                    "Budget planning tool with real-time variance tracking"
                ]
            }
        }

        data = profession_data.get(profession.lower(), profession_data["software_engineer"])

        # Generate realistic resume content
        content = f"""
{person_name}
Senior {profession.replace('_', ' ').title()}
Email: {person_name.lower().replace(' ', '.')}@email.com
Phone: (555) 123-4567
LinkedIn: linkedin.com/in/{person_name.lower().replace(' ', '')}

PROFESSIONAL SUMMARY
Experienced {profession.replace('_', ' ')} with 8+ years of expertise in {', '.join(data['skills'][:5])}.
Proven track record of delivering high-impact solutions and leading cross-functional teams to achieve business objectives.

TECHNICAL SKILLS
• Programming/Tools: {', '.join(data['skills'][:8])}
• Methodologies: Agile, Scrum, DevOps, Lean
• Other: Team Leadership, Strategic Planning, Problem Solving

PROFESSIONAL EXPERIENCE

Senior {profession.replace('_', ' ').title()} | TechCorp Inc. | 2020 - Present
• {data['experience'][0]}
• {data['experience'][1]}
• {data['experience'][2]}
• {data['experience'][3]}

{profession.replace('_', ' ').title()} | InnovateIT Solutions | 2018 - 2020
• Collaborated with product teams to deliver scalable solutions
• Mentored junior team members and conducted code reviews
• Participated in architecture decisions and technology selection
• Contributed to company's technical blog and knowledge sharing

Junior {profession.replace('_', ' ').title()} | StartupXYZ | 2016 - 2018
• Gained hands-on experience with {', '.join(data['skills'][2:5])}
• Worked on {data['projects'][0].lower()}
• Participated in daily standups and sprint planning
• Contributed to open-source projects and community events

EDUCATION
Bachelor of Science in Computer Science | University of Technology | 2016
• Relevant Coursework: Data Structures, Algorithms, Database Systems, Software Engineering
• Dean's List: Fall 2015, Spring 2016
• Senior Project: {data['projects'][1]}

CERTIFICATIONS
• AWS Certified Solutions Architect
• Certified Scrum Master (CSM)
• {profession.replace('_', ' ').title()} Professional Certification

PROJECT HIGHLIGHTS
1. {data['projects'][0]}
   - Technologies: {', '.join(data['skills'][:4])}
   - Impact: Increased efficiency by 45% and reduced costs by $200K annually

2. {data['projects'][1]}
   - Technologies: {', '.join(data['skills'][2:6])}
   - Impact: Improved user experience and received industry recognition

3. {data['projects'][2]}
   - Technologies: {', '.join(data['skills'][1:5])}
   - Impact: Streamlined operations and enhanced decision-making capabilities

AWARDS & RECOGNITION
• Employee of the Year 2022 - TechCorp Inc.
• Innovation Award for Outstanding Technical Achievement - 2021
• Speaker at TechConf 2023 on "{profession.replace('_', ' ').title()} Best Practices"
"""
        return content.strip()

    def create_test_tenant(self, profession: str) -> Dict[str, Any]:
        """Create a test tenant for a specific profession"""

        person_names = [
            "Alex Johnson", "Sarah Chen", "Michael Rodriguez", "Emily Davis",
            "David Kim", "Jessica Thompson", "Ryan O'Connor", "Maria Garcia"
        ]

        name = random.choice(person_names)
        email = f"test.{profession}.{random.randint(1000, 9999)}@testmail.com"

        tenant_data = {
            "name": name,
            "email": email,
            "password": "TestPassword123!",
            "profession": profession.replace('_', ' ').title(),
            "bio": f"Experienced {profession.replace('_', ' ')} passionate about technology and innovation."
        }

        try:
            response = requests.post(f"{self.base_url}/tenant", json=tenant_data, timeout=30)
            if response.status_code == 200:
                tenant_info = response.json()
                tenant_info["test_person_name"] = name
                self.tenants[tenant_info["tenant_id"]] = tenant_info
                self.log_result(f"Create {profession} tenant", "PASS", {
                    "tenant_id": tenant_info["tenant_id"],
                    "name": name,
                    "message": f"Created tenant {tenant_info['tenant_id']}"
                })
                return tenant_info
            else:
                self.log_result(f"Create {profession} tenant", "FAIL", {
                    "error": f"HTTP {response.status_code}: {response.text}"
                })
                return None
        except Exception as e:
            self.log_result(f"Create {profession} tenant", "FAIL", {
                "error": str(e)
            })
            return None

    def upload_test_document(self, tenant_info: Dict[str, Any], profession: str) -> bool:
        """Upload test document for a tenant"""

        if not tenant_info:
            return False

        tenant_id = tenant_info["tenant_id"]
        person_name = tenant_info["test_person_name"]

        # Generate realistic document content
        content = self.create_test_document_content(profession, person_name)

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_file_path = f.name

        try:
            with open(temp_file_path, 'rb') as file:
                files = {
                    'file': (f'{person_name.replace(" ", "_")}_resume.txt', file, 'text/plain')
                }
                data = {
                    'source_type': 'resume',
                    'tenant_id': tenant_id,
                    'title': f'{person_name} - Senior {profession.replace("_", " ").title()} Resume'
                }

                response = requests.post(f"{self.base_url}/ingest", files=files, data=data, timeout=60)

                if response.status_code == 200:
                    result = response.json()
                    self.log_result(f"Upload {profession} document", "PASS", {
                        "tenant_id": tenant_id,
                        "document_id": result.get("document_id"),
                        "chunks": result.get("chunk_count"),
                        "message": f"Uploaded and processed document with {result.get('chunk_count', 0)} chunks"
                    })
                    return True
                else:
                    self.log_result(f"Upload {profession} document", "FAIL", {
                        "tenant_id": tenant_id,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    })
                    return False

        except Exception as e:
            self.log_result(f"Upload {profession} document", "FAIL", {
                "tenant_id": tenant_id,
                "error": str(e)
            })
            return False
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass

    def test_qa_scenarios(self, tenant_info: Dict[str, Any], profession: str):
        """Test Q&A functionality with various scenarios"""

        if not tenant_info:
            return

        tenant_id = tenant_info["tenant_id"]
        person_name = tenant_info["test_person_name"]

        # Define test scenarios for each profession
        test_scenarios = {
            "software_engineer": [
                ("What programming languages do you know?", "short"),
                ("Tell me about your experience with cloud technologies", "detailed"),
                ("Describe a challenging project you worked on", "star"),
                ("What is your experience with Docker and Kubernetes?", "detailed"),
                ("How many years of experience do you have?", "short"),
                ("What databases have you worked with?", "short")
            ],
            "data_scientist": [
                ("What machine learning frameworks do you use?", "short"),
                ("Tell me about your experience with predictive modeling", "detailed"),
                ("Describe a data science project that had business impact", "star"),
                ("What statistical analysis tools do you know?", "detailed"),
                ("Have you worked with deep learning?", "short"),
                ("What visualization tools do you use?", "short")
            ],
            "product_manager": [
                ("What is your experience with product strategy?", "detailed"),
                ("Tell me about a successful product launch", "star"),
                ("How do you prioritize product features?", "detailed"),
                ("What analytics tools do you use?", "short"),
                ("Have you managed cross-functional teams?", "short"),
                ("What is your approach to user research?", "detailed")
            ],
            "marketing_manager": [
                ("What digital marketing channels do you specialize in?", "short"),
                ("Tell me about a successful marketing campaign", "star"),
                ("What is your experience with SEO?", "detailed"),
                ("What marketing tools and platforms do you use?", "detailed"),
                ("How do you measure campaign performance?", "detailed"),
                ("Have you managed marketing budgets?", "short")
            ],
            "financial_analyst": [
                ("What financial modeling experience do you have?", "detailed"),
                ("Tell me about a complex analysis you conducted", "star"),
                ("What financial software do you use?", "short"),
                ("How do you approach risk assessment?", "detailed"),
                ("Have you worked with investment analysis?", "short"),
                ("What reporting tools do you know?", "short")
            ]
        }

        scenarios = test_scenarios.get(profession, test_scenarios["software_engineer"])

        for question, mode in scenarios:
            try:
                qa_data = {
                    "question": question,
                    "mode": mode,
                    "tenant_id": tenant_id
                }

                response = requests.post(f"{self.base_url}/ask", json=qa_data, timeout=45)

                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("answer", "")
                    citations = result.get("citations", [])

                    # Quality checks
                    quality_issues = []
                    if len(answer) < 20:
                        quality_issues.append("Answer too short")
                    if "I don't have that information" in answer and len(citations) > 0:
                        quality_issues.append("Claims no info but has citations")
                    if mode == "short" and len(answer) > 300:
                        quality_issues.append("Short mode response too long")
                    if mode == "star" and not any(keyword in answer.lower() for keyword in ["situation", "task", "action", "result", "project", "challenge"]):
                        quality_issues.append("STAR mode doesn't follow format")

                    status = "PASS" if not quality_issues else "WARN"

                    self.log_result(f"Q&A: {question[:50]}... ({profession})", status, {
                        "tenant_id": tenant_id,
                        "mode": mode,
                        "answer_length": len(answer),
                        "citations_count": len(citations),
                        "quality_issues": quality_issues,
                        "message": f"Answer: {answer[:100]}..." if len(answer) > 100 else answer
                    })

                else:
                    self.log_result(f"Q&A: {question[:50]}... ({profession})", "FAIL", {
                        "tenant_id": tenant_id,
                        "error": f"HTTP {response.status_code}: {response.text}"
                    })

                # Small delay between requests
                time.sleep(1)

            except Exception as e:
                self.log_result(f"Q&A: {question[:50]}... ({profession})", "FAIL", {
                    "tenant_id": tenant_id,
                    "error": str(e)
                })

    def test_document_retrieval(self, tenant_id: str, profession: str):
        """Test document retrieval functionality"""

        try:
            response = requests.get(f"{self.base_url}/documents/{tenant_id}", timeout=30)

            if response.status_code == 200:
                result = response.json()
                documents = result.get("documents", [])

                if len(documents) > 0:
                    self.log_result(f"Document retrieval ({profession})", "PASS", {
                        "tenant_id": tenant_id,
                        "document_count": len(documents),
                        "message": f"Retrieved {len(documents)} documents"
                    })
                else:
                    self.log_result(f"Document retrieval ({profession})", "WARN", {
                        "tenant_id": tenant_id,
                        "error": "No documents found"
                    })
            else:
                self.log_result(f"Document retrieval ({profession})", "FAIL", {
                    "tenant_id": tenant_id,
                    "error": f"HTTP {response.status_code}: {response.text}"
                })

        except Exception as e:
            self.log_result(f"Document retrieval ({profession})", "FAIL", {
                "tenant_id": tenant_id,
                "error": str(e)
            })

    def test_health_check(self):
        """Test basic health check"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                self.log_result("Health Check", "PASS", {
                    "message": "Backend is responsive"
                })
                return True
            else:
                self.log_result("Health Check", "FAIL", {
                    "error": f"HTTP {response.status_code}"
                })
                return False
        except Exception as e:
            self.log_result("Health Check", "FAIL", {
                "error": str(e)
            })
            return False

    def run_comprehensive_tests(self):
        """Run full test suite across multiple professions"""

        print("🧪 Starting ProfileGPT Comprehensive Testing Suite")
        print("=" * 60)

        # Test health first
        if not self.test_health_check():
            print("❌ Backend health check failed. Exiting...")
            return

        # Test different professions
        professions = [
            "software_engineer",
            "data_scientist",
            "product_manager",
            "marketing_manager",
            "financial_analyst"
        ]

        for profession in professions:
            print(f"\n📋 Testing {profession.replace('_', ' ').title()} Profile")
            print("-" * 40)

            # Create tenant
            tenant_info = self.create_test_tenant(profession)
            if not tenant_info:
                continue

            # Upload document
            if self.upload_test_document(tenant_info, profession):
                # Wait for processing
                time.sleep(3)

                # Test document retrieval
                self.test_document_retrieval(tenant_info["tenant_id"], profession)

                # Test Q&A scenarios
                self.test_qa_scenarios(tenant_info, profession)

            print()

        # Print summary
        self.print_test_summary()

    def print_test_summary(self):
        """Print comprehensive test results summary"""

        print("\n" + "=" * 60)
        print("🏁 TEST SUMMARY")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        warned = len([r for r in self.test_results if r["status"] == "WARN"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])

        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"⚠️  Warnings: {warned}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total_tests*100):.1f}%")

        if failed > 0:
            print(f"\n❌ FAILED TESTS:")
            for result in self.test_results:
                if result["status"] == "FAIL":
                    print(f"  • {result['test_name']}: {result['details'].get('error', 'Unknown error')}")

        if warned > 0:
            print(f"\n⚠️  WARNINGS:")
            for result in self.test_results:
                if result["status"] == "WARN":
                    print(f"  • {result['test_name']}: {result['details'].get('error', 'Quality issue')}")

        print(f"\n📊 Tenants Created: {len(self.tenants)}")
        for tenant_id, tenant_info in self.tenants.items():
            print(f"  • {tenant_info['name']} ({tenant_info['profession']}) - ID: {tenant_id}")

def main():
    tester = ProfileGPTTester()
    tester.run_comprehensive_tests()

if __name__ == "__main__":
    main()