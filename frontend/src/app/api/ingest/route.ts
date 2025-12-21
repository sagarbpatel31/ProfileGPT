import { NextRequest, NextResponse } from 'next/server';
import OpenAI from 'openai';
import pdf from 'pdf-parse';
import { getBackendBaseUrl } from '@/lib/getBackendBaseUrl';

export const dynamic = 'force-dynamic';

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY || '',
});

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;
    const tenantId = (formData.get('tenant_id') as string) || 'demo-tenant';
    const sourceType = (formData.get('source_type') as string) || 'uploaded';

    if (!file) {
      return NextResponse.json({ error: 'No file uploaded' }, { status: 400 });
    }

    // Read file content
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    let textContent = '';
    const filename = file.name;

    // Simple text extraction based on file type
    if (filename.toLowerCase().endsWith('.txt')) {
      textContent = buffer.toString('utf-8');
    } else if (filename.toLowerCase().endsWith('.pdf')) {
      // Extract text from PDF using pdf-parse
      try {
        const pdfData = await pdf(buffer);
        textContent = pdfData.text.trim();

        if (!textContent) {
          textContent = `PDF file '${filename}' was processed but no readable text could be extracted. This may be due to:
1. The PDF being image-based (scanned document)
2. The PDF being password protected
3. The PDF having formatting that prevents text extraction

Please try converting your PDF to a text (.txt) file for better results.`;
        }
      } catch (error) {
        console.error('PDF parsing error:', error);
        textContent = `Error processing PDF file '${filename}'. Please convert to a text (.txt) file for better compatibility.`;
      }
    } else if (filename.toLowerCase().endsWith('.docx')) {
      textContent = `DOCX file '${filename}' received. Content extraction would require additional libraries in production.`;
    } else {
      textContent = `File '${filename}' received. Type: ${filename.split('.').pop() || 'unknown'}`;
    }

    // Generate a quick summary (limit processing time to improve upload speed)
    let summary = "File uploaded successfully.";
    if (process.env.OPENAI_API_KEY && textContent.length > 50 && textContent.length < 5000) {
      try {
        // Only generate summary for smaller documents to keep upload fast
        const response = await openai.chat.completions.create({
          model: 'gpt-4o-mini',
          messages: [
            {
              role: 'system',
              content: 'Create a very brief 1-sentence summary of this document.'
            },
            {
              role: 'user',
              content: textContent.substring(0, 1000) // Smaller content for faster processing
            }
          ],
          max_tokens: 50, // Reduced for faster generation
          temperature: 0.3
        });
        summary = response.choices[0].message.content || summary;
      } catch (summaryError) {
        console.error('Summary generation error:', summaryError);
        summary = "File processed successfully.";
      }
    } else if (textContent.length >= 5000) {
      summary = "Large document processed successfully.";
    }

    // Send the file to the backend API for persistent storage/chunking
    const backendFormData = new FormData();
    backendFormData.append(
      'file',
      new Blob([buffer], { type: file.type || 'application/octet-stream' }),
      filename
    );
    backendFormData.append('source_type', sourceType);
    backendFormData.append('tenant_id', tenantId);
    if (formData.get('title')) {
      backendFormData.append('title', formData.get('title') as string);
    }

    const backendUrl = `${getBackendBaseUrl()}/ingest`;
    const backendResponse = await fetch(backendUrl, {
      method: 'POST',
      body: backendFormData,
    });

    const backendData = await backendResponse.json().catch(() => ({}));
    if (!backendResponse.ok) {
      const errorMessage =
        backendData?.detail ||
        backendData?.message ||
        'Backend ingestion failed';
      return NextResponse.json(
        { error: errorMessage },
        { status: backendResponse.status }
      );
    }

    const preview =
      textContent.length > 0
        ? textContent.substring(0, 500) + (textContent.length > 500 ? '...' : '')
        : undefined;

    return NextResponse.json({
      message:
        backendData.message || 'Document uploaded and processed successfully',
      document: {
        id: backendData.document_id || backendData.id || filename,
        title: backendData.filename || filename,
        source_type: backendData.source_type || sourceType,
        status: backendData.status || 'processed',
        summary,
        size: buffer.length,
        content: preview,
        chunks_created: backendData.chunk_count || 0,
      },
      backend: backendData,
    });

  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json(
      { error: 'Upload error occurred' },
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
