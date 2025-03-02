import os
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
import json
import hashlib
from datetime import datetime

from ..core.pdf_processor import PDFProcessor
from ..core.llm_interface import LLMInterface
from ..db.chroma_manager import ChromaManager

logger = logging.getLogger(__name__)

class PaperSummarizer:
    """Manages the process of summarizing research papers."""
    
    def __init__(self, 
                llm_interface: Optional[LLMInterface] = None,
                db_manager: Optional[ChromaManager] = None,
                chunk_size: int = 8000,
                chunk_overlap: int = 200,
                output_token_limit: int = 4096):
        """
        Initialize the paper summarizer.
        
        Args:
            llm_interface: LLM interface for API calls
            db_manager: Database manager for storing summaries
            chunk_size: Size of chunks for PDF processing
            chunk_overlap: Overlap between chunks
            output_token_limit: Maximum number of tokens for the output
        """
        self.pdf_processor = PDFProcessor(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        self.llm_interface = llm_interface or LLMInterface()
        self.db_manager = db_manager or ChromaManager()
        self.output_token_limit = output_token_limit
    
    def _generate_paper_id(self, filepath: str, title: str) -> str:
        """
        Generate a unique ID for a paper based on filepath and title.
        
        More robust implementation that handles variations better.
        
        Args:
            filepath: Path to the PDF file
            title: Paper title
            
        Returns:
            A unique paper ID
        """
        # Use filename if available, otherwise use title
        filename = os.path.basename(filepath)
        
        # Combine filename and title for better uniqueness
        combined = f"{filename}_{title}"
        
        # Remove special characters and normalize spaces
        combined = re.sub(r'[^\w\s]', '', combined)
        combined = re.sub(r'\s+', '_', combined.strip()).lower()
        
        # Create a hash of the combined string
        hash_obj = hashlib.md5(combined.encode())
        paper_id = hash_obj.hexdigest()[:10]
        
        return paper_id
    
    async def determine_paper_domain(self, 
                                    title: str, 
                                    summary: str) -> str:
        """
        Determine the research domain of a paper.
        
        Args:
            title: Paper title
            summary: Paper summary
            
        Returns:
            Research domain (e.g., NLP, CV, RL)
        """
        system_message = """You are ResearchPal, an expert research assistant.
        Your task is to determine the specific research domain of a paper based on its title and summary.
        Provide a precise categorization using standard terminology such as:
        - Natural Language Processing (NLP)
        - Computer Vision (CV)
        - Reinforcement Learning (RL)
        - Graph Neural Networks (GNN)
        - Generative Models
        - etc.
        
        Be specific where possible and keep the domain name concise."""
        
        prompt = f"""Determine the specific research domain for the following paper.
        
        Title: {title}
        
        Summary: {summary}
        
        Output only the domain name, nothing else. 
        Example good outputs: "Natural Language Processing", "Computer Vision", "Reinforcement Learning", etc.
        Be specific but concise."""
        
        try:
            domain = await self.llm_interface.query_model(
                prompt=prompt,
                system_message=system_message,
                temperature=0.0,
                max_tokens=50
            )
            
            # Clean up and simplify
            domain = domain.strip().strip('"').strip("'")
            if len(domain) > 50:  # If it's too verbose, truncate
                domain = domain.split(',')[0].split(' and ')[0].strip()
                
            logger.info(f"Determined domain: {domain}")
            return domain
        except Exception as e:
            logger.error(f"Failed to determine paper domain: {e}")
            return "Unknown"
    
    def check_paper_exists(self, filepath: str) -> Optional[str]:
        """
        Check if a paper has already been processed by filepath.
        
        Args:
            filepath: Path to the PDF file
            
        Returns:
            Paper ID if found, None otherwise
        """
        try:
            # Normalize the filepath to handle path variations
            normalized_path = os.path.abspath(os.path.expanduser(filepath))
            
            # A more robust approach would be to add a unique index on filepaths in the DB,
            # but for now, we'll query all papers and check manually
            filename = os.path.basename(normalized_path)
            
            # Search for papers with the same filename (not perfect but a start)
            papers = self.search_papers(filename, n_results=20)
            
            for paper in papers:
                # Get the stored filepath and normalize it too
                paper_path = paper.get("filepath", "")
                if paper_path:
                    paper_path = os.path.abspath(os.path.expanduser(paper_path))
                    
                    # Check if paths match
                    if paper_path == normalized_path:
                        return paper.get("paper_id")
                    
                    # Also check if filenames match exactly (as a fallback)
                    if os.path.basename(paper_path) == os.path.basename(normalized_path):
                        # Check if the titles are similar (use fuzzy matching if available)
                        paper_title = paper.get("title", "")
                        
                        # For now, just a simple check
                        if paper_title and len(paper_title) > 5:
                            # Get metadata from the file to check title
                            extracted_data = self.pdf_processor.extract_and_chunk(normalized_path)
                            metadata = extracted_data.get("metadata", {})
                            title = metadata.get("title", "")
                            
                            # Simple similarity check
                            if title and paper_title in title or title in paper_title:
                                return paper.get("paper_id")
            
            # Not found
            return None
        
        except Exception as e:
            logger.error(f"Error checking if paper exists: {e}")
            return None
    
    async def summarize_paper(self, 
                             filepath: str, 
                             generate_code: bool = False,
                             generate_blog: bool = False,
                             blog_style_sample: str = "",
                             model: str = None,
                             output_token_limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Process and summarize a research paper.
        
        Args:
            filepath: Path to the PDF file
            generate_code: Whether to generate implementation code
            generate_blog: Whether to generate a blog post
            blog_style_sample: Sample of user's blog writing style
            model: Model to use for summarization
            output_token_limit: Maximum number of tokens for the output, overrides the default
            
        Returns:
            Dictionary with paper summary and generated content
        """
        logger.info(f"Processing paper: {filepath}")
        
        # Use provided token limit or default
        token_limit = output_token_limit or self.output_token_limit
        
        # Extract and chunk the PDF
        extracted_data = self.pdf_processor.extract_and_chunk(filepath)
        metadata = extracted_data["metadata"]
        chunks = extracted_data["chunks"]
        
        logger.info(f"Extracted {len(chunks)} chunks from paper")
        
        # Generate chunk summaries in parallel
        chunk_summary_tasks = []
        for i, chunk in enumerate(chunks):
            is_first = (i == 0)
            is_last = (i == len(chunks) - 1)
            
            task = self.llm_interface.summarize_paper_chunk(
                chunk=chunk,
                metadata=metadata,
                is_first_chunk=is_first,
                is_last_chunk=is_last,
                model=model
            )
            chunk_summary_tasks.append(task)
        
        chunk_summaries = await asyncio.gather(*chunk_summary_tasks)
        logger.info(f"Generated summaries for {len(chunk_summaries)} chunks")
        
        # Merge chunk summaries into a full paper summary
        full_summary = await self.llm_interface.merge_chunk_summaries(
            summaries=chunk_summaries,
            metadata=metadata,
            model=model
        )
        
        logger.info("Generated full paper summary")
        
        # Generate comprehensive analysis
        logger.info("Generating comprehensive analysis...")
        analysis = await self.llm_interface.generate_comprehensive_analysis(
            paper_summary=full_summary,
            paper_title=metadata.get("title", ""),
            model=model,
            max_tokens=token_limit
        )
        
        logger.info("Generated comprehensive analysis")
        
        # Generate similar paper recommendations
        similar_papers = await self.llm_interface.generate_similar_papers(
            paper_summary=full_summary,
            paper_title=metadata.get("title", ""),
            model=model
        )
        
        logger.info(f"Generated {len(similar_papers)} similar paper recommendations")
        
        # Generate code implementation if requested
        code_implementation = None
        if generate_code and full_summary.get("ARCHITECTURE"):
            # Use Gemini Flash 2.0 by default for code generation if no model specified
            code_model = model if model else "gemini-1.5-flash-2.0"
            code_implementation = await self.llm_interface.generate_code_implementation(
                architecture_details=full_summary.get("ARCHITECTURE", ""),
                paper_title=metadata.get("title", ""),
                model=code_model
            )
            logger.info("Generated code implementation")
        
        # Generate blog post if requested
        blog_post = None
        if generate_blog:
            blog_post = await self.llm_interface.generate_blog_post(
                paper_summary=full_summary,
                paper_title=metadata.get("title", ""),
                blog_style_sample=blog_style_sample,
                model=model
            )
            logger.info("Generated blog post")
        
        # Generate paper_id for storage
        paper_id = self._generate_paper_id(
            filepath=filepath,
            title=metadata.get("title", "")
        )
        
        # Determine paper domain
        domain = await self.determine_paper_domain(
            title=metadata.get("title", ""),
            summary=full_summary.get("OVERVIEW", "")
        )
        
        # Extract additional fields from analysis
        takeaways = analysis.get("TAKEAWAYS", [])
        important_ideas = analysis.get("IMPORTANT_IDEAS", [])
        future_directions = analysis.get("FUTURE_IDEAS", []) or full_summary.get("FUTURE_DIRECTIONS", [])
        novelty = analysis.get("NOVELTY", "") or full_summary.get("IMPLICATIONS", "")
        limitations = analysis.get("LIMITATIONS", [])
        practical_applications = analysis.get("PRACTICAL_APPLICATIONS", [])
        related_work = analysis.get("RELATED_WORK", "")
        
        # Prepare results
        result = {
            "paper_id": paper_id,
            "title": metadata.get("title", ""),
            "filepath": filepath,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata,
            "domain": domain,
            "summary": full_summary.get("OVERVIEW", ""),
            "problem_statement": full_summary.get("PROBLEM_STATEMENT", ""),
            "methodology": full_summary.get("METHODOLOGY", ""),
            "architecture": full_summary.get("ARCHITECTURE", ""),
            "key_results": full_summary.get("KEY_RESULTS", ""),
            "implications": full_summary.get("IMPLICATIONS", ""),
            "takeaways": takeaways,
            "important_ideas": important_ideas,
            "future_directions": future_directions,
            "novelty": novelty,
            "limitations": limitations,
            "practical_applications": practical_applications,
            "related_work": related_work,
            "background": full_summary.get("BACKGROUND", ""),
            "math_formulations": full_summary.get("MATH_FORMULATIONS", ""),
            "similar_papers": similar_papers,
            "highlighted_text": extracted_data.get("highlighted_text", []),
            "figures_tables": extracted_data.get("figures_tables", [])
        }
        
        # Add optional generated content
        if code_implementation:
            result["code_implementation"] = code_implementation
        
        if blog_post:
            result["blog_post"] = blog_post
        
        # Store in database
        self._store_paper_summary(result)
        
        return result
    
    def _store_paper_summary(self, result: Dict[str, Any]) -> None:
        """Store paper summary in the database."""
        try:
            self.db_manager.add_paper(
                paper_id=result["paper_id"],
                title=result["title"],
                filepath=result["filepath"],
                summary=result["summary"],
                takeaways=result["takeaways"],
                architecture=result["architecture"],
                important_ideas=result.get("important_ideas", []),
                future_ideas=result["future_directions"],
                background=result["background"],
                math_formulations=result["math_formulations"],
                similar_papers=[p.get("title", "") for p in result.get("similar_papers", [])],
                novelty=result.get("novelty", ""),
                domain=result.get("domain", "Unknown")
            )
            logger.info(f"Stored paper summary in database with ID: {result['paper_id']}")
        except Exception as e:
            logger.error(f"Failed to store paper summary in database: {e}")
    
    def get_paper_summary(self, paper_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a paper summary from the database."""
        try:
            paper = self.db_manager.get_paper(paper_id)
            return paper
        except Exception as e:
            logger.error(f"Failed to retrieve paper with ID {paper_id}: {e}")
            return None
    
    def search_papers(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for papers in the database using a text query."""
        try:
            # Check if it's a domain-specific search
            if query.lower().startswith("domain:"):
                domain = query.split(":", 1)[1].strip()
                papers = self.db_manager.search_by_domain(domain, n_results=n_results)
            else:
                papers = self.db_manager.search_papers(query, n_results=n_results)
            return papers
        except Exception as e:
            logger.error(f"Failed to search papers with query '{query}': {e}")
            return []
    
    def update_paper_field(self, paper_id: str, field: str, value: Any) -> bool:
        """Update a specific field for a paper in the database."""
        try:
            self.db_manager.update_paper_field(paper_id, field, value)
            logger.info(f"Updated field '{field}' for paper with ID {paper_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to update field '{field}' for paper with ID {paper_id}: {e}")
            return False