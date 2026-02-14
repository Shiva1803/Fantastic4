"""
QueryEngine service for RAG-based question answering within spaces.

Uses vector search to find relevant content, then sends context
to an LLM to generate an informed answer with source references.
"""

import os
import time
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from groq import Groq
from backend.services.content_manager import ContentManager


class QueryEngine:
    """
    RAG-based query engine for answering questions about space content.
    
    Flow:
    1. Search VectorStore for relevant items
    2. Build context from top results
    3. Send question + context to LLM
    4. Return answer with source references
    """
    
    def __init__(self, content_manager: ContentManager):
        """
        Initialize the QueryEngine.
        
        Args:
            content_manager: ContentManager instance (shared with routes)
        """
        self.content_manager = content_manager
        self.max_retries = 3
        
        # Query history (in-memory)
        self._queries: Dict[str, Dict] = {}
        
        # Rate limiting: {space_id: [timestamp, ...]}
        self._rate_limits: Dict[str, List[float]] = {}
        
        # Initialize Groq client
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            self.client = Groq(api_key=api_key)
            self.model = "llama-3.3-70b-versatile"
        else:
            self.client = None
    
    def _check_rate_limit(self, space_id: str) -> bool:
        """Check if the space has exceeded rate limit (10 queries/minute)."""
        now = time.time()
        if space_id not in self._rate_limits:
            self._rate_limits[space_id] = []
        
        # Remove timestamps older than 60 seconds
        self._rate_limits[space_id] = [
            ts for ts in self._rate_limits[space_id] if now - ts < 60
        ]
        
        return len(self._rate_limits[space_id]) < 10
    
    def _record_query_time(self, space_id: str):
        """Record a query timestamp for rate limiting."""
        if space_id not in self._rate_limits:
            self._rate_limits[space_id] = []
        self._rate_limits[space_id].append(time.time())
    
    def query(self, space_id: str, question: str) -> Dict:
        """
        Answer a question using content from a space.
        
        Args:
            space_id: Space to search within
            question: User's question
            
        Returns:
            Dict with query_id, question, answer, sources, timestamp
            
        Raises:
            ValueError: If inputs are invalid or rate limit exceeded
            RuntimeError: If LLM call fails
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        # Rate limiting
        if not self._check_rate_limit(space_id):
            raise ValueError("Rate limit exceeded. Please wait a moment before asking another question.")
        
        self._record_query_time(space_id)
        
        # Step 1: Find relevant content via vector search
        search_results = self.content_manager.search_items(space_id, question, top_k=5)
        
        # Step 2: Build context from results
        context = self._build_context(search_results)
        
        # Step 3: Generate answer via LLM
        answer = self._generate_answer(question, context)
        
        # Step 4: Build source references
        sources = []
        for result in search_results:
            sources.append({
                'itemId': result.get('id'),
                'type': result.get('type'),
                'content': result.get('content', '')[:200],  # Preview
                'score': result.get('score', 0)
            })
        
        # Store query in history
        query_id = str(uuid.uuid4())
        query_record = {
            'id': query_id,
            'spaceId': space_id,
            'question': question,
            'answer': answer,
            'sources': sources,
            'createdAt': datetime.now().isoformat()
        }
        
        self._queries[query_id] = query_record
        return query_record
    
    def get_queries(self, space_id: str, limit: int = 20, offset: int = 0) -> List[Dict]:
        """
        Get query history for a space.
        
        Args:
            space_id: Space ID
            limit: Max results to return
            offset: Pagination offset
            
        Returns:
            List of query records, newest first
        """
        queries = [
            q for q in self._queries.values()
            if q['spaceId'] == space_id
        ]
        queries.sort(key=lambda x: x['createdAt'], reverse=True)
        return queries[offset:offset + limit]
    
    def _build_context(self, search_results: List[Dict]) -> str:
        """Build LLM context from search results."""
        if not search_results:
            return "No relevant content found in this space."
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            item_type = result.get('type', 'unknown')
            content = result.get('content', '')
            notes = result.get('notes', '')
            score = result.get('score', 0)
            
            # For files, use extracted text from metadata
            if item_type == 'file':
                extracted = result.get('metadata', {}).get('extracted_text', '')
                if extracted:
                    content = f"[File: {content}] {extracted[:1000]}"
                else:
                    content = f"[File: {content}] (No text extracted)"
            
            entry = f"Source {i} (relevance: {score}):\n{content}"
            if notes:
                entry += f"\nNotes: {notes}"
            context_parts.append(entry)
        
        return "\n\n---\n\n".join(context_parts)
    
    def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer using LLM with RAG context."""
        if not self.client:
            # Fallback if no API key: return context-based summary
            return f"⚠️ LLM not configured (set GROQ_API_KEY). Based on your space content, here are the most relevant items:\n\n{context}"
        
        prompt = f"""You are a helpful assistant that answers questions based on the user's saved content.
Use ONLY the provided context to answer. If the context doesn't contain enough information, say so clearly.
Be concise and direct. Reference specific sources when appropriate.

Context from user's space:
{context}

Question: {question}

Answer:"""
        
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "You answer questions based on the user's saved content. Be accurate, helpful, and cite your sources."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise RuntimeError(f"Failed to generate answer after {self.max_retries} attempts: {e}")
                time.sleep(2 ** attempt)
        
        raise RuntimeError("Unexpected error in _generate_answer")
