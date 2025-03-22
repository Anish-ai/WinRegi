"""
AI-powered search engine for WinRegi application
Handles search queries and returns relevant Windows settings and commands
"""
from typing import List, Dict, Any
import re
import traceback
from .nlp_processor import NLPProcessor
from ..database.db_manager import DatabaseManager

class SearchEngine:
    """AI-powered search engine for Windows settings and commands"""
    
    def __init__(self, db_manager: DatabaseManager = None):
        """Initialize the search engine
        
        Args:
            db_manager: Database manager instance
        """
        self.nlp = NLPProcessor()
        self.db_manager = db_manager if db_manager else DatabaseManager()
        
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Search for settings and commands matching the query
        
        Args:
            query: Search query
            
        Returns:
            List of search results
        """
        # Record search in history
        self.db_manager.add_search_history(query)
        
        # Get settings matching the query
        settings_results = self.db_manager.search_settings(query)
        
        # Add result type to settings
        for result in settings_results:
            result['result_type'] = 'setting'
        
        # Get commands matching the query
        command_results = self.db_manager.get_commands_in_search_results(query)
        
        # Combine results
        all_results = settings_results + command_results
        
        # Sort results by relevance (simple implementation)
        # In a real AI-powered search, this would use more sophisticated ranking
        all_results.sort(key=lambda x: self._calculate_relevance(x, query), reverse=True)
        
        return all_results
    
    def _score_results(self, results: List[Dict[str, Any]], processed_query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Score search results based on relevance to the query
        
        Args:
            results: Raw search results
            processed_query: Processed query information
            
        Returns:
            Results with relevance scores
        """
        try:
            scored_results = []
            
            for result in results:
                # Calculate relevance score
                score = self._calculate_relevance(result, processed_query)
                
                # Add score to result
                result_with_score = result.copy()
                result_with_score['relevance_score'] = score
                
                scored_results.append(result_with_score)
            
            return scored_results
        except Exception as e:
            print(f"Error scoring results: {e}")
            # Return the original results with a default score as fallback
            return [dict(r, relevance_score=0.5) for r in results]
    
    def _calculate_relevance(self, result: Dict[str, Any], query: str) -> float:
        """Calculate relevance score for a result
        
        Args:
            result: Search result
            query: Search query string
            
        Returns:
            Relevance score between 0 and 1
        """
        try:
            score = 0.0
            query_lower = query.lower()
            keywords = query_lower.split()
            
            # Check name match
            name_lower = result['name'].lower()
            for keyword in keywords:
                if keyword in name_lower:
                    # Direct name match is highly relevant
                    score += 0.5
                    break
            
            # Check description match
            if 'description' in result and result['description']:
                desc_lower = result['description'].lower()
                for keyword in keywords:
                    if keyword in desc_lower:
                        score += 0.3
                        break
            
            # Check category match
            if 'category_name' in result and result['category_name']:
                category_lower = result['category_name'].lower()
                for keyword in keywords:
                    if keyword in category_lower:
                        score += 0.2
                        break
            
            # Normalize score to be between 0 and 1
            return min(score, 1.0)
        except Exception as e:
            print(f"Error calculating relevance: {e}")
            # Return a default middle-of-the-road score as fallback
            return 0.5
    
    def get_setting_recommendations(self, query: str = None) -> List[Dict[str, Any]]:
        """Get setting recommendations based on a query or general recommendations
        
        Args:
            query: Optional search query
            
        Returns:
            List of recommended settings
        """
        try:
            if query:
                # If query is provided, use it for recommendations
                return self.search(query)
            else:
                # Otherwise, provide general recommendations
                try:
                    # Get settings recommendations
                    categories = self.db_manager.get_all_categories()
                    recommendations = []
                    
                    for category in categories[:3]:  # Get settings from top 3 categories
                        category_settings = self.db_manager.get_settings_by_category(category['id'])
                        if category_settings:
                            for setting in category_settings[:2]:  # Get top 2 settings from each category
                                setting['result_type'] = 'setting'
                                recommendations.append(setting)
                    
                    # Get popular commands (would normally be based on usage stats)
                    commands = self.db_manager.get_all_commands()
                    if commands:
                        # Take top 3 commands (in a real app, these would be sorted by popularity)
                        for command in commands[:3]:
                            command['result_type'] = 'command'
                            recommendations.append(command)
                    
                    return recommendations
                except Exception as e:
                    print(f"Error getting setting recommendations: {e}")
                    return []
        except Exception as e:
            print(f"Error in get_setting_recommendations: {e}")
            return []