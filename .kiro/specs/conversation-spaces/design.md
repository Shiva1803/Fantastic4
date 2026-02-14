# Conversation Spaces - Design Document

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Spaces Page  │  │ Space Detail │  │ Query Interface│     │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Space Routes │  │ Content Routes│  │ Query Routes │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       Services Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ SpaceManager │  │ FileProcessor │  │ QueryEngine  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                         │
│  │ VectorStore  │  │ EmbeddingGen │                         │
│  └──────────────┘  └──────────────┘                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Storage                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   SQLite     │  │  File Storage │  │ Vector DB    │      │
│  │  (Metadata)  │  │   (Content)   │  │ (Embeddings) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Data Models

### Space
```python
class Space:
    id: str                    # UUID
    user_id: str              # User identifier
    name: str                 # "Personal", "Work", etc.
    description: str          # Optional description
    created_at: datetime
    updated_at: datetime
    item_count: int           # Number of items in space
```

### SpaceItem
```python
class SpaceItem:
    id: str                   # UUID
    space_id: str             # Foreign key to Space
    type: str                 # "message", "file", "conversation"
    content: str              # Text content or file path
    metadata: dict            # Additional info (file_name, date, etc.)
    notes: str                # User-added context
    created_at: datetime
    embedding_id: str         # Reference to vector embedding
```

### Query
```python
class Query:
    id: str                   # UUID
    space_id: str             # Foreign key to Space
    question: str             # User's question
    answer: str               # AI's response
    sources: List[str]        # IDs of SpaceItems used
    created_at: datetime
```

## Core Services

### 1. SpaceManager
**Responsibility**: CRUD operations for spaces

```python
class SpaceManager:
    def create_space(user_id: str, name: str, description: str) -> Space
    def get_spaces(user_id: str) -> List[Space]
    def get_space(space_id: str) -> Space
    def update_space(space_id: str, name: str, description: str) -> Space
    def delete_space(space_id: str) -> bool
```

### 2. ContentManager
**Responsibility**: Save and manage content in spaces

```python
class ContentManager:
    def save_message(space_id: str, content: str, notes: str) -> SpaceItem
    def save_file(space_id: str, file: File, notes: str) -> SpaceItem
    def get_items(space_id: str) -> List[SpaceItem]
    def delete_item(item_id: str) -> bool
```

### 3. FileProcessor
**Responsibility**: Extract text from various file formats

```python
class FileProcessor:
    def process_pdf(file_path: str) -> str
    def process_image(file_path: str) -> str  # OCR
    def process_document(file_path: str) -> str
    def extract_text(file: File) -> str
```

**Implementation**:
- PDF: Use `PyPDF2` or `pdfplumber`
- Images: Use `pytesseract` for OCR
- Documents: Use `python-docx` for DOCX

### 4. EmbeddingGenerator
**Responsibility**: Generate vector embeddings for content

```python
class EmbeddingGenerator:
    def __init__(self, api_key: str, provider: str):
        # Use OpenAI or Groq for embeddings
        pass
    
    def generate_embedding(text: str) -> List[float]
    def generate_batch_embeddings(texts: List[str]) -> List[List[float]]
```

**Implementation**:
- Use OpenAI's `text-embedding-3-small` model
- Or use open-source models via Hugging Face

### 5. VectorStore
**Responsibility**: Store and search vector embeddings

```python
class VectorStore:
    def add_embedding(item_id: str, embedding: List[float], metadata: dict)
    def search(query_embedding: List[float], space_id: str, top_k: int) -> List[dict]
    def delete_embedding(item_id: str)
```

**Implementation Options**:
- **Simple**: Use FAISS (Facebook AI Similarity Search) - local, no server needed
- **Advanced**: Use Pinecone or Weaviate - cloud-based, scalable

**Recommendation**: Start with FAISS for MVP

### 6. QueryEngine
**Responsibility**: Answer user questions using RAG (Retrieval Augmented Generation)

```python
class QueryEngine:
    def __init__(self, vector_store: VectorStore, llm_client):
        pass
    
    def query(space_id: str, question: str) -> QueryResult:
        # 1. Generate embedding for question
        # 2. Search vector store for relevant content
        # 3. Retrieve top K relevant items
        # 4. Build context from retrieved items
        # 5. Send to LLM with question
        # 6. Return answer with sources
        pass
```

**RAG Flow**:
```
User Question
     ↓
Generate Embedding
     ↓
Vector Search (find similar content)
     ↓
Retrieve Top K Items (e.g., top 5)
     ↓
Build Context (combine retrieved content)
     ↓
LLM Prompt: "Based on this context: {context}, answer: {question}"
     ↓
AI Response + Source References
```

## API Endpoints

### Space Management
```
POST   /api/spaces                    # Create space
GET    /api/spaces                    # List all spaces
GET    /api/spaces/:id                # Get space details
PUT    /api/spaces/:id                # Update space
DELETE /api/spaces/:id                # Delete space
```

### Content Management
```
POST   /api/spaces/:id/items          # Save content to space
GET    /api/spaces/:id/items          # List items in space
DELETE /api/spaces/:id/items/:itemId  # Delete item
POST   /api/spaces/:id/upload         # Upload file
```

### Query
```
POST   /api/spaces/:id/query          # Ask question
GET    /api/spaces/:id/queries        # Get query history
```

## Frontend Pages

### 1. Spaces List Page (`/spaces`)
- Grid/list of all user's spaces
- Create new space button
- Each space shows: name, description, item count
- Click to open space detail

### 2. Space Detail Page (`/spaces/:id`)
- Space name and description (editable)
- List of saved items with previews
- "Add Content" button (message or file)
- Query interface at top
- Delete space option

### 3. Query Interface (within Space Detail)
- Text input for questions
- Submit button
- Answer display with source references
- Query history below

## Technical Stack

### Backend
- **Framework**: Flask (existing)
- **Database**: SQLite (existing) for metadata
- **Vector DB**: FAISS (local, simple)
- **File Storage**: Local filesystem (backend/uploads/)
- **PDF Processing**: `pdfplumber`
- **OCR**: `pytesseract` + Tesseract
- **Embeddings**: OpenAI API or Sentence Transformers
- **LLM**: Groq (existing setup)

### Frontend
- **Framework**: React + TypeScript (existing)
- **Routing**: React Router (existing)
- **File Upload**: HTML5 File API
- **UI**: Tailwind CSS (existing)

## Implementation Phases

### Phase 1: Basic Space Management (Week 1)
- Create Space data model
- Implement SpaceManager service
- Build Spaces List page
- Build Space Detail page
- CRUD operations for spaces

### Phase 2: Content Saving (Week 2)
- Create SpaceItem data model
- Implement ContentManager service
- Add message saving functionality
- Add file upload functionality
- Implement FileProcessor for PDFs

### Phase 3: Vector Search (Week 3)
- Integrate FAISS vector store
- Implement EmbeddingGenerator
- Generate embeddings for saved content
- Build vector search functionality

### Phase 4: Query Engine (Week 4)
- Implement QueryEngine with RAG
- Build query interface UI
- Display answers with sources
- Add query history

### Phase 5: Polish & Features (Week 5)
- Add OCR for images
- Improve UI/UX
- Add search across all spaces
- Performance optimization
- Error handling

## Security Considerations

1. **File Upload Validation**
   - Validate file types (whitelist: PDF, PNG, JPG, DOCX, TXT)
   - Limit file size (10MB max)
   - Scan for malware (optional)

2. **Content Privacy**
   - All content is user-specific
   - No sharing between users (V1)
   - Secure file storage with user-specific directories

3. **API Security**
   - Require authentication for all endpoints
   - Validate user owns the space before operations
   - Rate limiting on query endpoint

## Performance Optimization

1. **Embedding Generation**
   - Batch process embeddings
   - Cache embeddings
   - Use smaller embedding models for speed

2. **Vector Search**
   - Index optimization in FAISS
   - Limit search to specific space
   - Cache frequent queries

3. **File Processing**
   - Process files asynchronously
   - Show progress indicator
   - Store processed text separately

## Testing Strategy

1. **Unit Tests**
   - Test each service independently
   - Mock external dependencies (LLM, embeddings)

2. **Integration Tests**
   - Test full RAG pipeline
   - Test file processing pipeline

3. **Property-Based Tests**
   - Vector search returns relevant results
   - Embeddings are consistent
   - Query answers are accurate

## Future Enhancements (Post-V1)

1. **Automatic Categorization**: AI suggests which space to save content
2. **Smart Summaries**: Auto-generate summaries of saved content
3. **Conversation Threading**: Link related messages together
4. **Export/Import**: Backup and restore spaces
5. **Mobile App**: Native iOS/Android apps
6. **Real-time Sync**: Sync across devices
7. **Sharing**: Share spaces with other users
8. **Integrations**: WhatsApp, Telegram, Email
