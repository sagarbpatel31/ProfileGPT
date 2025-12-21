import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { name, email, password, profession, bio } = body;

    // Generate a unique tenant ID based on email
    const tenantId = email ? email.replace(/[^a-zA-Z0-9]/g, '-').toLowerCase() : 'demo-tenant';

    // Create tenant data
    const tenantData = {
      tenant_id: tenantId,
      name: name || "Demo User",
      email: email || "demo@example.com",
      profession: profession || "Professional",
      bio: bio || "",
      api_key: `api_${Math.random().toString(36).substring(2, 15)}`,
      embed_code: `<script src="https://profile-gpt.vercel.app/widget.js?tenant=${tenantId}"></script>`,
      chat_url: `https://profile-gpt.vercel.app/profile/${tenantId}`
    };

    // In a real app, you would store this in a database
    // For demo purposes, we'll just return the data

    return NextResponse.json({
      ...tenantData,
      message: "Tenant created successfully"
    });

  } catch (error) {
    console.error('Tenant creation error:', error);
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