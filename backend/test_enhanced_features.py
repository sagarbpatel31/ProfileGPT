#!/usr/bin/env python3
"""
Enhanced feature testing for ProfileGPT improvements
Tests STAR methodology, advanced document processing, and response quality
"""

import requests
import json
import time
import random
from datetime import datetime

class EnhancedProfileGPTTester:
    def __init__(self, base_url="https://profilegpt-production.up.railway.app"):
        self.base_url = base_url
        self.test_results = []

    def log_result(self, test_name: str, status: str, details: dict = None):
        """Log test results with detailed analysis"""
        result = {
            "test_name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)

        color = "\033[92m" if status == "PASS" else "\033[93m" if status == "WARN" else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{status}: {test_name}{reset}")

        if details:
            if "answer" in details:
                print(f"  📝 Answer: {details['answer'][:100]}...")
            if "chunk_count" in details:
                print(f"  📊 Chunks: {details['chunk_count']}")
            if "metrics_found" in details:
                print(f"  📈 Metrics: {details['metrics_found']}")
            if "star_format_score" in details:
                print(f"  ⭐ STAR Score: {details['star_format_score']}/10")
        print()

    def create_enhanced_test_tenant(self) -> dict:
        """Create test tenant for enhanced feature testing"""

        tenant_data = {
            "name": "Dr. Alex Chen",
            "email": f"enhanced.test.{random.randint(1000, 9999)}@testmail.com",
            "password": "TestPassword123!",
            "profession": "Senior Software Engineer & Tech Lead",
            "bio": "Experienced software engineer with expertise in AI/ML and team leadership."
        }

        try:
            response = requests.post(f"{self.base_url}/tenant", json=tenant_data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                self.log_result("Create Enhanced Test Tenant", "PASS", {
                    "tenant_id": result["tenant_id"],
                    "message": "Created enhanced test tenant"
                })
                return result
            else:
                self.log_result("Create Enhanced Test Tenant", "FAIL", {
                    "error": f"HTTP {response.status_code}"
                })
                return None
        except Exception as e:
            self.log_result("Create Enhanced Test Tenant", "FAIL", {"error": str(e)})
            return None

    def upload_comprehensive_resume(self, tenant_info: dict) -> bool:
        """Upload a comprehensive resume for testing enhanced features"""

        if not tenant_info:
            return False

        # Create comprehensive resume content with STAR examples
        resume_content = """
DR. ALEX CHEN
Senior Software Engineer & Technical Lead
Email: alex.chen@techcorp.com | Phone: (555) 987-6543
LinkedIn: linkedin.com/in/alexchen | GitHub: github.com/alexchen

PROFESSIONAL SUMMARY
Experienced Senior Software Engineer with 8+ years of expertise in Python, machine learning, and distributed systems. Led cross-functional teams of 12+ engineers, delivering scalable solutions serving 2M+ users. Specialized in AI/ML implementation, microservices architecture, and performance optimization resulting in 40% efficiency improvements.

TECHNICAL SKILLS
• Programming Languages: Python, JavaScript, TypeScript, Go, Java, SQL
• ML/AI Frameworks: TensorFlow, PyTorch, Scikit-learn, Hugging Face, OpenAI API
• Cloud & Infrastructure: AWS (EC2, S3, Lambda, RDS), Docker, Kubernetes, Terraform
• Databases: PostgreSQL, MongoDB, Redis, Elasticsearch, Vector databases
• Web Technologies: React, Node.js, FastAPI, GraphQL, REST APIs
• Tools: Git, Jenkins, JIRA, Prometheus, Grafana, MLflow

PROFESSIONAL EXPERIENCE

Senior Software Engineer & Technical Lead | TechCorp Solutions | March 2020 - Present
• Led development of AI-powered recommendation system serving 2.5M users, increasing engagement by 35%
• Managed team of 8 developers across 3 time zones, implementing agile practices reducing delivery time by 50%
• Architected microservices platform handling 50M+ API calls daily with 99.9% uptime
• Optimized machine learning pipelines reducing model training time from 6 hours to 45 minutes
• Implemented automated testing strategy increasing code coverage from 60% to 95%
• Mentored 5 junior engineers, with 4 receiving promotions within 18 months

SITUATION: Legacy monolithic application was causing performance bottlenecks and hindering team productivity
TASK: Migrate to microservices architecture while maintaining zero downtime and improving system performance
ACTION: Designed and implemented gradual migration strategy using Docker containers and Kubernetes orchestration
RESULT: Achieved 40% performance improvement, reduced deployment time from 2 hours to 15 minutes, and enabled team to deploy 3x more frequently

Senior Software Engineer | InnovateTech Inc. | June 2018 - February 2020
• Developed real-time analytics platform processing 100GB+ data daily using Apache Spark
• Built machine learning models for fraud detection achieving 92% accuracy and preventing $2M+ losses
• Created automated CI/CD pipelines using Jenkins reducing manual deployment errors by 85%
• Collaborated with product team to define technical requirements for 5 major feature releases
• Implemented caching strategies using Redis improving API response times by 60%

Software Engineer | DataSoft Corp | September 2016 - May 2018
• Built data processing pipelines handling 10M+ records daily using Python and PostgreSQL
• Developed RESTful APIs serving mobile applications with 500K+ active users
• Implemented monitoring and alerting systems using Prometheus and Grafana
• Participated in code reviews and maintained coding standards across the development team
• Contributed to open-source projects including popular Python libraries

EDUCATION
Master of Science in Computer Science (AI/ML Specialization) | Stanford University | 2016
• Thesis: "Deep Learning for Natural Language Processing in Healthcare"
• Relevant Coursework: Machine Learning, Deep Learning, Distributed Systems, Algorithms
• GPA: 3.8/4.0

Bachelor of Science in Computer Engineering | UC Berkeley | 2014
• Senior Project: "Real-time Image Recognition System using Convolutional Neural Networks"
• Dean's List: Fall 2013, Spring 2014

PROJECT HIGHLIGHTS

AI-Powered Customer Support Chatbot (2023)
SITUATION: Customer support team was overwhelmed with 10,000+ daily tickets, causing delayed responses
TASK: Develop intelligent chatbot to handle routine inquiries and reduce support workload by 60%
ACTION: Implemented GPT-based chatbot using OpenAI API, integrated with company knowledge base and CRM
RESULT: Reduced ticket volume by 65%, improved response time from 4 hours to under 30 seconds, saved $500K annually

Real-time Fraud Detection System (2022)
• Technologies: Python, TensorFlow, Apache Kafka, Redis, AWS Lambda
• Processed 1M+ transactions per day with sub-100ms latency
• Achieved 94% fraud detection accuracy with 0.1% false positive rate
• Prevented estimated $3M+ in fraudulent transactions annually

Scalable Microservices Architecture (2021)
• Technologies: Docker, Kubernetes, Go, PostgreSQL, gRPC
• Migrated monolithic application to 15 microservices
• Improved system reliability from 95% to 99.9% uptime
• Reduced infrastructure costs by 30% through efficient resource utilization

CERTIFICATIONS & AWARDS
• AWS Certified Solutions Architect - Professional (2023)
• Google Cloud Professional Machine Learning Engineer (2022)
• Certified Kubernetes Administrator (CKA) (2021)
• Employee of the Year 2022 - TechCorp Solutions
• Innovation Award for Outstanding Technical Achievement - 2023

PUBLICATIONS & SPEAKING
• "Scaling Machine Learning in Production" - MLConf 2023 (Keynote Speaker)
• "Microservices Best Practices" - IEEE Software Magazine (2022)
• "Deep Learning for Fraud Detection" - ACM Conference Proceedings (2021)

ADDITIONAL INFORMATION
• Languages: English (Native), Mandarin (Fluent), Spanish (Conversational)
• Open Source Contributions: 1000+ GitHub contributions, maintainer of 3 popular Python packages
• Volunteer: Mentor at Girls Who Code, technical advisor for 2 AI startups
"""

        try:
            # Create temporary file with comprehensive content
            import tempfile
            import os

            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(resume_content)
                temp_file_path = f.name

            with open(temp_file_path, 'rb') as file:
                files = {
                    'file': ('alex_chen_comprehensive_resume.txt', file, 'text/plain')
                }
                data = {
                    'source_type': 'resume',
                    'tenant_id': tenant_info['tenant_id'],
                    'title': 'Dr. Alex Chen - Senior Software Engineer Resume'
                }

                response = requests.post(f"{self.base_url}/ingest", files=files, data=data, timeout=60)

                if response.status_code == 200:
                    result = response.json()
                    self.log_result("Upload Comprehensive Resume", "PASS", {
                        "document_id": result.get("document_id"),
                        "chunk_count": result.get("chunk_count"),
                        "text_length": result.get("text_length"),
                        "message": f"Uploaded with {result.get('chunk_count', 0)} chunks"
                    })
                    return True
                else:
                    self.log_result("Upload Comprehensive Resume", "FAIL", {
                        "error": f"HTTP {response.status_code}: {response.text}"
                    })
                    return False

        except Exception as e:
            self.log_result("Upload Comprehensive Resume", "FAIL", {"error": str(e)})
            return False
        finally:
            try:
                os.unlink(temp_file_path)
            except:
                pass

    def test_star_methodology(self, tenant_info: dict):
        """Test STAR methodology responses"""

        if not tenant_info:
            return

        star_questions = [
            "Tell me about a challenging project you led and how you overcame obstacles",
            "Describe a time when you had to improve system performance",
            "Give me an example of how you handled a difficult technical problem",
            "Tell me about a situation where you had to work with a cross-functional team",
            "Describe a time when you implemented a new technology or process"
        ]

        for question in star_questions:
            try:
                qa_data = {
                    "question": question,
                    "mode": "star",
                    "tenant_id": tenant_info["tenant_id"]
                }

                response = requests.post(f"{self.base_url}/ask", json=qa_data, timeout=45)

                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("answer", "")

                    # Analyze STAR format quality
                    star_score = self.analyze_star_format(answer)

                    status = "PASS" if star_score >= 7 else "WARN" if star_score >= 4 else "FAIL"

                    self.log_result(f"STAR: {question[:50]}...", status, {
                        "answer": answer,
                        "star_format_score": star_score,
                        "context_used": result.get("context_used", 0),
                        "chunk_metadata": result.get("chunk_metadata", {})
                    })
                else:
                    self.log_result(f"STAR: {question[:50]}...", "FAIL", {
                        "error": f"HTTP {response.status_code}"
                    })

                time.sleep(2)  # Pause between requests

            except Exception as e:
                self.log_result(f"STAR: {question[:50]}...", "FAIL", {"error": str(e)})

    def analyze_star_format(self, answer: str) -> int:
        """Analyze how well the answer follows STAR format (0-10 scale)"""
        score = 0
        answer_lower = answer.lower()

        # Check for STAR components
        star_keywords = {
            "situation": ["situation", "context", "background", "challenge", "problem"],
            "task": ["task", "responsibility", "goal", "objective", "required"],
            "action": ["action", "implemented", "developed", "created", "designed", "led", "managed"],
            "result": ["result", "outcome", "achieved", "improved", "reduced", "increased", "saved"]
        }

        components_found = 0
        for component, keywords in star_keywords.items():
            if any(keyword in answer_lower for keyword in keywords):
                components_found += 1
                score += 2

        # Check for metrics and quantifiable results
        if any(char in answer for char in ['%', '$']) or any(word in answer for word in ['million', 'thousand', 'hours', 'minutes']):
            score += 2

        # Check for specific technical details
        technical_terms = ["python", "aws", "docker", "api", "system", "application", "database"]
        if any(term in answer_lower for term in technical_terms):
            score += 1

        # Check for structured presentation
        if len(answer.split('.')) >= 4:  # Multiple sentences indicate structure
            score += 1

        return min(score, 10)

    def test_enhanced_context_gathering(self, tenant_info: dict):
        """Test enhanced context gathering and relevance scoring"""

        if not tenant_info:
            return

        context_questions = [
            ("What machine learning frameworks have you used?", "skills"),
            ("How many years of experience do you have in Python?", "experience"),
            ("What was the impact of your fraud detection project?", "metrics"),
            ("Tell me about your leadership experience", "leadership"),
            ("What cloud technologies do you know?", "technical"),
            ("Describe your most successful project", "projects")
        ]

        for question, expected_type in context_questions:
            try:
                qa_data = {
                    "question": question,
                    "mode": "detailed",
                    "tenant_id": tenant_info["tenant_id"]
                }

                response = requests.post(f"{self.base_url}/ask", json=qa_data, timeout=45)

                if response.status_code == 200:
                    result = response.json()
                    answer = result.get("answer", "")
                    chunk_metadata = result.get("chunk_metadata", {})

                    # Analyze context relevance
                    relevance_score = self.analyze_context_relevance(answer, expected_type)

                    status = "PASS" if relevance_score >= 7 else "WARN" if relevance_score >= 4 else "FAIL"

                    self.log_result(f"Context ({expected_type}): {question[:40]}...", status, {
                        "answer": answer[:200] + "..." if len(answer) > 200 else answer,
                        "relevance_score": relevance_score,
                        "chunks_used": chunk_metadata.get("total_chunks", 0),
                        "sections_used": chunk_metadata.get("sections_used", []),
                        "contains_metrics": chunk_metadata.get("contains_metrics", False)
                    })
                else:
                    self.log_result(f"Context ({expected_type}): {question[:40]}...", "FAIL", {
                        "error": f"HTTP {response.status_code}"
                    })

                time.sleep(1.5)

            except Exception as e:
                self.log_result(f"Context ({expected_type}): {question[:40]}...", "FAIL", {"error": str(e)})

    def analyze_context_relevance(self, answer: str, expected_type: str) -> int:
        """Analyze how relevant the answer is to the expected question type (0-10 scale)"""
        score = 5  # Base score
        answer_lower = answer.lower()

        type_keywords = {
            "skills": ["python", "javascript", "tensorflow", "aws", "docker", "framework", "language"],
            "experience": ["years", "experience", "worked", "role", "position", "since"],
            "metrics": ["%", "$", "million", "improved", "reduced", "increased", "saved", "achieved"],
            "leadership": ["led", "managed", "team", "mentor", "supervised", "guided", "directed"],
            "technical": ["technology", "system", "architecture", "implementation", "platform"],
            "projects": ["project", "built", "developed", "created", "implemented", "designed"]
        }

        expected_keywords = type_keywords.get(expected_type, [])
        keyword_matches = sum(1 for keyword in expected_keywords if keyword in answer_lower)

        # Score based on keyword relevance
        score += min(keyword_matches, 3)

        # Check answer length appropriateness
        if 50 <= len(answer) <= 500:
            score += 1

        # Check for specific details
        if any(char.isdigit() for char in answer):
            score += 1

        return min(score, 10)

    def run_enhanced_tests(self):
        """Run comprehensive enhanced feature tests"""

        print("🚀 Starting Enhanced ProfileGPT Feature Testing")
        print("=" * 60)

        # Create test tenant
        tenant_info = self.create_enhanced_test_tenant()
        if not tenant_info:
            print("❌ Failed to create test tenant. Exiting...")
            return

        # Upload comprehensive resume
        if not self.upload_comprehensive_resume(tenant_info):
            print("❌ Failed to upload test document. Exiting...")
            return

        # Wait for processing
        print("⏳ Waiting for document processing...")
        time.sleep(5)

        # Test STAR methodology
        print("\n⭐ Testing STAR Methodology Responses")
        print("-" * 40)
        self.test_star_methodology(tenant_info)

        # Test enhanced context gathering
        print("\n🎯 Testing Enhanced Context Gathering")
        print("-" * 40)
        self.test_enhanced_context_gathering(tenant_info)

        # Print comprehensive summary
        self.print_enhanced_summary()

    def print_enhanced_summary(self):
        """Print comprehensive test results summary"""

        print("\n" + "=" * 60)
        print("📊 ENHANCED FEATURE TEST SUMMARY")
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

        # Analyze STAR format performance
        star_tests = [r for r in self.test_results if "STAR:" in r["test_name"]]
        if star_tests:
            avg_star_score = sum(r["details"].get("star_format_score", 0) for r in star_tests) / len(star_tests)
            print(f"⭐ Average STAR Format Score: {avg_star_score:.1f}/10")

        # Analyze context gathering performance
        context_tests = [r for r in self.test_results if "Context" in r["test_name"]]
        if context_tests:
            avg_context_score = sum(r["details"].get("relevance_score", 0) for r in context_tests) / len(context_tests)
            print(f"🎯 Average Context Relevance Score: {avg_context_score:.1f}/10")

        print(f"\n🎉 Enhanced ProfileGPT features {'✅ WORKING WELL' if passed/total_tests > 0.8 else '⚠️ NEED IMPROVEMENT'}")

def main():
    tester = EnhancedProfileGPTTester()
    tester.run_enhanced_tests()

if __name__ == "__main__":
    main()