"""
Intelligent Skill Discovery Engine for ProfileGPT
Automatically learns new skills from context and web sources
"""

import os
import re
import json
import logging
import requests
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        # Model not found, use spacy without the model
        nlp = None
except ImportError:
    spacy = None
    nlp = None

from database import DatabaseManager

logger = logging.getLogger(__name__)

@dataclass
class SkillContext:
    skill_name: str
    context: str
    evidence: str
    confidence: float
    source: str
    discovered_at: datetime
    category: str = "technical"  # technical, soft, domain
    related_skills: List[str] = None

class IntelligentSkillDiscovery:
    """Intelligent skill discovery that learns from user interactions and web context"""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.known_skills_cache = set()
        self.skill_patterns = self._load_skill_patterns()
        self.web_cache = {}  # Simple caching for web lookups
        self.openai_client = None

        if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "sk-demo-key-placeholder":
            try:
                self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            except Exception:
                pass

    def _load_skill_patterns(self) -> Dict[str, List[str]]:
        """Load patterns to identify different types of skills"""
        return {
            "programming_languages": [
                r"\b(python|javascript|java|c\+\+|c#|typescript|go|rust|swift|kotlin|scala|ruby|php|perl|r|matlab|julia)\b",
                r"\b(objective-c|visual basic|fortran|cobol|ada|haskell|erlang|clojure|f#|dart)\b"
            ],
            "frameworks": [
                r"\b(react|angular|vue|django|flask|spring|express|fastapi|nextjs|nuxt|gatsby)\b",
                r"\b(tensorflow|pytorch|scikit-learn|pandas|numpy|keras|opencv|hugging face)\b",
                r"\b(docker|kubernetes|jenkins|gitlab|github actions|terraform|ansible)\b"
            ],
            "databases": [
                r"\b(postgresql|mysql|mongodb|redis|elasticsearch|cassandra|neo4j|dynamodb)\b",
                r"\b(sqlite|oracle|sql server|mariadb|couchdb|influxdb|clickhouse)\b"
            ],
            "cloud_platforms": [
                r"\b(aws|azure|google cloud|gcp|digital ocean|linode|heroku|vercel|netlify)\b",
                r"\b(firebase|supabase|planetscale|railway|render)\b"
            ],
            "soft_skills": [
                r"\b(leadership|communication|teamwork|problem.?solving|critical thinking)\b",
                r"\b(project management|time management|mentoring|coaching|public speaking)\b",
                r"\b(agile|scrum|kanban|cross.?functional|stakeholder management)\b"
            ],
            "ai_ml": [
                r"\b(machine learning|deep learning|neural networks|natural language processing|nlp)\b",
                r"\b(computer vision|reinforcement learning|generative ai|llm|transformer)\b",
                r"\b(mlops|model deployment|feature engineering|data science|statistics)\b"
            ],
            "specialized_domains": [
                r"\b(cybersecurity|blockchain|fintech|healthtech|edtech|iot|embedded)\b",
                r"\b(devops|sre|platform engineering|data engineering|analytics)\b"
            ]
        }

    def discover_skills_from_text(self, text: str, source: str = "user_input") -> List[SkillContext]:
        """Discover skills from any text input"""
        discovered_skills = []
        text_lower = text.lower()

        # Use NLP if available for better entity recognition
        if nlp:
            doc = nlp(text)
            entities = [(ent.text, ent.label_) for ent in doc.ents]
        else:
            entities = []

        # Pattern-based skill discovery
        for category, patterns in self.skill_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    skill_name = match.group().title()

                    # Extract context around the skill mention
                    start = max(0, match.start() - 100)
                    end = min(len(text), match.end() + 100)
                    context = text[start:end].strip()

                    # Calculate confidence based on context
                    confidence = self._calculate_skill_confidence(skill_name, context, category)

                    if confidence > 0.3:  # Threshold for skill acceptance
                        discovered_skills.append(SkillContext(
                            skill_name=skill_name,
                            context=context,
                            evidence=context,
                            confidence=confidence,
                            source=source,
                            discovered_at=datetime.now(),
                            category=category.replace("_", " "),
                            related_skills=self._find_related_skills(skill_name, text_lower)
                        ))

        # Enhance with web research for unknown skills
        unique_skills = {s.skill_name: s for s in discovered_skills}
        enhanced_skills = []

        for skill_name, skill_context in unique_skills.items():
            if skill_name.lower() not in self.known_skills_cache:
                enhanced_context = self._enhance_skill_with_web_research(skill_context)
                enhanced_skills.append(enhanced_context)
                self.known_skills_cache.add(skill_name.lower())
            else:
                enhanced_skills.append(skill_context)

        return enhanced_skills

    def _calculate_skill_confidence(self, skill_name: str, context: str, category: str) -> float:
        """Calculate confidence score for a discovered skill"""
        confidence = 0.5  # Base confidence

        context_lower = context.lower()
        skill_lower = skill_name.lower()

        # Increase confidence based on context clues
        positive_indicators = [
            f"experienced in {skill_lower}",
            f"expert in {skill_lower}",
            f"proficient in {skill_lower}",
            f"skilled in {skill_lower}",
            f"worked with {skill_lower}",
            f"used {skill_lower}",
            f"{skill_lower} developer",
            f"{skill_lower} engineer",
            f"built with {skill_lower}",
            f"implemented {skill_lower}",
            f"years of {skill_lower}"
        ]

        for indicator in positive_indicators:
            if indicator in context_lower:
                confidence += 0.2

        # Check for project/experience mentions
        if any(word in context_lower for word in ["project", "built", "developed", "implemented", "created"]):
            confidence += 0.15

        # Check for proficiency levels
        proficiency_words = ["expert", "advanced", "senior", "lead", "principal", "years"]
        for word in proficiency_words:
            if word in context_lower:
                confidence += 0.1

        # Reduce confidence for vague mentions
        vague_indicators = ["heard of", "interested in", "learning", "want to learn"]
        for indicator in vague_indicators:
            if indicator in context_lower:
                confidence -= 0.3

        return min(1.0, max(0.0, confidence))

    def _find_related_skills(self, skill_name: str, text: str) -> List[str]:
        """Find skills related to the discovered skill"""
        related = []
        skill_lower = skill_name.lower()

        # Define skill relationships
        skill_relationships = {
            "python": ["django", "flask", "fastapi", "pandas", "numpy", "tensorflow", "pytorch"],
            "javascript": ["react", "node.js", "express", "vue", "angular"],
            "react": ["javascript", "typescript", "next.js", "redux"],
            "aws": ["docker", "kubernetes", "terraform", "cloud", "devops"],
            "machine learning": ["python", "tensorflow", "pytorch", "scikit-learn", "data science"],
            "docker": ["kubernetes", "devops", "aws", "azure", "containerization"]
        }

        # Check for related skills in the same text
        if skill_lower in skill_relationships:
            for related_skill in skill_relationships[skill_lower]:
                if related_skill.lower() in text:
                    related.append(related_skill.title())

        return related[:5]  # Limit to top 5 related skills

    def _enhance_skill_with_web_research(self, skill_context: SkillContext) -> SkillContext:
        """Enhance skill information with web research"""
        skill_name = skill_context.skill_name

        # Check cache first
        cache_key = hashlib.md5(skill_name.encode()).hexdigest()
        if cache_key in self.web_cache:
            cached_data = self.web_cache[cache_key]
            if cached_data["timestamp"] > datetime.now() - timedelta(hours=24):
                skill_context.evidence += f"\n\nResearched Info: {cached_data['description']}"
                return skill_context

        try:
            # Research skill from multiple sources
            wiki_info = self._research_skill_wikipedia(skill_name)
            github_info = self._research_skill_github(skill_name)

            enhanced_info = ""
            if wiki_info:
                enhanced_info += f"Definition: {wiki_info[:200]}... "
            if github_info:
                enhanced_info += f"GitHub Usage: {github_info['description']} (★{github_info['stars']})"

            if enhanced_info:
                skill_context.evidence += f"\n\nResearched Info: {enhanced_info}"
                skill_context.confidence += 0.1  # Boost confidence with research

                # Cache the result
                self.web_cache[cache_key] = {
                    "description": enhanced_info,
                    "timestamp": datetime.now()
                }

        except Exception as e:
            logger.warning(f"Web research failed for {skill_name}: {e}")

        return skill_context

    def _research_skill_wikipedia(self, skill_name: str) -> Optional[str]:
        """Research skill information from Wikipedia"""
        if not BeautifulSoup:
            return None

        try:
            # Search Wikipedia
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{skill_name.replace(' ', '_')}"
            response = requests.get(search_url, timeout=5)

            if response.status_code == 200:
                data = response.json()
                return data.get("extract", "")

        except Exception as e:
            logger.debug(f"Wikipedia research failed: {e}")

        return None

    def _research_skill_github(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """Research skill popularity and usage from GitHub"""
        try:
            # GitHub API to search repositories
            search_url = f"https://api.github.com/search/repositories?q={skill_name}&sort=stars&order=desc&per_page=1"
            headers = {"Accept": "application/vnd.github.v3+json"}

            response = requests.get(search_url, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get("items"):
                    repo = data["items"][0]
                    return {
                        "name": repo["name"],
                        "description": repo["description"] or "",
                        "stars": repo["stargazers_count"],
                        "language": repo["language"]
                    }

        except Exception as e:
            logger.debug(f"GitHub research failed: {e}")

        return None

    def learn_from_query(self, question: str, conversation_context: str = "") -> List[SkillContext]:
        """Learn new skills from user queries and conversation context"""
        combined_text = f"{question} {conversation_context}"

        # Discover skills mentioned in the question
        discovered_skills = self.discover_skills_from_text(combined_text, "query_context")

        # Store learned skills
        for skill in discovered_skills:
            self._store_discovered_skill(skill)

        return discovered_skills

    def enhance_skill_with_ai(self, skill_context: SkillContext) -> SkillContext:
        """Use AI to enhance skill understanding and categorization"""
        if not self.openai_client:
            return skill_context

        try:
            prompt = f"""
            Analyze this skill and provide enhanced information:

            Skill: {skill_context.skill_name}
            Context: {skill_context.context}
            Category: {skill_context.category}

            Please provide:
            1. A better category (technical/soft/domain-specific)
            2. Proficiency level indicated (beginner/intermediate/advanced/expert)
            3. Related skills that often go together
            4. Industry relevance score (1-10)

            Respond in JSON format:
            {{
                "category": "...",
                "proficiency": "...",
                "related_skills": ["..."],
                "relevance_score": 8,
                "enhanced_description": "..."
            }}
            """

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=300
            )

            ai_analysis = json.loads(response.choices[0].message.content)

            # Enhance the skill context with AI insights
            skill_context.category = ai_analysis.get("category", skill_context.category)
            skill_context.confidence = min(1.0, skill_context.confidence + (ai_analysis.get("relevance_score", 5) / 20))
            if ai_analysis.get("related_skills"):
                skill_context.related_skills = ai_analysis["related_skills"]

            if ai_analysis.get("enhanced_description"):
                skill_context.evidence += f"\n\nAI Analysis: {ai_analysis['enhanced_description']}"

        except Exception as e:
            logger.warning(f"AI enhancement failed for {skill_context.skill_name}: {e}")

        return skill_context

    def _store_discovered_skill(self, skill_context: SkillContext) -> bool:
        """Store discovered skill in the database"""
        try:
            # Check if skill already exists
            existing_skill = self.db.get_skill_by_name(skill_context.skill_name)

            if not existing_skill:
                # Store new skill
                skill_data = {
                    "name": skill_context.skill_name,
                    "category": skill_context.category,
                    "confidence": skill_context.confidence,
                    "evidence": skill_context.evidence,
                    "source": skill_context.source,
                    "related_skills": skill_context.related_skills or [],
                    "discovered_at": skill_context.discovered_at.isoformat()
                }

                return self.db.store_discovered_skill(skill_data)
            else:
                # Update existing skill with new evidence
                return self.db.update_skill_evidence(skill_context.skill_name, skill_context.evidence)

        except Exception as e:
            logger.error(f"Failed to store skill {skill_context.skill_name}: {e}")
            return False

    def get_skill_insights(self, skill_name: str) -> Dict[str, Any]:
        """Get comprehensive insights about a skill"""
        # Discover and enhance skill information
        skill_context = SkillContext(
            skill_name=skill_name,
            context="",
            evidence="",
            confidence=0.5,
            source="insight_request",
            discovered_at=datetime.now()
        )

        # Enhance with web research
        enhanced_skill = self._enhance_skill_with_web_research(skill_context)

        # Enhance with AI if available
        if self.openai_client:
            enhanced_skill = self.enhance_skill_with_ai(enhanced_skill)

        return {
            "skill_name": enhanced_skill.skill_name,
            "category": enhanced_skill.category,
            "confidence": enhanced_skill.confidence,
            "evidence": enhanced_skill.evidence,
            "related_skills": enhanced_skill.related_skills or [],
            "research_enhanced": True if enhanced_skill.evidence else False
        }

    def adaptive_skill_learning(self, user_documents: List[str], recent_queries: List[str]) -> Dict[str, List[SkillContext]]:
        """Continuously learn and adapt skills based on user interactions"""
        learning_results = {
            "new_skills": [],
            "updated_skills": [],
            "skill_trends": []
        }

        # Analyze all user content for skill evolution
        all_text = " ".join(user_documents + recent_queries)
        discovered_skills = self.discover_skills_from_text(all_text, "adaptive_learning")

        for skill in discovered_skills:
            enhanced_skill = self.enhance_skill_with_ai(skill) if self.openai_client else skill

            if self._store_discovered_skill(enhanced_skill):
                learning_results["new_skills"].append(enhanced_skill)

        # Analyze skill trends and recommendations
        skill_trends = self._analyze_skill_trends(discovered_skills)
        learning_results["skill_trends"] = skill_trends

        return learning_results

    def _analyze_skill_trends(self, skills: List[SkillContext]) -> List[Dict[str, Any]]:
        """Analyze trending skills and provide recommendations"""
        trends = []

        # Group skills by category
        skill_categories = {}
        for skill in skills:
            if skill.category not in skill_categories:
                skill_categories[skill.category] = []
            skill_categories[skill.category].append(skill)

        # Analyze each category
        for category, category_skills in skill_categories.items():
            if len(category_skills) >= 2:  # At least 2 skills in category
                avg_confidence = sum(s.confidence for s in category_skills) / len(category_skills)

                trends.append({
                    "category": category,
                    "skill_count": len(category_skills),
                    "average_confidence": avg_confidence,
                    "trending_skills": [s.skill_name for s in sorted(category_skills, key=lambda x: x.confidence, reverse=True)[:3]],
                    "recommendation": f"Strong focus on {category} skills detected. Consider highlighting these in profiles."
                })

        return trends

# Usage example for testing
if __name__ == "__main__":
    # Example usage
    from database import DatabaseManager

    db = DatabaseManager()
    skill_discovery = IntelligentSkillDiscovery(db)

    # Test skill discovery
    sample_text = """
    I'm a senior software engineer with 5+ years of experience in Python, React, and AWS.
    I've built scalable microservices using FastAPI and Django, deployed on Kubernetes clusters.
    Recently worked on machine learning projects using TensorFlow and PyTorch.
    Strong background in agile methodologies and cross-functional team leadership.
    """

    discovered_skills = skill_discovery.discover_skills_from_text(sample_text, "test")

    for skill in discovered_skills:
        print(f"Discovered: {skill.skill_name} (confidence: {skill.confidence:.2f})")
        print(f"Category: {skill.category}")
        print(f"Evidence: {skill.evidence[:100]}...")
        print("---")