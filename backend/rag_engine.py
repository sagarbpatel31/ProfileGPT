"""
RAG (Retrieval-Augmented Generation) Engine for ProfileGPT
"""
import re
import uuid
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import time
import numpy as np
import hashlib

from database import DatabaseManager, Document, Chunk

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

    def generate_response(self, question: str, context: str, mode: str = "detailed") -> str:
        """Generate a conversational response based on actual resume context"""
        question_lower = question.lower()

        # Extract key information from context
        if not context or context.strip() == "":
            return self._friendly_no_context_response(question, mode)

        # Handle personal/casual questions first
        if any(keyword in question_lower for keyword in ["how are you", "how's it going", "how you doing", "what's up", "hey", "hi", "hello"]):
            return self._handle_personal_greeting(context, question, mode)

        # Analyze the question type and context to provide personalized responses
        elif any(keyword in question_lower for keyword in ["python", "programming", "coding", "development"]):
            return self._analyze_python_skills(context, question, mode)

        elif any(keyword in question_lower for keyword in ["experience", "work", "job", "career", "background"]):
            return self._analyze_experience(context, question, mode)

        elif any(keyword in question_lower for keyword in ["skills", "technologies", "tech", "tools"]):
            return self._analyze_technical_skills(context, question, mode)

        elif any(keyword in question_lower for keyword in ["projects", "built", "developed", "created"]):
            return self._analyze_projects(context, question, mode)

        elif any(keyword in question_lower for keyword in ["education", "degree", "university", "study"]):
            return self._analyze_education(context, question, mode)

        elif any(keyword in question_lower for keyword in ["embedded", "hardware", "firmware", "cisco"]):
            return self._analyze_embedded_experience(context, question, mode)

        elif any(keyword in question_lower for keyword in ["ai", "ml", "machine learning", "deep learning"]):
            return self._analyze_ai_experience(context, question, mode)

        else:
            return self._generate_general_response(context, question, mode)

    def _analyze_python_skills(self, context: str, question: str, mode: str) -> str:
        """Analyze Python skills from resume context"""
        if mode == "short":
            return "Yes, I have 2+ years of professional Python experience at Cisco and R-Tek."
        elif mode == "star":
            return "Situation: Working as Embedded Software Engineer at Cisco Systems\nTask: Automate board health monitoring and testing\nAction: Developed Python scripts for automated testing pipelines and QA processes\nResult: Cut manual QA time significantly and enabled daily Linux image testing"

        return ("Absolutely! I have strong Python experience from multiple professional roles:\n\n"
                "• **Cisco Systems**: Used Python extensively to automate board health monitoring, cutting manual QA time and enabling daily Linux image testing pipelines\n\n"
                "• **R-Tek (Current)**: Developing firmware-to-cloud communication protocols and automated testing frameworks using Python\n\n"
                "• **AI/ML Research**: Applied Python with PyTorch, Pandas, and NumPy for deep learning projects like marine plastic debris detection using satellite imagery\n\n"
                "• **Scope**: My Python skills span embedded systems automation, data processing, and machine learning applications")

    def _analyze_experience(self, context: str, question: str, mode: str) -> str:
        """Analyze work experience from context"""
        if mode == "short":
            return "2+ years as Embedded Software Engineer at Cisco, currently Software Developer at R-Tek."
        elif mode == "star":
            return "Situation: Joined Cisco Systems as Embedded Software Engineer\nTask: Lead board bring-up and validation for next-gen enterprise switches\nAction: Developed C/C++ CLI tools, automated Python testing, collaborated across teams\nResult: Achieved high hardware feature verification rate and streamlined board bring-up process"

        return ("I'm an experienced Embedded Software Engineer with 2+ years at Cisco Systems and currently working as a Software Developer at R-Tek. "
                "At Cisco, I led board bring-up and validation for next-generation enterprise switches, working with PHY, FPGA, PoE, and TPM components. I developed C/C++ CLI tools with real-time telemetry support and automated testing pipelines using Python. "
                "Currently at R-Tek, I'm integrating embedded hardware modules like Raspberry Pi, STM32, and ESP32 with cloud services for IoT solutions. "
                "I also have research experience as a Deep Learning Researcher at Omdena, where I developed ResAttUNet models for satellite imagery analysis. "
                "My background combines embedded systems expertise with AI/ML research and cloud integration.")

    def _analyze_technical_skills(self, context: str, question: str, mode: str) -> str:
        """Analyze technical skills from context"""
        if mode == "short":
            return "C/C++, Python, embedded systems, Linux, AI/ML, IoT, and hardware integration."
        elif mode == "star":
            return "Situation: Working across embedded systems and AI domains\nTask: Master diverse technical stacks\nAction: Gained expertise in C/C++, Python, embedded systems, AI/ML frameworks\nResult: Successfully delivered projects spanning firmware, automation, and deep learning"

        return ("I have a comprehensive technical skill set spanning multiple domains:\n\n"
                "• **Programming Languages**: Python, C/C++, Bash scripting\n\n"
                "• **Embedded Systems**: Raspberry Pi, Arduino, STM32, ESP32, Nvidia Jetson Nano, I2C, SPI, UART protocols\n\n"
                "• **AI/ML Stack**: PyTorch, Pandas, Computer Vision, Deep Learning (UNet, Attention UNet), NumPy\n\n"
                "• **Development Tools**: Eclipse IDE, VS Code, GDB, Git, Docker, CI/CD pipelines, MATLAB/Simulink\n\n"
                "• **Operating Systems**: Strong Linux background with device drivers and system-level programming\n\n"
                "My unique combination of embedded systems expertise and AI/ML knowledge allows me to work on cutting-edge projects like autonomous drones and IoT-cloud integration.")

    def _analyze_projects(self, context: str, question: str, mode: str) -> str:
        """Analyze projects from context"""
        if mode == "short":
            return "Built autonomous GPS-less drone, marine plastic detection AI, and IoT cloud systems."
        elif mode == "star":
            return "Situation: Need for autonomous inspection drone without GPS\nTask: Develop complete autonomous navigation system\nAction: Implemented SLAM, path planning, obstacle avoidance using ROS and C++/Python\nResult: Successfully created drone with real-time UI-based goal navigation"

        return ("I've worked on several innovative projects combining embedded systems and AI:\n\n"
                "• **Autonomous Drone Development**: Built a GPS-less inspection drone using Nvidia Jetson Nano and Intel RealSense T265, implementing SLAM, path planning, and obstacle avoidance with ROS\n\n"
                "• **Marine Plastic Detection**: As a Deep Learning Researcher at Omdena, developed an optimized ResAttUNet model achieving 80+ IoU accuracy for detecting plastic debris in satellite imagery of Mediterranean seas\n\n"
                "• **IoT Cloud Integration**: Currently developing firmware-to-cloud communication protocols for embedded modules, enabling real-time data acquisition and remote monitoring\n\n"
                "• **Enterprise Switch Validation**: Led board bring-up for next-gen Cisco switches, developing CLI tools and automated testing frameworks\n\n"
                "These projects showcase my ability to bridge hardware, software, and AI technologies.")

    def _analyze_education(self, context: str, question: str, mode: str) -> str:
        """Analyze educational background"""
        if mode == "short":
            return "MS Computer Science (in progress), MS Embedded Systems from UCI (3.95 GPA), BTech ECE Gold Medalist."
        elif mode == "star":
            return "Situation: Pursuing advanced education in technology\nTask: Build strong academic foundation\nAction: Completed MS in Embedded Systems at UCI with 3.95 GPA, pursuing MS Computer Science\nResult: Gold Medalist in BTech, strong academic performance supporting professional growth"

        return ("I have a strong educational foundation in computer science and embedded systems: "
                "**Current**: Pursuing Master of Science in Computer Science at Sofia University (expected June 2027). "
                "**Completed**: Master of Embedded and Cyber Physical Systems from UC Irvine with an impressive 3.95/4.0 GPA. "
                "**Undergraduate**: Bachelor of Technology in Electronics and Communication Engineering from Charotar University with a perfect 4.0 GPA and Gold Medalist recognition. "
                "My academic background provides a solid theoretical foundation that I've successfully applied in professional roles at companies like Cisco Systems. The combination of embedded systems specialization and computer science breadth gives me a unique perspective on hardware-software integration.")

    def _analyze_embedded_experience(self, context: str, question: str, mode: str) -> str:
        """Analyze embedded systems experience"""
        if mode == "short":
            return "2+ years at Cisco with embedded systems, firmware, and hardware validation expertise."
        elif mode == "star":
            return "Situation: Cisco needed next-gen switch validation\nTask: Lead board bring-up for complex hardware\nAction: Developed C/C++ tools, automated testing, coordinated with multiple teams\nResult: Achieved high validation rates and streamlined development process"

        return ("I have extensive embedded systems experience, primarily from my 2+ years at Cisco Systems where I specialized in enterprise-grade hardware: "
                "**Hardware Validation**: Led board bring-up and validation for next-generation enterprise switches, working with PHY, FPGA, PoE, and TPM components. "
                "**Firmware Development**: Created embedded firmware in C++ for PSE/PSU modules, optimizing runtime diagnostics and reducing response times. "
                "**Real-time Systems**: Developed CLI tools with support for real-time voltage, thermal, and PoE telemetry monitoring. "
                "**Integration**: Currently at R-Tek, I'm integrating various embedded platforms (Raspberry Pi, STM32, ESP32) with cloud services for IoT applications. "
                "**Protocols**: Proficient in I2C, SPI, UART communication protocols and have experience with FreeRTOS and Linux device drivers. "
                "My embedded expertise spans from low-level firmware to system-level integration.")

    def _analyze_ai_experience(self, context: str, question: str, mode: str) -> str:
        """Analyze AI/ML experience"""
        if mode == "short":
            return "Deep learning researcher with ResAttUNet models, PyTorch, and satellite imagery analysis."
        elif mode == "star":
            return "Situation: Need to detect marine plastic debris in satellite imagery\nTask: Develop accurate segmentation model\nAction: Created optimized ResAttUNet with PyTorch, curated Mediterranean dataset\nResult: Achieved 80+ IoU accuracy and contributed to open-source community"

        return ("I have significant AI/ML experience, particularly in computer vision and deep learning:\n\n"
                "• **Research Role**: Working as a Deep Learning Researcher at Omdena on marine plastic debris detection using satellite imagery\n\n"
                "• **Model Development**: Developed and trained an optimized ResAttUNet deep learning model achieving over 80% IoU accuracy for binary segmentation\n\n"
                "• **Data Engineering**: Curated Mediterranean-specific datasets by merging multiple sources (Litter Windrows, MARIDA), applied ACOLITE correction and class balancing techniques\n\n"
                "• **Technical Stack**: Proficient with PyTorch, Pandas, NumPy, and computer vision libraries for deep learning applications\n\n"
                "• **NVIDIA Certification**: Currently advancing my Generative AI and LLM expertise through NVIDIA certification programs\n\n"
                "• **Autonomous Systems**: Applied AI in autonomous drone development, implementing SLAM and path planning algorithms\n\n"
                "My AI background combines practical research experience with real-world applications in autonomous systems.")

    def _generate_general_response(self, context: str, question: str, mode: str) -> str:
        """Generate a general response based on context"""
        if mode == "short":
            return "Based on my background, I can provide insights into embedded systems, AI/ML, and software development."
        elif mode == "star":
            return "Situation: Working across multiple technical domains\nTask: Provide comprehensive technical insights\nAction: Leverage experience in embedded systems, AI, and software development\nResult: Deliver well-rounded perspective on technology challenges"

        return ("Based on my background as an Embedded Software Engineer with AI/ML research experience, I can provide insights across several technical domains. "
                "My professional journey spans embedded systems development at Cisco, IoT cloud integration at R-Tek, and deep learning research at Omdena. "
                "I'm particularly passionate about the convergence of embedded systems and AI, which I believe will drive the next generation of autonomous and intelligent systems. "
                "Feel free to ask me about any specific aspects of my experience - whether it's embedded development, AI/ML projects, hardware integration, or my educational background!")

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

    def _handle_personal_greeting(self, context: str, question: str, mode: str) -> str:
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

class RAGEngine:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.llm = MockLLM()
        self.embedding_model = MockEmbedding()

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

        # Update document status
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
        context = '\n\n'.join([f"From {chunk.title} ({chunk.source_type}): {chunk.text[:300]}..."
                              for chunk in context_chunks])

        # 3. Generate answer using LLM
        answer = self.llm.generate_response(question, context, mode)

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

    def check_skill(self, skill_name: str, tenant_id: str = "demo-tenant") -> Dict[str, Any]:
        """Check if a skill exists and return evidence"""
        return self.db.get_skill_evidence(skill_name, tenant_id)