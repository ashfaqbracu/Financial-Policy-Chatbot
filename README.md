# Financial Policy Chatbot

An AI-powered chatbot that answers questions about financial policy documents using Retrieval Augmented Generation (RAG) technology with accurate page number tracking and conversation memory.

## Features

- 📄 **Document Processing**: Extracts and processes information from PDF policy documents
- 🔍 **Intelligent Search**: Uses ChromaDB for fast, semantic search of document content
- 🧠 **Conversation Memory**: Remembers recent conversation context for natural follow-up questions
- 📋 **Accurate Citations**: Precise page number tracking with source attribution
- 💬 **Natural Language**: Understands questions in plain English
- ✓ **Source Verification**: Shows whether page numbers were extracted from document footers

## Quick Start

### 1. Prerequisites
- Python 3.8 or higher
- OpenAI API key

### 2. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Add your OpenAI API key to .env file
# Replace [YOUR API KEY HERE] with your actual key
```

### 3. Initialize Database
```bash
python fill_db.py
```

### 4. Run Chatbot
```bash
python financial_chatbot.py
```

## Project Structure

```
RAG/
├── .env                    # Environment variables (OpenAI API key)
├── requirements.txt        # Python dependencies
├── policy.pdf             # Financial policy document
├── fill_db.py             # Database setup script
├── financial_chatbot.py   # Main chatbot application
├── chroma_db/             # ChromaDB database (auto-created)
├── venv/                  # Virtual environment (optional)
├── README.md              # This file
└── QUICKSTART.md          # Quick setup guide
```

## Usage Examples

### Interactive Chat
```
💬 Your question: What is the total budget for this year?
📋 Response: According to the policy document on page 7, the total budget...

💬 Your question: What about debt obligations?
📋 Response: Regarding debt obligations, page 8 shows that...

💬 Your question: How do these compare?
📋 Response: Comparing the budget and debt figures from the previous discussion...
```

### Special Commands
- `help` - Show detailed help information
- `history` - Display recent conversation history
- `exit` or `quit` - End the conversation

## Key Features Explained

### 🧠 **Conversation Memory**
The chatbot remembers your recent questions and answers, allowing for natural follow-up conversations:
- Tracks last 10 conversation exchanges
- Uses context for better responses
- Understands references like "What about that?" or "Tell me more"

### 📋 **Accurate Page Numbers**
Advanced page number extraction ensures reliable citations:
- **Footer Extraction**: Parses page numbers from document footers (marked with ✓)
- **PDF Metadata**: Falls back to PDF page information when needed
- **Source Attribution**: Shows exactly where information comes from

### 🔍 **Smart Search**
Vector-based semantic search finds relevant content even when you don't use exact document terms:
- Understands intent: "How much debt?" finds "outstanding obligations"
- Context-aware: Retrieves multiple relevant sections
- Ranked results: Shows most relevant information first

## Technical Details

### Architecture
1. **Document Processing**: PDF text extraction and intelligent chunking
2. **Vector Database**: ChromaDB for semantic search with embeddings
3. **AI Generation**: OpenAI GPT-4o for contextual responses
4. **Memory System**: Conversation history management

### Page Number Accuracy
- Handles footer format: "2005-06 Budget Paper No. 3 **9** Financial Policy..."
- Maps PDF pages to actual document pages correctly
- Provides transparency about extraction method

### Configuration
- **Chunk Size**: 1000 characters with 200 character overlap
- **Search Results**: Top 3 most relevant chunks per query
- **Memory**: Last 10 conversation exchanges
- **Model**: GPT-4o with temperature 0.1 for consistency

## Troubleshooting

### Common Issues

**"Database not found" error**:
```bash
python fill_db.py  # Run this first
```

**OpenAI API errors**:
- Check your API key in `.env` file
- Ensure sufficient API credits

**PDF loading errors**:
- Verify `policy.pdf` exists in project directory
- Check file isn't corrupted or password-protected

### Getting Help
1. Check error messages carefully
2. Ensure virtual environment is activated
3. Verify all dependencies are installed: `pip install -r requirements.txt`
4. Confirm `.env` file configuration

## Dependencies

- **chromadb**: Vector database for semantic search
- **openai**: OpenAI API client for GPT responses  
- **python-dotenv**: Environment variable management
- **langchain_community**: Document loaders and processing
- **langchain_text_splitters**: Text chunking utilities
- **pypdf**: PDF processing and extraction

## Example Questions

Try asking questions like:
- "What is the total budget allocation?"
- "What are the main debt obligations?"
- "How much is allocated for infrastructure?"
- "What are the revenue sources?"
- "Tell me about the balanced budget policy"
- "What's the government's debt strategy?"

The chatbot understands context, so you can follow up with:
- "What about education funding?"
- "How does this compare to last year?"
- "Tell me more about that"

## License

This project is provided for educational and demonstration purposes.
