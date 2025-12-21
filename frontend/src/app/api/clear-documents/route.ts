import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST() {
  try {
    // Clear all stored documents
    (globalThis as any).documentStore = {};

    return NextResponse.json({
      message: "All documents cleared successfully"
    });

  } catch (error) {
    console.error('Clear documents error:', error);
    return NextResponse.json(
      { error: 'Failed to clear documents' },
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