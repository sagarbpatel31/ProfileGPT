"""
RAG (Retrieval-Augmented Generation) Engine for ProfileGPT
"""
import re
import uuid
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from dataclasses import dataclass
import time
import numpy as np
import hashlib

from database import DatabaseManager, Document, Chunk

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    SentenceTransformer = None

KNOWN_SKILLS = {
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "java": "Java",
    "c++": "C++",
    "c#": "C#",
    "c": "C",
    "go": "Go",
    "golang": "Go",
    "rust": "Rust",
    "docker": "Docker",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "react": "React",
    "node": "Node.js",
    "node.js": "Node.js",
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "mongodb": "MongoDB",
    "linux": "Linux"
}

PROFILE_TOPIC_TEMPLATES = [
    {
        "id": "technical",
        "title": "Technical Skills",
        "description": "Tools, languages, and frameworks in daily use",
        "keywords": ["python", "c++", "java", "docker", "react", "node", "firmware", "linux"],
        "sample_questions": [
            "Which tools do you use most often?",
            "How do you keep your technical stack current?"
        ]
    },
    {
        "id": "projects",
        "title": "Projects & Impact",
        "description": "Notable work and measurable outcomes",
        "keywords": ["project", "delivered", "impact", "built", "developed", "achieved", "led"],
        "sample_questions": [
            "Share a project with business impact.",
            "How do you measure project success?"
        ]
    },
    {
        "id": "ai_innovation",
        "title": "AI & Innovation",
        "description": "Automation, ML, and experimentation",
        "keywords": ["ai", "ml", "machine", "learning", "model", "vision", "innovation", "automation", "slam"],
        "sample_questions": [
            "What AI/ML systems have you built?",
            "Have you automated any workflows recently?"
        ]
    },
    {
        "id": "research",
        "title": "Research & Publications",
        "description": "Academic or research contributions",
        "keywords": ["research", "publication", "paper", "scholar", "study"],
        "sample_questions": [
            "Tell me about your research focus.",
            "Any publications or talks worth highlighting?"
        ]
    },
    {
        "id": "healthcare",
        "title": "Healthcare & Life Sciences",
        "description": "Clinical, biomedical, or pharma expertise",
        "keywords": ["patient", "clinical", "medical", "health", "biomedical", "pharma"],
        "sample_questions": [
            "How have you impacted patient care?",
            "Describe a healthcare project you led."
        ]
    },
    {
        "id": "mechanical",
        "title": "Mechanical & Industrial",
        "description": "Mechanical, manufacturing, or CAD experience",
        "keywords": ["mechanical", "manufacturing", "cad", "solidworks", "thermal", "hardware design"],
        "sample_questions": [
            "What mechanical systems have you built?",
            "How do you ensure manufacturability?"
        ]
    }
]

@dataclass
class RAGResponse:
    answer: str
    citations: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    latency_ms: int
    mode: str

class MockLLM:
    """Conversational LLM that analyzes resume content like ChatGPT"""

    def __init__(self):
        pass

    def _extract_context_points(self, summaries: List[Dict[str, str]], limit: int = 4) -> List[str]:
        return [
            f"{summary['title']}: {summary['sentence']}"
            for summary in summaries[:limit]
        ]

    def _format_short_points(self, points: List[str], fallback: str, limit: int = 2) -> str:
        cleaned = [p.replace("•", "").strip(" -:") for p in points if p.strip()]
        if cleaned:
            return "; ".join(cleaned[:limit])
        return fallback

    def _summaries_from_chunks(self, question: str, chunks: List[Dict[str, Any]], limit: int = 8) -> List[Dict[str, str]]:
        """Grab relevant sentences from context matching keywords"""
        keywords = [word for word in re.sub(r"[^\w\s]", "", question.lower()).split() if len(word) > 2]
        summaries: List[Dict[str, str]] = []

        for chunk in chunks:
            text = chunk.get("text", "")
            if not text:
                continue

            sentences = re.split(r'(?<=[.!?])\s+', text)
            match_added = False

            for sentence in sentences:
                clean = sentence.strip()
                if not clean:
                    continue
                lower = clean.lower()
                if keywords and any(keyword in lower for keyword in keywords):
                    summaries.append({
                        "sentence": clean,
                        "title": chunk.get("title", "Document"),
                        "section": chunk.get("section"),
                    })
                    match_added = True
                    break

            if not match_added and sentences:
                summaries.append({
                    "sentence": sentences[0].strip(),
                    "title": chunk.get("title", "Document"),
                    "section": chunk.get("section")
                })

            if len(summaries) >= limit:
                break

        return summaries[:limit]

    def generate_response(self, question: str, chunks: List[Dict[str, Any]], mode: str = "detailed") -> str:
        """Generate a conversational response based on actual resume context"""
        question_lower = question.lower()
        summaries = self._summaries_from_chunks(question, chunks)

        if not summaries:
            return self._friendly_no_context_response(question, mode)

        # Handle personal/casual questions first
        if any(keyword in question_lower for keyword in ["how are you", "how's it going", "how you doing", "what's up", "hey", "hi", "hello"]):
            return self._handle_personal_greeting(summaries, question, mode)

        # Analyze the question type and context to provide personalized responses
        elif any(keyword in question_lower for keyword in ["python", "programming", "coding", "development"]):
            return self._analyze_python_skills(summaries, question, mode)

        elif any(keyword in question_lower for keyword in ["experience", "work", "job", "career", "background"]):
            return self._analyze_experience(summaries, question, mode)

        elif any(keyword in question_lower for keyword in ["skills", "technologies", "tech", "tools"]):
            return self._analyze_technical_skills(summaries, question, mode)

        elif any(keyword in question_lower for keyword in ["projects", "built", "developed", "created"]):
            return self._analyze_projects(summaries, question, mode)

        elif any(keyword in question_lower for keyword in ["education", "degree", "university", "study"]):
            return self._analyze_education(summaries, question, mode)

        elif any(keyword in question_lower for keyword in ["embedded", "hardware", "firmware", "cisco"]):
            return self._analyze_embedded_experience(summaries, question, mode)

        elif any(keyword in question_lower for keyword in ["rtos", "real-time", "freertos", "real time operating", "scheduler"]):
            return self._analyze_rtos_experience(summaries, question, mode)

        elif any(keyword in question_lower for keyword in ["ai", "ml", "machine learning", "deep learning"]):
            return self._analyze_ai_experience(summaries, question, mode)

        elif any(keyword in question_lower for keyword in ["healthcare", "patient", "clinical", "medical", "hospital"]):
            return self._analyze_healthcare_experience(summaries, question, mode)

        else:
            return self._generate_general_response(summaries, question, mode)

    def _analyze_python_skills(self, summaries: List[Dict[str, str]], question: str, mode: str) -> str:
        """Analyze Python skills from resume context"""
        raw_points = self._extract_context_points(summaries, limit=4)
        if not raw_points:
            raw_points = [
                "Automates hardware validation and health checks via Python scripting.",
                "Builds firmware-to-cloud telemetry services and diagnostics pipelines.",
                "Uses PyTorch, Pandas, and NumPy for ML research prototypes."
            ]

        if mode == "short":
            return self._format_short_points(raw_points, "Python covers automation, telemetry, and ML prototyping.")
        elif mode == "star":
            return ("Situation: Needed faster quality feedback during Cisco board bring-up\n"
                    "Task: Reduce manual QA cycles and capture telemetry data\n"
                    "Action: Built Python pipelines that triggered tests, parsed logs, and published dashboards\n"
                    "Result: Enabled daily CI-style validation and freed the hardware team from manual testing")

        bullet_points = "\n".join([f"• {point}" for point in raw_points])
        return ("Here’s how I apply Python:\n"
                f"{bullet_points}\n"
                "• Tooling: PyTorch, FastAPI, Pandas, NumPy, automation frameworks")

    def _analyze_experience(self, summaries: List[Dict[str, str]], question: str, mode: str) -> str:
        """Analyze work experience from context"""
        raw_points = self._extract_context_points(summaries, limit=4)

        if not raw_points:
            raw_points = [
                "Led embedded switch bring-up at Cisco, covering FPGA, PoE, and security modules.",
                "Built firmware-to-cloud data paths for R-Tek IoT devices (Raspberry Pi, STM32, ESP32).",
                "Collaborated on AI research projects translating ML outputs into production-ready tooling."
            ]

        if mode == "short":
            return self._format_short_points(raw_points, "Embedded engineer blending Cisco hardware + IoT cloud work.")
        elif mode == "star":
            return ("Situation: Owned validation for Cisco's next-gen enterprise switch platform\n"
                    "Task: Ensure every board feature (PHY/FPGA/PoE) worked before release\n"
                    "Action: Built diagnostic CLI tools, automated tests, and coordinated across silicon teams\n"
                    "Result: Accelerated bring-up cycles and improved release confidence for the hardware org")

        bullet_points = "\n".join([f"• {point}" for point in raw_points])
        return ("Experience snapshot:\n"
                f"{bullet_points}\n"
                "• Collaboration: cross-functional work with hardware, cloud, and research teams")

    def _analyze_technical_skills(self, summaries: List[Dict[str, str]], question: str, mode: str) -> str:
        """Analyze technical skills from context"""
        raw_points = self._extract_context_points(summaries, limit=5)

        fallback_points = [
            "Programming: Python, C/C++, Bash, ROS nodes, automation scripting.",
            "Embedded platforms: Raspberry Pi, STM32, ESP32, Nvidia Jetson, I2C/SPI/UART.",
            "AI/ML: PyTorch, computer vision (UNet/ResAttUNet), Pandas/Numpy for data.",
            "Cloud & DevOps: FastAPI services, Docker, CI/CD pipelines, observability.",
            "Operating Systems: Linux bring-up, device drivers, low-level debugging."
        ]

        if not raw_points or raw_points == ["•"]:
            raw_points = fallback_points

        if mode == "short":
            return self._format_short_points(raw_points, "Daily stack spans Python/C++, embedded Linux, and ML tooling.")
        elif mode == "star":
            return ("Situation: Teams needed one engineer who could span firmware to AI\n"
                    "Task: Deliver end-to-end solutions without handoffs between specialists\n"
                    "Action: Became fluent in C/C++, Python, ROS, cloud services, and ML frameworks\n"
                    "Result: Delivered projects like autonomous drones and IoT telemetry pipelines independently")

        bullet_points = "\n".join([f"• {point}" for point in raw_points])
        return ("Technical strengths:\n"
                f"{bullet_points}")

    def _analyze_projects(self, summaries: List[Dict[str, str]], question: str, mode: str) -> str:
        """Analyze projects from context"""
        raw_points = self._extract_context_points(summaries, limit=4)
        if not raw_points:
            raw_points = [
                "Autonomous drone platform with GPS-less navigation using Jetson Nano + SLAM.",
                "Marine plastic detection model (ResAttUNet) delivering >80 IoU on satellite imagery.",
                "Enterprise switch validation tooling (C/C++ CLI + automation) at Cisco.",
                "IoT firmware-to-cloud telemetry stack spanning Raspberry Pi/STM32 hardware."
            ]

        if mode == "short":
            return self._format_short_points(raw_points, "Delivered drones, ML research, and IoT telemetry projects.")
        elif mode == "star":
            return ("Situation: Needed autonomous inspection without GPS indoors\n"
                    "Task: Build a fully autonomous drone platform\n"
                    "Action: Implemented SLAM, visual odometry, and ROS navigation nodes across Jetson + T265 sensors\n"
                    "Result: Drone executes missions via UI commands and avoids obstacles in real time")

        bullet_points = "\n".join([f"• {point}" for point in raw_points[:4]])
        return ("Representative projects:\n"
                f"{bullet_points}\n"
                "Each project blends embedded hardware, AI models, and production-ready automation.")

    def _analyze_education(self, summaries: List[Dict[str, str]], question: str, mode: str) -> str:
        """Analyze educational background"""
        points = self._extract_context_points(summaries, limit=3)
        if mode == "short":
            return "MS Computer Science (in progress), MS Embedded Systems from UCI (3.95 GPA), BTech ECE Gold Medalist."
        elif mode == "star":
            return "Situation: Pursuing advanced education in technology\nTask: Build strong academic foundation\nAction: Completed MS in Embedded Systems at UCI with 3.95 GPA, pursuing MS Computer Science\nResult: Gold Medalist in BTech, strong academic performance supporting professional growth"

        bullet_points = "\n".join([f"• {point}" for point in points]) if points else (
            "• MS Computer Science (in progress)\n"
            "• MS Embedded & Cyber-Physical Systems, UC Irvine (3.95 GPA)\n"
            "• BTech Electronics & Communication, Gold Medalist"
        )

        return ("I have a strong educational foundation:\n"
                f"{bullet_points}\n"
                "• Combines embedded specialization with computer science breadth.")

    def _analyze_embedded_experience(self, summaries: List[Dict[str, str]], question: str, mode: str) -> str:
        """Analyze embedded systems experience"""
        if mode == "short":
            raw_points = self._extract_context_points(summaries, limit=4)
            if not raw_points:
                raw_points = [
                    "Cisco board bring-up (PHY/FPGA/PoE diagnostics).",
                    "Firmware + RTOS tasks in C/C++ for telemetry.",
                    "IoT integrations across Raspberry Pi, STM32, ESP32."
                ]
            return self._format_short_points(raw_points, "Embedded engineer with Cisco validation + RTOS experience.")
        elif mode == "star":
            return "Situation: Cisco needed next-gen switch validation\nTask: Lead board bring-up for complex hardware\nAction: Developed C/C++ tools, automated testing, coordinated with multiple teams\nResult: Achieved high validation rates and streamlined development process"

        bullet_points = "\n".join([f"• {point}" for point in points]) if points else (
            "• Hardware validation for Cisco enterprise switches (PHY/FPGA/PoE)\n"
            "• Firmware in C++ for diagnostics, telemetry, and CLI tools\n"
            "• Integrations across Raspberry Pi, STM32, ESP32 with cloud services"
        )

        return ("Embedded systems profile:\n"
                f"{bullet_points}\n"
                "• Comfortable from low-level firmware to system-level integration.")

    def _analyze_rtos_experience(self, summaries: List[Dict[str, str]], question: str, mode: str) -> str:
        """Describe RTOS expertise explicitly"""
        points = [s for s in summaries if any(keyword in s['sentence'].lower() for keyword in ["rtos", "real-time", "free rtos", "scheduler"])]
        formatted = self._extract_context_points(points, limit=3)

        if mode == "short":
            return "Comfortable with FreeRTOS/Linux RTOS work: interrupt handling, scheduling, and telemetry loops."
        elif mode == "star":
            return ("Situation: Needed deterministic telemetry for Cisco switch bring-up\n"
                    "Task: Build RTOS routines handling PoE diagnostics + safety\n"
                    "Action: Implemented FreeRTOS tasks, ISR hooks, and watchdog flows on embedded controllers\n"
                    "Result: Reliable runtime diagnostics and faster board validation cycles")

        if not formatted:
            formatted = [
                "Developed FreeRTOS tasks for telemetry, safety shutdown, and diagnostics loops.",
                "Integrated RTOS scheduling with C/C++ CLI utilities to monitor board health.",
                "Comfortable managing interrupts, timers, and cooperative scheduling patterns."
            ]

        bullet_points = "\n".join(f"• {point}" for point in formatted)
        return ("RTOS background:\n"
                f"{bullet_points}\n"
                "• Experience spans FreeRTOS, Linux-based RT scheduling, and microcontroller interrupt design.")

    def _analyze_ai_experience(self, summaries: List[Dict[str, str]], question: str, mode: str) -> str:
        """Analyze AI/ML experience"""
        points = self._extract_context_points(summaries, limit=4)
        if not points:
            points = [
                "Developed ResAttUNet segmentation models (>80 IoU) for marine plastic detection with Omdena.",
                "Implemented SLAM, obstacle avoidance, and sensor fusion for a Jetson-powered autonomous drone.",
                "Automated telemetry and anomaly detection for embedded platforms using ML heuristics."
            ]

        if mode == "short":
            return self._format_short_points(points, "AI/ML work spans computer vision, SLAM robotics, and telemetry ML.")
        elif mode == "star":
            return ("Situation: Environmental partners needed satellite-based plastic detection\n"
                    "Task: Build a high-precision segmentation model\n"
                    "Action: Curated Mediterranean datasets, optimized ResAttUNet, and deployed inference tooling\n"
                    "Result: Delivered >80 IoU accuracy and operational dashboards used by the research team")

        bullet_points = "\n".join([f"• {point}" for point in points[:4]])
        return ("AI/ML contributions:\n"
                f"{bullet_points}\n"
                "• Stack: PyTorch, OpenCV, ROS, Pandas/NumPy, model evaluation + deployment workflows")

    def _analyze_healthcare_experience(self, summaries: List[Dict[str, str]], question: str, mode: str) -> str:
        """Highlight healthcare/data-science experience"""
        points = self._extract_context_points(summaries, limit=4)
        if mode == "short":
            return self._format_short_points(points, "Healthcare DS building ICU readmission & sepsis models with clinicians.")
        elif mode == "star":
            return ("Situation: ICU teams struggled with late readmission alerts\n"
                    "Task: Deliver a predictive model clinicians could trust\n"
                    "Action: Engineered LightGBM features from vitals, aligned explanations with physicians\n"
                    "Result: Earlier interventions and dashboards adopted by critical-care units")

        bullet_points = "\n".join([f"• {point}" for point in points[:4]])
        return ("Healthcare impact:\n"
                f"{bullet_points}\n"
                "• Tooling: Python, LightGBM, TensorFlow, SQL, FHIR/HL7 data pipelines")

    def _generate_general_response(self, summaries: List[Dict[str, str]], question: str, mode: str) -> str:
        """Generate a general response based on context"""
        points = self._extract_context_points(summaries, limit=4)
        if not points:
            points = [
                "Embedded systems development at Cisco (board bring-up, firmware, diagnostics).",
                "IoT firmware-to-cloud integrations at R-Tek (Raspberry Pi, STM32, ESP32).",
                "Deep learning research via Omdena, focusing on computer vision and environmental data."
            ]

        if mode == "short":
            return self._format_short_points(points, "Embedded engineer with AI research and IoT/cloud integration experience.")
        elif mode == "star":
            return ("Situation: Career spans embedded hardware and AI projects\n"
                    "Task: Provide reliable technical guidance across both domains\n"
                    "Action: Led hardware validation, built automation pipelines, and shipped ML solutions\n"
                    "Result: Deliver end-to-end insights from silicon to cloud + AI")

        bullet_points = "\n".join([f"• {point}" for point in points[:4]])
        return ("Background summary:\n"
                f"{bullet_points}\n"
                "Happy to dive deeper into any of these areas.")

    def _friendly_no_context_response(self, question: str, mode: str) -> str:
        """Provide a friendly response when no context is available"""
        if mode == "short":
            return "I'd be happy to help! Could you ask about my specific experience or skills?"
        elif mode == "star":
            return "Situation: Question about my background\nTask: Provide helpful information\nAction: Ready to share details about my experience\nResult: Please ask about specific skills, projects, or experience areas"

        return ("Hi there! I'd be happy to answer questions about my background and experience. "
                "I'm Sagar Patel, an Embedded Software Engineer with experience at Cisco Systems and current work at R-Tek, plus AI/ML research experience. "
                "Feel free to ask me about my Python skills, embedded systems experience, AI/ML projects, education, or any specific technologies you're curious about. "
                "What would you like to know more about?")

    def _handle_personal_greeting(self, summaries: List[Dict[str, str]], question: str, mode: str) -> str:
        """Handle personal greetings and casual questions"""
        question_lower = question.lower()

        if mode == "short":
            return "I'm doing great! Excited to share my technical experience with you."
        elif mode == "star":
            return "Situation: Professional conversation\\nTask: Share my background effectively\\nAction: Ready to discuss my experience\\nResult: Let's talk about my technical journey!"

        if "how are you" in question_lower or "how's it going" in question_lower or "how you doing" in question_lower:
            return ("I'm doing great, thank you for asking! 🚀\\n\\n"
                   "I'm currently energized by my work combining embedded systems and AI:\\n\\n"
                   "• Working on exciting IoT cloud integration projects at R-Tek\\n\\n"
                   "• Advancing my expertise through NVIDIA's Generative AI certification\\n\\n"
                   "• Continuing research in deep learning and computer vision\\n\\n"
                   "As someone passionate about technology, I'm always excited to discuss my journey in embedded systems, AI/ML research, and the fascinating intersection of hardware and software. What would you like to know about my experience?")

        elif any(greeting in question_lower for greeting in ["hey", "hi", "hello", "what's up"]):
            return ("Hey there! 👋\\n\\n"
                   "Nice to meet you! I'm Sagar Patel, an Embedded Software Engineer with a passion for bridging hardware and AI technologies.\\n\\n"
                   "Here's a quick intro:\\n\\n"
                   "• **Current Role**: Software Developer at R-Tek, working on IoT cloud integration\\n\\n"
                   "• **Background**: 2+ years at Cisco Systems doing enterprise switch validation\\n\\n"
                   "• **Research**: Deep Learning Researcher at Omdena, focusing on satellite imagery AI\\n\\n"
                   "• **Education**: MS in Embedded Systems from UC Irvine (3.95 GPA)\\n\\n"
                   "I love talking about Python, embedded systems, AI/ML, autonomous drones, and the future of intelligent hardware. What interests you most?")

        else:
            return ("Thanks for reaching out! I'm Sagar, and I'm passionate about technology and innovation.\\n\\n"
                   "I specialize in embedded systems and AI/ML, currently working on some exciting projects that combine both worlds. "
                   "Whether you're curious about my technical experience, recent projects, or just want to chat about technology trends, I'm here to help!\\n\\n"
                   "What would you like to explore about my background?")

class MockEmbedding:
    """Mock embedding model for demo purposes"""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def encode(self, text: str) -> np.ndarray:
        """Generate mock embedding for text"""
        # Create deterministic embedding based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        seed = int(text_hash[:8], 16)
        np.random.seed(seed)

        embedding = np.random.normal(0, 1, self.dimension).astype(np.float32)
        # Normalize
        embedding = embedding / np.linalg.norm(embedding)
        return embedding

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between embeddings"""
        return np.dot(embedding1, embedding2)


class TransformerEmbedding:
    """SentenceTransformer-backed embeddings for higher-quality retrieval."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        if not SentenceTransformer:
            raise RuntimeError("sentence-transformers is not installed")
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()

    def encode(self, text: str) -> np.ndarray:
        """Return normalized embedding for the given text."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        if isinstance(embedding, list):
            embedding = np.array(embedding)
        return embedding.astype(np.float32)

    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        return float(np.dot(embedding1, embedding2))

class ProfileInsightsCache:
    """Simple cache with TTL for tenant insights so we don't rescan documents each request."""

    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}

    def get(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        entry = self._cache.get(tenant_id)
        if not entry:
            return None
        if time.time() - entry["timestamp"] > self.ttl_seconds:
            self._cache.pop(tenant_id, None)
            return None
        return entry["value"]

    def set(self, tenant_id: str, value: Dict[str, Any]):
        self._cache[tenant_id] = {"value": value, "timestamp": time.time()}

    def invalidate(self, tenant_id: str):
        self._cache.pop(tenant_id, None)


class RAGEngine:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.llm = MockLLM()
        if SentenceTransformer:
            try:
                self.embedding_model = TransformerEmbedding()
                print(f"✅ Using SentenceTransformer embeddings ({self.embedding_model.model_name})")
            except Exception as e:
                print(f"⚠️  Failed to load SentenceTransformer ({e}), using mock embeddings.")
                self.embedding_model = MockEmbedding()
        else:
            self.embedding_model = MockEmbedding()
        self.insights_cache = ProfileInsightsCache()

    def chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)

        return chunks

    def ingest_document(self, tenant_id: str, source_type: str, title: str, content: str, url: Optional[str] = None) -> str:
        """Ingest a document into the RAG system"""
        doc_id = str(uuid.uuid4())

        # Create document record
        doc = Document(
            id=doc_id,
            tenant_id=tenant_id,
            source_type=source_type,
            title=title,
            url=url,
            content=content,
            status="processing",
            created_at=time.time()
        )

        self.db.add_document(doc)

        # Chunk the content
        chunks = self.chunk_text(content)

        # Process each chunk
        for i, chunk_text in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"

            # Generate embedding
            embedding = self.embedding_model.encode(chunk_text)

            # Extract basic tags (skills, technologies, etc.)
            tags = self._extract_tags(chunk_text)

            # Create chunk
            chunk = Chunk(
                id=chunk_id,
                tenant_id=tenant_id,
                doc_id=doc_id,
                source_type=source_type,
                title=title,
                section=f"Section {i+1}",
                url=url,
                text=chunk_text,
                embedding=embedding,
                tags=tags
            )

            self.db.add_chunk(chunk)

            # Extract and link skills
            self._extract_and_link_skills(chunk, chunk_text)

        # Invalidate cached insights since the tenant's corpus changed
        self.insights_cache.invalidate(tenant_id)

        return doc_id

    def _extract_tags(self, text: str) -> Dict[str, Any]:
        """Extract tags from text (skills, technologies, etc.)"""
        # Common technical skills and technologies
        skills = [
            'python', 'javascript', 'react', 'node.js', 'fastapi', 'django', 'flask',
            'postgresql', 'mysql', 'mongodb', 'redis', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'git', 'linux', 'machine learning', 'ai',
            'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            'html', 'css', 'typescript', 'java', 'c++', 'golang', 'rust'
        ]

        found_skills = []
        text_lower = text.lower()

        for skill in skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)

        return {
            'skills': found_skills,
            'word_count': len(text.split()),
            'has_metrics': bool(re.search(r'\d+%|\d+\+|\$\d+', text))
        }

    def _extract_and_link_skills(self, chunk: Chunk, text: str):
        """Extract skills from chunk and create skill-evidence links"""
        skills_found = chunk.tags.get('skills', [])

        for skill in skills_found:
            # Find skill in database or create it
            skill_id = self._get_or_create_skill(chunk.tenant_id, skill)

            # Calculate confidence based on context
            confidence = self._calculate_skill_confidence(skill, text)

            # Extract evidence text
            evidence = self._extract_evidence_text(skill, text)

            # This would normally insert into skill_evidence table
            # For demo, we'll skip the database insertion

    def _get_or_create_skill(self, tenant_id: str, skill_name: str) -> str:
        """Get or create skill in database"""
        # For demo, just return a mock skill ID
        return f"skill_{skill_name.replace(' ', '_').lower()}"

    def _calculate_skill_confidence(self, skill: str, text: str) -> float:
        """Calculate confidence score for skill based on context"""
        text_lower = text.lower()
        skill_lower = skill.lower()

        # Base confidence if skill is mentioned
        confidence = 0.5

        # Boost if mentioned with experience indicators
        if any(phrase in text_lower for phrase in ['experience with', 'expert in', 'proficient', 'years of']):
            confidence += 0.3

        # Boost if mentioned with project context
        if any(phrase in text_lower for phrase in ['built', 'developed', 'created', 'implemented']):
            confidence += 0.2

        return min(confidence, 1.0)

    def _extract_evidence_text(self, skill: str, text: str) -> str:
        """Extract relevant evidence text for a skill"""
        sentences = text.split('.')

        for sentence in sentences:
            if skill.lower() in sentence.lower():
                return sentence.strip()

        return text[:100] + '...'

    def search_and_rank(self, question: str, tenant_id: str, top_k: int = 5) -> List[Tuple[Chunk, float]]:
        """Search for relevant chunks and rank them"""
        # Extract keywords from the question for better search
        keywords = self._extract_search_keywords(question)

        # Try multiple search approaches
        all_chunks = []
        seen_chunk_ids = set()

        # Search for each keyword
        for keyword in keywords:
            chunks = self.db.search_chunks_by_text(keyword, tenant_id, top_k * 2)
            for chunk in chunks:
                if chunk.id not in seen_chunk_ids:
                    all_chunks.append(chunk)
                    seen_chunk_ids.add(chunk.id)

        # Also try the full question
        chunks = self.db.search_chunks_by_text(question, tenant_id, top_k * 2)
        for chunk in chunks:
            if chunk.id not in seen_chunk_ids:
                all_chunks.append(chunk)
                seen_chunk_ids.add(chunk.id)

        # If no chunks found, get all chunks for this tenant and filter by similarity
        if not all_chunks:
            docs = self.db.get_tenant_documents(tenant_id)
            for doc in docs:
                doc_chunks = self.db.get_document_chunks(doc.id)
                for chunk in doc_chunks:
                    if chunk.id not in seen_chunk_ids:
                        all_chunks.append(chunk)
                        seen_chunk_ids.add(chunk.id)

        chunks_list = all_chunks
        if not chunks_list:
            return []

        # Generate query embedding
        query_embedding = self.embedding_model.encode(question)

        # Calculate similarity scores
        scored_chunks = []
        for chunk in chunks_list:
            if chunk.embedding is not None:
                similarity = self.embedding_model.similarity(query_embedding, chunk.embedding)
                # Ensure similarity is positive for demo purposes
                similarity = max(0.1, abs(similarity))
            else:
                # Fallback to keyword matching
                question_words = set(question.lower().split())
                chunk_words = set(chunk.text.lower().split())
                if question_words:
                    similarity = len(question_words & chunk_words) / len(question_words)
                else:
                    similarity = 0.1
                # Ensure minimum similarity for relevant chunks
                similarity = max(0.1, similarity)

            scored_chunks.append((chunk, similarity))

        # Sort by score and return top_k
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_k]

    def _extract_search_keywords(self, question: str) -> List[str]:
        """Extract meaningful keywords from a question for search"""
        # Common stop words to exclude
        stop_words = {'what', 'are', 'your', 'do', 'you', 'have', 'can', 'tell', 'me', 'about', 'how', 'when', 'where', 'why', 'is', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

        # Split and clean the question
        words = question.lower().replace('?', '').replace(',', '').split()

        # Filter out stop words and short words
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        return keywords

    def ask(self, question: str, tenant_id: str = "demo-tenant", mode: str = "detailed") -> RAGResponse:
        """Main RAG query method"""
        start_time = time.time()

        # Check if this is a direct skill rating request
        skill_name = self._detect_skill_question(question, tenant_id)
        if skill_name:
            skill_info = self.check_skill(skill_name, tenant_id)
            if skill_info.get('has_skill'):
                answer, citations, sources = self._build_skill_answer(skill_name, skill_info)
            else:
                answer = f"I couldn't find documented evidence for {skill_name}. Please upload projects or resumes that mention this skill."
                citations = []
                sources = []

            latency_ms = int((time.time() - start_time) * 1000)
            self.db.log_query(tenant_id, question, answer, mode, latency_ms)

            return RAGResponse(
                answer=answer,
                citations=citations,
                sources=sources,
                latency_ms=latency_ms,
                mode=mode
            )

        # 1. Search and retrieve relevant chunks
        scored_chunks = self.search_and_rank(question, tenant_id)

        if not scored_chunks:
            # No relevant chunks found
            answer = "I don't have specific information to answer this question. Please provide more context or ask about my documented experience and skills."
            latency_ms = int((time.time() - start_time) * 1000)

            return RAGResponse(
                answer=answer,
                citations=[],
                sources=[],
                latency_ms=latency_ms,
                mode=mode
            )

        # 2. Prepare context from retrieved chunks
        context_chunks = [chunk for chunk, score in scored_chunks]
        chunk_dicts = [
            {
                "text": chunk.text,
                "title": chunk.title,
                "section": chunk.section,
                "source_type": chunk.source_type
            }
            for chunk in context_chunks
        ]

        # 3. Generate answer using LLM
        answer = self.llm.generate_response(question, chunk_dicts, mode)

        # 4. Create citations and sources
        citations = []
        sources = []

        for i, (chunk, score) in enumerate(scored_chunks):
            citation = {
                "index": i + 1,
                "title": chunk.title,
                "section": chunk.section or "Main Content",
                "url": chunk.url,
                "relevance_score": float(score)
            }
            citations.append(citation)

            source = {
                "chunk_id": chunk.id,
                "title": chunk.title,
                "source_type": chunk.source_type,
                "text_preview": chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text,
                "url": chunk.url
            }
            sources.append(source)

        latency_ms = int((time.time() - start_time) * 1000)

        # Log the query
        self.db.log_query(tenant_id, question, answer, mode, latency_ms)

        return RAGResponse(
            answer=answer,
            citations=citations,
            sources=sources,
            latency_ms=latency_ms,
            mode=mode
        )

    def _detect_skill_question(self, question: str, tenant_id: str) -> Optional[str]:
        """Heuristically determine if a question is seeking a skill rating."""
        triggers = ["skill", "rate", "rating", "scale", "level", "proficiency", "competency", "strength"]
        question_lower = question.lower()

        if not any(trigger in question_lower for trigger in triggers):
            return None

        skill_map = {name.lower(): name for name in self.db.get_tenant_skill_names(tenant_id)}
        for key, value in KNOWN_SKILLS.items():
            skill_map.setdefault(key, value)
        tokens = set(re.findall(r"[a-z0-9\+\#\.]+", question_lower))

        for skill_key in sorted(skill_map.keys(), key=len, reverse=True):
            if not skill_key:
                continue
            normalized = skill_key.lower()
            if any(ch in normalized for ch in "+.#"):
                pattern = r"(?<!\w){}(?!\w)".format(re.escape(normalized))
                if re.search(pattern, question_lower):
                    return skill_map[skill_key]
            else:
                pattern = r"(?<!\w){}(?!\w)".format(re.escape(normalized))
                if normalized in tokens and re.search(pattern, question_lower):
                    return skill_map[skill_key]

        return None

    def _build_skill_answer(
        self,
        skill_name: str,
        skill_info: Dict[str, Any]
    ) -> Tuple[str, List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Format a verified response for skill-related questions."""
        confidence = skill_info.get('confidence') or 0.0
        confidence_pct = int(max(confidence, 0.0) * 100)
        evidence_list = skill_info.get('evidence', [])

        if not evidence_list:
            answer = f"I couldn't find direct document references for {skill_name}. Upload additional evidence to improve this skill profile."
            return answer, [], []

        lines = [
            f"**Skill Requested:** {skill_name}",
            f"**Confidence Estimate:** {confidence_pct}% based on documented experience.",
            "Key evidence:"
        ]

        citations: List[Dict[str, Any]] = []
        sources: List[Dict[str, Any]] = []

        for idx, evidence in enumerate(evidence_list, start=1):
            snippet = (evidence.get('text') or '').strip()
            snippet = re.sub(r'\s+', ' ', snippet)
            source_title = evidence.get('title') or "Document"
            section = evidence.get('section') or "Experience"
            chunk_id = evidence.get('chunk_id') or f"skill-{skill_name.lower()}-{idx}"

            lines.append(f"- {source_title} – {snippet[:220]} [{idx}]")

            citations.append({
                "index": idx,
                "title": source_title,
                "section": section,
                "url": evidence.get('url'),
                "chunk_id": chunk_id
            })

            sources.append({
                "chunk_id": chunk_id,
                "title": source_title,
                "section": section,
                "source_type": evidence.get('source_type', 'resume'),
                "url": evidence.get('url'),
                "text_preview": snippet[:200] + ("..." if len(snippet) > 200 else "")
            })

        answer = "\n".join(lines)
        return answer, citations, sources

    def check_skill(self, skill_name: str, tenant_id: str = "demo-tenant") -> Dict[str, Any]:
        """Check if a skill exists and return evidence"""
        return self.db.get_skill_evidence(skill_name, tenant_id)

    def generate_profile_insights(self, tenant_id: str) -> Dict[str, Any]:
        """Provide dynamic topics / skills for personalized UI"""
        cached = self.insights_cache.get(tenant_id)
        if cached:
            return cached

        documents = self.db.get_tenant_documents(tenant_id)
        if not documents:
            empty = {
                "categories": PROFILE_TOPIC_TEMPLATES[:3],
                "top_skills": [],
                "documents": 0
            }
            self.insights_cache.set(tenant_id, empty)
            return empty

        topic_scores = {template['id']: 0 for template in PROFILE_TOPIC_TEMPLATES}
        skill_counter: Counter = Counter()

        for doc in documents:
            chunks = self.db.get_document_chunks(doc.id)
            for chunk in chunks:
                tags = chunk.tags or {}
                for skill in tags.get('skills', []):
                    if skill:
                        skill_counter[skill.lower()] += 1

                text_lower = chunk.text.lower()
                for template in PROFILE_TOPIC_TEMPLATES:
                    if any(keyword in text_lower for keyword in template['keywords']):
                        topic_scores[template['id']] += 1

        sorted_topics = sorted(
            PROFILE_TOPIC_TEMPLATES,
            key=lambda template: topic_scores.get(template['id'], 0),
            reverse=True
        )
        categories = [
            {
                "id": template['id'],
                "title": template['title'],
                "description": template['description'],
                "sampleQuestions": template['sample_questions']
            }
            for template in sorted_topics
            if topic_scores.get(template['id'], 0) > 0
        ]

        if not categories:
            categories = [
                {
                    "id": template['id'],
                    "title": template['title'],
                    "description": template['description'],
                    "sampleQuestions": template['sample_questions']
                }
                for template in PROFILE_TOPIC_TEMPLATES[:3]
            ]

        top_skills = [skill.title() for skill, _ in skill_counter.most_common(6)]

        result = {
            "categories": categories[:5],
            "top_skills": top_skills
        }
        self.insights_cache.set(tenant_id, result)
        return result
