"""
NLP processor for AI search functionality
Handles natural language processing for search queries
"""
import re
import string
from typing import List, Dict, Any, Set

class NLPProcessor:
    """Processes natural language queries for search functionality"""
    
    def __init__(self):
        """Initialize the NLP processor"""
        self.common_words = {
            "the", "a", "an", "and", "or", "but", "if", "because", "as", "what",
            "how", "when", "where", "who", "will", "way", "about", "many", "then",
            "them", "these", "so", "some", "can", "could", "would", "should", "my",
            "your", "his", "her", "their", "its", "our", "i", "we", "you", "they",
            "it", "is", "are", "was", "were", "be", "been", "being", "have", "has",
            "had", "do", "does", "did", "doing", "to", "for", "with", "in", "on", 
            "at", "by", "of", "from", "up", "down", "that", "this"
        }
        
        # Common Windows settings related phrases and their mappings
        self.domain_mappings = {
            "speed up": ["performance", "visual effects", "animations"],
            "faster": ["performance", "optimize", "speed"],
            "slow": ["performance", "optimize", "speed"],
            "dark mode": ["theme", "dark theme", "personalization"],
            "light mode": ["theme", "light theme", "personalization"],
            "night mode": ["night light", "blue light", "display"],
            "blue light": ["night light", "display", "color"],
            "privacy": ["tracking", "telemetry", "data collection"],
            "battery": ["power", "energy", "power plan"],
            "power": ["battery", "energy", "power plan"],
            "wifi": ["network", "wireless", "internet"],
            "internet": ["network", "connection", "wifi"]
        }
    
    def preprocess_query(self, query: str) -> str:
        """Preprocess the query string
        
        Args:
            query: Raw query string
            
        Returns:
            Preprocessed query string
        """
        # Convert to lowercase
        query = query.lower()
        
        # Remove punctuation
        query = query.translate(str.maketrans("", "", string.punctuation))
        
        return query
    
    def tokenize(self, text: str) -> List[str]:
        """Split text into tokens
        
        Args:
            text: Text to tokenize
            
        Returns:
            List of tokens
        """
        # Simple whitespace tokenization
        return text.split()
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove common stopwords from tokens
        
        Args:
            tokens: List of tokens
            
        Returns:
            Filtered list of tokens
        """
        return [token for token in tokens if token not in self.common_words]
    
    def expand_domain_terms(self, tokens: List[str]) -> Set[str]:
        """Expand tokens with domain-specific related terms
        
        Args:
            tokens: List of tokens
            
        Returns:
            Set of expanded tokens
        """
        expanded = set(tokens)
        
        # Check for multi-word mappings
        text = " ".join(tokens)
        for key, values in self.domain_mappings.items():
            if key in text:
                expanded.update(values)
        
        # Check individual tokens
        for token in tokens:
            if token in self.domain_mappings:
                expanded.update(self.domain_mappings[token])
        
        return expanded
    
    def extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from a query
        
        Args:
            query: Search query
            
        Returns:
            List of keywords
        """
        # Preprocess query
        processed_query = self.preprocess_query(query)
        
        # Tokenize
        tokens = self.tokenize(processed_query)
        
        # Remove stopwords
        filtered_tokens = self.remove_stopwords(tokens)
        
        # Expand with domain-specific terms
        expanded_tokens = self.expand_domain_terms(filtered_tokens)
        
        return list(expanded_tokens)
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process a search query
        
        Args:
            query: Search query string
            
        Returns:
            Dictionary with processed query information
        """
        # Extract keywords
        keywords = self.extract_keywords(query)
        
        # Determine query intent
        intent = self.determine_intent(query)
        
        return {
            "original_query": query,
            "processed_query": self.preprocess_query(query),
            "keywords": keywords,
            "intent": intent
        }
    
    def determine_intent(self, query: str) -> Dict[str, Any]:
        """Determine the intent of a query
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with intent information
        """
        query_lower = query.lower()
        
        # Check for how-to intent
        how_to_patterns = ["how to", "how do i", "how can i"]
        is_how_to = any(pattern in query_lower for pattern in how_to_patterns)
        
        # Check for question intent
        question_words = ["what", "why", "when", "where", "which", "who"]
        is_question = query_lower.startswith(tuple(question_words)) or "?" in query
        
        # Check for enable/disable intent
        enable_patterns = ["enable", "turn on", "activate", "show"]
        disable_patterns = ["disable", "turn off", "deactivate", "hide"]
        
        is_enable = any(pattern in query_lower for pattern in enable_patterns)
        is_disable = any(pattern in query_lower for pattern in disable_patterns)
        
        return {
            "is_how_to": is_how_to,
            "is_question": is_question,
            "is_enable": is_enable,
            "is_disable": is_disable,
            "primary_type": self._determine_primary_intent_type(is_how_to, is_question, is_enable, is_disable)
        }
    
    def _determine_primary_intent_type(self, is_how_to: bool, is_question: bool, is_enable: bool, is_disable: bool) -> str:
        """Determine the primary intent type
        
        Args:
            is_how_to: Whether the query is a how-to question
            is_question: Whether the query is a question
            is_enable: Whether the query is about enabling a feature
            is_disable: Whether the query is about disabling a feature
            
        Returns:
            Primary intent type
        """
        if is_how_to:
            return "how_to"
        elif is_question:
            return "question"
        elif is_enable:
            return "enable"
        elif is_disable:
            return "disable"
        else:
            return "search"