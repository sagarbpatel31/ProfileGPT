import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

// Simple demo login - in production, this would validate against a database
const DEMO_USERS = {
  'demo@example.com': {
    password: 'demo123',
    tenant_id: 'demo-tenant',
    name: 'Demo User',
    email: 'demo@example.com',
    profession: 'Software Engineer',
    api_key: 'demo-api-key',
    embed_code: '<script src="https://profile-gpt.vercel.app/widget.js?tenant=demo-tenant"></script>',
    chat_url: 'https://profile-gpt.vercel.app/profile/demo-tenant'
  }
};

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = body;

    console.log('Login attempt:', { email, password: password ? '[PROVIDED]' : '[MISSING]' });

    if (!email || !password) {
      console.log('Missing email or password');
      return NextResponse.json(
        { error: 'Email and password are required' },
        { status: 400 }
      );
    }

    // Check for demo user or any stored users in localStorage (this is a demo implementation)
    const normalizedEmail = email.toLowerCase().trim();
    const demoUser = (DEMO_USERS as any)[normalizedEmail];

    console.log('Looking for user with email:', normalizedEmail);
    console.log('Available demo users:', Object.keys(DEMO_USERS));
    console.log('Found demo user:', !!demoUser);

    if (demoUser) {
      console.log('Password match:', demoUser.password === password);
      console.log('Expected password:', demoUser.password);
      console.log('Provided password:', password);
    }

    if (demoUser && demoUser.password === password) {
      // Return user data without password
      const { password: _, ...userInfo } = demoUser;
      console.log('Login successful for:', email);
      return NextResponse.json(userInfo);
    }

    // If no user found, return error
    console.log('Login failed for:', email);
    return NextResponse.json(
      { detail: 'Invalid email or password' },
      { status: 401 }
    );

  } catch (error) {
    console.error('Login error:', error);
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