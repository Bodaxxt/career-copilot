export interface UploadResponse {
  cv_id: string;
  file_url: string;
  status: 'parsed_pending' | 'processing' | 'completed' | 'failed';
  original_filename?: string;
}

export interface UploadErrorResponse {
  detail: string;
  error?: string;
}

export interface CVMetadata {
  id: string;
  userId: string;
  title: string;
  fileUrl?: string;
  isPrimary: boolean;
  status: string;
  createdAt: string;
  updatedAt: string;
}
