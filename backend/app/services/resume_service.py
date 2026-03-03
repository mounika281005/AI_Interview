"""
==============================================================================
AI Mock Interview System - Resume Parsing Service
==============================================================================

Service for parsing and extracting information from resumes.
Includes AI-powered validation to clean and verify parsed data.

Author: AI Mock Interview System
Version: 1.0.0
==============================================================================
"""

import re
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from app.config import settings

logger = logging.getLogger(__name__)


class ResumeParsingService:
    """
    Service for parsing resumes and extracting structured information.

    Supports PDF and text-based resumes.
    """

    def __init__(self):
        """Initialize the resume parsing service."""
        self.common_skills = self._load_common_skills()
        self.job_titles = self._load_common_job_titles()

    def _load_common_skills(self) -> List[str]:
        """Load list of common technical skills for matching."""
        return [
            # Programming Languages
            "Python", "JavaScript", "Java", "C++", "C#", "TypeScript", "Go", "Rust",
            "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "SQL",

            # Web Technologies
            "React", "Angular", "Vue", "Node.js", "Express", "Django", "Flask",
            "FastAPI", "Spring", "ASP.NET", "Laravel", "Rails", "HTML", "CSS",
            "Sass", "Less", "Bootstrap", "Tailwind", "jQuery", "Next.js", "Nuxt.js",

            # Databases
            "PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra", "DynamoDB",
            "Oracle", "SQL Server", "SQLite", "Elasticsearch", "Neo4j",

            # Cloud & DevOps
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "GitLab CI",
            "GitHub Actions", "Terraform", "Ansible", "Chef", "Puppet", "CircleCI",

            # Data Science & ML
            "TensorFlow", "PyTorch", "Scikit-learn", "Pandas", "NumPy", "Keras",
            "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
            "Data Analysis", "Statistics",

            # Mobile
            "iOS", "Android", "React Native", "Flutter", "Xamarin",

            # Other
            "Git", "REST API", "GraphQL", "Microservices", "Agile", "Scrum",
            "JIRA", "Linux", "Unix", "Bash", "PowerShell", "CI/CD"
        ]

    def _load_common_job_titles(self) -> List[str]:
        """Load list of common job titles for matching."""
        return [
            "Software Engineer", "Senior Software Engineer", "Lead Software Engineer",
            "Frontend Developer", "Backend Developer", "Full Stack Developer",
            "Web Developer", "Mobile Developer", "iOS Developer", "Android Developer",
            "DevOps Engineer", "Site Reliability Engineer", "SRE",
            "Data Scientist", "Data Engineer", "Data Analyst",
            "Machine Learning Engineer", "AI Engineer",
            "Product Manager", "Technical Product Manager",
            "QA Engineer", "Test Engineer", "Automation Engineer",
            "Security Engineer", "Cloud Engineer", "Solutions Architect",
            "Engineering Manager", "Tech Lead", "CTO", "VP Engineering"
        ]

    async def parse_resume(self, file_path: str, file_name: str) -> Dict[str, Any]:
        """
        Parse a resume file and extract structured information.

        Flow:
        1. Extract raw text from file (PDF/DOCX/TXT)
        2. Clean text
        3. Detect sections using regex
        4. Create structured JSON
        5. Validate data with AI (clean summary)
        6. Return validated JSON

        Args:
            file_path: Path to the resume file
            file_name: Original filename

        Returns:
            Dictionary with parsed and AI-validated resume data
        """
        try:
            # Step 1: Extract raw text from file
            text = await self._extract_text_from_file(file_path)

            if not text:
                raise ValueError("Could not extract text from resume")

            # Step 2-3: Clean text and detect sections using regex
            parsed_data = {
                "parsed_at": datetime.utcnow().isoformat(),
                "file_name": file_name,
                "raw_text": text[:5000],
                "extracted_skills": self._extract_skills(text),
                "work_experience": self._extract_work_experience(text),
                "education": self._extract_education(text),
                "projects": self._extract_projects(text),
                "certifications": self._extract_certifications(text),
                "contact_info": self._extract_contact_info(text),
                "summary": self._extract_summary(text),
                "total_years_experience": self._calculate_years_experience(text)
            }

            # Step 4-5: Validate and clean with AI
            validated_data = await self._validate_with_ai(parsed_data)
            if validated_data:
                # Merge AI-validated data with original (AI overrides regex results)
                parsed_data = self._merge_validated_data(parsed_data, validated_data)
                parsed_data["ai_validated"] = True
            else:
                parsed_data["ai_validated"] = False

            return parsed_data

        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            raise

    async def _validate_with_ai(self, parsed_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate and clean parsed resume data using AI.

        Sends the regex-parsed JSON to the LLM which returns a clean,
        verified summary without assumptions or fabricated data.

        Args:
            parsed_data: Raw regex-parsed resume data

        Returns:
            AI-validated clean JSON, or None if AI validation fails
        """
        try:
            # Build candidate JSON from parsed data (exclude raw_text to save tokens)
            candidate_data = {
                "extracted_skills": parsed_data.get("extracted_skills", []),
                "work_experience": parsed_data.get("work_experience", []),
                "education": parsed_data.get("education", []),
                "projects": parsed_data.get("projects", []),
                "certifications": parsed_data.get("certifications", []),
                "summary": parsed_data.get("summary", ""),
                "total_years_experience": parsed_data.get("total_years_experience", 0)
            }
            candidate_json = json.dumps(candidate_data, indent=2)

            prompt = f"""You are a resume analyzer.

Rules:
- Do NOT assume or calculate missing information
- Use only the given JSON data
- If experience_years is 0, the candidate is a fresher
- Do not add extra skills or roles
- Do not infer seniority

Clean and validate the data below:
- Remove duplicate skills
- Fix obvious skill name typos (e.g., "Pythn" → "Python")
- Remove empty or invalid entries from work_experience, education, projects
- Ensure total_years_experience matches the work_experience dates (do NOT increase it)
- Keep only skills that are real technologies, languages, frameworks, or tools
- Standardize skill names (e.g., "js" → "JavaScript", "node" → "Node.js")

Return a clean summary in JSON format only:

{{
  "extracted_skills": ["skill1", "skill2", ...],
  "work_experience": [
    {{"title": "...", "company": "...", "duration": "..."}}
  ],
  "education": [
    {{"degree": "...", "institution": "...", "year": "..."}}
  ],
  "projects": [
    {{"name": "...", "description": "...", "technologies": ["..."]}}
  ],
  "certifications": ["..."],
  "summary": "...",
  "total_years_experience": 0,
  "experience_level": "fresher|junior|mid|senior"
}}

IMPORTANT:
- Return ONLY valid JSON, no extra text.
- Do NOT add any skill, role, or experience not present in the input.
- If a field is empty or missing, keep it as empty ([] or "").

Candidate Data:
{candidate_json}"""

            # Call AI provider
            ai_provider = settings.ai_provider
            response_text = None

            if ai_provider == "openai" and settings.openai_api_key:
                response_text = await self._call_openai(prompt)
            elif ai_provider == "google" and settings.google_api_key:
                response_text = await self._call_google(prompt)
            elif ai_provider == "huggingface" and settings.huggingface_api_key:
                response_text = await self._call_huggingface(prompt)

            if not response_text:
                logger.info("No AI provider available for resume validation, skipping")
                return None

            # Parse AI response
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            validated = json.loads(response_text.strip())
            logger.info("AI resume validation successful")
            return validated

        except Exception as e:
            logger.warning(f"AI resume validation failed: {e}, using regex-only data")
            return None

    async def _call_openai(self, prompt: str) -> Optional[str]:
        """Call OpenAI API for resume validation."""
        try:
            import asyncio
            import openai
            openai.api_key = settings.openai_api_key

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: openai.chat.completions.create(
                    model=settings.ai_model,
                    messages=[
                        {"role": "system", "content": "You are a resume analyzer. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=2000
                )
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI resume validation error: {e}")
            return None

    async def _call_google(self, prompt: str) -> Optional[str]:
        """Call Google Generative AI for resume validation."""
        try:
            import asyncio
            import google.generativeai as genai
            genai.configure(api_key=settings.google_api_key)
            model = genai.GenerativeModel('gemini-pro')

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, lambda: model.generate_content(prompt)
            )
            return response.text
        except Exception as e:
            logger.error(f"Google AI resume validation error: {e}")
            return None

    async def _call_huggingface(self, prompt: str) -> Optional[str]:
        """Call Hugging Face API for resume validation."""
        try:
            import aiohttp

            headers = {
                "Authorization": f"Bearer {settings.huggingface_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": settings.huggingface_model,
                "messages": [
                    {"role": "system", "content": "You are a resume analyzer. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 2000,
                "temperature": 0.1
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    settings.huggingface_api_url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"HuggingFace resume validation error: {response.status} - {error_text}")
                        return None
                    result = await response.json()
                    return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"HuggingFace resume validation error: {e}")
            return None

    def _merge_validated_data(
        self, original: Dict[str, Any], validated: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge AI-validated data into original parsed data.

        AI-validated fields override regex-parsed fields, but original
        metadata (parsed_at, file_name, raw_text, contact_info) is preserved.
        """
        merged = original.copy()

        # Override with AI-validated fields if present and non-empty.
        # For list/string fields, treat empty ([]/'' ) as "no data".
        for key in [
            "extracted_skills", "work_experience", "education",
            "projects", "certifications", "summary",
        ]:
            if key in validated and validated[key]:
                merged[key] = validated[key]

        # total_years_experience is numeric — 0 is a valid value (fresher),
        # so we must not skip it when it's falsy.
        if "total_years_experience" in validated and validated["total_years_experience"] is not None:
            merged["total_years_experience"] = validated["total_years_experience"]

        # Add experience_level from AI if provided
        if "experience_level" in validated and validated["experience_level"]:
            merged["experience_level"] = validated["experience_level"]

        return merged

    async def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text from PDF or text file."""
        try:
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext == '.pdf':
                return await self._extract_text_from_pdf(file_path)
            elif file_ext in ['.txt', '.text']:
                return await self._extract_text_from_txt(file_path)
            elif file_ext in ['.doc', '.docx']:
                return await self._extract_text_from_docx(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")

        except Exception as e:
            logger.error(f"Error extracting text from file: {e}")
            raise

    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        try:
            # Try using PyPDF2
            try:
                import PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                pass

            # Fallback: Try pdfplumber
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                pass

            # Final fallback: Basic text extraction
            logger.warning("PDF parsing libraries not available. Using basic extraction.")
            with open(file_path, 'rb') as file:
                content = file.read()
                # Very basic PDF text extraction (not reliable)
                text = content.decode('utf-8', errors='ignore')
                return text

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            raise

    async def _extract_text_from_txt(self, file_path: str) -> str:
        """Extract text from text file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            return file.read()

    async def _extract_text_from_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            import docx
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
        except ImportError:
            logger.warning("python-docx not available. Cannot parse DOCX files.")
            raise ValueError("DOCX parsing not supported. Please convert to PDF or TXT.")

    def _extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from resume text."""
        found_skills = []
        text_lower = text.lower()

        for skill in self.common_skills:
            # Case-insensitive search with word boundaries
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.append(skill)

        # Also look for skills in a "Skills" section
        skills_section = self._extract_section(text, ["skills", "technical skills", "technologies"])
        if skills_section:
            # Split by common separators
            additional_skills = re.split(r'[,;•\n\|]', skills_section)
            for skill in additional_skills:
                skill = skill.strip()
                if skill and len(skill) > 2 and skill not in found_skills:
                    found_skills.append(skill)

        return list(set(found_skills))  # Remove duplicates

    def _extract_work_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience from resume.

        Heuristic per block of text inside the experience section:
        1. A line containing a known job title starts a new entry.
        2. The first non-title, non-date line after the title is treated as
           the company name.
        3. A date-range pattern (e.g. "2020 – 2023" or "2021 – present") is
           captured as the duration.
        4. Remaining lines are accumulated as description text.
        """
        experiences = []

        exp_section = self._extract_section(
            text,
            ["experience", "work experience", "professional experience", "employment"]
        )

        if not exp_section:
            return experiences

        lines = exp_section.split('\n')
        current_exp = {}
        title_matched_on_current_line = False

        for line in lines:
            line = line.strip()
            if not line:
                if current_exp:
                    experiences.append(current_exp)
                    current_exp = {}
                continue

            # Check if line contains a known job title → start new entry
            title_matched_on_current_line = False
            for title in self.job_titles:
                if title.lower() in line.lower():
                    if current_exp:
                        experiences.append(current_exp)
                    current_exp = {
                        "title": line,
                        "company": "",
                        "duration": "",
                        "description": ""
                    }
                    title_matched_on_current_line = True
                    break

            if title_matched_on_current_line:
                # Date may appear on the same line as the title
                date_match = re.search(
                    r'20\d{2}\s*[-–]\s*(20\d{2}|present|current)', line.lower()
                )
                if date_match and current_exp:
                    current_exp["duration"] = date_match.group(0)
                continue

            if not current_exp:
                continue

            # Check for date-range on this line
            date_match = re.search(
                r'20\d{2}\s*[-–]\s*(20\d{2}|present|current)', line.lower()
            )
            if date_match:
                current_exp["duration"] = date_match.group(0)
                # Rest of line (minus the date) might be a company name
                remainder = line[:date_match.start()].strip().rstrip('|,–-').strip()
                if remainder and not current_exp["company"]:
                    current_exp["company"] = remainder
                continue

            # If we haven't captured the company yet, treat this line as company
            if not current_exp["company"]:
                current_exp["company"] = line
            else:
                # Accumulate as description
                if current_exp["description"]:
                    current_exp["description"] += " " + line
                else:
                    current_exp["description"] = line

        if current_exp:
            experiences.append(current_exp)

        return experiences[:10]

    def _extract_education(self, text: str) -> List[Dict[str, str]]:
        """Extract education information from resume.

        Heuristic: the line that contains a degree keyword is captured as
        the degree, and the next non-empty, non-degree line is treated as
        the institution name.
        """
        education = []

        edu_section = self._extract_section(text, ["education", "academic background"])

        if not edu_section:
            return education

        degree_keywords = [
            "bachelor", "master", "phd", "doctorate", "associate", "diploma",
            "b.s.", "m.s.", "b.a.", "m.a.", "b.tech", "m.tech", "mba",
            "b.e.", "m.e.", "bca", "mca", "b.sc", "m.sc",
        ]

        lines = edu_section.split('\n')
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            i += 1
            if not line:
                continue

            is_degree_line = any(kw in line.lower() for kw in degree_keywords)
            if not is_degree_line:
                continue

            entry = {
                "degree": line,
                "institution": "",
                "year": self._extract_year(line),
            }

            # Look ahead for an institution line (next non-empty, non-degree line)
            while i < len(lines):
                next_line = lines[i].strip()
                i += 1
                if not next_line:
                    break  # blank line ends this education block
                if any(kw in next_line.lower() for kw in degree_keywords):
                    # It's another degree — rewind so outer loop picks it up
                    i -= 1
                    break
                # Treat first non-degree line as institution
                if not entry["institution"]:
                    entry["institution"] = next_line
                    # Also try to extract year from institution line if missing
                    if not entry["year"]:
                        entry["year"] = self._extract_year(next_line)

            education.append(entry)

        return education

    def _extract_projects(self, text: str) -> List[Dict[str, str]]:
        """Extract project information from resume.

        After building each project block, scan the combined text for any
        known skills so the ``technologies`` list is populated.
        """
        projects = []

        proj_section = self._extract_section(
            text, ["projects", "personal projects", "side projects"]
        )

        if not proj_section:
            return projects

        # Some resumes flatten all projects into a single paragraph like:
        # "Project A|Python, ... <desc> Project B|React, ... <desc> ..."
        # Detect those title anchors and split into separate project blocks.
        anchor_pattern = re.compile(
            r"([A-Z][A-Za-z0-9][A-Za-z0-9&\-\+\.\s]{1,80})\|"
        )
        anchors = list(anchor_pattern.finditer(proj_section))
        if len(anchors) > 1:
            for i, match in enumerate(anchors):
                start = match.start()
                end = anchors[i + 1].start() if i + 1 < len(anchors) else len(proj_section)
                block = proj_section[start:end].strip(" \n|")
                if not block:
                    continue

                name = match.group(1).strip()
                remainder = block[len(match.group(0)):].strip()

                projects.append({
                    "name": name,
                    "description": remainder,
                    "technologies": []
                })

        lines = proj_section.split('\n')
        current_project = None

        for line in lines:
            line = line.strip()
            if not line:
                if current_project:
                    projects.append(current_project)
                    current_project = None
                continue

            if not current_project:
                current_project = {
                    "name": line,
                    "description": "",
                    "technologies": []
                }
            else:
                if current_project["description"]:
                    current_project["description"] += " " + line
                else:
                    current_project["description"] = line

        if current_project:
            projects.append(current_project)

        # De-duplicate by normalized name while preserving order
        deduped = []
        seen_names = set()
        for proj in projects:
            name_key = (proj.get("name") or "").strip().lower()
            if not name_key or name_key in seen_names:
                continue
            seen_names.add(name_key)
            deduped.append(proj)
        projects = deduped

        # Populate technologies by scanning each project's text for known skills
        for proj in projects:
            block = f"{proj['name']} {proj['description']}".lower()
            techs = []
            for skill in self.common_skills:
                pattern = r'\b' + re.escape(skill.lower()) + r'\b'
                if re.search(pattern, block):
                    techs.append(skill)
            proj["technologies"] = techs

        return projects[:5]

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications from resume."""
        certifications = []

        cert_section = self._extract_section(
            text,
            ["certifications", "certificates", "licenses"]
        )

        if cert_section:
            lines = cert_section.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 5:
                    certifications.append(line)

        return certifications

    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from resume."""
        contact = {}

        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        if email_match:
            contact["email"] = email_match.group(0)

        # Extract phone
        phone_match = re.search(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        if phone_match:
            contact["phone"] = phone_match.group(0)

        # Extract LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', text.lower())
        if linkedin_match:
            contact["linkedin"] = linkedin_match.group(0)

        return contact

    def _extract_summary(self, text: str) -> str:
        """Extract professional summary from resume."""
        summary_section = self._extract_section(
            text,
            ["summary", "professional summary", "objective", "profile"]
        )

        if summary_section:
            # Return first 500 characters
            return summary_section[:500].strip()

        # Fallback: Return first few lines
        lines = text.split('\n')
        summary_lines = []
        for line in lines[:10]:
            line = line.strip()
            if len(line) > 20:
                summary_lines.append(line)
                if len(' '.join(summary_lines)) > 200:
                    break

        return ' '.join(summary_lines)[:500]

    def _calculate_years_experience(self, text: str) -> int:
        """Calculate total years of experience from the work-experience section only.

        Previous implementation scanned the entire resume, accidentally counting
        date ranges from education (e.g. "2018-2022") and projects, which
        inflated the total for candidates with no real work experience.
        """
        # Only look at the work-experience section
        exp_section = self._extract_section(
            text,
            ["experience", "work experience", "professional experience", "employment"]
        )

        if not exp_section:
            return 0

        year_ranges = re.findall(
            r'(20\d{2})\s*[-–]\s*(20\d{2}|present|current)',
            exp_section.lower()
        )

        total_years = 0
        current_year = datetime.now().year

        for start, end in year_ranges:
            start_year = int(start)
            end_year = current_year if end in ('present', 'current') else int(end)
            total_years += max(0, end_year - start_year)

        # Cap at 50 years
        return min(total_years, 50)

    def _extract_section(self, text: str, section_names: List[str]) -> Optional[str]:
        """Extract a specific section from resume text."""
        text_lower = text.lower()

        for section_name in section_names:
            # Look for section header
            pattern = r'\n\s*' + re.escape(section_name) + r'\s*[:\n]'
            match = re.search(pattern, text_lower)

            if match:
                start_idx = match.end()
                # Find next section or end of text
                next_section_match = re.search(
                    r'\n\s*[A-Z][A-Za-z\s]{3,30}[:\n]',
                    text[start_idx:]
                )

                if next_section_match:
                    end_idx = start_idx + next_section_match.start()
                else:
                    end_idx = len(text)

                return text[start_idx:end_idx].strip()

        return None

    def _extract_year(self, text: str) -> str:
        """Extract year from text."""
        year_match = re.search(r'20\d{2}', text)
        return year_match.group(0) if year_match else ""
