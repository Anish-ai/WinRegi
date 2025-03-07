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
            query: Search query string
            
        Returns:
            List of matching settings and commands
        """
        try:
            # Process the query with NLP
            processed_query = self.nlp.process_query(query)
            
            # Log the search query (non-critical, so wrap in try-except)
            try:
                self.db_manager.log_search_query(query)
            except Exception as e:
                print(f"Error logging search query: {e}")
                # Continue with search even if logging fails
            
            # Get matching settings from database
            setting_results = self.db_manager.search_settings(query)
            
            # Get matching commands from database
            command_results = self.db_manager.get_commands_in_search_results(query)
            
            # If no results, return empty list early
            if not setting_results and not command_results:
                return []
            
            # Process settings results    
            if setting_results:
                # Enhance settings results with relevance scoring
                scored_settings = self._score_results(setting_results, processed_query)
                
                # Sort by relevance score
                sorted_settings = sorted(scored_settings, key=lambda x: x['relevance_score'], reverse=True)
                
                # Filter out low-relevance results
                if sorted_settings and sorted_settings[0]['relevance_score'] > 0.5:
                    threshold = max(0.3, sorted_settings[0]['relevance_score'] * 0.5)
                    filtered_settings = [r for r in sorted_settings if r['relevance_score'] >= threshold]
                else:
                    filtered_settings = sorted_settings
                    
                # Mark results as settings
                for result in filtered_settings:
                    result['result_type'] = 'setting'
            else:
                filtered_settings = []
            
            # Combine results
            combined_results = filtered_settings + command_results
            
            # Sort combined results by relevance (commands have no score, so they go at the end)
            # Use result_type as secondary sort to group settings and commands
            def sort_key(item):
                if 'relevance_score' in item:
                    return (item['relevance_score'], item.get('result_type', 'setting'))
                return (0, item.get('result_type', 'command'))
                
            combined_results = sorted(combined_results, key=sort_key, reverse=True)
            
            return combined_results
        except Exception as e:
            print(f"Error in search engine: {e}")
            traceback.print_exc()
            # Return empty results on error rather than crashing
            return []
    
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
    
    def _calculate_relevance(self, result: Dict[str, Any], processed_query: Dict[str, Any]) -> float:
        """Calculate relevance score for a result
        
        Args:
            result: Search result
            processed_query: Processed query information
            
        Returns:
            Relevance score between 0 and 1
        """
        try:
            score = 0.0
            keywords = processed_query['keywords']
            
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
            
            # Intent-based scoring
            intent = processed_query['intent']
            
            # For enable/disable intents, check if the setting has matching actions
            if intent['is_enable'] or intent['is_disable']:
                try:
                    setting_id = result['id']
                    actions = self.db_manager.get_actions_for_setting(setting_id)
                    
                    action_types = [action['name'].lower() for action in actions]
                    enable_keywords = ["enable", "on", "activate"]
                    disable_keywords = ["disable", "off", "deactivate"]
                    
                    has_enable_action = any(any(k in action for k in enable_keywords) for action in action_types)
                    has_disable_action = any(any(k in action for k in disable_keywords) for action in action_types)
                    
                    # If the intent matches available actions, increase score
                    if (intent['is_enable'] and has_enable_action) or (intent['is_disable'] and has_disable_action):
                        score += 0.2
                except Exception as e:
                    print(f"Error in intent-based scoring: {e}")
                    # Continue even if this part fails
            
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