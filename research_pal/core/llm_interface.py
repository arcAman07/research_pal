"""
LLM Interface for ResearchPal - Enhanced version with better Gemini support.
"""
import os
import json
import logging
import re
from typing import Dict, List, Any, Optional, Union
import httpx
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class LLMInterface:
    """Interface for interacting with various LLM APIs."""
    
    def __init__(self, default_model: str = None):
        """
        Initialize the LLM interface.
        
        Args:
            default_model: Default model to use for queries
        """
        # API keys should be set in environment variables
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.google_api_key = os.environ.get("GOOGLE_API_KEY")
        
        # Determine default model based on available API keys
        if default_model is None:
            # If Google API key is available but OpenAI is not, use Gemini as default
            if self.google_api_key and not self.openai_api_key:
                self.default_model = "gemini-1.5-flash"
            # If OpenAI API key is available or both are available, use OpenAI as default
            else:
                # Try to get from environment or use a reasonable default
                self.default_model = os.environ.get("RESEARCHPAL_DEFAULT_MODEL", "gpt-4o-mini")
        else:
            self.default_model = default_model
        
        # Ensure default model aligns with available API keys
        if "gemini" in self.default_model and not self.google_api_key:
            logger.warning(f"Default model {self.default_model} requires Google API key which is not available")
            if self.openai_api_key:
                logger.warning(f"Switching to gpt-4o-mini")
                self.default_model = "gpt-4o-mini"
        elif "gpt" in self.default_model and not self.openai_api_key:
            logger.warning(f"Default model {self.default_model} requires OpenAI API key which is not available")
            if self.google_api_key:
                logger.warning(f"Switching to gemini-1.5-flash")
                self.default_model = "gemini-1.5-flash"
        
        # Model mappings and configurations
        self.model_configs = {
            # OpenAI models
            "gpt-4o-mini": {
                "provider": "openai",
                "max_tokens": 128000,  # Input context
                "max_output_tokens": 4096,
                "cost_per_1k_input": 0.15,  # USD per 1k tokens
                "cost_per_1k_output": 0.60,
                "capabilities": ["text", "code", "reasoning"]
            },
            "gpt-4o": {
                "provider": "openai",
                "max_tokens": 128000,
                "max_output_tokens": 4096,
                "cost_per_1k_input": 5.00,
                "cost_per_1k_output": 15.00,
                "capabilities": ["text", "code", "vision", "reasoning"]
            },
            
            # Google/Gemini models
            "gemini-1.5-flash": {
                "provider": "google",
                "model_name": "gemini-1.5-flash-latest",
                "max_tokens": 1000000,
                "max_output_tokens": 8192,
                "cost_per_1k_input": 0.00035,
                "cost_per_1k_output": 0.00085,
                "capabilities": ["text", "code", "vision"]
            },
            "gemini-1.5-flash-2.0": {
                "provider": "google",
                "model_name": "gemini-1.5-flash-2.0-experimental",
                "max_tokens": 1000000,
                "max_output_tokens": 8192,
                "cost_per_1k_input": 0.0005, # Experimental pricing
                "cost_per_1k_output": 0.0015, # Experimental pricing
                "capabilities": ["text", "code", "vision", "reasoning"]
            },
            "gemini-1.5-pro": {
                "provider": "google",
                "model_name": "gemini-1.5-pro-latest",
                "max_tokens": 1000000,
                "max_output_tokens": 8192,
                "cost_per_1k_input": 0.00125,
                "cost_per_1k_output": 0.00375,
                "capabilities": ["text", "code", "vision", "reasoning"]
            },
        }
        
        # Warning for missing API keys
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        
        if not self.google_api_key:
            logger.warning("GOOGLE_API_KEY not found in environment variables")
    
    def get_model_info(self, model_name: str = None) -> Dict[str, Any]:
        """Get information about a specific model."""
        if model_name is None:
            model_name = self.default_model
            
        return self.model_configs.get(model_name, {})
    
    def _select_provider(self, model: str = None) -> str:
        """Determine which provider to use based on model."""
        if model is None:
            model = self.default_model
        
        model_info = self.get_model_info(model)
        return model_info.get("provider", "openai")
    
    def _get_actual_model_name(self, model: str = None) -> str:
        """Get the actual API model name to use."""
        if model is None:
            model = self.default_model
            
        model_info = self.get_model_info(model)
        
        # If it's a Google model, use the model_name field
        if model_info.get("provider") == "google":
            return model_info.get("model_name", model)
            
        # Otherwise return the model name directly
        return model
    
    @retry(
        wait=wait_random_exponential(min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectTimeout))
    )
    async def query_openai(self, 
                          prompt: str, 
                          system_message: str = "",
                          model: Optional[str] = None,
                          temperature: float = 0.0,
                          max_tokens: int = 4000) -> str:
        """
        Query OpenAI API with a prompt.
        
        Args:
            prompt: User prompt to send to the API
            system_message: System message for context
            model: Model to use (defaults to self.default_model)
            temperature: Temperature parameter (0.0 = deterministic)
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            API response text
        """
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not found")
        
        if model is None:
            model = self.default_model
            
        # If it's not an OpenAI model, use the default
        if self._select_provider(model) != "openai":
            logger.warning(f"Model {model} is not an OpenAI model. Using {self.default_model} instead.")
            model = self.default_model
        
        # Get actual model name
        model_name = self._get_actual_model_name(model)
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        data = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=60.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            return result["choices"][0]["message"]["content"]
    
    @retry(
        wait=wait_random_exponential(min=1, max=10),
        stop=stop_after_attempt(3),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.ConnectTimeout))
    )
    async def query_google(self,
                          prompt: str,
                          system_message: str = "",
                          model: str = None,
                          temperature: float = 0.0,
                          max_tokens: int = 4000) -> str:
        """
        Query Google AI Studio (Gemini) API with a prompt.
        
        Args:
            prompt: User prompt to send to the API
            system_message: System message for context
            model: Model to use
            temperature: Temperature parameter
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            API response text
        """
        if not self.google_api_key:
            raise ValueError("Google API key not found")
        
        if model is None:
            model = "gemini-1.5-flash"
        
        # If it's not a Google model, use gemini-1.5-flash
        if self._select_provider(model) != "google":
            logger.warning(f"Model {model} is not a Google model. Using gemini-1.5-flash instead.")
            model = "gemini-1.5-flash"
        
        # Get actual model name
        model_name = self._get_actual_model_name(model)
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Construct the API URL with the API key
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={self.google_api_key}"
        
        # Prepare the content parts
        contents = []
        
        if system_message:
            # Add system message as a separate content item
            contents.append({
                "role": "user",
                "parts": [{"text": f"<system>\n{system_message}\n</system>"}]
            })
        
        # Add user prompt
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })
        
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.95,
                "topK": 40
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_ONLY_HIGH"
                }
            ]
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                headers=headers,
                json=data,
                timeout=60.0
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Parse the response to extract the generated text
            if "candidates" in result and len(result["candidates"]) > 0:
                candidate = result["candidates"][0]
                if "content" in candidate and "parts" in candidate["content"]:
                    # Extract text from all parts
                    text_parts = [part["text"] for part in candidate["content"]["parts"] if "text" in part]
                    return "\n".join(text_parts)
            
            return "No response generated"
    
    async def query_model(self,
                         prompt: str,
                         system_message: str = "",
                         model: str = None,
                         temperature: float = 0.0,
                         max_tokens: int = 4000) -> str:
        """
        Query the appropriate API based on the model.
        
        Args:
            prompt: User prompt to send to the API
            system_message: System message for context
            model: Model to use
            temperature: Temperature parameter
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            API response text
        """
        if model is None:
            model = self.default_model
        
        provider = self._select_provider(model)
        
        if provider == "google":
            return await self.query_google(
                prompt=prompt,
                system_message=system_message,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        else:  # default to OpenAI
            return await self.query_openai(
                prompt=prompt,
                system_message=system_message,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
    
    async def summarize_paper_chunk(self, 
                                   chunk: str, 
                                   metadata: Dict[str, Any],
                                   is_first_chunk: bool = False,
                                   is_last_chunk: bool = False,
                                   model: str = None) -> Dict[str, Any]:
        """
        Summarize a single chunk of a research paper.
        
        Args:
            chunk: Text chunk from the paper
            metadata: Paper metadata
            is_first_chunk: Whether this is the first chunk (contains intro)
            is_last_chunk: Whether this is the last chunk (contains conclusion)
            model: Model to use for summarization
        Returns:
            Dictionary with summary information
        """
        system_message = """You are ResearchPal, an expert research assistant specializing in scientific literature analysis. 
        Your task is to analyze a chunk of text from a research paper and extract key information.
        
        Be precise, factual, and comprehensive. Focus on identifying:
        1. Main concepts and contributions
        2. Methodologies described
        3. Results presented
        4. Important mathematical formulations
        5. Model architectures (if applicable)
        
        If this chunk appears to be from the introduction, provide more context about the paper's goals.
        If this chunk appears to be from the methodology, focus on technical details.
        If this chunk appears to be from the results section, focus on findings and evaluation.
        If this chunk appears to be from the conclusion, summarize the paper's contributions.
        
        Extract any numerical results, key figures, tables, or important equations."""
        
        prompt = f"""Analyze the following chunk of text from a research paper titled "{metadata.get('title', 'Unknown')}":
        
        ```
        {chunk}
        ```
        
        First determine which section(s) of the paper this chunk belongs to.
        
        {'This appears to be the beginning of the paper (likely includes abstract and introduction).' if is_first_chunk else ''}
        {'This appears to be the end of the paper (likely includes conclusion and references).' if is_last_chunk else ''}
        
        Provide a detailed analysis of this chunk with the following information:
        
        1. SECTION_IDENTIFICATION: Identify which section(s) of the paper this chunk belongs to
        2. SUMMARY: Summarize the key information in this chunk (200-300 words)
        3. KEY_FINDINGS: List up to 5 key findings or points from this chunk
        4. TECHNICAL_DETAILS: Extract any important technical details, methodologies, or algorithms
        5. MATH_FORMULATIONS: Extract any important mathematical formulations or equations
        6. ARCHITECTURE_DETAILS: If a model architecture is described, provide details
        7. RESULTS: Extract any experimental results or evaluations
        
        Format your response as a JSON object with these fields."""
        
        # Use the specified model or default
        if model is None:
            model = self.default_model
        
        # Query the appropriate API
        response = await self.query_model(
            prompt=prompt,
            system_message=system_message,
            model=model,
            temperature=0.0
        )
        
        # Extract JSON from the response
        try:
            # Find JSON in the response (in case there's text before/after)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > 0:
                json_str = response[json_start:json_end]
                summary_data = json.loads(json_str)
            else:
                # If no JSON brackets found, try to parse the whole response
                summary_data = json.loads(response)
                
            return summary_data
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from response: {response}")
            # Return a structured response even if JSON parsing fails
            return {
                "SECTION_IDENTIFICATION": "Unknown",
                "SUMMARY": response[:500],  # First 500 chars as fallback
                "KEY_FINDINGS": [],
                "TECHNICAL_DETAILS": "",
                "MATH_FORMULATIONS": "",
                "ARCHITECTURE_DETAILS": "",
                "RESULTS": ""
            }
    
    async def merge_chunk_summaries(self, 
                                   summaries: List[Dict[str, Any]], 
                                   metadata: Dict[str, Any],
                                   model: str = None) -> Dict[str, Any]:
        """
        Merge multiple chunk summaries into a cohesive full paper summary.
        
        Args:
            summaries: List of chunk summary dictionaries
            metadata: Paper metadata
            model: Model to use for merging
            
        Returns:
            Comprehensive paper summary
        """
        # Combine all summaries
        combined_summary = "\n\n".join([s.get("SUMMARY", "") for s in summaries])
        
        # Collect all key findings
        key_findings = []
        for summary in summaries:
            findings = summary.get("KEY_FINDINGS", [])
            if isinstance(findings, list):
                key_findings.extend(findings)
            elif isinstance(findings, str):
                key_findings.append(findings)
        
        # Collect technical details
        tech_details = "\n\n".join([s.get("TECHNICAL_DETAILS", "") for s in summaries if s.get("TECHNICAL_DETAILS")])
        
        # Collect math formulations
        math_formulations = "\n\n".join([s.get("MATH_FORMULATIONS", "") for s in summaries if s.get("MATH_FORMULATIONS")])
        
        # Collect architecture details
        architecture_details = "\n\n".join([s.get("ARCHITECTURE_DETAILS", "") for s in summaries if s.get("ARCHITECTURE_DETAILS")])
        
        # Collect results
        results = "\n\n".join([s.get("RESULTS", "") for s in summaries if s.get("RESULTS")])
        
        # Now generate a comprehensive summary using another LLM call
        system_message = """You are ResearchPal, an expert research assistant specializing in scientific literature analysis.
        Your task is to create a comprehensive, well-structured summary of a research paper based on section summaries.
        
        Be precise, factual, and comprehensive. Organize the information logically.
        Focus on presenting the paper's contributions, methodologies, results, and implications.
        
        Your summary should be suitable for a researcher who wants to understand the paper without reading it entirely."""
        
        title = metadata.get("title", "Unknown Paper")
        authors = metadata.get("author", "")
        
        prompt = f"""Create a comprehensive summary of the research paper titled "{title}" by {authors}.
        
        I'll provide you with summaries from different sections of the paper. Please synthesize this information into a cohesive, well-structured summary of the entire paper.
        
        Here are the section summaries:
        
        {combined_summary}
        
        Here are the key findings identified across the paper:
        {json.dumps(key_findings, indent=2)}
        
        Technical details and methodologies:
        {tech_details}
        
        Mathematical formulations:
        {math_formulations}
        
        Architecture details (if applicable):
        {architecture_details}
        
        Results and evaluations:
        {results}
        
        Please provide a comprehensive summary with the following sections:
        1. OVERVIEW: A brief overview of the paper (100-150 words)
        2. PROBLEM_STATEMENT: The problem addressed by the paper
        3. METHODOLOGY: The approach and methods used
        4. ARCHITECTURE: Detailed architecture description (if applicable)
        5. KEY_RESULTS: The main results and findings
        6. IMPLICATIONS: Implications and importance of the work
        7. TAKEAWAYS: Major takeaways (in bullet points)
        8. FUTURE_DIRECTIONS: Potential future research directions mentioned or implied
        9. BACKGROUND: Important background information
        10. MATH_FORMULATIONS: Important mathematical formulations (if applicable)
        
        Format your response as a JSON object with these fields."""
        
        # Use the specified model or default
        if model is None:
            model = self.default_model
        
        # Use appropriate API to generate comprehensive summary
        response = await self.query_model(
            prompt=prompt,
            system_message=system_message,
            model=model,
            temperature=0.2,
            max_tokens=4000
        )
        
        # Extract JSON from the response
        try:
            # Find JSON in the response (in case there's text before/after)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > 0:
                json_str = response[json_start:json_end]
                full_summary = json.loads(json_str)
            else:
                # If no JSON brackets found, try to parse the whole response
                full_summary = json.loads(response)
            
            # Ensure all expected fields are present
            expected_fields = [
                "OVERVIEW", "PROBLEM_STATEMENT", "METHODOLOGY", "ARCHITECTURE", "KEY_RESULTS",
                "IMPLICATIONS", "TAKEAWAYS", "FUTURE_DIRECTIONS", "BACKGROUND", "MATH_FORMULATIONS"
            ]
            
            for field in expected_fields:
                if field not in full_summary:
                    full_summary[field] = ""
            
            return full_summary
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from response: {response}")
            # Return a structured response even if JSON parsing fails
            return {
                "OVERVIEW": response[:500],  # First 500 chars as fallback
                "PROBLEM_STATEMENT": "",
                "METHODOLOGY": "",
                "ARCHITECTURE": "",
                "KEY_RESULTS": "",
                "IMPLICATIONS": "",
                "TAKEAWAYS": [],
                "FUTURE_DIRECTIONS": [],
                "BACKGROUND": "",
                "MATH_FORMULATIONS": ""
            }
    
    async def generate_comprehensive_analysis(self,
                                             paper_summary: Dict[str, Any],
                                             paper_title: str,
                                             model: str = None,
                                             max_tokens: int = 4096) -> Dict[str, Any]:
        """
        Generate a comprehensive analysis of the paper based on its summary.
        
        Args:
            paper_summary: Dictionary containing paper summary
            paper_title: Title of the paper
            model: Model to use for analysis
            max_tokens: Maximum number of tokens in the response
            
        Returns:
            Dictionary with comprehensive analysis sections
        """
        # Import the prompt here to avoid circular imports
        from research_pal.prompts import COMPREHENSIVE_ANALYSIS_PROMPT
        
        system_message = COMPREHENSIVE_ANALYSIS_PROMPT
        
        # Create a concise representation of the paper
        overview = paper_summary.get("OVERVIEW", "") or paper_summary.get("summary", "")
        problem = paper_summary.get("PROBLEM_STATEMENT", "") or paper_summary.get("problem_statement", "")
        methodology = paper_summary.get("METHODOLOGY", "") or paper_summary.get("methodology", "")
        results = paper_summary.get("KEY_RESULTS", "") or paper_summary.get("key_results", "")
        implications = paper_summary.get("IMPLICATIONS", "") or paper_summary.get("implications", "")
        
        prompt = f"""Generate a comprehensive analysis of the paper titled "{paper_title}" based on the following summary:
        
        Overview:
        {overview}
        
        Problem Statement:
        {problem}
        
        Methodology:
        {methodology}
        
        Key Results:
        {results}
        
        Implications:
        {implications}
        
        Please provide the analysis in the requested format with TAKEAWAYS, IMPORTANT_IDEAS, FUTURE_IDEAS, NOVELTY, LIMITATIONS, PRACTICAL_APPLICATIONS, and RELATED_WORK sections."""
        
        # Use the specified model or default
        if model is None:
            model = self.default_model
        
        # Use appropriate API to generate comprehensive analysis
        response = await self.query_model(
            prompt=prompt,
            system_message=system_message,
            model=model,
            temperature=0.3,
            max_tokens=max_tokens
        )
        
        # Extract JSON from the response
        try:
            # Find JSON in the response (in case there's text before/after)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > 0:
                json_str = response[json_start:json_end]
                analysis_data = json.loads(json_str)
            else:
                # If no JSON brackets found, try to parse the whole response
                analysis_data = json.loads(response)
            
            return analysis_data
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from response: {response}")
            # Return a structured response even if JSON parsing fails
            return {
                "TAKEAWAYS": [],
                "IMPORTANT_IDEAS": [],
                "FUTURE_IDEAS": [],
                "NOVELTY": "",
                "LIMITATIONS": [],
                "PRACTICAL_APPLICATIONS": [],
                "RELATED_WORK": ""
            }
    
    async def generate_code_implementation(self, 
                                         architecture_details: str, 
                                         paper_title: str,
                                         model: str = "gemini-1.5-flash-2.0") -> str:
        """
        Generate code implementation of a model architecture from a paper.
        
        Args:
            architecture_details: Description of the architecture
            paper_title: Title of the paper
            model: Model to use for code generation (default to Gemini Flash 2.0)
            
        Returns:
            Python code implementing the architecture
        """
        system_message = """You are ResearchPal, an expert in implementing machine learning and deep learning architectures from research papers.
        Your task is to generate clean, working Python code that implements the architecture described in a research paper.
        
        Use PyTorch as the default framework unless otherwise specified.
        Include comprehensive comments explaining each part of the implementation.
        Follow best practices for code organization and structure.
        Make reasonable assumptions when details are unclear, and document these assumptions in comments."""
        
        prompt = f"""Generate a Python implementation of the model architecture described in the paper titled "{paper_title}".
        
        Here is the description of the architecture:
        
        ```
        {architecture_details}
        ```
        
        Please provide a complete, working implementation that includes:
        
        1. All necessary imports
        2. The model class(es) definition
        3. Any helper functions or utility classes needed
        4. Example usage showing how to instantiate and use the model
        5. Comprehensive comments explaining the implementation
        
        Make reasonable assumptions if some details are not provided, and document these assumptions in comments.
        
        The code should follow best practices and be ready to use with minimal modifications."""
        
        # For code generation, we'll prefer Gemini Flash 2.0 which is good for coding tasks
        response = await self.query_model(
            prompt=prompt,
            system_message=system_message,
            model=model,
            temperature=0.2,
            max_tokens=8000
        )
        
        # Extract code from the response (in case there's text before/after code blocks)
        code_pattern = r"```python(.*?)```"
        code_blocks = re.findall(code_pattern, response, re.DOTALL)
        
        if code_blocks:
            # Combine all code blocks
            full_code = "\n\n".join([block.strip() for block in code_blocks])
            return full_code
        else:
            # If no code blocks found, return the entire response
            return response
    
    async def generate_similar_papers(self, 
                                     paper_summary: Dict[str, Any],
                                     paper_title: str,
                                     model: str = None) -> List[Dict[str, str]]:
        """
        Generate recommendations for similar papers.
        
        Args:
            paper_summary: Dictionary containing paper summary
            paper_title: Title of the paper
            model: Model to use for recommendations
            
        Returns:
            List of similar paper recommendations
        """
        system_message = """You are ResearchPal, an expert research assistant with extensive knowledge of scientific literature.
        Your task is to recommend similar papers based on the summary of a given paper.
        
        Provide recommendations that are relevant, diverse, and high-quality.
        Include both seminal works and recent advances in the field.
        For each recommendation, provide the title, authors, year, and a brief explanation of its relevance."""
        
        # Create a concise representation of the paper
        overview = paper_summary.get("OVERVIEW", "") or paper_summary.get("summary", "")
        problem = paper_summary.get("PROBLEM_STATEMENT", "") or paper_summary.get("problem_statement", "")
        methodology = paper_summary.get("METHODOLOGY", "") or paper_summary.get("methodology", "")
        
        prompt = f"""Based on the following summary of the paper titled "{paper_title}", recommend 5 similar papers that would be relevant to someone interested in this research.
        
        Paper Overview:
        {overview}
        
        Problem Statement:
        {problem}
        
        Methodology:
        {methodology}
        
        Please recommend 5 papers that are:
        1. Closely related to this research topic
        2. A mix of foundational papers and recent advances
        3. Diverse in their approaches to the problem
        
        For each recommendation, provide:
        - Title
        - Authors
        - Year of publication (approximate if unsure)
        - A brief explanation of why it's relevant to someone interested in the original paper
        
        Format your response as a JSON array of objects with these fields."""
        
        # Use the specified model or default
        if model is None:
            model = self.default_model
        
        # Use appropriate API to generate similar paper recommendations
        response = await self.query_model(
            prompt=prompt,
            system_message=system_message,
            model=model,
            temperature=0.3
        )
        
        # Extract JSON from the response
        try:
            # Find JSON in the response (in case there's text before/after)
            json_start = response.find('[')
            json_end = response.rfind(']') + 1
            if json_start >= 0 and json_end > 0:
                json_str = response[json_start:json_end]
                recommendations = json.loads(json_str)
            else:
                # If no JSON array found, try to parse as a JSON object
                recommendations = json.loads(response)
                # If it's an object with a recommendations field, use that
                if isinstance(recommendations, dict) and "recommendations" in recommendations:
                    recommendations = recommendations.get("recommendations", [])
                
            return recommendations
            
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from response: {response}")
            # Return a structured response even if JSON parsing fails
            return [
                {
                    "title": "Error parsing recommendations",
                    "authors": "",
                    "year": "",
                    "relevance": "Failed to generate proper recommendations"
                }
            ]
    
    async def generate_blog_post(self,
                               paper_summary: Dict[str, Any],
                               paper_title: str,
                               blog_style_sample: str = "",
                               model: str = None) -> str:
        """
        Generate a blog post about the paper based on its summary.
        
        Args:
            paper_summary: Dictionary containing paper summary
            paper_title: Title of the paper
            blog_style_sample: Optional sample of user's blog writing style
            model: Model to use for blog generation
            
        Returns:
            Formatted blog post
        """
        system_message = """You are ResearchPal, an expert in communicating complex research in an accessible way.
        Your task is to generate a well-structured, engaging blog post about a research paper that balances technical accuracy with readability.
        
        The blog post should:
        1. Have an engaging title and introduction
        2. Explain the paper's significance and context
        3. Break down complex concepts using analogies when helpful
        4. Include section headings for better readability
        5. End with implications and takeaways
        
        Adapt your writing style to match the sample provided, if available."""