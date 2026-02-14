"""
Flask API routes for Conversation Autopilot.

This module defines all HTTP endpoints for the application.
"""

from flask import Blueprint, request, jsonify
from backend.services.style_analyzer import StyleAnalyzer
from backend.services.response_generator import ResponseGenerator
from backend.services.escalation_detector import EscalationDetector
from backend.services.conversation_summarizer import ConversationSummarizer
from backend.services.cache_manager import CacheManager
from backend.services.space_manager import SpaceManager
from backend.services.content_manager import ContentManager
from backend.services.query_engine import QueryEngine
from backend.models.data_models import Message, StyleProfile, Space, SpaceItem, Query
import os

# Create blueprint
api = Blueprint('api', __name__, url_prefix='/api')

# Initialize services (singleton instances)
cache_manager = CacheManager()
space_manager = SpaceManager()
content_manager = ContentManager()
query_engine = QueryEngine(content_manager)
style_analyzer = None
response_generator = None
escalation_detector = None
conversation_summarizer = None


def get_style_analyzer():
    """Get or create StyleAnalyzer instance."""
    global style_analyzer
    if style_analyzer is None:
        # Check API_PROVIDER env variable, default to openai
        api_provider = os.getenv('API_PROVIDER', 'openai').lower()
        
        if api_provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
        elif api_provider == 'groq':
            api_key = os.getenv('GROQ_API_KEY')
        else:
            api_key = os.getenv('OPENROUTER_API_KEY')
            
        style_analyzer = StyleAnalyzer(api_key=api_key, api_provider=api_provider)
    return style_analyzer


def get_response_generator():
    """Get or create ResponseGenerator instance."""
    global response_generator
    if response_generator is None:
        # Check API_PROVIDER env variable, default to openai
        api_provider = os.getenv('API_PROVIDER', 'openai').lower()
        
        if api_provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
        elif api_provider == 'groq':
            api_key = os.getenv('GROQ_API_KEY')
        else:
            api_key = os.getenv('OPENROUTER_API_KEY')
            
        response_generator = ResponseGenerator(api_key=api_key, api_provider=api_provider)
    return response_generator


def get_escalation_detector():
    """Get or create EscalationDetector instance."""
    global escalation_detector
    if escalation_detector is None:
        # Check API_PROVIDER env variable, default to openai
        api_provider = os.getenv('API_PROVIDER', 'openai').lower()
        
        if api_provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
        elif api_provider == 'groq':
            api_key = os.getenv('GROQ_API_KEY')
        else:
            api_key = os.getenv('OPENROUTER_API_KEY')
            
        escalation_detector = EscalationDetector(api_key=api_key, api_provider=api_provider)
    return escalation_detector


def get_conversation_summarizer():
    """Get or create ConversationSummarizer instance."""
    global conversation_summarizer
    if conversation_summarizer is None:
        # Check API_PROVIDER env variable, default to openai
        api_provider = os.getenv('API_PROVIDER', 'openai').lower()
        
        if api_provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
        elif api_provider == 'groq':
            api_key = os.getenv('GROQ_API_KEY')
        else:
            api_key = os.getenv('OPENROUTER_API_KEY')
            
        conversation_summarizer = ConversationSummarizer(api_key=api_key, api_provider=api_provider)
    return conversation_summarizer


@api.route('/train', methods=['POST'])
def train():
    """
    POST /api/train
    
    Analyzes training data to extract user's texting style.
    
    Request Body:
        {
            "trainingData": ["message1", "message2", ...],
            "userId": "optional-user-id"
        }
    
    Response:
        {
            "styleProfile": {
                "sentenceLength": "short" | "medium" | "long",
                "emojiFrequency": 0.0-1.0,
                "commonEmojis": ["😊", ...],
                "punctuationStyle": "minimal" | "standard" | "heavy",
                "tone": "casual" | "formal" | "mixed",
                "commonPhrases": ["hey", ...],
                "formalityLevel": 0.0-1.0,
                "analysisTimestamp": "ISO 8601"
            }
        }
    
    Errors:
        400: Invalid request or insufficient training data (< 10 messages)
        500: API error or processing failure
    """
    try:
        # Parse request body
        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({
                'error': 'Request body is required'
            }), 400
        
        training_data = data.get('trainingData')
        user_id = data.get('userId', 'default-user')
        
        # Validate training data
        if not training_data:
            return jsonify({
                'error': 'trainingData field is required'
            }), 400
        
        if not isinstance(training_data, list):
            return jsonify({
                'error': 'trainingData must be an array of strings'
            }), 400
        
        if len(training_data) < 10:
            return jsonify({
                'error': 'Insufficient training data. Please provide at least 10 messages.',
                'provided': len(training_data),
                'required': 10
            }), 400
        
        # Analyze style
        analyzer = get_style_analyzer()
        style_profile = analyzer.analyze(training_data)
        
        # Cache the profile
        cache_manager.set_style_profile(user_id, style_profile)
        
        # Return profile as JSON
        return jsonify({
            'styleProfile': style_profile.to_dict(),
            'userId': user_id
        }), 200
        
    except ValueError as e:
        # Handle validation errors from StyleAnalyzer
        return jsonify({
            'error': str(e)
        }), 400
        
    except RuntimeError as e:
        # Handle API errors
        return jsonify({
            'error': 'Failed to analyze style',
            'details': str(e)
        }), 500
        
    except Exception as e:
        # Handle unexpected errors
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@api.route('/respond', methods=['POST'])
def respond():
    """
    POST /api/respond
    
    Generates a response to an incoming message, with optional escalation detection.
    
    Request Body:
        {
            "sessionId": "session-123",
            "styleProfile": {...},
            "conversationHistory": [...],
            "incomingMessage": "message text",
            "autopilotEnabled": true
        }
    
    Response:
        {
            "response": "generated response text",
            "escalation": {
                "detected": false,
                "confidenceScore": 85,
                "reason": "...",
                "category": null
            }
        }
    
    Errors:
        400: Invalid request
        500: API error or generation failure
    """
    try:
        # Parse request body
        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({'error': 'Request body is required'}), 400
        
        session_id = data.get('sessionId')
        style_profile_dict = data.get('styleProfile')
        conversation_history_dicts = data.get('conversationHistory', [])
        incoming_message = data.get('incomingMessage')
        autopilot_enabled = data.get('autopilotEnabled', True)
        
        # Validate required fields
        if not incoming_message:
            return jsonify({'error': 'incomingMessage is required'}), 400
        
        if not style_profile_dict:
            return jsonify({'error': 'styleProfile is required'}), 400
        
        # Convert dicts to objects
        style_profile = StyleProfile.from_dict(style_profile_dict)
        conversation_history = [
            Message.from_dict(msg_dict) 
            for msg_dict in conversation_history_dicts
        ]
        
        # Always detect escalation
        global escalation_detector
        if escalation_detector is None:
            escalation_detector = get_escalation_detector()
        escalation_result = escalation_detector.detect(incoming_message, conversation_history)
        
        # Generate response only if autopilot is enabled and no escalation
        response_text = None
        if autopilot_enabled and not escalation_result.detected:
            global response_generator
            if response_generator is None:
                response_generator = get_response_generator()
            response_text = response_generator.generate(
                style_profile,
                conversation_history,
                incoming_message
            )
        
        return jsonify({
            'response': response_text,
            'escalation': escalation_result.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
        
    except RuntimeError as e:
        return jsonify({
            'error': 'Failed to generate response',
            'details': str(e)
        }), 500
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@api.route('/summarize', methods=['POST'])
def summarize():
    """
    POST /api/summarize
    
    Generates a summary of a conversation session.
    
    Request Body:
        {
            "sessionId": "session-123",
            "messages": [...],
            "styleProfile": {...}
        }
    
    Response:
        {
            "summary": {
                "sessionId": "session-123",
                "transcript": [...],
                "commitments": [...],
                "actionItems": [...],
                "keyTopics": [...],
                "aiMessageCount": 5,
                "humanMessageCount": 3,
                "escalationCount": 1,
                "duration": 300
            }
        }
    
    Errors:
        400: Invalid request
        500: API error or summarization failure
    """
    try:
        # Parse request body
        data = request.get_json(silent=True)
        
        if data is None:
            return jsonify({'error': 'Request body is required'}), 400
        
        session_id = data.get('sessionId', 'unknown')
        messages_dicts = data.get('messages', [])
        style_profile_dict = data.get('styleProfile')
        
        # Validate required fields
        if not messages_dicts:
            return jsonify({'error': 'messages array is required'}), 400
        
        if not style_profile_dict:
            return jsonify({'error': 'styleProfile is required'}), 400
        
        # Convert dicts to objects
        messages = [Message.from_dict(msg_dict) for msg_dict in messages_dicts]
        style_profile = StyleProfile.from_dict(style_profile_dict)
        
        # Generate summary
        global conversation_summarizer
        if conversation_summarizer is None:
            conversation_summarizer = get_conversation_summarizer()
        summary = conversation_summarizer.summarize(messages, style_profile, session_id)
        
        # Clear session from cache after summary
        cache_manager.delete_session(session_id)
        
        return jsonify({
            'summary': summary.to_dict()
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
        
    except RuntimeError as e:
        return jsonify({
            'error': 'Failed to generate summary',
            'details': str(e)
        }), 500
        
    except Exception as e:
        return jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500


@api.route('/spaces', methods=['POST'])
def create_space():
    """
    POST /api/spaces
    
    Create a new space.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        user_id = data.get('userId')
        name = data.get('name')
        description = data.get('description')
        
        if not user_id:
            return jsonify({'error': 'userId is required'}), 400
        if not name:
            return jsonify({'error': 'name is required'}), 400
            
        space = space_manager.create_space(user_id, name, description)
        
        return jsonify(space.to_dict()), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@api.route('/spaces', methods=['GET'])
def get_spaces():
    """
    GET /api/spaces
    
    Get all spaces for a user.
    Query param: userId
    """
    try:
        user_id = request.args.get('userId')
        if not user_id:
            return jsonify({'error': 'userId query parameter is required'}), 400
            
        spaces = space_manager.get_spaces(user_id)
        return jsonify([space.to_dict() for space in spaces]), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@api.route('/spaces/<space_id>', methods=['GET'])
def get_space(space_id):
    """
    GET /api/spaces/:id
    
    Get space details.
    """
    try:
        space = space_manager.get_space(space_id)
        if not space:
            return jsonify({'error': 'Space not found'}), 404
            
        return jsonify(space.to_dict()), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@api.route('/spaces/<space_id>', methods=['PUT'])
def update_space(space_id):
    """
    PUT /api/spaces/:id
    
    Update space details.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        name = data.get('name')
        description = data.get('description')
        
        space = space_manager.update_space(space_id, name, description)
        if not space:
            return jsonify({'error': 'Space not found'}), 404
            
        return jsonify(space.to_dict()), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@api.route('/spaces/<space_id>', methods=['DELETE'])
def delete_space(space_id):
    """
    DELETE /api/spaces/:id
    
    Delete a space.
    """
    try:
        result = space_manager.delete_space(space_id)
        if not result:
            return jsonify({'error': 'Space not found'}), 404
            
        return jsonify({'message': 'Space deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

@api.route('/spaces/<space_id>/items', methods=['GET'])
def get_space_items(space_id):
    """
    GET /api/spaces/:id/items
    
    Get all items in a space.
    """
    try:
        # Verify space exists
        space = space_manager.get_space(space_id)
        if not space:
            return jsonify({'error': 'Space not found'}), 404
            
        items = content_manager.get_items(space_id)
        return jsonify([item.to_dict() for item in items]), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@api.route('/spaces/<space_id>/items', methods=['POST'])
def save_message(space_id):
    """
    POST /api/spaces/:id/items
    
    Save a text message to a space.
    """
    try:
        # Verify space exists
        space = space_manager.get_space(space_id)
        if not space:
            return jsonify({'error': 'Space not found'}), 404
            
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        content = data.get('content')
        notes = data.get('notes')
        
        if not content:
            return jsonify({'error': 'content is required'}), 400
            
        item = content_manager.save_message(space_id, content, notes)
        
        # Increment item count in space
        space.item_count += 1
        return jsonify(item.to_dict()), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@api.route('/spaces/<space_id>/upload', methods=['POST'])
def upload_file(space_id):
    """
    POST /api/spaces/:id/upload
    
    Upload a file to a space.
    Multipart form data: file, notes (optional)
    """
    try:
        # Verify space exists
        space = space_manager.get_space(space_id)
        if not space:
            return jsonify({'error': 'Space not found'}), 404
            
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
            
        file = request.files['file']
        notes = request.form.get('notes')
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
            
        item = content_manager.save_file(space_id, file, notes)
        
        # Increment item count
        space.item_count += 1
        return jsonify(item.to_dict()), 201
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@api.route('/spaces/<space_id>/items/<item_id>', methods=['DELETE'])
def delete_item(space_id, item_id):
    """
    DELETE /api/spaces/:id/items/:itemId
    
    Delete an item from a space.
    """
    try:
        # Verify space exists
        space = space_manager.get_space(space_id)
        if not space:
            return jsonify({'error': 'Space not found'}), 404
            
        result = content_manager.delete_item(item_id)
        if not result:
            return jsonify({'error': 'Item not found'}), 404
            
        # Decrement item count
        if space.item_count > 0:
            space.item_count -= 1
            
        return jsonify({'message': 'Item deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@api.route('/spaces/<space_id>/search', methods=['POST'])
def search_space(space_id):
    """
    POST /api/spaces/:id/search
    
    Semantic search within a space.
    
    Request Body:
        { "query": "search text", "topK": 5 }
    """
    try:
        # Verify space exists
        space = space_manager.get_space(space_id)
        if not space:
            return jsonify({'error': 'Space not found'}), 404
            
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        query = data.get('query')
        top_k = data.get('topK', 5)
        
        if not query or not query.strip():
            return jsonify({'error': 'query is required'}), 400
            
        results = content_manager.search_items(space_id, query, top_k)
        
        return jsonify({
            'query': query,
            'results': results,
            'total': len(results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@api.route('/spaces/<space_id>/query', methods=['POST'])
def query_space(space_id):
    """
    POST /api/spaces/:id/query
    
    Ask a question about space content (RAG).
    
    Request Body:
        { "question": "What does my content say about X?" }
    """
    try:
        space = space_manager.get_space(space_id)
        if not space:
            return jsonify({'error': 'Space not found'}), 404
            
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        question = data.get('question')
        if not question or not question.strip():
            return jsonify({'error': 'question is required'}), 400
            
        result = query_engine.query(space_id, question)
        return jsonify({'query': result}), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@api.route('/spaces/<space_id>/queries', methods=['GET'])
def get_query_history(space_id):
    """
    GET /api/spaces/:id/queries
    
    Get query history for a space.
    Query params: limit (default 20), offset (default 0)
    """
    try:
        space = space_manager.get_space(space_id)
        if not space:
            return jsonify({'error': 'Space not found'}), 404
            
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        queries = query_engine.get_queries(space_id, limit, offset)
        return jsonify({'queries': queries, 'total': len(queries)}), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500


@api.route('/search', methods=['POST'])
def global_search():
    """
    POST /api/search
    
    Search across all spaces.
    
    Request Body:
        { "query": "search text", "userId": "user123", "topK": 5 }
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
            
        query = data.get('query')
        user_id = data.get('userId')
        top_k = data.get('topK', 5)
        
        if not query or not query.strip():
            return jsonify({'error': 'query is required'}), 400
        if not user_id:
            return jsonify({'error': 'userId is required'}), 400
        
        # Search across all user spaces
        user_spaces = space_manager.get_spaces(user_id)
        all_results = []
        
        for space in user_spaces:
            results = content_manager.search_items(space.id, query, top_k)
            for result in results:
                result['spaceName'] = space.name
            all_results.extend(results)
        
        # Sort by score and limit
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        all_results = all_results[:top_k * 2]  # Allow more results across spaces
        
        return jsonify({
            'query': query,
            'results': all_results,
            'total': len(all_results)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Internal server error', 'details': str(e)}), 500

