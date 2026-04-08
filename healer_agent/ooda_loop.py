"""
OODA Loop (Observe, Orient, Decide, Act) implementation for the healing agent.
This is the core decision-making cycle for autonomous error detection and healing.
"""
import asyncio
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference


class OODALoop:
    """
    OODA Loop for autonomous healing:
    - Observe: Monitor logs for errors
    - Orient: Analyze error context and read relevant code
    - Decide: Use LLM to generate fix
    - Act: Apply patch with approval
    """
    
    def __init__(
        self,
        mcp_client,
        base_dir: Path,
        watsonx_api_key: str,
        watsonx_project_id: str,
        watsonx_url: str = "https://us-south.ml.cloud.ibm.com",
    ):
        self.mcp_client = mcp_client
        self.base_dir = base_dir
        self.incidents: List[Dict[str, Any]] = []
        self.pending_approval: Optional[Dict[str, Any]] = None
        
        # Initialize Watsonx AI with Granite 3.0
        self.credentials = Credentials(
            api_key=watsonx_api_key,
            url=watsonx_url,
        )
        
        self.model = ModelInference(
            model_id="ibm/granite-3-8b-instruct",
            credentials=self.credentials,
            project_id=watsonx_project_id,
            params={
                "decoding_method": "greedy",
                "max_new_tokens": 2000,
                "temperature": 0.3,
            }
        )
        
    async def observe(self) -> str:
        """
        Observe: Read application logs from MCP monitoring resource.
        Returns the log content.
        """
        logs = await self.mcp_client.read_logs()
        return logs
    
    def orient(self, logs: str) -> Optional[Dict[str, Any]]:
        """
        Orient: Analyze logs to detect errors and extract context.
        Returns error information including file path and line number.
        """
        # Look for error patterns in logs
        error_patterns = [
            r"ERROR.*?(\w+Error).*?in (\w+)",  # General error pattern
            r"Traceback.*?File \"([^\"]+)\", line (\d+)",  # Python traceback
            r"(\w+Error): (.+)",  # Error with message
        ]
        
        errors = []
        for pattern in error_patterns:
            matches = re.finditer(pattern, logs, re.MULTILINE | re.DOTALL)
            for match in matches:
                errors.append(match.groups())
        
        if not errors:
            return None
        
        # Extract file information from logs
        file_pattern = r'File "([^"]+\.py)", line (\d+)'
        file_matches = re.findall(file_pattern, logs)
        
        error_context = {
            "timestamp": datetime.now().isoformat(),
            "error_type": errors[0][0] if errors else "Unknown",
            "error_message": logs.split("ERROR")[-1].strip()[:200] if "ERROR" in logs else "",
            "file_path": file_matches[0][0] if file_matches else None,
            "line_number": int(file_matches[0][1]) if file_matches else None,
            "full_logs": logs,
        }
        
        # Read the source code if file path is available
        if error_context["file_path"]:
            try:
                file_path = self.base_dir / error_context["file_path"]
                if file_path.exists():
                    with open(file_path, "r") as f:
                        error_context["source_code"] = f.read()
            except Exception as e:
                error_context["source_code"] = f"Error reading file: {str(e)}"
        
        return error_context
    
    async def decide(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decide: Use Granite 3.0 to analyze the error and generate a fix.
        Returns a decision with reasoning, fix code, and risk level.
        """
        prompt = self._build_prompt(error_context)
        
        try:
            # Call Granite 3.0 model
            response = self.model.generate_text(prompt=prompt)
            
            # Parse the JSON response
            decision = self._parse_llm_response(response)
            
            # Add metadata
            decision["error_context"] = error_context
            decision["timestamp"] = datetime.now().isoformat()
            
            return decision
            
        except Exception as e:
            return {
                "reasoning": f"Error calling LLM: {str(e)}",
                "fix_code": None,
                "risk_level": "high",
                "error": str(e),
            }
    
    def _build_prompt(self, error_context: Dict[str, Any]) -> str:
        """Build the prompt for the LLM."""
        prompt = f"""You are an expert software engineer analyzing a production error.

**Error Information:**
- Type: {error_context.get('error_type', 'Unknown')}
- Message: {error_context.get('error_message', 'No message')}
- File: {error_context.get('file_path', 'Unknown')}
- Line: {error_context.get('line_number', 'Unknown')}

**Source Code:**
```python
{error_context.get('source_code', 'Source code not available')}
```

**Recent Logs:**
```
{error_context.get('full_logs', 'No logs available')[-500:]}
```

**Task:**
Analyze this error and provide a fix. Output your response as a JSON object with the following structure:

{{
  "reasoning": "Your step-by-step analysis of the error and why your fix works",
  "fix_code": "The complete fixed version of the source code",
  "risk_level": "low|medium|high - assess the risk of applying this fix",
  "confidence": "0-100 - your confidence in this fix"
}}

Important:
- Provide the COMPLETE fixed source code, not just the changed lines
- Ensure the fix handles edge cases
- Consider backward compatibility
- Be conservative with risk assessment

Output only the JSON object, no additional text."""

        return prompt
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured decision."""
        try:
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                decision = json.loads(json_match.group())
                return decision
            
            # Fallback: return raw response
            return {
                "reasoning": response,
                "fix_code": None,
                "risk_level": "high",
                "confidence": 0,
            }
        except json.JSONDecodeError:
            return {
                "reasoning": f"Failed to parse LLM response: {response[:200]}",
                "fix_code": None,
                "risk_level": "high",
                "confidence": 0,
            }
    
    async def act(self, decision: Dict[str, Any], approved: bool = False) -> Dict[str, Any]:
        """
        Act: Apply the patch if approved.
        Returns the result of the action.
        """
        if not approved:
            # Store for manual approval
            self.pending_approval = decision
            return {
                "status": "pending_approval",
                "message": "Waiting for manual approval",
                "decision": decision,
            }
        
        # Apply the patch
        error_context = decision.get("error_context", {})
        file_path = error_context.get("file_path")
        fix_code = decision.get("fix_code")
        
        if not file_path or not fix_code:
            return {
                "status": "error",
                "message": "Missing file path or fix code",
            }
        
        # Apply patch via MCP
        result = await self.mcp_client.apply_patch(file_path, fix_code)
        
        if result.get("success"):
            # Verify health after patch
            health_result = await self.mcp_client.verify_health(verbose=True)
            
            return {
                "status": "applied",
                "message": result.get("message", "Patch applied successfully"),
                "health_check": health_result,
            }
        
        return {
            "status": "error",
            "message": result.get("message", "Failed to apply patch"),
        }
    
    async def run_cycle(self) -> Optional[Dict[str, Any]]:
        """
        Run one complete OODA cycle.
        Returns incident information if an error was detected.
        """
        # Observe
        logs = await self.observe()
        
        # Orient
        error_context = self.orient(logs)
        
        if not error_context:
            return None  # No errors detected
        
        # Decide
        decision = await self.decide(error_context)
        
        # Create incident record
        incident = {
            "id": len(self.incidents) + 1,
            "timestamp": datetime.now().isoformat(),
            "error_context": error_context,
            "decision": decision,
            "status": "detected",
        }
        
        self.incidents.append(incident)
        
        # Store for approval (Act will be called separately)
        self.pending_approval = decision
        
        return incident
    
    async def approve_and_act(self) -> Dict[str, Any]:
        """Approve and execute the pending decision."""
        if not self.pending_approval:
            return {
                "status": "error",
                "message": "No pending approval",
            }
        
        result = await self.act(self.pending_approval, approved=True)
        
        # Update incident status
        if self.incidents:
            self.incidents[-1]["status"] = result.get("status", "unknown")
            self.incidents[-1]["action_result"] = result
        
        self.pending_approval = None
        
        return result

# Made with Bob
