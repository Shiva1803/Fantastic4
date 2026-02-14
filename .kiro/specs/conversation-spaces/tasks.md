# Conversation Spaces - Implementation Tasks

## Phase 1: Basic Space Management (Week 1)

### 1.1 Backend: Space Data Model
- [ ] Create `Space` model in `backend/models/data_models.py`
- [ ] Add database schema for spaces table
- [ ] Add validation for space name (required, max 50 chars)
- [ ] Add validation for description (optional, max 500 chars)

### 1.2 Backend: SpaceManager Service
- [ ] Create `backend/services/space_manager.py`
- [ ] Implement `create_space(user_id, name, description)`
- [ ] Implement `get_spaces(user_id)`
- [ ] Implement `get_space(space_id)`
- [ ] Implement `update_space(space_id, name, description)`
- [ ] Implement `delete_space(space_id)`
- [ ] Add error handling for all methods

### 1.3 Backend: Space API Routes
- [ ] Create space routes in `backend/api/routes.py`
- [ ] `POST /api/spaces` - Create space
- [ ] `GET /api/spaces` - List all spaces
- [ ] `GET /api/spaces/:id` - Get space details
- [ ] `PUT /api/spaces/:id` - Update space
- [ ] `DELETE /api/spaces/:id` - Delete space
- [ ] Add request validation
- [ ] Add error responses

### 1.4 Frontend: Spaces List Page
- [ ] Create `frontend/src/pages/SpacesPage.tsx`
- [ ] Add route `/spaces` in App.tsx
- [ ] Display grid of spaces
- [ ] Show space name, description, item count
- [ ] Add "Create Space" button
- [ ] Add click handler to navigate to space detail

### 1.5 Frontend: Create Space Modal
- [ ] Create `frontend/src/components/CreateSpaceModal.tsx`
- [ ] Add form with name and description inputs
- [ ] Add validation (name required)
- [ ] Call API to create space
- [ ] Show success/error messages
- [ ] Refresh spaces list after creation

### 1.6 Frontend: Space Detail Page
- [ ] Create `frontend/src/pages/SpaceDetailPage.tsx`
- [ ] Add route `/spaces/:id`
- [ ] Display space name and description
- [ ] Add edit button for name/description
- [ ] Add delete button with confirmation
- [ ] Show empty state when no items

## Phase 2: Content Saving (Week 2)

### 2.1 Backend: SpaceItem Data Model
- [ ] Create `SpaceItem` model in `backend/models/data_models.py`
- [ ] Add database schema for space_items table
- [ ] Add foreign key to spaces table
- [ ] Add type field (message, file, conversation)
- [ ] Add metadata field (JSON)

### 2.2 Backend: ContentManager Service
- [ ] Create `backend/services/content_manager.py`
- [ ] Implement `save_message(space_id, content, notes)`
- [ ] Implement `save_file(space_id, file, notes)`
- [ ] Implement `get_items(space_id)`
- [ ] Implement `delete_item(item_id)`
- [ ] Add pagination for get_items

### 2.3 Backend: File Storage
- [ ] Create `backend/uploads/` directory structure
- [ ] Implement file saving with unique names
- [ ] Add file size validation (10MB max)
- [ ] Add file type validation (PDF, PNG, JPG, DOCX, TXT)
- [ ] Implement file deletion

### 2.4 Backend: Content API Routes
- [ ] `POST /api/spaces/:id/items` - Save message
- [ ] `POST /api/spaces/:id/upload` - Upload file
- [ ] `GET /api/spaces/:id/items` - List items
- [ ] `DELETE /api/spaces/:id/items/:itemId` - Delete item
- [ ] Add multipart/form-data handling for uploads

### 2.5 Frontend: Add Content Interface
- [ ] Create `frontend/src/components/AddContentModal.tsx`
- [ ] Add tabs for "Message" and "File"
- [ ] Message tab: textarea for content, input for notes
- [ ] File tab: file upload input, input for notes
- [ ] Call appropriate API based on tab
- [ ] Show upload progress for files

### 2.6 Frontend: Items List
- [ ] Display list of items in Space Detail page
- [ ] Show item type icon (message/file)
- [ ] Show content preview (first 100 chars)
- [ ] Show date saved
- [ ] Add delete button per item
- [ ] Add pagination controls

## Phase 3: Vector Search (Week 3)

### 3.1 Backend: Install Dependencies
- [ ] Add `faiss-cpu` to requirements.txt
- [ ] Add `sentence-transformers` to requirements.txt
- [ ] Install dependencies

### 3.2 Backend: EmbeddingGenerator Service
- [ ] Create `backend/services/embedding_generator.py`
- [ ] Initialize sentence transformer model
- [ ] Implement `generate_embedding(text)`
- [ ] Implement `generate_batch_embeddings(texts)`
- [ ] Add caching for embeddings

### 3.3 Backend: VectorStore Service
- [ ] Create `backend/services/vector_store.py`
- [ ] Initialize FAISS index
- [ ] Implement `add_embedding(item_id, embedding, metadata)`
- [ ] Implement `search(query_embedding, space_id, top_k)`
- [ ] Implement `delete_embedding(item_id)`
- [ ] Save/load FAISS index to disk

### 3.4 Backend: Embedding Generation on Save
- [ ] Update ContentManager to generate embeddings
- [ ] Generate embedding when saving message
- [ ] Generate embedding when saving file (after text extraction)
- [ ] Store embedding in VectorStore
- [ ] Link embedding_id to SpaceItem

### 3.5 Backend: FileProcessor Service
- [ ] Create `backend/services/file_processor.py`
- [ ] Install `pdfplumber` dependency
- [ ] Implement `process_pdf(file_path)`
- [ ] Implement `extract_text(file)`
- [ ] Handle errors gracefully
- [ ] Return extracted text

### 3.6 Backend: File Processing Pipeline
- [ ] Update save_file to extract text from PDFs
- [ ] Store extracted text in SpaceItem.content
- [ ] Generate embedding from extracted text
- [ ] Handle processing errors

## Phase 4: Query Engine (Week 4)

### 4.1 Backend: QueryEngine Service
- [ ] Create `backend/services/query_engine.py`
- [ ] Implement `query(space_id, question)`
- [ ] Generate embedding for question
- [ ] Search VectorStore for relevant items
- [ ] Retrieve top 5 relevant SpaceItems
- [ ] Build context from retrieved items
- [ ] Send to LLM with RAG prompt
- [ ] Parse and return answer with sources

### 4.2 Backend: Query Data Model
- [ ] Create `Query` model in `backend/models/data_models.py`
- [ ] Add database schema for queries table
- [ ] Store question, answer, sources, timestamp

### 4.3 Backend: Query API Routes
- [ ] `POST /api/spaces/:id/query` - Ask question
- [ ] `GET /api/spaces/:id/queries` - Get query history
- [ ] Add request validation
- [ ] Add rate limiting (10 queries/minute)

### 4.4 Frontend: Query Interface
- [ ] Create `frontend/src/components/QueryInterface.tsx`
- [ ] Add text input for question
- [ ] Add submit button
- [ ] Show loading state while querying
- [ ] Display answer with formatting
- [ ] Display source references with links

### 4.5 Frontend: Query History
- [ ] Display list of past queries below interface
- [ ] Show question and answer
- [ ] Show timestamp
- [ ] Make clickable to view full details
- [ ] Add pagination

### 4.6 Frontend: Source References
- [ ] Create `frontend/src/components/SourceCard.tsx`
- [ ] Display source item preview
- [ ] Link to full item content
- [ ] Show relevance score (optional)

## Phase 5: Polish & Features (Week 5)

### 5.1 Backend: OCR for Images
- [ ] Install `pytesseract` and Tesseract
- [ ] Implement `process_image(file_path)` in FileProcessor
- [ ] Add OCR support for PNG, JPG files
- [ ] Handle OCR errors

### 5.2 Backend: Document Processing
- [ ] Install `python-docx` dependency
- [ ] Implement `process_document(file_path)` for DOCX
- [ ] Add support for TXT files
- [ ] Update file processing pipeline

### 5.3 Frontend: Search Across Spaces
- [ ] Add global search bar in Spaces List page
- [ ] Call API to search all spaces
- [ ] Display results grouped by space
- [ ] Link to source items

### 5.4 Frontend: UI/UX Improvements
- [ ] Add loading skeletons
- [ ] Add empty states with helpful messages
- [ ] Add error boundaries
- [ ] Improve mobile responsiveness
- [ ] Add keyboard shortcuts

### 5.5 Backend: Performance Optimization
- [ ] Add database indexes
- [ ] Optimize vector search
- [ ] Add caching for frequent queries
- [ ] Batch process embeddings

### 5.6 Testing
- [ ] Write unit tests for all services
- [ ] Write integration tests for RAG pipeline
- [ ] Write API endpoint tests
- [ ] Test file upload edge cases
- [ ] Test query accuracy

### 5.7 Documentation
- [ ] Update README with Spaces feature
- [ ] Add API documentation
- [ ] Add user guide
- [ ] Add developer setup guide

## Optional Enhancements

### 6.1 Conversation Import
- [ ]* Add "Import Conversation" feature
- [ ]* Parse WhatsApp/Telegram export format
- [ ]* Bulk save messages to space

### 6.2 Smart Summaries
- [ ]* Auto-generate summary for each space
- [ ]* Show summary on space card
- [ ]* Update summary when content changes

### 6.3 Export/Backup
- [ ]* Add "Export Space" feature
- [ ]* Generate JSON export of all items
- [ ]* Add "Import Space" feature

### 6.4 Advanced Search
- [ ]* Add filters (date range, type)
- [ ]* Add sorting options
- [ ]* Add full-text search (non-AI)
