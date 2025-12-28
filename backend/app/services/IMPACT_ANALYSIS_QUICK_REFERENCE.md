# Impact Analysis Agent - Quick Reference Guide

## Overview
The unified Impact Analysis Agent provides comprehensive impact analysis and tech stack recommendations. It can operate in two modes:
1. **Service Mode** - Integrated into SDLC workflow
2. **Standalone Mode** - Independent FastAPI server

## Usage Examples

### 1. SDLC Workflow Integration (Service Mode)

```python
from app.services.impact_analysis_agent import impact_analysis_service

# Basic impact analysis
result = await impact_analysis_service.analyze_impact(
    prd_content="Your PRD content here",
    architecture_content="Your architecture document here",
    github_url="https://github.com/user/repo"
)

# Access results
report = result["report_content"]  # Markdown report
file_id = result["file_id"]        # For download
project_info = result["project_info"]  # Extracted metadata
```

### 2. Tech Stack Focused Analysis

```python
# Detailed tech stack analysis with alternatives
tech_analysis = await impact_analysis_service.analyze_with_tech_stack_focus(
    repo_url="https://github.com/user/repo",
    architecture_content="Architecture document content",
    prd_content="Optional PRD content"
)

print(tech_analysis)  # Detailed tech stack recommendations
```

### 3. Repository Analysis Only

```python
# Analyze repository structure and technologies
repo_data = impact_analysis_service.clone_and_analyze_repo(
    "https://github.com/user/repo"
)

print(repo_data["languages"])      # Detected languages
print(repo_data["structure"])      # File structure
print(repo_data["dependencies"])   # Dependencies found
```

### 4. File Processing

```python
# Extract text from uploaded files
file_data = await file.read()  # From FastAPI UploadFile
text = impact_analysis_service.extract_text_from_file(
    file_data, 
    "document.pdf"
)

# Generate PDF report
pdf_bytes = impact_analysis_service.generate_pdf(
    content="Report content here",
    title="Impact Analysis Report"
)

# Generate DOCX report
docx_bytes = impact_analysis_service.generate_docx(
    content="Report content here",
    title="Impact Analysis Report"
)
```

### 5. Standalone Server Mode

```bash
# Start standalone server
cd backend/app/services
python impact_analysis_agent.py

# Server will start on available port (8090+)
# Access web UI at: http://localhost:8090
```

## API Endpoints (Standalone Mode)

### GET /
Web interface for uploading files and analyzing projects

### POST /upload-file
Upload and extract text from documents
```json
{
  "file": "multipart/form-data"
}
```

Response:
```json
{
  "success": true,
  "extracted_text": "...",
  "filename": "document.pdf"
}
```

### POST /analyze
Perform comprehensive analysis
```json
{
  "repo_url": "https://github.com/user/repo",
  "architecture_content": "...",
  "prd_content": "...",
  "include_tech_stack": true
}
```

Response:
```json
{
  "success": true,
  "analysis": "...",
  "document_id": "uuid",
  "timestamp": "2025-12-27T10:54:14Z"
}
```

## Configuration

### Environment Variables

```bash
# Primary LLM (Internal Service)
# Configured in app.services.llm

# Fallback LLM (Groq API)
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
GROQ_TEMPERATURE=0.3
GROQ_MAX_TOKENS=4500

# Repository Analysis
GIT_CLONE_TIMEOUT=60
MAX_ARCH_CHARS=3000

# File Storage
GENERATED_FILES_DIR=generated_files
```

### Optional Dependencies

```bash
# For PDF/DOCX processing
pip install PyPDF2 python-docx reportlab

# For standalone server
pip install fastapi uvicorn
```

## Output Structure

### Comprehensive Report Sections

1. **Project Summary**
   - Business goals
   - User flows
   - Platform scope

2. **Architecture Overview**
   - System diagram (ASCII)
   - Data flow
   - Component relationships

3. **Tech Stack Impact**
   - Frontend analysis
   - Backend analysis
   - Database analysis
   - Strengths/limitations

4. **Alternative Technologies**
   - Backend alternatives (3+ options)
   - Database alternatives (3+ options)
   - Frontend alternatives (3+ options)
   - Migration impact

5. **Database Impact**
   - Schema design
   - Scalability analysis
   - Performance considerations

6. **API Design Impact**
   - Endpoint design
   - Security considerations
   - Versioning strategy

7. **Security Analysis**
   - Authentication/Authorization
   - Data protection
   - Threat assessment
   - Compliance

8. **Performance & Scalability**
   - Traffic handling
   - Scaling strategies
   - Bottleneck identification

9. **Business & Cost Impact**
   - Development costs
   - Operational costs
   - ROI analysis
   - Timeline estimates

10. **Risk Analysis**
    - Technical risks
    - Business risks
    - Security risks
    - Mitigation strategies

11. **Implementation Roadmap**
    - Phase-wise breakdown
    - Dependencies
    - Critical path

12. **Impact Scorecard**
    - Technical robustness (1-10)
    - Scalability (1-10)
    - Security (1-10)
    - Maintainability (1-10)
    - Business alignment (1-10)

13. **Recommendations**
    - Architecture improvements
    - Technology upgrades
    - Risk mitigation
    - Next steps

## Common Use Cases

### Use Case 1: SDLC Step 3 (Automated)
```python
# In agents.py orchestrate_full_sdlc endpoint
impact_data = await impact_analysis_service.analyze_impact(
    "Source Project Context", 
    arch_context, 
    github_url
)

return {
    "status": "success",
    "step": 3,
    "agent": "Impact Analysis Agent",
    "output": impact_data["report_content"],
    "file_id": impact_data["file_id"]
}
```

### Use Case 2: Manual Analysis
```python
# Direct service call
result = await impact_analysis_service.analyze_impact(
    prd_content=prd_text,
    architecture_content=arch_text,
    github_url="https://github.com/user/repo",
    include_tech_stack_analysis=True
)

# Save to file
with open("impact_report.md", "w") as f:
    f.write(result["report_content"])
```

### Use Case 3: Tech Stack Comparison
```python
# Compare multiple tech stacks
analysis = await impact_analysis_service.analyze_with_tech_stack_focus(
    repo_url="https://github.com/user/repo",
    architecture_content=arch_doc,
    prd_content=prd_doc
)

# Analysis includes detailed alternatives and recommendations
```

## Troubleshooting

### Issue: "No LLM service available"
**Solution**: Configure either:
- Internal LLM service in `app.services.llm`, OR
- Set `GROQ_API_KEY` environment variable

### Issue: "PDF generation not supported"
**Solution**: Install reportlab
```bash
pip install reportlab
```

### Issue: "Repository clone failed"
**Solution**: 
- Check network connectivity
- Verify repository URL is public
- Increase `GIT_CLONE_TIMEOUT`
- Check git is installed

### Issue: "Rate limit exceeded"
**Solution**:
- Wait 60 seconds before retrying
- Service automatically retries with backoff
- Consider upgrading Groq API plan

### Issue: "File extraction failed"
**Solution**: Install required dependencies
```bash
pip install PyPDF2 python-docx
```

## Best Practices

1. **Always provide architecture content** - It's the primary input for analysis
2. **Include GitHub URL when possible** - Enables repository analysis
3. **Use PRD content for context** - Improves analysis quality
4. **Enable tech stack analysis** - Provides comprehensive alternatives
5. **Review generated reports** - Verify recommendations match requirements
6. **Store file_id for downloads** - Enables later retrieval

## Performance Tips

1. **Repository Size**: Large repos may take longer to clone
2. **Content Length**: Truncate very long documents (>5000 chars)
3. **Concurrent Requests**: Service handles one analysis at a time
4. **Caching**: Results are stored temporarily for download

## Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **File Uploads**: Validate file types and sizes
3. **Repository Access**: Only clone public repositories
4. **Output Sanitization**: Review generated content before sharing

## Support & Maintenance

### Logs Location
- Service logs: Console output
- Generated files: `GENERATED_FILES_DIR` (default: `generated_files/`)
- Temporary files: System temp directory

### Monitoring
- Check LLM service availability
- Monitor API rate limits
- Track analysis completion times
- Review error rates

### Updates
- Keep dependencies updated
- Monitor for security patches
- Review API changes (Groq, internal LLM)

## Additional Resources

- Full documentation: `IMPACT_ANALYSIS_CONSOLIDATION.md`
- Source code: `app/services/impact_analysis_agent.py`
- SDLC integration: `app/api/agents.py`
- Storage service: `app/core/storage.py`
