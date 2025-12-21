import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

// Supported platforms for URL import
const SUPPORTED_PLATFORMS = [
  {
    name: "GitHub",
    domain: "github.com",
    example: "https://github.com/username",
    note: "Profile pages"
  },
  {
    name: "LinkedIn",
    domain: "linkedin.com",
    example: "https://linkedin.com/in/username",
    note: "Public profiles"
  },
  {
    name: "Dev.to",
    domain: "dev.to",
    example: "https://dev.to/username",
    note: "Developer profiles"
  },
  {
    name: "Stack Overflow",
    domain: "stackoverflow.com",
    example: "https://stackoverflow.com/users/123/username",
    note: "User profiles"
  },
  {
    name: "Medium",
    domain: "medium.com",
    example: "https://medium.com/@username",
    note: "Writer profiles"
  },
  {
    name: "Personal Portfolio",
    domain: "custom",
    example: "https://yoursite.com",
    note: "Any public site"
  }
];

export async function GET(request: NextRequest) {
  try {
    return NextResponse.json({
      supported_platforms: SUPPORTED_PLATFORMS,
      total: SUPPORTED_PLATFORMS.length
    });
  } catch (error) {
    console.error('Platforms API error:', error);
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
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}