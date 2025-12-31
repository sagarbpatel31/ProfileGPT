import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';

export const dynamic = 'force-dynamic';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || '',
});

// Question intent analysis
function analyzeQuestionIntent(lowerQuestion: string): string {
  // Educational background
  if (lowerQuestion.includes('education') || lowerQuestion.includes('degree') ||
      lowerQuestion.includes('university') || lowerQuestion.includes('study') ||
      lowerQuestion.includes('academic') || lowerQuestion.includes('graduate')) {
    return 'education';
  }

  // Programming languages and skills specifically
  if (lowerQuestion.includes('programming language') ||
      lowerQuestion.includes('programming skill') ||
      lowerQuestion.includes('main programming') ||
      (lowerQuestion.includes('language') && !lowerQuestion.includes('spoken')) ||
      (lowerQuestion.includes('which') && lowerQuestion.includes('language')) ||
      (lowerQuestion.includes('programming') && lowerQuestion.includes('skill'))) {
    return 'programming_languages';
  }

  // Technical skills and tools (broader)
  if (lowerQuestion.includes('technical competenc') ||
      lowerQuestion.includes('core competenc') ||
      lowerQuestion.includes('technical skill') ||
      lowerQuestion.includes('technolog') ||
      lowerQuestion.includes('tool') ||
      lowerQuestion.includes('framework') ||
      (lowerQuestion.includes('skill') && !lowerQuestion.includes('programming'))) {
    return 'technical_skills';
  }

  // Work experience and roles
  if (lowerQuestion.includes('experience') || lowerQuestion.includes('role') ||
      lowerQuestion.includes('job') || lowerQuestion.includes('position') ||
      lowerQuestion.includes('career') || lowerQuestion.includes('work') ||
      lowerQuestion.includes('employ')) {
    return 'experience';
  }

  // Projects and achievements
  if (lowerQuestion.includes('project') || lowerQuestion.includes('achieve') ||
      lowerQuestion.includes('accomplish') || lowerQuestion.includes('built') ||
      lowerQuestion.includes('created') || lowerQuestion.includes('developed')) {
    return 'projects';
  }

  // Professional summary
  if (lowerQuestion.includes('summary') || lowerQuestion.includes('about') ||
      lowerQuestion.includes('background') || lowerQuestion.includes('tell me') ||
      lowerQuestion.includes('who is') || lowerQuestion.includes('introduction')) {
    return 'summary';
  }

  // Default to general inquiry
  return 'general';
}

// Extract relevant content based on question intent
function extractRelevantContent(content: string, intent: string, lowerQuestion: string): any {
  const lines = content.split('\n').filter(line => line.trim());

  switch (intent) {
    case 'education':
      return extractEducationData(lines);
    case 'programming_languages':
      return extractProgrammingLanguagesData(lines);
    case 'technical_skills':
      return extractTechnicalSkillsData(lines);
    case 'experience':
      return extractExperienceData(lines);
    case 'projects':
      return extractProjectsData(lines);
    case 'summary':
      return extractSummaryData(lines, content);
    default:
      return extractContextualData(lines, lowerQuestion);
  }
}

// Generate contextual response based on extracted content
function generateContextualResponse(question: string, contentData: any, intent: string, mode?: string): string {
  if (!contentData || (Array.isArray(contentData) && contentData.length === 0)) {
    return "I don't have specific information about that in the uploaded documents. Please check the document content or provide more details.";
  }

  const isShort = mode === 'short';

  switch (intent) {
    case 'education':
      return formatEducationResponse(contentData, isShort);
    case 'programming_languages':
      return formatProgrammingLanguagesResponse(contentData, isShort);
    case 'technical_skills':
      return formatTechnicalSkillsResponse(contentData, isShort);
    case 'experience':
      return formatExperienceResponse(contentData, isShort);
    case 'projects':
      return formatProjectsResponse(contentData, isShort);
    case 'summary':
      return formatSummaryResponse(contentData, isShort);
    default:
      return formatGeneralResponse(contentData, question, isShort);
  }
}

// Dynamic intelligent response generation without OpenAI
function generateIntelligentResponse(question: string, documentContent: string, mode?: string): string {
  const lowerQuestion = question.toLowerCase();

  console.log('=== DEBUG: generateIntelligentResponse ===');
  console.log('Question:', question);
  console.log('Document content length:', documentContent.length);
  console.log('Document content preview:', documentContent.substring(0, 200));

  // Analyze question intent and extract relevant information dynamically
  const questionIntent = analyzeQuestionIntent(lowerQuestion);
  console.log('Question intent:', questionIntent);

  const relevantContent = extractRelevantContent(documentContent, questionIntent, lowerQuestion);
  console.log('Relevant content:', relevantContent);

  // Generate contextual response based on intent and content
  const response = generateContextualResponse(question, relevantContent, questionIntent, mode);
  console.log('Generated response:', response);
  console.log('=== END DEBUG ===');

  return response;
}

function extractProfessionalSummary(content: string, mode?: string): string {
  const lines = content.split('\n').filter(line => line.trim());

  // Find name (usually first meaningful line that's not contact info)
  const nameMatch = lines.find(line => {
    const trimmed = line.trim();
    return trimmed.length < 50 &&
           trimmed.length > 5 &&
           /^[A-Z][a-z]+ [A-Z][a-z]+/.test(trimmed) &&
           !trimmed.includes('@') &&
           !trimmed.includes('|') &&
           !trimmed.includes('http') &&
           !trimmed.includes('(') &&
           !trimmed.includes('LinkedIn');
  });

  const name = nameMatch?.trim() || 'This professional';

  // Find summary section or extract key info
  let summaryText = '';
  const summaryIndex = lines.findIndex(line =>
    line.toUpperCase().includes('SUMMARY') ||
    line.toUpperCase().includes('OBJECTIVE') ||
    line.toUpperCase().includes('PROFILE')
  );

  if (summaryIndex !== -1) {
    // Get lines after SUMMARY header until next section
    for (let i = summaryIndex + 1; i < lines.length; i++) {
      const line = lines[i]?.trim();
      if (!line) continue;

      // Stop if we hit another section header (all caps, standalone words)
      if (line.toUpperCase() === 'EXPERIENCE' ||
          line.toUpperCase() === 'EDUCATION' ||
          line.toUpperCase() === 'SKILLS' ||
          line.toUpperCase() === 'PROJECTS' ||
          line.toUpperCase() === 'TECHNICAL SKILLS' ||
          line.toUpperCase() === 'CERTIFICATIONS') {
        break;
      }

      summaryText += line + ' ';
    }
  } else {
    // No explicit summary section found - generate from available content
    summaryText = generateSummaryFromContent(content, name);
  }

  // Clean up the summary text
  summaryText = summaryText.replace(/\s+/g, ' ').trim();

  if (mode === 'short') {
    return `**${name}** - ${summaryText.substring(0, 200).trim()}${summaryText.length > 200 ? '...' : ''}`;
  }

  return `**Professional Summary for ${name}**\n\n${summaryText || 'Professional with diverse experience and skills as detailed in uploaded documents.'}`;
}

function extractProgrammingLanguages(content: string, mode?: string): string {
  const lines = content.split('\n').filter(line => line.trim());

  // Programming languages list - more comprehensive
  const programmingLanguages = [
    'Python', 'JavaScript', 'Java', 'C++', 'C', 'C#', 'TypeScript', 'Ruby', 'PHP', 'Swift',
    'Kotlin', 'Go', 'Rust', 'Scala', 'R', 'MATLAB', 'Perl', 'Assembly', 'SQL', 'HTML', 'CSS',
    'Dart', 'Objective-C', 'Shell', 'Bash', 'PowerShell', 'Verilog', 'VHDL', 'Lua', 'Haskell'
  ];

  const foundLanguages: string[] = [];

  // Look in skills section first
  const skillsIndex = lines.findIndex(line =>
    line.toUpperCase().includes('SKILL') ||
    line.toUpperCase().includes('TECHNICAL') ||
    line.toUpperCase().includes('PROGRAMMING') ||
    line.toUpperCase().includes('LANGUAGE')
  );

  if (skillsIndex !== -1) {
    // Extract from skills section
    for (let i = skillsIndex + 1; i < lines.length && i < skillsIndex + 10; i++) {
      const line = lines[i];
      if (line && !line.toUpperCase().match(/^(EXPERIENCE|EDUCATION|PROJECTS|SUMMARY)/)) {
        programmingLanguages.forEach(lang => {
          if (line.includes(lang) && !foundLanguages.includes(lang)) {
            foundLanguages.push(lang);
          }
        });
      } else {
        break;
      }
    }
  }

  // Also search entire content for programming languages
  programmingLanguages.forEach(lang => {
    const regex = new RegExp(`\\b${lang}\\b`, 'gi');
    if (regex.test(content) && !foundLanguages.includes(lang)) {
      foundLanguages.push(lang);
    }
  });

  if (foundLanguages.length === 0) {
    return "Programming languages information can be found in the uploaded documents. Please refer to the skills section for specific language proficiencies.";
  }

  if (mode === 'short') {
    return `**Programming Languages:** ${foundLanguages.slice(0, 5).join(', ')}${foundLanguages.length > 5 ? ', and more...' : ''}`;
  }

  return `**Programming Languages:**\\n\\n• ${foundLanguages.join('\\n• ')}`;
}

function extractSkills(content: string, mode?: string): string {
  const lines = content.split('\n').filter(line => line.trim());
  const skills: string[] = [];

  // Find skills section
  const skillsIndex = lines.findIndex(line =>
    line.toUpperCase().includes('SKILL') ||
    line.toUpperCase().includes('TECHNICAL') ||
    line.toUpperCase().includes('COMPETENC')
  );

  if (skillsIndex !== -1) {
    // Extract skills from skills section
    for (let i = skillsIndex + 1; i < lines.length && i < skillsIndex + 10; i++) {
      if (lines[i] && !lines[i].toUpperCase().match(/^(EXPERIENCE|EDUCATION|PROJECTS|SUMMARY)/)) {
        const line = lines[i].trim();
        if (line.length > 5) {
          skills.push(line);
        }
      } else {
        break;
      }
    }
  } else {
    // Extract skills from content
    const techSkills = content.match(/(?:Python|JavaScript|Java|C\+\+|React|Node\.js|SQL|AWS|Docker|Git|Machine Learning|AI|TensorFlow|PyTorch|Kubernetes|Linux|Windows|MacOS|Android|iOS|Swift|Kotlin|Ruby|PHP|HTML|CSS|TypeScript|Angular|Vue|MongoDB|PostgreSQL|MySQL|Redis|Elasticsearch|Kafka|Jenkins|Terraform|Ansible|CI\/CD)/gi);
    if (techSkills) {
      skills.push(...[...new Set(techSkills)]);
    }
  }

  if (skills.length === 0) {
    return "Core competencies and skills information can be found in the uploaded documents. Please refer to the skills section for detailed technical proficiencies.";
  }

  if (mode === 'short') {
    return `**Core Skills:** ${skills.slice(0, 6).join(', ')}${skills.length > 6 ? ', and more...' : ''}`;
  }

  return `**Core Technical Competencies:**\n\n• ${skills.join('\n• ')}`;
}

function cleanExperienceEntry(entry: string): string {
  return entry
    .replace(/\s+/g, ' ') // Replace multiple spaces with single space
    .replace(/\n\s*\n/g, '\n') // Remove empty lines
    .replace(/\*\*([^*]+)\*\*\s+\*\*([^*]+)\*\*/g, '**$1 $2**') // Merge adjacent bold text
    .trim();
}

function extractExperience(content: string, mode?: string): string {
  const lines = content.split('\n').filter(line => line.trim());
  const experiences: string[] = [];

  // Find experience section - be more flexible with detection
  const expIndex = lines.findIndex(line => {
    const upper = line.toUpperCase().trim();
    return upper === 'EXPERIENCE' ||
           upper === 'EMPLOYMENT' ||
           upper === 'WORK HISTORY' ||
           upper === 'PROFESSIONAL EXPERIENCE' ||
           upper === 'WORK EXPERIENCE' ||
           upper.includes('EXPERIENCE') && upper.length < 25;
  });


  if (expIndex !== -1) {
    // Extract experience details - be more flexible with parsing
    let currentExp = '';
    let experienceCount = 0;

    for (let i = expIndex + 1; i < lines.length && experienceCount < 5; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      // Stop if we hit another major section
      const upperLine = line.toUpperCase();
      if (upperLine === 'EDUCATION' ||
          upperLine === 'SKILLS' ||
          upperLine === 'TECHNICAL SKILLS' ||
          upperLine === 'PROJECTS' ||
          upperLine === 'CERTIFICATIONS' ||
          (upperLine.includes('EDUCATION') && upperLine.length < 25) ||
          (upperLine.includes('SKILLS') && upperLine.length < 25)) {
        break;
      }

      // Detect job title patterns
      const isJobTitle = !line.startsWith('•') &&
                        line.length > 8 &&
                        !line.includes('|') &&
                        !line.match(/^\d/) &&
                        !line.includes('@') &&
                        (line.includes('Engineer') ||
                         line.includes('Developer') ||
                         line.includes('Manager') ||
                         line.includes('Analyst') ||
                         line.includes('Intern') ||
                         line.includes('Specialist') ||
                         line.includes('Lead') ||
                         line.includes('Senior') ||
                         line.includes('Director') ||
                         line.includes('Coordinator') ||
                         line.includes('Research') ||
                         // Or if it's the first substantial line and looks like a title
                         (!currentExp && line.length > 10 && line.length < 80 && !line.includes('@')));

      // Detect company/date line
      const isCompanyLine = line.includes('|') ||
                           (line.match(/\d{4}/) && (line.includes('-') || line.includes('Present') || line.includes('Current'))) ||
                           line.match(/\w+\s+\d{4}\s*-\s*(\w+\s+\d{4}|Present)/);

      if (isJobTitle) {
        // Save previous experience with proper formatting
        if (currentExp.trim()) {
          experiences.push(cleanExperienceEntry(currentExp.trim()));
          experienceCount++;
        }
        currentExp = `**${line}**`;
      } else if (isCompanyLine) {
        currentExp += `  \n*${line}*`; // Add spacing and italics for company/date
      } else if (line.startsWith('•')) {
        // Add bullet points with proper spacing
        currentExp += `  \n${line}`;
      } else if (line.length > 15 && currentExp && !line.includes('@') && !line.includes('http')) {
        // Add description lines with spacing
        currentExp += `  \n• ${line}`;
      }
    }

    // Add the last experience with proper formatting
    if (currentExp.trim()) {
      experiences.push(cleanExperienceEntry(currentExp.trim()));
      experienceCount++;
    }
  }


  if (experiences.length === 0) {
    // Try alternative parsing - look for any lines that might be job titles
    const jobTitleLines = lines.filter(line => {
      const trimmed = line.trim();
      return trimmed.length > 10 &&
             (trimmed.includes('Engineer') ||
              trimmed.includes('Developer') ||
              trimmed.includes('Manager') ||
              trimmed.includes('Analyst') ||
              trimmed.includes('Intern') ||
              trimmed.includes('Lead') ||
              trimmed.includes('Senior'));
    });

    if (jobTitleLines.length > 0) {
      return `**Professional Experience:**\n\n${jobTitleLines.slice(0, 3).map(job => `• ${job}`).join('\n')}`;
    }

    return "Professional experience details are available in the uploaded documents. Please refer to the experience section for comprehensive work history.";
  }

  if (mode === 'short') {
    const firstExp = experiences[0]?.substring(0, 200);
    return `**Recent Experience:** ${firstExp}${experiences[0]?.length > 200 ? '...' : ''}`;
  }

  return `**Professional Experience:**\n\n${experiences.slice(0, 3).join('\n\n---\n\n')}`;
}

function extractEducation(content: string, mode?: string): string {
  const lines = content.split('\n').filter(line => line.trim());
  const educationEntries: string[] = [];

  // Find education section
  const eduIndex = lines.findIndex(line => {
    const upper = line.toUpperCase().trim();
    return upper === 'EDUCATION' ||
           upper === 'ACADEMIC BACKGROUND' ||
           upper === 'ACADEMIC' ||
           (upper.includes('EDUCATION') && upper.length < 25);
  });


  if (eduIndex !== -1) {
    let currentEducation = '';

    for (let i = eduIndex + 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line) continue;

      // Stop if we hit another section
      const upperLine = line.toUpperCase();
      if (upperLine === 'EXPERIENCE' ||
          upperLine === 'SKILLS' ||
          upperLine === 'TECHNICAL SKILLS' ||
          upperLine === 'PROJECTS' ||
          upperLine === 'CERTIFICATIONS' ||
          (upperLine.includes('EXPERIENCE') && upperLine.length < 25) ||
          (upperLine.includes('SKILLS') && upperLine.length < 25)) {
        break;
      }

      // Check if this line contains a degree
      const hasDegree = line.match(/(Bachelor|Master|PhD|B\.S\.|B\.A\.|M\.S\.|M\.A\.|MBA|Associates?|Doctorate)/i);

      // Check if this line looks like a university/school name
      const isUniversity = line.match(/(University|College|Institute|School|Academy)/i) &&
                          !line.includes('Expected:') &&
                          !line.includes('GPA:') &&
                          !line.includes('–');

      // Check if this line has location info
      const hasLocation = line.match(/[A-Z][a-z]+,\s*[A-Z]{2}/) || // City, ST format
                         line.match(/[A-Z][a-z]+,\s*[A-Z][a-z]+/) || // City, Country format
                         line.includes(', CA') || line.includes(', NY') || line.includes(', TX');

      // Check if this line has date info
      const hasDate = line.match(/\d{4}/) ||
                     line.includes('Expected:') ||
                     line.includes('Present') ||
                     line.includes('Dec ') ||
                     line.includes('Jun ') ||
                     line.includes('May ') ||
                     line.includes('Jan ');

      // Check if this line has GPA
      const hasGPA = line.includes('GPA:') || line.includes('GPA ') || line.match(/GPA\s*[:–]\s*[\d\.]+/);

      if (hasDegree) {
        // Start a new education entry
        if (currentEducation) {
          educationEntries.push(currentEducation.trim());
        }
        currentEducation = `**${line}**`;
      } else if (isUniversity) {
        // Add university name
        currentEducation += `\n${line}`;
      } else if ((hasDate || hasGPA) && currentEducation) {
        // Add date or GPA info
        currentEducation += `\n${line}`;
      } else if (hasLocation && currentEducation && !currentEducation.includes(',')) {
        // Add location if not already present
        currentEducation += ` | ${line}`;
      }
    }

    // Add the last education entry
    if (currentEducation) {
      educationEntries.push(currentEducation.trim());
    }

    // Remove duplicates and clean up
    const cleanedEducation = [...new Set(educationEntries)]
      .map(entry => {
        // Clean up formatting
        return entry
          .replace(/\|\s*\|/g, '|') // Remove double pipes
          .replace(/\n\s*\n/g, '\n') // Remove double newlines
          .replace(/\*\*([^*]+)\*\*\s*\*\*([^*]+)\*\*/g, '**$1 $2**') // Merge adjacent bold text
          .trim();
      })
      .filter(entry => entry.length > 10); // Remove very short entries
  }


  if (educationEntries.length === 0) {
    // Fallback: look for degree patterns anywhere in the document
    const degreeMatches = content.match(/(Bachelor|Master|PhD|B\.S\.|B\.A\.|M\.S\.|M\.A\.|MBA|Associates?)[\s\w]+in[\s\w]+/gi);
    if (degreeMatches) {
      return `**Educational Background:**\n\n• ${degreeMatches.slice(0, 3).join('\n• ')}`;
    }
    return "Educational background information is detailed in the uploaded documents.";
  }

  if (mode === 'short') {
    const firstEntry = educationEntries[0].replace(/\*\*/g, '').split('\n')[0]; // Remove bold and take first line
    return `**Education:** ${firstEntry}`;
  }

  return `**Educational Background:**\n\n${educationEntries.join('\n\n')}`;
}

function extractProjects(content: string, mode?: string): string {
  const lines = content.split('\n').filter(line => line.trim());
  const projects: string[] = [];

  // Find projects section
  const projIndex = lines.findIndex(line =>
    line.toUpperCase().includes('PROJECT') ||
    line.toUpperCase().includes('ACHIEVEMENT')
  );

  if (projIndex !== -1) {
    for (let i = projIndex + 1; i < lines.length && i < projIndex + 10; i++) {
      if (lines[i] && !lines[i].toUpperCase().match(/^(EXPERIENCE|EDUCATION|SKILLS|SUMMARY)/)) {
        const line = lines[i].trim();
        if (line.length > 10) {
          projects.push(line);
        }
      } else {
        break;
      }
    }
  }

  if (projects.length === 0) {
    return "Project details and achievements are documented in the uploaded materials.";
  }

  if (mode === 'short') {
    return `**Key Projects:** ${projects[0]?.substring(0, 150)}${projects[0]?.length > 150 ? '...' : ''}`;
  }

  return `**Notable Projects & Achievements:**\n\n• ${projects.slice(0, 3).join('\n• ')}`;
}

function extractBackground(content: string, mode?: string): string {
  const summary = extractProfessionalSummary(content, 'detailed');
  const experience = extractExperience(content, 'short');

  if (mode === 'short') {
    return summary.substring(0, 200) + '...';
  }

  return `${summary}\n\n${experience}`;
}

function extractKeyHighlights(content: string, mode?: string): string {
  const summary = extractProfessionalSummary(content, mode);
  const skills = extractSkills(content, 'short');

  return `${summary}\n\n${skills}`;
}

function generateSummaryFromContent(content: string, name: string): string {
  const lines = content.split('\n').filter(line => line.trim());

  // Extract current/recent job title and company
  let currentRole = '';
  let yearsExp = '';
  let keySkills: string[] = [];
  let topCompanies: string[] = [];
  let education = '';

  // Find current job title from experience section
  const expIndex = lines.findIndex(line => line.toUpperCase() === 'EXPERIENCE');
  if (expIndex !== -1) {
    // Look for the first job title and company after EXPERIENCE header
    for (let i = expIndex + 1; i < Math.min(expIndex + 10, lines.length); i++) {
      const line = lines[i]?.trim();
      if (!line || line.startsWith('•')) continue;

      if (!currentRole && line.length > 5 && !line.includes('|') && !line.match(/\d{4}/)) {
        currentRole = line;
      } else if (line.includes('|') || line.match(/\d{4}/)) {
        // Extract company and years
        const parts = line.split('|').map(p => p.trim());
        if (parts.length >= 2) {
          topCompanies.push(parts[0]);
          // Look for years to calculate experience
          const yearMatch = line.match(/(\d{4})\s*-\s*(Present|\d{4})/);
          if (yearMatch) {
            const startYear = parseInt(yearMatch[1]);
            const endYear = yearMatch[2] === 'Present' ? new Date().getFullYear() : parseInt(yearMatch[2]);
            yearsExp = `${endYear - startYear}+ years`;
          }
        }
        break;
      }
    }
  }

  // Extract key technical skills
  const skillsIndex = lines.findIndex(line =>
    line.toUpperCase().includes('SKILLS') ||
    line.toUpperCase().includes('TECHNICAL')
  );

  if (skillsIndex !== -1) {
    // Get skills section content
    for (let i = skillsIndex + 1; i < Math.min(skillsIndex + 8, lines.length); i++) {
      const line = lines[i]?.trim();
      if (!line) continue;
      if (line.toUpperCase() === 'EDUCATION' ||
          line.toUpperCase() === 'PROJECTS' ||
          line.toUpperCase() === 'EXPERIENCE') break;

      // Extract technology names from skills lines
      const techs = line.match(/(Python|JavaScript|Java|C\+\+|C\/C\+\+|React|Node\.js|AWS|Docker|Kubernetes|Machine Learning|AI|TensorFlow|PyTorch|SQL|MongoDB|PostgreSQL|Git|Linux|Android|iOS|Swift|Kotlin|Ruby|PHP|HTML|CSS|TypeScript|Angular|Vue|Redis|Kafka|Jenkins|CI\/CD|Embedded|FPGA|Verilog|VHDL)/gi);
      if (techs) {
        keySkills.push(...techs);
      }
    }
  }

  // Extract education degree
  const eduIndex = lines.findIndex(line => line.toUpperCase() === 'EDUCATION');
  if (eduIndex !== -1) {
    for (let i = eduIndex + 1; i < Math.min(eduIndex + 5, lines.length); i++) {
      const line = lines[i]?.trim();
      if (!line) continue;
      if (line.match(/(Bachelor|Master|PhD|B\.S\.|M\.S\.|MBA)/i)) {
        education = line.split('|')[0]?.trim() || line.trim();
        break;
      }
    }
  }

  // Build intelligent summary
  let summary = '';

  // Start with role and experience
  if (currentRole && yearsExp && topCompanies.length > 0) {
    summary = `${currentRole} with ${yearsExp} of experience at ${topCompanies[0]}`;
  } else if (currentRole) {
    summary = `${currentRole} with proven experience`;
  } else {
    // Try to infer from skills
    if (keySkills.some(skill => ['C++', 'C/C++', 'Embedded', 'FPGA', 'Verilog'].includes(skill))) {
      summary = `Embedded Software Engineer`;
    } else if (keySkills.some(skill => ['React', 'JavaScript', 'Node.js', 'HTML', 'CSS'].includes(skill))) {
      summary = `Full-Stack Developer`;
    } else if (keySkills.some(skill => ['Python', 'Machine Learning', 'AI', 'TensorFlow', 'PyTorch'].includes(skill))) {
      summary = `AI/ML Engineer`;
    } else if (keySkills.some(skill => ['Java', 'Python', 'SQL'].includes(skill))) {
      summary = `Software Engineer`;
    } else {
      summary = `Technology Professional`;
    }

    if (yearsExp) {
      summary += ` with ${yearsExp} of experience`;
    } else {
      summary += ` with strong technical background`;
    }
  }

  // Add key skills
  const topSkills = [...new Set(keySkills)].slice(0, 4);
  if (topSkills.length > 0) {
    summary += `. Expertise in ${topSkills.join(', ')}`;
  }

  // Add education if significant
  if (education && (education.includes('Master') || education.includes('PhD') || education.includes('Bachelor'))) {
    summary += `. ${education}`;
  }

  // Add companies if multiple
  if (topCompanies.length > 1) {
    summary += `. Previously worked at ${topCompanies.slice(0, 2).join(' and ')}`;
  }

  return summary + '.';
}

// Data extraction functions for new dynamic system
function extractEducationData(lines: string[]): any[] {
  const education: any[] = [];
  const eduIndex = lines.findIndex(line => line.toUpperCase().includes('EDUCATION'));

  if (eduIndex !== -1) {
    let currentEdu: any = {};

    for (let i = eduIndex + 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (!line || line.toUpperCase().match(/^(EXPERIENCE|SKILLS|PROJECTS)/)) break;

      const degreeMatch = line.match(/(Bachelor|Master|PhD|B\.S\.|M\.S\.|MBA)/i);
      const universityMatch = line.match(/(University|College|Institute)/i);
      const yearMatch = line.match(/\d{4}/);
      const gpaMatch = line.match(/GPA\s*[:–]\s*([\d\.]+)/i);

      if (degreeMatch) {
        if (Object.keys(currentEdu).length > 0) education.push(currentEdu);
        currentEdu = { degree: line.trim() };
      } else if (universityMatch) {
        currentEdu.university = line.trim();
      } else if (yearMatch) {
        currentEdu.year = yearMatch[0];
      } else if (gpaMatch) {
        currentEdu.gpa = gpaMatch[1];
      }
    }

    if (Object.keys(currentEdu).length > 0) education.push(currentEdu);
  }

  return education;
}

function extractProgrammingLanguagesData(lines: string[]): string[] {
  const languages = ['Python', 'JavaScript', 'Java', 'C++', 'C', 'C#', 'TypeScript', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Go', 'Rust', 'R', 'SQL', 'HTML', 'CSS', 'Assembly', 'Verilog', 'VHDL'];
  const found: string[] = [];

  const content = lines.join(' ');
  languages.forEach(lang => {
    const regex = new RegExp(`\\b${lang}\\b`, 'i');
    if (regex.test(content) && !found.includes(lang)) {
      found.push(lang);
    }
  });

  return found;
}

function extractTechnicalSkillsData(lines: string[]): string[] {
  const skills: string[] = [];
  const skillsIndex = lines.findIndex(line => line.toUpperCase().includes('SKILL') || line.toUpperCase().includes('TECHNICAL'));

  if (skillsIndex !== -1) {
    for (let i = skillsIndex + 1; i < lines.length && i < skillsIndex + 10; i++) {
      const line = lines[i];
      if (line && !line.toUpperCase().match(/^(EXPERIENCE|EDUCATION|PROJECTS)/)) {
        const cleanLine = line.trim().replace(/^[•\-*]\s*/, '');
        if (cleanLine.length > 3) skills.push(cleanLine);
      } else {
        break;
      }
    }
  }

  return skills;
}

function extractExperienceData(lines: string[]): any[] {
  const experiences: any[] = [];

  console.log('=== DEBUG: extractExperienceData ===');
  console.log('Total lines:', lines.length);
  console.log('First 10 lines:', lines.slice(0, 10));

  const expIndex = lines.findIndex(line => {
    const upperLine = line.toUpperCase().trim();
    return upperLine === 'EXPERIENCE' ||
           upperLine === 'WORK EXPERIENCE' ||
           upperLine === 'PROFESSIONAL EXPERIENCE' ||
           upperLine === 'EMPLOYMENT' ||
           upperLine === 'WORK HISTORY';
  });
  console.log('Experience section index:', expIndex);

  if (expIndex !== -1) {
    console.log('Experience section found at line:', lines[expIndex]);
    let currentExp: any = {};

    for (let i = expIndex + 1; i < lines.length; i++) {
      const line = lines[i].trim();
      console.log(`Processing line ${i}: "${line}"`);

      if (!line || line.toUpperCase().match(/^(EDUCATION|SKILLS|PROJECTS|CERTIFICATIONS)/)) {
        console.log('Stopping at line:', line.toUpperCase());
        break;
      }

      // NEW LOGIC: Detect "Job Title | Company - Location Date" pattern
      const jobTitlePattern = line.match(/^([^|]+)\s*\|\s*([^–-]+)[\s–-]+(.+)$/);

      if (jobTitlePattern) {
        // This is a job title line: "Deep Learning Researcher | Omdena - Remote, Los Angeles, CA   Mar 2025 – Jun 2025"
        console.log('Found job title pattern:', jobTitlePattern);

        // Save previous experience
        if (Object.keys(currentExp).length > 0) {
          experiences.push(currentExp);
        }

        // Extract components
        const title = jobTitlePattern[1].trim();
        const companyAndLocation = jobTitlePattern[2].trim();
        const dateInfo = jobTitlePattern[3].trim();

        currentExp = {
          title: title,
          company: companyAndLocation,
          duration: dateInfo
        };

        console.log('Extracted job:', currentExp);
      }
      // Project line detection
      else if (line.toLowerCase().startsWith('project:')) {
        if (currentExp.title) {
          currentExp.project = line.substring(8).trim();
          console.log('Added project:', currentExp.project);
        }
      }
      // Bullet points
      else if ((line.startsWith('•') || line.startsWith('●')) && currentExp.title) {
        if (!currentExp.achievements) currentExp.achievements = [];
        currentExp.achievements.push(line.substring(1).trim());
        console.log('Added achievement:', line.substring(1).trim());
      }
      // Multi-line bullet points (text that continues from previous bullet)
      else if (line.length > 20 && currentExp.title && !line.includes('@') && !line.includes('http') &&
               !line.match(/^[A-Z][a-z]+\s*\|/) && currentExp.achievements && currentExp.achievements.length > 0) {
        // Append to last achievement
        const lastIndex = currentExp.achievements.length - 1;
        currentExp.achievements[lastIndex] += ' ' + line;
        console.log('Extended last achievement:', currentExp.achievements[lastIndex]);
      }
    }

    // Add the last experience
    if (Object.keys(currentExp).length > 0) {
      experiences.push(currentExp);
    }
  } else {
    console.log('No EXPERIENCE section found in document');
  }

  console.log('Final extracted experiences:', experiences);
  console.log('=== END DEBUG extractExperienceData ===');

  return experiences;
}

function extractProjectsData(lines: string[]): any[] {
  const projects: any[] = [];
  const projIndex = lines.findIndex(line => line.toUpperCase().includes('PROJECT'));

  if (projIndex !== -1) {
    let currentProject: any = {};

    for (let i = projIndex + 1; i < lines.length && i < projIndex + 15; i++) {
      const line = lines[i].trim();
      if (!line || line.toUpperCase().match(/^(EXPERIENCE|EDUCATION|SKILLS|CERTIFICATIONS)/)) break;

      if (!line.startsWith('•') && line.length > 10 && !currentProject.name) {
        currentProject.name = line;
      } else if (line.startsWith('•')) {
        if (!currentProject.details) currentProject.details = [];
        currentProject.details.push(line.substring(1).trim());
      }
    }

    if (Object.keys(currentProject).length > 0) projects.push(currentProject);
  }

  return projects;
}

function extractSummaryData(lines: string[], content: string): any {
  const name = lines.find(line => line.trim().length < 50 && line.trim().length > 5 &&
                          /^[A-Z][a-z]+ [A-Z][a-z]+/.test(line.trim()) &&
                          !line.includes('@'))?.trim() || 'This professional';

  console.log('=== DEBUG: extractSummaryData ===');
  console.log('Looking for SUMMARY section...');

  const summaryIndex = lines.findIndex(line => {
    const upperLine = line.toUpperCase().trim();
    return upperLine === 'SUMMARY' || upperLine === 'PROFESSIONAL SUMMARY' || upperLine === 'OBJECTIVE';
  });

  console.log('Summary section index:', summaryIndex);
  if (summaryIndex !== -1) {
    console.log('Summary section found at line:', lines[summaryIndex]);
  }

  let summary = '';

  if (summaryIndex !== -1) {
    for (let i = summaryIndex + 1; i < lines.length; i++) {
      const line = lines[i]?.trim();
      console.log(`Processing summary line ${i}: "${line}"`);

      if (!line) continue;

      // Stop if we hit another section header
      if (line.toUpperCase().match(/^(EXPERIENCE|EDUCATION|SKILLS|PROJECTS|TECHNICAL SKILLS|CERTIFICATIONS)$/)) {
        console.log('Stopping at section:', line.toUpperCase());
        break;
      }

      summary += line + ' ';
    }
  }

  const finalSummary = summary.trim();
  console.log('Final extracted summary:', finalSummary);
  console.log('=== END DEBUG extractSummaryData ===');

  return { name, summary: finalSummary || null };
}

function extractContextualData(lines: string[], lowerQuestion: string): any {
  // Search for specific terms mentioned in the question
  const relevantLines: string[] = [];
  const questionWords = lowerQuestion.split(' ').filter(word => word.length > 3);

  lines.forEach(line => {
    const lowerLine = line.toLowerCase();
    if (questionWords.some(word => lowerLine.includes(word))) {
      relevantLines.push(line.trim());
    }
  });

  return relevantLines.slice(0, 5); // Limit to most relevant
}

// Formatting functions for responses
function formatEducationResponse(data: any[], isShort: boolean): string {
  if (data.length === 0) return "No education information found in the documents.";

  if (isShort) {
    const first = data[0];
    return `**Education:** ${first.degree || 'Degree information available'} ${first.university ? `from ${first.university}` : ''} ${first.year || ''}`.trim();
  }

  const formatted = data.map(edu => {
    let text = `**${edu.degree || 'Degree'}**`;
    if (edu.university) {
      text += `\n*${edu.university}*`;
      if (edu.year) text += ` | ${edu.year}`;
      if (edu.gpa) text += ` | GPA: ${edu.gpa}`;
    } else {
      if (edu.year) text += ` | ${edu.year}`;
      if (edu.gpa) text += ` | GPA: ${edu.gpa}`;
    }
    return text;
  });

  return `**Educational Background:**\n\n${formatted.join('\n\n')}`;
}

function formatProgrammingLanguagesResponse(data: string[], isShort: boolean): string {
  if (data.length === 0) return "No specific programming languages mentioned in the documents.";

  if (isShort) {
    return `**Programming Languages:** ${data.slice(0, 4).join(', ')}${data.length > 4 ? ', and more...' : ''}`;
  }

  return `**Programming Languages:**\n\n  ◦ ${data.join('\n  ◦ ')}`;
}

function formatTechnicalSkillsResponse(data: string[], isShort: boolean): string {
  if (data.length === 0) return "No specific technical skills section found in the documents.";

  if (isShort) {
    return `**Technical Skills:** ${data.slice(0, 3).join(', ')}${data.length > 3 ? ', and more...' : ''}`;
  }

  return `**Technical Competencies:**\n\n  ◦ ${data.join('\n  ◦ ')}`;
}

// Helper function to format date ranges consistently
function formatDateRange(duration: string): string {
  if (!duration) return '';

  // Handle various date formats and normalize to "MMM YYYY - MMM YYYY" format
  const cleanDuration = duration.trim();

  // Handle "Present" or "Current"
  if (cleanDuration.toLowerCase().includes('present') || cleanDuration.toLowerCase().includes('current')) {
    const match = cleanDuration.match(/(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\w+)\s+(\d{4})/i);
    if (match) {
      return `${match[1]} ${match[2]} - Present`;
    }
  }

  // Handle date ranges with various separators (-, –, to)
  const datePattern = /(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\w+)\s+(\d{4})\s*[-–to]+\s*(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\w+)?\s*(\d{4}|Present)/i;
  const match = cleanDuration.match(datePattern);

  if (match) {
    const startMonth = match[1];
    const startYear = match[2];
    const endMonth = match[3] || match[1]; // Use start month if end month not specified
    const endYear = match[4];

    if (endYear === 'Present') {
      return `${startMonth} ${startYear} - Present`;
    } else {
      return `${startMonth} ${startYear} - ${endMonth} ${endYear}`;
    }
  }

  // If no pattern matches, return as-is
  return cleanDuration;
}

function formatExperienceResponse(data: any[], isShort: boolean): string {
  if (data.length === 0) return "No work experience section found in the documents.";

  if (isShort) {
    const recent = data[0];
    return `**Recent Role:** ${recent.title} ${recent.company ? `at ${recent.company}` : ''}`.trim();
  }

  const formatted = data.slice(0, 3).map(exp => {
    // Format the job title as a clear heading
    let text = `**${exp.title}**`;

    // Build company/location/date line
    const parts = [];
    if (exp.company) parts.push(exp.company);
    if (exp.location) parts.push(exp.location);

    let orgLine = parts.join(' – ');
    if (exp.duration) {
      const formattedDuration = formatDateRange(exp.duration);
      orgLine += ` | ${formattedDuration}`;
    }

    if (orgLine) {
      text += `\n*${orgLine}*`;
    }

    // Add project information if available (as a subtitle)
    if (exp.project) {
      text += `\n**Project:** ${exp.project}`;
    }

    // Add achievements with proper indentation and clean bullet style
    if (exp.achievements && exp.achievements.length > 0) {
      text += '\n';
      const cleanAchievements = exp.achievements.slice(0, 6).map((achievement: string) => {
        // Remove existing bullets and clean text
        let cleanText = achievement.replace(/^[•●]\s*/, '').trim();

        // Handle multiline achievements by joining them properly
        if (cleanText.length > 100) {
          // Split long lines for better readability
          const words = cleanText.split(' ');
          const lines = [];
          let currentLine = '';

          words.forEach(word => {
            if ((currentLine + ' ' + word).length > 100 && currentLine) {
              lines.push(currentLine.trim());
              currentLine = '  ' + word;
            } else {
              currentLine += (currentLine ? ' ' : '') + word;
            }
          });

          if (currentLine) lines.push(currentLine.trim());

          return `    ▪ ${lines.join('\n      ')}`;
        } else {
          return `    ▪ ${cleanText}`;
        }
      });

      text += cleanAchievements.join('\n\n');
    }

    return text;
  });

  return `**Professional Experience:**\n\n${formatted.join('\n\n' + '─'.repeat(50) + '\n\n')}`;
}

function formatProjectsResponse(data: any[], isShort: boolean): string {
  if (data.length === 0) return "No projects section found in the documents.";

  if (isShort) {
    return `**Key Project:** ${data[0].name || 'Project details available in documents'}`;
  }

  const formatted = data.slice(0, 3).map(proj => {
    let text = `**${proj.name}**`;
    if (proj.details && proj.details.length > 0) {
      const cleanDetails = proj.details.slice(0, 4).map((detail: string) => {
        const cleanText = detail.replace(/^[•●]\s*/, '').trim();
        return `  ◦ ${cleanText}`;
      });
      text += `\n${cleanDetails.join('\n')}`;
    }
    return text;
  });

  return `**Notable Projects:**\n\n${formatted.join('\n\n───────────────────\n\n')}`;
}

function formatSummaryResponse(data: any, isShort: boolean): string {
  if (isShort) {
    return `**${data.name}** - ${data.summary ? data.summary.substring(0, 150) + '...' : 'Professional with documented experience and skills.'}`;
  }

  return `**Professional Summary for ${data.name}**\n\n${data.summary || 'Experienced professional with comprehensive background as detailed in uploaded documents.'}`;
}

function formatGeneralResponse(data: any[], question: string, isShort: boolean): string {
  if (data.length === 0) return "I couldn't find specific information about that in the uploaded documents.";

  const relevantInfo = data.slice(0, isShort ? 2 : 4).join(' ');

  if (isShort) {
    return `**Relevant Information:** ${relevantInfo.substring(0, 200)}${relevantInfo.length > 200 ? '...' : ''}`;
  }

  return `**Based on your question about "${question}":**\n\n${relevantInfo}`;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { question, tenantId, mode } = body;

    if (!question?.trim()) {
      return NextResponse.json({ error: 'Question is required' }, { status: 400 });
    }

    // Retrieve stored documents for the specific tenant only
    const currentTenantId = tenantId || 'demo-tenant';

    // Retrieve documents from Supabase instead of global store
    let documents: any[] = [];

    const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const supabaseServiceKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

    if (supabaseUrl && supabaseServiceKey) {
      try {
        const { createClient } = require('@supabase/supabase-js');
        const supabase = createClient(supabaseUrl, supabaseServiceKey);

        // Get documents for this tenant
        const { data: supabaseDocuments, error } = await supabase
          .from('documents')
          .select('*')
          .eq('tenant_id', currentTenantId)
          .eq('status', 'completed');

        if (error) {
          console.error('Supabase documents fetch error:', error);
        } else if (supabaseDocuments) {
          // Transform Supabase documents to expected format
          documents = supabaseDocuments.map((doc: any) => ({
            id: doc.id,
            title: doc.title,
            content: doc.content,
            tenantId: doc.tenant_id,
            source_type: doc.source_type
          }));
        }
      } catch (supabaseError) {
        console.error('Supabase connection error:', supabaseError);
      }
    }

    // Fallback to global store if Supabase isn't available
    if (documents.length === 0) {
      const documentStore = (globalThis as any).documentStore || {};
      const allDocuments = Object.values(documentStore) as any[];
      documents = allDocuments.filter((doc: any) =>
        doc.tenantId === currentTenantId || (!doc.tenantId && currentTenantId === 'demo-tenant')
      );
    }

    if (!process.env.OPENAI_API_KEY) {
      // Fallback response when no API key is available - provide intelligent extraction
      if (documents.length > 0) {
        // Use the most recent or largest document for primary extraction
        const primaryDoc = documents.reduce((prev: any, current: any) =>
          (current.content?.length || 0) > (prev.content?.length || 0) ? current : prev
        );

        const documentContent = primaryDoc.content || '';
        const answer = generateIntelligentResponse(question, documentContent, mode);

        return NextResponse.json({
          answer: answer,
          sources: documents.map((doc: any) => doc.title),
          note: "Response based on document analysis (OpenAI API key needed for enhanced AI responses)"
        });
      } else {
        return NextResponse.json({
          answer: "To create a tailored professional summary, I would need to see your resume, portfolio, or any other relevant documents that highlight your skills, experience, and career goals. Please upload those documents so I can provide you with a personalized summary that accurately reflects your professional background.",
          sources: []
        });
      }
    }

    let systemPrompt = '';
    let sources: string[] = [];

    if (documents.length > 0) {
      // Use actual document content for personalized responses
      const documentContent = documents.map((doc: any) => `Document: ${doc.title}\nContent: ${doc.content}`).join('\n\n');

      systemPrompt = `You are a professional portfolio assistant with access to the user's actual documents. You MUST answer questions based ONLY on the provided document content. DO NOT make up, assume, or infer any information that is not explicitly written in the documents.

CRITICAL RULES:
1. Only mention skills, experiences, companies, achievements, or qualifications that are explicitly stated in the documents
2. Adapt your language and terminology to match the professional field evident in the documents (engineering, medical, business, academic, etc.)
3. For technical fields: Focus on technical skills, tools, technologies, methodologies
4. For medical/biotech: Focus on clinical experience, research, certifications, procedures, specializations
5. For mechanical/engineering: Focus on design tools, manufacturing processes, materials, systems
6. For management/business: Focus on leadership experience, business metrics, team management, strategic initiatives
7. For any field: Always reference actual job titles, companies, projects, and achievements as stated
8. If the document content shows it's a PDF that couldn't be processed, clearly state this limitation
9. If information is not available in the documents, say "This information is not available in your uploaded documents"
10. Never generate or assume any professional details not mentioned in the actual content
11. Be precise and quote directly from the document content when possible

Available Documents:
${documentContent}

Answer the user's question using ONLY the information explicitly provided in the above documents. Adapt your response style to match the professional field while strictly adhering to the document content. If the information isn't there, clearly state that it's not available in the uploaded documents.`;

      sources = documents.map((doc: any) => doc.title);
    } else {
      // Fallback for when no documents are available
      systemPrompt = `You are a professional portfolio assistant. No documents are currently available. Encourage the user to upload their resume, portfolio, or other professional documents for personalized responses.

Explain that you need access to their actual documents (resume, portfolio, LinkedIn profile, etc.) to provide specific insights about their skills and experience.`;
    }

    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        {
          role: 'system',
          content: systemPrompt
        },
        {
          role: 'user',
          content: question
        }
      ],
      max_tokens: 800,
      temperature: 0.3 // Lower temperature for more factual responses
    });

    return NextResponse.json({
      answer: response.choices[0].message.content,
      sources: sources,
      note: documents.length > 0 ? "Response based on your uploaded documents." : "Upload documents for personalized responses."
    });

  } catch (error) {
    console.error('Ask API error:', error);
    return NextResponse.json(
      { error: 'Server error occurred' },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
