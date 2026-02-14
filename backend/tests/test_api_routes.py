"""
Tests for Flask API routes.

Tests all HTTP endpoints with various scenarios.
"""

import pytest
import json
from unittest.mock import Mock, patch
from backend.app import app
from backend.models.data_models import StyleProfile, Message, EscalationResult


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_training_data():
    """Sample training data for testing."""
    return {
        'trainingData': [
            'hey how are you',
            'good thanks!',
            'wanna hang out?',
            'sure sounds good',
            'cool see you later',
            'bye!',
            'talk soon',
            'yeah definitely',
            'catch you later',
            'peace out'
        ],
        'userId': 'test-user'
    }


@pytest.fixture
def sample_style_profile():
    """Sample style profile for testing."""
    return {
        'sentenceLength': 'medium',
        'emojiFrequency': 0.5,
        'commonEmojis': ['😊', '👍'],
        'punctuationStyle': 'standard',
        'tone': 'casual',
        'commonPhrases': ['hey', 'cool'],
        'formalityLevel': 0.3,
        'analysisTimestamp': '2024-01-01T12:00:00Z'
    }


@pytest.fixture
def sample_messages():
    """Sample conversation messages for testing."""
    return [
        {
            'id': 'msg-1',
            'sender': 'friend',
            'text': 'Want to grab lunch?',
            'timestamp': '2024-01-01T12:00:00Z',
            'isAiGenerated': False
        }
    ]


class TestTrainEndpoint:
    """Tests for POST /api/train endpoint."""
    
    @patch('backend.api.routes.get_style_analyzer')
    def test_train_success(self, mock_get_analyzer, client, sample_training_data):
        """Test successful training with valid data."""
        # Mock StyleAnalyzer
        mock_profile = StyleProfile(
            sentence_length='medium',
            emoji_frequency=0.5,
            common_emojis=['😊'],
            punctuation_style='standard',
            tone='casual',
            common_phrases=['hey'],
            formality_level=0.3,
            analysis_timestamp='2024-01-01T12:00:00Z'
        )
        
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = mock_profile
        mock_get_analyzer.return_value = mock_analyzer
        
        # Make request
        response = client.post(
            '/api/train',
            data=json.dumps(sample_training_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'styleProfile' in data
        assert data['styleProfile']['tone'] == 'casual'
        assert data['userId'] == 'test-user'
    
    def test_train_missing_body(self, client):
        """Test training with missing request body."""
        response = client.post('/api/train')
        if response.status_code != 400:
            print(f"Response data: {response.data.decode()}")
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_train_missing_training_data(self, client):
        """Test training with missing trainingData field."""
        response = client.post(
            '/api/train',
            data=json.dumps({'userId': 'test'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'trainingData' in data['error']
    
    def test_train_insufficient_data(self, client):
        """Test training with fewer than 10 messages."""
        response = client.post(
            '/api/train',
            data=json.dumps({
                'trainingData': ['msg1', 'msg2', 'msg3'],
                'userId': 'test'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Insufficient' in data['error']
        assert data['provided'] == 3
        assert data['required'] == 10
    
    def test_train_invalid_data_type(self, client):
        """Test training with non-array trainingData."""
        response = client.post(
            '/api/train',
            data=json.dumps({
                'trainingData': 'not an array',
                'userId': 'test'
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'array' in data['error']
    
    @patch('backend.api.routes.get_style_analyzer')
    def test_train_analyzer_error(self, mock_get_analyzer, client, sample_training_data):
        """Test training when analyzer raises error."""
        mock_analyzer = Mock()
        mock_analyzer.analyze.side_effect = RuntimeError('API Error')
        mock_get_analyzer.return_value = mock_analyzer
        
        response = client.post(
            '/api/train',
            data=json.dumps(sample_training_data),
            content_type='application/json'
        )
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data


class TestRespondEndpoint:
    """Tests for POST /api/respond endpoint."""
    
    def test_respond_success_no_escalation(
        self,
        client,
        sample_style_profile,
        sample_messages
    ):
        """Test successful response generation without escalation."""
        with patch('backend.api.routes.escalation_detector') as mock_detector, \
             patch('backend.api.routes.response_generator') as mock_generator:
            
            # Create mock escalation result
            mock_escalation = EscalationResult(
                detected=False,
                confidence_score=85,
                reason='Casual conversation',
                category=None
            )
            mock_detector.detect.return_value = mock_escalation
            
            # Create mock response
            mock_generator.generate.return_value = 'Sure, sounds good!'
            
            # Make request
            response = client.post(
                '/api/respond',
                data=json.dumps({
                    'sessionId': 'session-123',
                    'styleProfile': sample_style_profile,
                    'conversationHistory': sample_messages,
                    'incomingMessage': 'Want to grab lunch?',
                    'autopilotEnabled': True
                }),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['response'] == 'Sure, sounds good!'
            assert data['escalation']['detected'] is False
            assert data['escalation']['confidenceScore'] == 85
    
    def test_respond_with_escalation(
        self,
        client,
        sample_style_profile,
        sample_messages
    ):
        """Test response when escalation is detected."""
        with patch('backend.api.routes.escalation_detector') as mock_detector:
            # Create mock escalation result
            mock_escalation = EscalationResult(
                detected=True,
                confidence_score=95,
                reason='Serious health concern',
                category='serious_question'
            )
            mock_detector.detect.return_value = mock_escalation
            
            # Make request
            response = client.post(
                '/api/respond',
                data=json.dumps({
                    'sessionId': 'session-123',
                    'styleProfile': sample_style_profile,
                    'conversationHistory': sample_messages,
                    'incomingMessage': 'My mom is in the hospital',
                    'autopilotEnabled': True
                }),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['response'] is None  # No response due to escalation
            assert data['escalation']['detected'] is True
            assert data['escalation']['confidenceScore'] == 95
    
    def test_respond_autopilot_disabled(
        self,
        client,
        sample_style_profile,
        sample_messages
    ):
        """Test response when autopilot is disabled."""
        with patch('backend.api.routes.escalation_detector') as mock_detector:
            # Create mock escalation result
            mock_escalation = EscalationResult(
                detected=False,
                confidence_score=85,
                reason='Casual conversation',
                category=None
            )
            mock_detector.detect.return_value = mock_escalation
            
            # Make request with autopilot disabled
            response = client.post(
                '/api/respond',
                data=json.dumps({
                    'sessionId': 'session-123',
                    'styleProfile': sample_style_profile,
                    'conversationHistory': sample_messages,
                    'incomingMessage': 'Want to grab lunch?',
                    'autopilotEnabled': False
                }),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['response'] is None  # No response due to autopilot disabled
            assert data['escalation']['detected'] is False
    
    def test_respond_missing_message(self, client, sample_style_profile):
        """Test respond with missing incoming message."""
        response = client.post(
            '/api/respond',
            data=json.dumps({
                'styleProfile': sample_style_profile,
                'conversationHistory': []
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_respond_missing_style_profile(self, client):
        """Test respond with missing style profile."""
        response = client.post(
            '/api/respond',
            data=json.dumps({
                'incomingMessage': 'test',
                'conversationHistory': []
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestSummarizeEndpoint:
    """Tests for POST /api/summarize endpoint."""
    
    def test_summarize_success(
        self,
        client,
        sample_style_profile,
        sample_messages
    ):
        """Test successful conversation summarization."""
        from backend.models.data_models import ConversationSummary, Message
        
        with patch('backend.api.routes.conversation_summarizer') as mock_summarizer:
            # Create mock summary
            mock_summary = ConversationSummary(
                session_id='session-123',
                transcript=[Message.from_dict(sample_messages[0])],
                commitments=['Lunch tomorrow'],
                action_items=['Confirm time'],
                key_topics=['Lunch plans'],
                ai_message_count=0,
                human_message_count=1,
                escalation_count=0,
                duration=0
            )
            mock_summarizer.summarize.return_value = mock_summary
            
            # Make request
            response = client.post(
                '/api/summarize',
                data=json.dumps({
                    'sessionId': 'session-123',
                    'messages': sample_messages,
                    'styleProfile': sample_style_profile
                }),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'summary' in data
            assert data['summary']['sessionId'] == 'session-123'
            assert len(data['summary']['commitments']) > 0
    
    def test_summarize_missing_messages(self, client, sample_style_profile):
        """Test summarize with missing messages."""
        response = client.post(
            '/api/summarize',
            data=json.dumps({
                'sessionId': 'session-123',
                'styleProfile': sample_style_profile
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_summarize_missing_style_profile(self, client, sample_messages):
        """Test summarize with missing style profile."""
        response = client.post(
            '/api/summarize',
            data=json.dumps({
                'sessionId': 'session-123',
                'messages': sample_messages
            }),
            content_type='application/json'
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data


class TestHealthEndpoint:
    """Tests for GET /health endpoint."""
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'ok'
