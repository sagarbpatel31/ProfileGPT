"""
ProfileGPT - AI-Powered Portfolio Assistant
"""
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
import io
import re
from typing import List, Dict, Any, Optional, Tuple
import openai
from openai import OpenAI
import PyPDF2
from docx import Document
import tiktoken
import uuid
from datetime import datetime
import json

# Enable logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="ProfileGPT API", version="1.0.0")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# In-memory storage for demo (replace with real database in production)
documents_store = {}
chunks_store = {}
tenant_store = {}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://profile-gpt-sagarbpatel31s-projects.vercel.app",
        "http://localhost:3000",  # For local development
        "https://localhost:3000", # For local development with HTTPS
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"Hello": "World", "PORT": os.getenv("PORT", "unknown")}

@app.get("/health")
def health():
    logger.info("Health endpoint called")
    return {"status": "ok", "port": os.getenv("PORT", "unknown")}

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract and clean text from PDF file content with enhanced formatting preservation"""
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text_parts = []

        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text:
                # Clean and normalize the text
                cleaned_text = clean_extracted_text(page_text)
                if cleaned_text.strip():
                    text_parts.append(cleaned_text)

        full_text = "\n\n".join(text_parts)
        return enhance_text_structure(full_text)
    except Exception as e:
        logger.error(f"Error extracting PDF text: {e}")
        return ""

def extract_text_from_docx(file_content: bytes) -> str:
    """Extract and clean text from DOCX file content with enhanced formatting preservation"""
    try:
        doc = Document(io.BytesIO(file_content))
        text_parts = []

        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                cleaned_text = clean_extracted_text(paragraph.text)
                if cleaned_text.strip():
                    text_parts.append(cleaned_text)

        full_text = "\n".join(text_parts)
        return enhance_text_structure(full_text)
    except Exception as e:
        logger.error(f"Error extracting DOCX text: {e}")
        return ""

def clean_extracted_text(text: str) -> str:
    """Clean and normalize extracted text"""
    if not text:
        return ""

    # Remove excessive whitespace and normalize line breaks
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text)

    # Fix common extraction issues
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
    text = re.sub(r'(\d)([A-Za-z])', r'\1 \2', text)  # Add space between numbers and letters
    text = re.sub(r'([A-Za-z])(\d)', r'\1 \2', text)  # Add space between letters and numbers

    # Clean up common formatting artifacts
    text = re.sub(r'[^\w\s\-\.,;:()@#$%&*+=<>?/!"\'\[\]{}|\\`~]', ' ', text)

    return text.strip()

def enhance_text_structure(text: str) -> str:
    """Enhance text structure by identifying sections and improving formatting"""
    if not text:
        return ""

    # Common resume section headers
    section_patterns = [
        r'(PROFESSIONAL\s+SUMMARY|SUMMARY|OBJECTIVE)',
        r'(TECHNICAL\s+SKILLS|SKILLS|CORE\s+COMPETENCIES)',
        r'(PROFESSIONAL\s+EXPERIENCE|WORK\s+EXPERIENCE|EXPERIENCE)',
        r'(EDUCATION|ACADEMIC\s+BACKGROUND)',
        r'(PROJECTS?|KEY\s+PROJECTS?|PROJECT\s+HIGHLIGHTS?)',
        r'(CERTIFICATIONS?|LICENSES?)',
        r'(AWARDS?|ACHIEVEMENTS?|RECOGNITION)',
        r'(PUBLICATIONS?|RESEARCH)',
    ]

    # Add section breaks for better chunking
    for pattern in section_patterns:
        text = re.sub(f'({pattern})', r'\n\n\1\n', text, flags=re.IGNORECASE)

    # Ensure job titles and company names are properly separated
    text = re.sub(r'(\w+\s*\|\s*\w+.*?\|)', r'\n\1\n', text)  # Job | Company | Date format
    text = re.sub(r'(\d{4}\s*-\s*\d{4}|\d{4}\s*-\s*Present)', r' (\1)', text)  # Date ranges

    # Clean up excessive newlines but preserve structure
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()

def extract_structured_info(text: str) -> Dict[str, Any]:
    """Extract structured information from resume text for better context"""
    info = {
        "skills": [],
        "companies": [],
        "roles": [],
        "projects": [],
        "education": [],
        "achievements": [],
        "years_experience": None,
        "contact_info": {}
    }

    # Extract skills
    skill_patterns = [
        r'(?i)(?:skills?|technologies?|tools?|languages?):\s*([^\n]+)',
        r'(?i)(?:proficient|experienced|familiar)\s+(?:in|with):\s*([^\n]+)',
    ]

    for pattern in skill_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            skills = re.split(r'[,;•\|\-]', match)
            info["skills"].extend([skill.strip() for skill in skills if skill.strip()])

    # Extract company names
    company_matches = re.findall(r'(\w[\w\s&.,]+(?:Inc\.?|Corp\.?|LLC|Ltd\.?|Co\.?|Corporation|Company|Solutions?|Technologies?|Systems?))', text)
    info["companies"] = list(set([comp.strip() for comp in company_matches]))

    # Extract job titles (common patterns)
    role_patterns = [
        r'(?i)(senior|lead|principal|staff|director|manager|engineer|developer|scientist|analyst|specialist|architect|consultant)',
        r'(?i)(software|data|product|marketing|financial|business|technical|systems?)',
    ]

    for pattern in role_patterns:
        matches = re.findall(pattern + r'\s+\w+', text)
        info["roles"].extend([role.strip().title() for role in matches])

    # Extract years of experience
    exp_patterns = [
        r'(\d+)\+?\s*years?\s+(?:of\s+)?experience',
        r'(\d+)\+?\s*years?\s+(?:in|with)',
    ]

    for pattern in exp_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            info["years_experience"] = max([int(match) for match in matches])

    # Extract contact information
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        info["contact_info"]["email"] = email_match.group()

    phone_match = re.search(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', text)
    if phone_match:
        info["contact_info"]["phone"] = phone_match.group()

    linkedin_match = re.search(r'linkedin\.com/in/[\w\-]+', text, re.IGNORECASE)
    if linkedin_match:
        info["contact_info"]["linkedin"] = linkedin_match.group()

    return info

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    """Split text into overlapping chunks with enhanced context preservation"""
    if not text:
        return []

    # Extract structured information first
    structured_info = extract_structured_info(text)

    # Split text into semantic sections first
    sections = split_into_sections(text)

    encoding = tiktoken.get_encoding("cl100k_base")
    chunks = []

    for section_title, section_text in sections:
        if not section_text.strip():
            continue

        # Tokenize the section
        tokens = encoding.encode(section_text)

        # If section is small enough, keep it as one chunk
        if len(tokens) <= chunk_size:
            chunk_data = create_chunk_data(
                text=section_text,
                section=section_title,
                structured_info=structured_info,
                chunk_index=len(chunks)
            )
            chunks.append(chunk_data)
        else:
            # Split large sections into chunks with overlap
            start = 0
            section_chunk_index = 0
            while start < len(tokens):
                end = start + chunk_size
                chunk_tokens = tokens[start:end]
                chunk_text = encoding.decode(chunk_tokens)

                # Try to end at sentence boundary for better context
                chunk_text = ensure_sentence_boundary(chunk_text)

                chunk_data = create_chunk_data(
                    text=chunk_text,
                    section=f"{section_title} (Part {section_chunk_index + 1})",
                    structured_info=structured_info,
                    chunk_index=len(chunks)
                )
                chunks.append(chunk_data)

                start = end - overlap
                section_chunk_index += 1
                if start >= len(tokens):
                    break

    return chunks

def split_into_sections(text: str) -> List[Tuple[str, str]]:
    """Split text into logical sections based on headers and content structure"""
    sections = []

    # Common section headers in resumes/profiles
    section_headers = [
        r'(?i)(PROFESSIONAL\s+SUMMARY|SUMMARY|OBJECTIVE)',
        r'(?i)(TECHNICAL\s+SKILLS|SKILLS|CORE\s+COMPETENCIES|TECHNOLOGIES)',
        r'(?i)(PROFESSIONAL\s+EXPERIENCE|WORK\s+EXPERIENCE|EXPERIENCE|EMPLOYMENT)',
        r'(?i)(EDUCATION|ACADEMIC\s+BACKGROUND|QUALIFICATIONS)',
        r'(?i)(PROJECTS?|KEY\s+PROJECTS?|PROJECT\s+HIGHLIGHTS?|NOTABLE\s+PROJECTS?)',
        r'(?i)(CERTIFICATIONS?|LICENSES?|PROFESSIONAL\s+CERTIFICATIONS?)',
        r'(?i)(AWARDS?|ACHIEVEMENTS?|RECOGNITION|HONORS)',
        r'(?i)(PUBLICATIONS?|RESEARCH|PAPERS)',
        r'(?i)(ADDITIONAL\s+INFORMATION|OTHER\s+INFORMATION|MISC)',
    ]

    # Split by section headers
    current_section = "Introduction"
    current_content = []

    lines = text.split('\n')

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check if this line is a section header
        is_header = False
        for header_pattern in section_headers:
            if re.match(header_pattern, line):
                # Save current section if it has content
                if current_content:
                    sections.append((current_section, '\n'.join(current_content)))

                current_section = line
                current_content = []
                is_header = True
                break

        if not is_header:
            current_content.append(line)

    # Add the last section
    if current_content:
        sections.append((current_section, '\n'.join(current_content)))

    return sections

def ensure_sentence_boundary(text: str) -> str:
    """Ensure chunk ends at a sentence boundary for better context"""
    if not text:
        return text

    # Find the last sentence ending
    sentence_endings = ['. ', '! ', '? ', '.\n', '!\n', '?\n']

    last_ending_pos = -1
    for ending in sentence_endings:
        pos = text.rfind(ending)
        if pos > last_ending_pos:
            last_ending_pos = pos

    # If we found a sentence ending in the last 100 characters, use it
    if last_ending_pos > len(text) - 100 and last_ending_pos > len(text) * 0.7:
        return text[:last_ending_pos + 1].strip()

    return text

def create_chunk_data(text: str, section: str, structured_info: Dict[str, Any], chunk_index: int) -> Dict[str, Any]:
    """Create enhanced chunk data with metadata"""

    # Extract relevant skills and concepts from this chunk
    chunk_skills = []
    chunk_concepts = []

    text_lower = text.lower()

    # Check which skills from the document appear in this chunk
    for skill in structured_info.get("skills", []):
        if skill.lower() in text_lower:
            chunk_skills.append(skill)

    # Identify key concepts in this chunk
    concept_patterns = [
        r'(?i)(led|managed|developed|built|designed|implemented|created|optimized|improved)',
        r'(?i)(team|project|system|application|platform|solution|framework|architecture)',
        r'(?i)(performance|scalability|efficiency|quality|security|reliability)',
    ]

    for pattern in concept_patterns:
        matches = re.findall(pattern, text)
        chunk_concepts.extend([match.lower() for match in matches])

    return {
        "text": text,
        "section": section,
        "skills": list(set(chunk_skills)),
        "concepts": list(set(chunk_concepts)),
        "word_count": len(text.split()),
        "contains_metrics": bool(re.search(r'\d+%|\$\d+|\d+[KMB]|\d+x', text)),
        "contains_dates": bool(re.search(r'\d{4}', text)),
        "chunk_index": chunk_index,
        "structured_info": structured_info
    }

def find_relevant_chunks(question: str, tenant_id: str, limit: int = 7) -> List[Dict[str, Any]]:
    """Find relevant document chunks using enhanced semantic matching"""
    relevant_chunks = []
    question_lower = question.lower()

    # Get chunks for this tenant
    tenant_chunks = chunks_store.get(tenant_id, [])

    # Enhanced relevance scoring
    for chunk_data in tenant_chunks:
        score = calculate_chunk_relevance(question_lower, chunk_data)

        if score > 0:
            chunk_data["relevance_score"] = score
            relevant_chunks.append(chunk_data)

    # Sort by relevance and return top chunks
    relevant_chunks.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    return relevant_chunks[:limit]

def calculate_chunk_relevance(question_lower: str, chunk_data: Dict[str, Any]) -> float:
    """Calculate relevance score using multiple factors"""
    score = 0.0
    chunk_text_lower = chunk_data.get("text", "").lower()

    # 1. Exact keyword matching (high weight)
    question_words = [word for word in question_lower.split() if len(word) > 2]
    for word in question_words:
        score += chunk_text_lower.count(word) * 2.0

    # 2. Skill matching (high weight for technical questions)
    chunk_skills = chunk_data.get("skills", [])
    for skill in chunk_skills:
        if skill.lower() in question_lower:
            score += 5.0

    # 3. Concept matching (medium weight)
    chunk_concepts = chunk_data.get("concepts", [])
    for concept in chunk_concepts:
        if concept in question_lower:
            score += 3.0

    # 4. Section relevance (contextual weight)
    section = chunk_data.get("section", "").lower()
    section_weights = {
        "experience": ["experience", "work", "job", "role", "responsibility", "project", "led", "managed"],
        "skills": ["skill", "technology", "tool", "language", "framework", "platform"],
        "education": ["education", "degree", "university", "study", "learn"],
        "projects": ["project", "build", "develop", "create", "implement"],
        "achievements": ["achievement", "award", "recognition", "accomplish"],
    }

    for section_type, keywords in section_weights.items():
        if section_type in section:
            for keyword in keywords:
                if keyword in question_lower:
                    score += 4.0

    # 5. Metrics and quantifiable results (bonus for impact questions)
    if chunk_data.get("contains_metrics", False):
        impact_keywords = ["impact", "result", "improve", "increase", "reduce", "save", "achieve"]
        if any(keyword in question_lower for keyword in impact_keywords):
            score += 3.0

    # 6. Date relevance (recent experience might be more relevant)
    if chunk_data.get("contains_dates", False):
        if any(keyword in question_lower for keyword in ["recent", "current", "latest", "now"]):
            score += 2.0

    # 7. Chunk quality factors
    word_count = chunk_data.get("word_count", 0)
    if 50 <= word_count <= 300:  # Prefer chunks with substantial content
        score += 1.0

    return score

@app.post("/ask")
def ask_question(request: dict):
    logger.info(f"Ask endpoint called with: {request}")
    question = request.get("question", "")
    mode = request.get("mode", "detailed")
    tenant_id = request.get("tenant_id", "demo")

    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    # Get tenant info
    tenant_info = tenant_store.get(tenant_id, {})
    tenant_name = tenant_info.get("name", "User")

    # Find relevant document chunks
    relevant_chunks = find_relevant_chunks(question, tenant_id)

    # Build context from relevant chunks
    context_parts = []
    citations = []
    sources = []

    for i, chunk in enumerate(relevant_chunks):
        context_parts.append(f"Source {i+1}: {chunk['text']}")
        citations.append({
            "id": chunk["id"],
            "source": chunk["source_type"],
            "title": chunk["title"],
            "relevance_score": chunk.get("relevance_score", 0)
        })
        sources.append({
            "id": chunk["id"],
            "title": chunk["title"],
            "source_type": chunk["source_type"],
            "filename": chunk.get("filename", "")
        })

    context = "\n\n".join(context_parts) if context_parts else "No relevant documents found."

    # Create enhanced system prompt based on mode
    system_prompt = create_enhanced_system_prompt(
        tenant_name, mode, context, relevant_chunks, question
    )

def create_enhanced_system_prompt(tenant_name: str, mode: str, context: str,
                                relevant_chunks: List[Dict], question: str) -> str:
    """Create an enhanced system prompt with mode-specific instructions"""

    base_prompt = f"""You are an AI assistant representing {tenant_name}'s professional profile. Your role is to answer questions about their background, experience, and qualifications based solely on the provided documents."""

    if mode == "short":
        style_section = """
RESPONSE STYLE - CONCISE:
- Provide a direct, focused answer in 1-2 sentences maximum
- Include the most relevant facts or figures
- Avoid unnecessary elaboration
- Be specific and factual"""

    elif mode == "star":
        style_section = """
RESPONSE STYLE - STAR METHOD:
Structure your response using the STAR framework when describing experiences or projects:

**Situation**: Briefly set the context or challenge
**Task**: Explain the specific responsibility or goal
**Action**: Describe the concrete steps taken or skills applied
**Result**: Quantify the outcome, impact, or achievement

Format example:
"In [Situation], I was responsible for [Task]. I [Action using specific skills/tools]. This resulted in [quantified Result]."

Use this structure for project descriptions, achievements, and experience-related questions."""

    else:  # detailed
        style_section = """
RESPONSE STYLE - COMPREHENSIVE:
- Provide a thorough, well-structured response
- Include specific examples, technologies, and metrics when available
- Explain the context and significance of experiences
- Connect different aspects of experience when relevant
- Use technical details appropriately for the audience"""

    # Analyze available context for better prompting
    context_analysis = analyze_context_for_prompting(relevant_chunks, question)

    guidelines_section = f"""
RESPONSE GUIDELINES:
1. Only answer based on information in the provided context
2. If the context doesn't contain sufficient information, acknowledge this professionally
3. Be specific about technologies, metrics, and timeframes when available
4. Reference concrete examples and achievements
5. Maintain {tenant_name}'s professional voice and expertise level
6. {context_analysis['guidance']}

AVAILABLE CONTEXT SUMMARY:
- {len(relevant_chunks)} relevant document sections found
- Key sections: {', '.join([chunk.get('section', 'Unknown') for chunk in relevant_chunks[:3]])}
- Contains metrics: {'Yes' if any(chunk.get('contains_metrics', False) for chunk in relevant_chunks) else 'No'}
- Contains recent experience: {'Yes' if any(chunk.get('contains_dates', False) for chunk in relevant_chunks) else 'No'}

CONTEXT FROM {tenant_name.upper()}'S DOCUMENTS:
{context}"""

    return f"{base_prompt}\n{style_section}\n{guidelines_section}"

def analyze_context_for_prompting(relevant_chunks: List[Dict], question: str) -> Dict[str, Any]:
    """Analyze available context to provide better prompting guidance"""
    analysis = {
        "has_technical_details": False,
        "has_metrics": False,
        "has_project_details": False,
        "has_leadership_examples": False,
        "guidance": ""
    }

    question_lower = question.lower()

    # Analyze chunks for content types
    for chunk in relevant_chunks:
        text_lower = chunk.get("text", "").lower()

        if any(tech in text_lower for tech in ["python", "javascript", "aws", "docker", "sql", "react"]):
            analysis["has_technical_details"] = True

        if chunk.get("contains_metrics", False):
            analysis["has_metrics"] = True

        if any(word in text_lower for word in ["project", "built", "developed", "created"]):
            analysis["has_project_details"] = True

        if any(word in text_lower for word in ["led", "managed", "team", "mentor"]):
            analysis["has_leadership_examples"] = True

    # Create specific guidance based on question type and available content
    guidance_parts = []

    if "skill" in question_lower or "technology" in question_lower:
        if analysis["has_technical_details"]:
            guidance_parts.append("Include specific technologies and provide context of usage")
        else:
            guidance_parts.append("Focus on the skills mentioned and their application areas")

    if "project" in question_lower or "experience" in question_lower:
        if analysis["has_project_details"]:
            guidance_parts.append("Describe specific projects with their scope and technologies")
        if analysis["has_metrics"]:
            guidance_parts.append("Include quantifiable results and impact metrics")

    if "lead" in question_lower or "manage" in question_lower or "team" in question_lower:
        if analysis["has_leadership_examples"]:
            guidance_parts.append("Highlight leadership responsibilities and team management experience")

    analysis["guidance"] = ". ".join(guidance_parts) if guidance_parts else "Provide a comprehensive answer based on the available information"

    return analysis

def post_process_response(answer: str, mode: str, relevant_chunks: List[Dict]) -> str:
    """Post-process response for quality and formatting improvements"""
    if not answer:
        return answer

    # Remove excessive whitespace
    answer = re.sub(r'\s+', ' ', answer).strip()

    # Validate STAR format for star mode
    if mode == "star":
        answer = ensure_star_format(answer)

    # Ensure appropriate length for short mode
    if mode == "short":
        sentences = answer.split('. ')
        if len(sentences) > 2:
            answer = '. '.join(sentences[:2])
            if not answer.endswith('.'):
                answer += '.'

    # Add specific improvements based on available context
    if relevant_chunks:
        answer = enhance_with_context_clues(answer, relevant_chunks)

    return answer

def ensure_star_format(answer: str) -> str:
    """Ensure STAR format is properly structured"""
    star_keywords = ["situation", "task", "action", "result"]

    # Check if the response already follows STAR format
    answer_lower = answer.lower()
    has_star_structure = any(keyword in answer_lower for keyword in star_keywords)

    if not has_star_structure:
        # If it's a project or experience description, try to restructure
        if any(word in answer_lower for word in ["project", "developed", "built", "led", "managed", "implemented"]):
            # Add a note about STAR format if the content supports it
            answer += "\n\n(This experience demonstrates skills in project management, technical implementation, and measurable results.)"

    return answer

def enhance_with_context_clues(answer: str, relevant_chunks: List[Dict]) -> str:
    """Enhance answer with additional context clues from chunks"""
    # Check if we have metrics but answer doesn't include them
    has_metrics = any(chunk.get("contains_metrics", False) for chunk in relevant_chunks)
    answer_has_numbers = bool(re.search(r'\d+', answer))

    if has_metrics and not answer_has_numbers:
        # Look for metrics in chunks to potentially add
        for chunk in relevant_chunks[:2]:  # Check top 2 relevant chunks
            chunk_text = chunk.get("text", "")
            metrics = re.findall(r'(\d+%|\$[\d,]+|\d+[KMB]|\d+x|\d+\+)', chunk_text)
            if metrics:
                # Metrics are available but not included - this is expected behavior
                # The LLM should decide what to include
                break

    return answer

    user_prompt = f"Question: {question}"

    try:
        # Call OpenAI API with enhanced parameters
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3 if mode == "short" else 0.5,  # Lower temperature for concise responses
            max_tokens=150 if mode == "short" else 800,   # Adjust token limits by mode
            presence_penalty=0.1,
            frequency_penalty=0.1
        )

        answer = response.choices[0].message.content

        # Post-process response for quality
        answer = post_process_response(answer, mode, relevant_chunks)

        return {
            "answer": answer,
            "citations": citations,
            "sources": sources,
            "context_used": len(relevant_chunks),
            "mode": mode,
            "chunk_metadata": {
                "total_chunks": len(relevant_chunks),
                "sections_used": list(set([chunk.get("section", "Unknown") for chunk in relevant_chunks])),
                "contains_metrics": any(chunk.get("contains_metrics", False) for chunk in relevant_chunks),
                "avg_relevance_score": sum(chunk.get("relevance_score", 0) for chunk in relevant_chunks) / len(relevant_chunks) if relevant_chunks else 0
            }
        }

    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        return {
            "answer": f"I apologize, but I encountered an error while processing your question about {tenant_name}'s background. Please try again later.",
            "citations": citations,
            "sources": sources,
            "error": "AI_API_ERROR"
        }

@app.post("/tenant")
def create_tenant(request: dict):
    logger.info(f"=== TENANT CREATION REQUEST ===")
    logger.info(f"Request data: {request}")

    name = request.get("name", "")
    email = request.get("email", "")
    password = request.get("password", "")
    profession = request.get("profession", "")
    bio = request.get("bio", "")

    if not name or not email:
        raise HTTPException(status_code=400, detail="Name and email are required")

    # Generate tenant ID and API key
    tenant_id = str(uuid.uuid4())[:8]
    api_key = f"pk_test_{tenant_id}"

    # Store tenant data
    tenant_data = {
        "tenant_id": tenant_id,
        "name": name,
        "email": email,
        "profession": profession,
        "bio": bio,
        "api_key": api_key,
        "created_at": datetime.utcnow().isoformat(),
        "document_count": 0
    }
    tenant_store[tenant_id] = tenant_data

    # Initialize empty document and chunk stores for this tenant
    if tenant_id not in documents_store:
        documents_store[tenant_id] = []
    if tenant_id not in chunks_store:
        chunks_store[tenant_id] = []

    logger.info(f"Created tenant: {tenant_id} for {name}")

    return {
        "tenant_id": tenant_id,
        "name": name,
        "email": email,
        "api_key": api_key,
        "embed_code": f'<script src="https://profile-gpt-sagarbpatel31s-projects.vercel.app/widget.js" data-tenant="{tenant_id}"></script>',
        "chat_url": f"https://profile-gpt-sagarbpatel31s-projects.vercel.app?tenant={tenant_id}",
        "message": "Account created successfully! You can now upload documents to build your AI assistant."
    }

@app.post("/ingest")
async def ingest_document(
    file: UploadFile = File(...),
    source_type: str = Form(...),
    tenant_id: str = Form(...),
    title: str = Form(None)
):
    logger.info(f"=== DOCUMENT INGEST REQUEST ===")
    logger.info(f"File: {file.filename}, Size: {file.size}, Type: {file.content_type}")
    logger.info(f"Source Type: {source_type}, Tenant: {tenant_id}, Title: {title}")

    # Check if tenant exists
    if tenant_id not in tenant_store:
        raise HTTPException(status_code=404, detail="Tenant not found")

    try:
        # Read file content
        content = await file.read()
        logger.info(f"File content length: {len(content)} bytes")

        # Extract text based on file type
        text = ""
        if file.content_type == "application/pdf" or file.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(content)
        elif (file.content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              or file.filename.lower().endswith('.docx')):
            text = extract_text_from_docx(content)
        elif file.content_type == "text/plain" or file.filename.lower().endswith('.txt'):
            text = content.decode('utf-8', errors='ignore')
        else:
            # Try to decode as text anyway
            try:
                text = content.decode('utf-8', errors='ignore')
            except Exception:
                raise HTTPException(status_code=400, detail="Unsupported file type")

        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Could not extract meaningful text from document")

        # Generate document ID
        document_id = f"doc_{tenant_id}_{str(uuid.uuid4())[:8]}"

        # Create document record
        document_data = {
            "id": document_id,
            "tenant_id": tenant_id,
            "filename": file.filename,
            "title": title or file.filename,
            "source_type": source_type,
            "content_type": file.content_type,
            "size": len(content),
            "text_length": len(text),
            "created_at": datetime.utcnow().isoformat(),
            "status": "processing"
        }

        # Store document
        if tenant_id not in documents_store:
            documents_store[tenant_id] = []
        documents_store[tenant_id].append(document_data)

        # Process text into enhanced chunks
        chunk_list = chunk_text(text)
        logger.info(f"Created {len(chunk_list)} chunks from document")

        # Store chunks with enhanced metadata
        if tenant_id not in chunks_store:
            chunks_store[tenant_id] = []

        for i, chunk_data in enumerate(chunk_list):
            # Add document-specific metadata
            chunk_data.update({
                "id": f"{document_id}_chunk_{i}",
                "tenant_id": tenant_id,
                "document_id": document_id,
                "filename": file.filename,
                "title": title or file.filename,
                "source_type": source_type,
                "created_at": datetime.utcnow().isoformat()
            })
            chunks_store[tenant_id].append(chunk_data)

        # Update document status
        document_data["status"] = "completed"
        document_data["chunk_count"] = len(chunk_list)

        # Update tenant document count
        tenant_store[tenant_id]["document_count"] += 1

        logger.info(f"Successfully processed document {document_id} with {len(chunk_list)} chunks")

        return {
            "job_id": f"job_{document_id}",
            "status": "completed",
            "message": f"Document '{file.filename}' processed successfully! Created {len(chunk_list)} searchable chunks.",
            "document_id": document_id,
            "filename": file.filename,
            "source_type": source_type,
            "chunk_count": len(chunk_list),
            "text_length": len(text)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/documents/{tenant_id}")
def get_documents(tenant_id: str):
    logger.info(f"=== GET DOCUMENTS FOR TENANT: {tenant_id} ===")

    # Check if tenant exists
    if tenant_id not in tenant_store:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # Get documents for this tenant
    tenant_documents = documents_store.get(tenant_id, [])

    # Return document list
    return {
        "documents": tenant_documents,
        "total_count": len(tenant_documents),
        "tenant_id": tenant_id
    }

# Add middleware to log all requests
@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"=== REQUEST: {request.method} {request.url} ===")
    logger.info(f"Headers: {dict(request.headers)}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

# Add startup event for debugging
@app.on_event("startup")
async def startup_event():
    port = os.getenv("PORT", "unknown")
    logger.info(f"=== FastAPI starting up on PORT: {port} ===")
    logger.info(f"=== Environment variables: PORT={port} ===")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    logger.info(f"=== STARTING UVICORN ON PORT {port} ===")
    logger.info(f"=== ALL ENV VARS: {dict(os.environ)} ===")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")