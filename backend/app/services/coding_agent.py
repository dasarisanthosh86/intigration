import tempfile
import os
import re
from datetime import datetime
from typing import List, Dict, Optional
import time

from app.services.llm import llm_service
from app.constants.prompts import SYSTEM_PROMPTS, USER_PROMPTS
from app.constants.coding_templates import (
    MAIN_PY_TEMPLATE,
    MODELS_PY_TEMPLATE,
    SCHEMAS_PY_TEMPLATE,
    ROUTES_PY_TEMPLATE,
    DATABASE_PY_TEMPLATE,
    CONFIG_PY_TEMPLATE,
    REQUIREMENTS_TXT_TEMPLATE,
    README_MD_TEMPLATE,
    ENV_EXAMPLE_TEMPLATE
)
from app.constants.coding_config import FEATURE_KEYWORDS, DEFAULT_FEATURES, DEFAULT_ENV_CONFIG

class CodingService:
    def __init__(self):
        self.name = "Coding Agent"

    async def generate_code(self, prd_content: str, architecture_content: str, github_url: Optional[str] = None, project_type: str = "backend") -> str:
        """
        Generate production-ready code based on PRD and architecture.
        
        Args:
            prd_content: content of the PRD
            architecture_content: content of the architecture doc
            github_url: optional github url
            project_type: 'backend' (FastAPI) or 'frontend' (React)
        """
        try:
            print(f"[Coding Agent] Starting {project_type} code generation...")
            
            # Analyze PRD to extract key features
            features = self._extract_features_from_prd(prd_content)
            
            # Generate comprehensive code structure
            if project_type == "frontend":
                code_structure = await self._generate_frontend_structure(prd_content, architecture_content, features)
            else:
                code_structure = await self._generate_backend_structure(prd_content, architecture_content, features)
            
            # Create temporary directory for generated code
            temp_dir = tempfile.gettempdir()
            timestamp = int(time.time())
            code_dir = os.path.join(temp_dir, f"generated_{project_type}_{timestamp}")
            os.makedirs(code_dir, exist_ok=True)
            
            # Create project structure
            await self._create_project_files(code_dir, code_structure, features)
            
            print(f"[Coding Agent] {project_type.capitalize()} code generated successfully at: {code_dir}")
            return code_dir
            
        except Exception as e:
            print(f"[Coding Agent] Error: {e}")
            raise Exception(f"Failed to generate code: {e}")

    def _extract_features_from_prd(self, prd_content: str) -> List[str]:
        """
        Extract specific features from the PRD content using keyword matching.
        """
        features = []
        lines = prd_content.lower().split('\n')
        
        for line in lines:
            if any(keyword in line for keyword in FEATURE_KEYWORDS):
                clean_feature = line.replace('feature:', '').replace('requirement:', '').strip()
                # Clean bullet points
                clean_feature = re.sub(r'^[-•*]\s*', '', clean_feature)
                if 10 < len(clean_feature) < 120:
                    features.append(clean_feature.capitalize())
        
        # Deduplicate and limit
        unique_features = list(dict.fromkeys(features))
        
        if not unique_features:
            return DEFAULT_FEATURES
            
        return unique_features[:10]

    async def _generate_backend_structure(self, prd_content: str, architecture_content: str, features: List[str]) -> Dict[str, str]:
        """Generate backend code structure (FastAPI)."""
        system_prompt = SYSTEM_PROMPTS["CODING_AGENT"]
        features_formatted = "\n".join([f'- {feature}' for feature in features])
        
        user_prompt = USER_PROMPTS["GENERATE_CODE_STRUCTURE"].format(
            prd_content=prd_content[:1500],
            architecture_content=architecture_content[:1000],
            features_list=features_formatted
        )

        response = await llm_service.get_response(user_prompt, system_prompt)
        return self._parse_backend_response(response, features)

    async def _generate_frontend_structure(self, prd_content: str, architecture_content: str, features: List[str]) -> Dict[str, str]:
        """Generate frontend code structure (React/Vite)."""
        system_prompt = SYSTEM_PROMPTS["FRONTEND_CODING_AGENT"]
        features_formatted = "\n".join([f'- {feature}' for feature in features])
        
        user_prompt = USER_PROMPTS["GENERATE_FRONTEND_CODE"].format(
            prd_content=prd_content[:1500],
            architecture_content=architecture_content[:1000],
            features_list=features_formatted
        )

        response = await llm_service.get_response(user_prompt, system_prompt)
        return self._parse_frontend_response(response, features)

    def _parse_backend_response(self, response: str, features: List[str]) -> Dict[str, str]:
        """Parse LLM response for backend files (--- File: format)."""
        
        # Initialize with templates as fallback (Service-Based Architecture)
        code_structure = {
            "backend/main.py": self._generate_main_py(features),
            "backend/config.py": CONFIG_PY_TEMPLATE,
            "backend/models/schemas.py": SCHEMAS_PY_TEMPLATE,
            "backend/services/business_service.py": ROUTES_PY_TEMPLATE, # Re-using template logic for now
            "backend/utils/helpers.py": "# Helpers\n",
            "backend/requirements.txt": REQUIREMENTS_TXT_TEMPLATE,
            "README.md": self._generate_readme_md(features)
        }
        
        # New parsing logic to handle flat file structures defined by Agent-4
        parts = re.split(r'--- File: ', response)
        
        # If no parts found (LLM didn't follow format), fallback to old block parsing
        if len(parts) < 2:
            print("[Coding Agent] Warning: Standard file headers not found. Attempting code block fallback.")
            code_blocks = re.findall(r'```(?:python)?\n(.*?)\n```', response, re.DOTALL)
            if code_blocks:
                # Map linearly to critical files if structure is lost
                keys = list(code_structure.keys())
                for i, block in enumerate(code_blocks[:len(keys)]):
                    code_structure[keys[i]] = block.strip()
            return code_structure

        # Parse explicitly named files
        for part in parts[1:]:
            try:
                # split at first newline to separate filename from content
                if '\n' not in part: continue
                filename_line, content = part.split('\n', 1)
                filename = filename_line.strip()
                
                # Check for code blocks in content and strip them if present
                content = content.replace('```python', '').replace('```', '').strip()
                
                code_structure[filename] = content
            except ValueError:
                continue
        
        return code_structure

    def _parse_frontend_response(self, response: str, features: List[str]) -> Dict[str, str]:
        """Parse LLM response for frontend files (--- File: format)."""
        from app.constants.frontend_templates import (
            HTTP_CLIENT_TEMPLATE, ENV_TS_TEMPLATE, ENDPOINTS_TS_TEMPLATE, 
            ROUTES_TS_TEMPLATE, APP_TSX_TEMPLATE
        )

        # Default structure
        code_structure = {
            "src/api/httpClient.ts": HTTP_CLIENT_TEMPLATE,
            "src/config/env.ts": ENV_TS_TEMPLATE,
            "src/api/endpoints.ts": ENDPOINTS_TS_TEMPLATE,
            "src/constants/routes.ts": ROUTES_TS_TEMPLATE,
            "src/App.tsx": APP_TSX_TEMPLATE,
            "README.md": "# Frontend Application\n\nGenerated by Antigravity Agents."
        }
        
        # Regex to find "--- File: <filename>\n<content>"
        # It looks for lines starting with "--- File: ", capturing filename, then capturing content until next "--- File:" or end of string.
        # This is slightly complex because content can contain newlines.
        
        parts = re.split(r'--- File: ', response)
        # First part is usually empty or preamble
        for part in parts[1:]:
            try:
                # split at first newline to separate filename from content
                filename_line, content = part.split('\n', 1)
                filename = filename_line.strip()
                code_structure[filename] = content.strip()
            except ValueError:
                continue

        return code_structure



    def _generate_main_py(self, features: List[str]) -> str:
        return MAIN_PY_TEMPLATE.format(
            features=str(features),
            timestamp=datetime.utcnow().isoformat()
        )

    def _generate_readme_md(self, features: List[str]) -> str:
        features_list = "\n".join([f'- {feature}' for feature in features])
        return README_MD_TEMPLATE.format(
            features_list=features_list,
            timestamp=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        )

    async def _create_project_files(self, code_dir: str, code_structure: Dict[str, str], features: List[str]):
        """Create all project files in the specified directory."""
        
        for filename, content in code_structure.items():
            file_path = os.path.join(code_dir, filename)
            
            # Create subdirectories if needed
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
        
        # Create additional directories
        os.makedirs(os.path.join(code_dir, "tests"), exist_ok=True)
        os.makedirs(os.path.join(code_dir, "docs"), exist_ok=True)
        
        # Create .env example
        env_content = ENV_EXAMPLE_TEMPLATE.format(
            database_url=DEFAULT_ENV_CONFIG["DATABASE_URL"],
            secret_key=DEFAULT_ENV_CONFIG["SECRET_KEY"],
            algorithm=DEFAULT_ENV_CONFIG["ALGORITHM"],
            access_token_expire_minutes=DEFAULT_ENV_CONFIG["ACCESS_TOKEN_EXPIRE_MINUTES"]
        )
        
        with open(os.path.join(code_dir, ".env.example"), "w") as f:
            f.write(env_content)
        
        print(f"[Coding Agent] Created {len(code_structure)} files with {len(features)} features")

coding_service = CodingService()