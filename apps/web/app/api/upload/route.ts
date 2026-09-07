import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@clerk/nextjs/server';

export async function POST(request: NextRequest) {
  try {
    // 1. Authenticate with Clerk
    const { userId, getToken } = await auth();

    if (!userId) {
      return NextResponse.json(
        { detail: 'Unauthorized. Please log in to upload your CV.' },
        { status: 401 },
      );
    }

    // 2. Extract token and multipart form data
    const token = await getToken();
    const formData = await request.formData();
    const file = formData.get('file') as File | null;

    if (!file) {
      return NextResponse.json({ detail: 'No file provided in upload request.' }, { status: 400 });
    }

    // Client/Server size check (10MB)
    const MAX_SIZE = 10 * 1024 * 1024;
    if (file.size > MAX_SIZE) {
      return NextResponse.json(
        { detail: 'File too large. Maximum size allowed is 10MB.' },
        { status: 413 },
      );
    }

    // 3. Forward to FastAPI backend
    const backendUrl =
      process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

    const backendResponse = await fetch(`${backendUrl}/api/v1/cvs/upload`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token || userId}`,
      },
      body: formData,
    });

    const responseData = await backendResponse.json();

    return NextResponse.json(responseData, {
      status: backendResponse.status,
    });
  } catch (error: unknown) {
    console.error('Error proxying CV upload:', error);
    return NextResponse.json(
      {
        detail:
          error instanceof Error ? error.message : 'Internal server error while uploading CV.',
      },
      { status: 500 },
    );
  }
}
