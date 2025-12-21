import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';

export const dynamic = 'force-dynamic';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || '',
});

export async function POST(request: NextRequest) {
  try {
    // Retrieve stored documents
    const documentStore = (globalThis as any).documentStore || {};
    const documents = Object.values(documentStore) as any[];

    if (documents.length === 0) {
      return NextResponse.json({
        field: "general",
        categories: getDefaultCategories(),
        topSkills: []
      });
    }

    if (!process.env.OPENAI_API_KEY) {
      return NextResponse.json({
        field: "general",
        categories: getDefaultCategories(),
        topSkills: []
      });
    }

    // Analyze the document content to determine field and generate appropriate categories
    const documentContent = documents.map((doc: any) => doc.content).join('\n\n');

    const response = await openai.chat.completions.create({
      model: 'gpt-4o-mini',
      messages: [
        {
          role: 'system',
          content: `Analyze the professional documents and determine:
1. The primary professional field (e.g., "software engineering", "mechanical engineering", "medical", "biotech", "management", "business", "academic", etc.)
2. Generate 6 question categories relevant to this specific field
3. Extract the top 5-8 skills/specializations mentioned

Return a JSON response with this structure:
{
  "field": "detected field name",
  "categories": [
    {
      "id": "category_id",
      "title": "Category Title",
      "description": "Brief description",
      "sampleQuestions": ["Question 1", "Question 2", "Question 3"]
    }
  ],
  "topSkills": ["skill1", "skill2", "skill3", "skill4", "skill5"]
}

Make categories highly relevant to the detected field. For example:
- Software Engineering: Technical Skills, Projects, Experience, AI/ML, Tools, Education
- Mechanical Engineering: Design Experience, CAD/Simulation, Materials, Manufacturing, Projects, Education
- Medical: Clinical Experience, Specializations, Certifications, Research, Procedures, Education
- Management: Leadership, Strategy, Team Building, Business Impact, Operations, Background
- Biotech: Research, Lab Skills, Publications, Technologies, Projects, Education`
        },
        {
          role: 'user',
          content: documentContent.substring(0, 3000) // Limit for API
        }
      ],
      max_tokens: 1000,
      temperature: 0.3
    });

    let analysisResult;
    try {
      analysisResult = JSON.parse(response.choices[0].message.content || '{}');
    } catch (parseError) {
      console.error('Failed to parse AI analysis:', parseError);
      return NextResponse.json({
        field: "general",
        categories: getDefaultCategories(),
        topSkills: []
      });
    }

    return NextResponse.json(analysisResult);

  } catch (error) {
    console.error('Field analysis error:', error);
    return NextResponse.json({
      field: "general",
      categories: getDefaultCategories(),
      topSkills: []
    });
  }
}

function getDefaultCategories() {
  return [
    {
      id: 'bio',
      title: "Professional Background",
      description: "Career overview and experience",
      sampleQuestions: [
        "Give me a professional summary.",
        "What is their background?",
        "Describe their career focus."
      ]
    },
    {
      id: 'experience',
      title: "Work Experience",
      description: "Roles, responsibilities, and achievements",
      sampleQuestions: [
        "Walk me through their recent roles.",
        "What did they accomplish in their last job?",
        "Describe their career progression."
      ]
    },
    {
      id: 'skills',
      title: "Core Skills",
      description: "Key competencies and expertise",
      sampleQuestions: [
        "What are their core competencies?",
        "List their key skills and expertise.",
        "What are they specialized in?"
      ]
    },
    {
      id: 'projects',
      title: "Projects & Achievements",
      description: "Notable work and accomplishments",
      sampleQuestions: [
        "Share their most significant projects.",
        "What notable achievements do they have?",
        "Describe their impactful work."
      ]
    },
    {
      id: 'tools',
      title: "Tools & Technologies",
      description: "Software, equipment, and methodologies",
      sampleQuestions: [
        "What tools and technologies do they use?",
        "Describe their technical toolkit.",
        "What methodologies do they employ?"
      ]
    },
    {
      id: 'education',
      title: "Education & Credentials",
      description: "Academic background and certifications",
      sampleQuestions: [
        "Summarize their education.",
        "What credentials do they hold?",
        "Describe their academic background."
      ]
    }
  ];
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