# 📖 Career Copilot API Reference

All backend API routes are prefixed with `/api/v1`.

## Endpoints

### 1. Health Check
- **URL:** `/api/v1/health`
- **Method:** `GET`
- **Response:**
  ```json
  {
    "status": "healthy",
    "service": "career-copilot-api",
    "version": "1.0.0"
  }
  ```

### 2. Career Assessment
- **URL:** `/api/v1/assessment`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "skills": ["TypeScript", "FastAPI", "React", "Docker"],
    "target_role": "Senior Fullstack Engineer"
  }
  ```

### 3. Resume Analyze
- **URL:** `/api/v1/resumes/analyze`
- **Method:** `POST`
- **Request Body:**
  ```json
  {
    "content": "Resume text string...",
    "target_job_description": "Job specs..."
  }
  ```
