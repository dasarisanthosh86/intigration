import logging
import os
import tempfile
import uuid
import json
from datetime import datetime
from typing import Dict, Any, Optional

from app.services.llm import llm_service
from app.services.github_architecture_service import GitHubArchitectureService
from app.services.github_analyzer_service import GitHubAnalyzerService
from app.services.github_pdf_service import GitHubPDFService
from app.core.storage import register_report

logger = logging.getLogger(__name__)

class ArchitectureService:
    def __init__(self):
        self.github_analyzer = GitHubAnalyzerService()
        self.github_architect = GitHubArchitectureService()
        self.pdf_service = GitHubPDFService()
        
        # Cache to store analysis objects between steps (Step 2a -> Step 2b)
        # Key: github_url, Value: {'repo_analysis': obj, 'system_architecture': obj, 'prd_content': str}
        self._analysis_cache: Dict[str, Any] = {}

    async def analyze_architecture(self, prd_content: str, github_url: str) -> str:
        """
        Analyze system architecture using the new advanced GitHub services.
        Returns a Markdown summary for the frontend/user to see.
        """
        print(f"[Architecture Agent] Analyzing repository: {github_url}")
        
        try:
            # 1. Analyze Repository
            repo_analysis = self.github_analyzer.analyze_repository(github_url)
            
            # 2. Generate System Architecture
            # Note: We use the internal method because we already have repo_analysis
            system_architecture = self.github_architect._generate_unified_architecture(repo_analysis, prd_content)
            
            # 3. Cache the complex objects for the PDF generation step
            self._analysis_cache[github_url] = {
                'repo_analysis': repo_analysis,
                'system_architecture': system_architecture,
                'prd_content': prd_content
            }
            
            # 4. Generate a Markdown summary for the UI and Impact Analysis Agent
            markdown_report = await self._convert_architecture_to_markdown(system_architecture, prd_content, github_url)
            
            return markdown_report

        except Exception as e:
            logger.error(f"Architecture analysis failed: {e}")
            # Fallback to LLM if advanced analysis fails
            return await self._fallback_llm_analysis(prd_content, github_url)

    async def generate_architecture_report(self, analysis: str, github_url: str) -> str:
        """
        Generates the professional PDF report using the cached analysis data.
        """
        try:
            # Retrieve cached data if available
            cached_data = self._analysis_cache.get(github_url)
            
            if cached_data:
                print(f"[Architecture Agent] Using cached advanced analysis for PDF generation.")
                repo_analysis = cached_data['repo_analysis']
                system_architecture = cached_data['system_architecture']
                prd_content = cached_data['prd_content']
                
                # Generate PDF using the new comprehensive service
                temp_dir = tempfile.gettempdir()
                self.pdf_service.output_dir = temp_dir
                
                # The GitHubPDFService expects the repo_analysis object directly
                # It will convert it internally using analyze_repo_from_object
                print(f"[Architecture Agent] Generating PDF with:")
                print(f"  - Project: {system_architecture.project_info.get('name', 'Unknown')}")
                print(f"  - Endpoints: {len(repo_analysis.api_endpoints)}")
                print(f"  - Components: {len(repo_analysis.components)}")
                
                pdf_path = self.pdf_service.generate_architecture_pdf(
                    architecture=system_architecture,
                    github_url=github_url,
                    prd_included=bool(prd_content),
                    repo_analysis=repo_analysis,
                    prd_content=prd_content
                )
                
                if os.path.exists(pdf_path):
                    file_size = os.path.getsize(pdf_path)
                    print(f"[Architecture Agent] Advanced PDF created: {pdf_path}")
                    print(f"[Architecture Agent] PDF size: {file_size} bytes")
                    
                    if file_size < 1000:
                        print(f"[Architecture Agent] WARNING: PDF file is very small ({file_size} bytes), may be empty!")
                    
                    # Register file with ID
                    file_id = str(uuid.uuid4())
                    register_report(file_id, pdf_path)
                    return file_id
                else:
                    print(f"[Architecture Agent] ERROR: PDF was not created at {pdf_path}")
                    return None
            
            # Fallback if no cache (e.g. server restart or direct call)
            print(f"[Architecture Agent] No cache found. generating simple report from markdown.")
            from app.services.pdf_service import PDFService
            simple_pdf_service = PDFService()
            
            temp_dir = tempfile.gettempdir()
            file_id = str(uuid.uuid4())
            filename = f"architecture_report_{file_id}.pdf"
            file_path = os.path.join(temp_dir, filename)
            
            await simple_pdf_service.generate_from_markdown(analysis, file_path)
            register_report(file_id, file_path)
            return file_id

        except Exception as e:
            logger.error(f"Failed to generate architecture PDF: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def _convert_architecture_to_markdown(self, arch, prd_content: str, github_url: str) -> str:
        """Helper to convert SystemArchitecture object to the standard Markdown format using LLM for high fidelity."""
        try:
            from dataclasses import asdict
            arch_dict = asdict(arch)
            
            # Simplify dict for LLM to avoid token limits if necessary, but keep key info
            # We assume modern LLM context is sufficient.
            arch_json = json.dumps(arch_dict, default=str)
            
            system_prompt = """You are Agent-2: Principal Software Architect.
Your task is to convert the provided JSON System Architecture Analysis into a professional Markdown Application Architecture Document.

**CRITICAL INSTRUCTIONS:**
1. Use the EXACT structure provided below.
2. Do NOT use placeholders. Use the data from the JSON input to populate the sections.
3. GENERATE DYNAMIC MERMAID DIAGRAMS based on the 'data_flow' and 'tech_stack_summary' in the JSON.
   - For 'System Context': Show User -> Frontend -> Backend -> Database interactions.
   - For 'Layered Architecture': Show Presentation -> Business -> Data Layers with specific technologies found in JSON.
   
STRUCTURE:
# System Architecture Document: [Project Name from JSON]
**Version:** 1.0.0
**Date:** [Current Date]
**Repository:** [github_url]

## 1. Executive Summary
[Use 'project_info' description]

## 2. High-Level Architecture
The system operates as a [architecture_pattern].
[tech_stack_summary details]

### 2.1 System Context Diagram
```mermaid
graph TD
    ... [Generate based on analysis]
```

### 2.2 Layered Architecture Diagram
```mermaid
graph TD
    ... [Generate based on analysis]
```

## 3. Endpoints Specification
Total Endpoints: [total_endpoints]
### Key Endpoints
[List 5-10 key endpoints from 'api_documentation' formatted nicely]

## 4. Operational Workflows
[Describe request lifecycle based on architecture]

## 5. Deployment & Security
[Use 'deployment_architecture' and 'security_model']

## 6. Recommendations
[List recommendations from JSON]
"""
            user_prompt = f"Here is the System Architecture Analysis (JSON):\n{arch_json}\n\nGitHub URL: {github_url}"
            
            markdown_output = await llm_service.get_response(user_prompt, system_prompt)
            return markdown_output
            
        except Exception as e:
            logger.error(f"Failed to generate Markdown via LLM: {e}")
            # Fallback to simple static generation if LLM fails (e.g., context too large)
            return self._fallback_static_markdown(arch, github_url)

    def _fallback_static_markdown(self, arch, github_url: str) -> str:
        """Fallback method if LLM fails, ensuring at least some output is returned."""
        now = datetime.now().strftime('%Y-%m-%d')
        md = f"# System Architecture Document: {arch.project_info.get('name', 'Project')}\n\n"
        md += f"**Version:** 1.0.0\n**Date:** {now}\n**Repository:** {github_url}\n\n"
        md += "## Executive Summary\n" + f"{arch.project_info.get('description', 'No description.')}\n"
        
        # Add simpler version of content directly
        md += "\n## Architecture Overview\n"
        md += f"- **Pattern**: {arch.architecture_overview.get('architecture_pattern')}\n"
        md += f"- **Frontend**: {', '.join(arch.tech_stack_summary.get('frontend_technologies', []))}\n"
        md += f"- **Backend**: {', '.join(arch.tech_stack_summary.get('backend_technologies', []))}\n"
        
        return md

    async def _fallback_llm_analysis(self, prd_content: str, github_url: str) -> str:
        """Standard LLM fallback if deep analysis fails."""
        system_prompt = "You are Agent-2: Principal Software Architect. Generate a System Architecture Document."
        user_prompt = f"Analyze these requirements:\n{prd_content}\n\nFor Repo: {github_url}"
        print("[Architecture Agent] Falling back to standard LLM analysis.")
        return await llm_service.get_response(user_prompt, system_prompt)

architecture_service = ArchitectureService()