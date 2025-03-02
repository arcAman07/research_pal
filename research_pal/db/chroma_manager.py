import os
import chromadb
from chromadb.config import Settings
from typing import Dict, List, Optional, Any

class ChromaManager:
    """Manages interactions with ChromaDB for storing paper information."""
    
    def __init__(self, persist_directory: str = "~/.research_pal/chroma_db"):
        self.persist_directory = os.path.expanduser(persist_directory)
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Create or get collections for papers
        self.papers_collection = self.client.get_or_create_collection(
            name="papers",
            metadata={"description": "Research paper summaries and metadata"}
        )
    
    def add_paper(self, 
                 paper_id: str,
                 title: str,
                 filepath: str,
                 summary: str,
                 takeaways: List[str],
                 # Required parameters above, default parameters below
                 architecture: Optional[str] = None,
                 important_ideas: Optional[List[str]] = None,
                 future_ideas: Optional[List[str]] = None,
                 background: Optional[str] = None,
                 math_formulations: Optional[str] = None,
                 similar_papers: Optional[List[str]] = None,
                 novelty: Optional[str] = None,
                 domain: Optional[str] = "Unknown") -> None:
        """
        Add or update a paper in the database.
        
        Args:
            paper_id: Unique identifier for the paper (could be DOI or filename)
            title: Title of the paper
            filepath: Path to the PDF file
            summary: Full summary of the paper
            takeaways: List of major takeaways
            architecture: Description of the model architecture (if applicable)
            important_ideas: List of important ideas from the paper
            future_ideas: Potential future research directions
            background: Background information
            math_formulations: Mathematical formulations
            similar_papers: Recommended similar papers
            novelty: Description of the paper's novelty
            domain: Research domain (e.g., NLP, CV, RL)
        """
        # Create metadata dictionary
        metadata = {
            "title": title,
            "filepath": filepath,
            "domain": domain,
            "has_architecture": architecture is not None,
            "has_math": math_formulations is not None
        }
        
        # Create document content
        document = {
            "summary": summary,
            "takeaways": " | ".join(takeaways) if takeaways else "",
            "architecture": architecture or "",
            "important_ideas": " | ".join(important_ideas) if important_ideas else "",
            "future_ideas": " | ".join(future_ideas) if future_ideas else "",
            "background": background or "",
            "math_formulations": math_formulations or "",
            "similar_papers": " | ".join(similar_papers) if similar_papers else "",
            "novelty": novelty or "",
            "domain": domain
        }
        
        # Convert document to string for embedding
        document_text = " ".join([f"{k}: {v}" for k, v in document.items() if v])
        
        # Add to collection (upsert if already exists)
        self.papers_collection.upsert(
            ids=[paper_id],
            documents=[document_text],
            metadatas=[metadata]
        )
    
    def get_paper(self, paper_id: str) -> Dict[str, Any]:
        """Retrieve a paper by its ID."""
        results = self.papers_collection.get(ids=[paper_id])
        
        if not results["ids"]:
            return None
        
        # Parse the document text back into a structured format
        document_text = results["documents"][0]
        metadata = results["metadatas"][0]
        
        # Parse document sections
        sections = {}
        current_section = None
        current_content = []
        
        for line in document_text.split("\n"):
            if ": " in line and line.split(": ")[0].lower() in [
                "summary", "takeaways", "architecture", "important_ideas", 
                "future_ideas", "background", "math_formulations", 
                "similar_papers", "novelty", "domain"
            ]:
                # Save previous section
                if current_section:
                    sections[current_section] = "\n".join(current_content)
                
                # Start new section
                section_parts = line.split(": ", 1)
                current_section = section_parts[0].lower()
                current_content = [section_parts[1]] if len(section_parts) > 1 else []
            else:
                if current_section:
                    current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = "\n".join(current_content)
        
        # Process list fields
        for field in ["takeaways", "important_ideas", "future_ideas", "similar_papers"]:
            if field in sections:
                sections[field] = [item.strip() for item in sections[field].split("|") if item.strip()]
        
        # Combine with metadata
        result = {**sections, **metadata}
        return result
    
    def search_papers(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for papers using a text query.
        
        Args:
            query: Search query text
            n_results: Maximum number of results to return
            
        Returns:
            List of matching papers
        """
        # Check if this is a special query type
        if query.lower().startswith("domain:"):
            # Handle domain search separately
            domain = query.split(":", 1)[1].strip()
            return self.search_by_domain(domain, n_results=n_results)
        
        elif query.lower().startswith("title:"):
            # Enhanced title search
            title_query = query.split(":", 1)[1].strip()
            return self.search_by_title(title_query, n_results=n_results)
            
        # Standard vector search
        try:
            results = self.papers_collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            papers = []
            for i, paper_id in enumerate(results["ids"][0]):
                paper = self.get_paper(paper_id)
                if paper:  # Ensure paper exists
                    papers.append(paper)
                
            return papers
        except Exception as e:
            logger.error(f"Error searching papers: {e}")
            # Return empty list on error
            return []
    
    def search_by_domain(self, domain: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for papers by research domain."""
        # Get all papers with matching domain metadata
        results = self.papers_collection.get(
            where={"domain": {"$eq": domain}}
        )
        
        papers = []
        for i, paper_id in enumerate(results["ids"]):
            paper = self.get_paper(paper_id)
            papers.append(paper)
            
        # Limit to requested number
        return papers[:n_results]
    
    def search_by_title(self, title_query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for papers by title.
        
        Args:
            title_query: Title search query
            n_results: Maximum number of results to return
            
        Returns:
            List of papers with matching titles
        """
        try:
            # Two approaches for title search:
            
            # 1. Try metadata where filter first (more precise but requires exact match)
            title_results = self.papers_collection.get(
                where={"title": {"$contains": title_query}}
            )
            
            # 2. Use vector search as backup (better semantic matching)
            augmented_query = f"title: {title_query}"
            vector_results = self.papers_collection.query(
                query_texts=[augmented_query],
                n_results=n_results
            )
            
            # Combine results, prioritizing exact matches
            paper_ids = set()
            results = []
            
            # Add exact matches first
            if title_results["ids"]:
                for i, paper_id in enumerate(title_results["ids"]):
                    if paper_id not in paper_ids:
                        paper = self.get_paper(paper_id)
                        if paper:
                            results.append(paper)
                            paper_ids.add(paper_id)
            
            # Add vector matches
            if "ids" in vector_results and vector_results["ids"]:
                for i, paper_id in enumerate(vector_results["ids"][0]):
                    if paper_id not in paper_ids and len(results) < n_results:
                        paper = self.get_paper(paper_id)
                        if paper:
                            results.append(paper)
                            paper_ids.add(paper_id)
            
            # Sort results by relevance to the title query
            # Simple sorting - title contains query gets priority
            results.sort(key=lambda p: title_query.lower() in p.get("title", "").lower(), reverse=True)
            
            return results[:n_results]
        
        except Exception as e:
            logger.error(f"Error searching papers by title: {e}")
            # Return empty list on error
            return []
    
    def update_paper_field(self, paper_id: str, field: str, value: Any) -> None:
        """Update a specific field for a paper."""
        paper = self.get_paper(paper_id)
        if not paper:
            raise ValueError(f"Paper with ID {paper_id} not found")
        
        # Update the field
        paper[field] = value
        
        # Re-add the paper with updated information
        self.add_paper(
            paper_id=paper_id,
            title=paper.get("title", ""),
            filepath=paper.get("filepath", ""),
            summary=paper.get("summary", ""),
            takeaways=paper.get("takeaways", []),
            architecture=paper.get("architecture", ""),
            important_ideas=paper.get("important_ideas", []),
            future_ideas=paper.get("future_ideas", []),
            background=paper.get("background", ""),
            math_formulations=paper.get("math_formulations", ""),
            similar_papers=paper.get("similar_papers", []),
            novelty=paper.get("novelty", ""),
            domain=paper.get("domain", "Unknown")
        )