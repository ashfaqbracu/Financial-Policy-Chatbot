from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import os
import re

def extract_page_number_from_text(text):
    """
    Extract page number from footer text like '2005-06 Budget Paper No. 3 9 Financial Policy...'
    where the page number (9) appears after 'Budget Paper No. 3'
    """
    # Pattern to match the footer format and extract the page number
    # Made more specific to avoid false positives
    patterns = [
        r'2005-06 Budget Paper No\. \d+\s+(\d+)\s+Financial Policy',  # Most specific pattern
        r'Budget Paper No\. \d+\s+(\d+)\s+Financial Policy',         # Main pattern
        r'Budget.*?Paper.*?(\d+)\s+Financial Policy.*?Statement',     # Alternative pattern
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Debug: print what was found
            page_num = int(match.group(1))
            print(f"  ✓ Found page {page_num} using pattern: {pattern}")
            return page_num
    
    return None

def enhance_metadata_with_page_numbers(chunks):
    """
    Enhance chunk metadata by extracting actual page numbers from document text
    """
    enhanced_chunks = []
    
    print(f"Processing {len(chunks)} chunks for page number extraction...")
    
    for i, chunk in enumerate(chunks):
        # Get the raw text content
        text_content = chunk.page_content
        
        print(f"Chunk {i}: PDF page {chunk.metadata.get('page', 'unknown')}")
        
        # Try to extract page number from the text
        extracted_page = extract_page_number_from_text(text_content)
        
        # Copy original metadata
        enhanced_metadata = chunk.metadata.copy()
        
        # Add extracted page number if found
        if extracted_page is not None:
            enhanced_metadata['actual_page'] = extracted_page
            enhanced_metadata['page_source'] = 'extracted_from_footer'
            print(f"  → Using extracted page: {extracted_page}")
        else:
            # For this document, PDF pages 0-5 correspond to document pages 5-10
            # So PDF page 0 = document page 5, PDF page 1 = document page 6, etc.
            pdf_page = chunk.metadata.get('page', 0)
            actual_doc_page = pdf_page + 5  # Adjust based on document's starting page
            enhanced_metadata['actual_page'] = actual_doc_page
            enhanced_metadata['page_source'] = 'pdf_metadata'
            print(f"  → Using PDF metadata page {pdf_page} → document page: {actual_doc_page}")
        
        # Create new chunk with enhanced metadata
        enhanced_chunk = type(chunk)(
            page_content=chunk.page_content,
            metadata=enhanced_metadata
        )
        enhanced_chunks.append(enhanced_chunk)
    
    return enhanced_chunks

# setting the environment

PDF_PATH = r"policy.pdf"
CHROMA_PATH = r"chroma_db"

# Check if PDF file exists
if not os.path.exists(PDF_PATH):
    print(f"Error: {PDF_PATH} not found. Please ensure the policy.pdf file is in the current directory.")
    exit(1)

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

collection = chroma_client.get_or_create_collection(name="financial_policy")

# loading the document

print("Loading financial policy document...")
loader = PyPDFLoader(PDF_PATH)

raw_documents = loader.load()

print(f"Loaded {len(raw_documents)} pages from the policy document.")

# splitting the document

print("Splitting document into chunks...")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Larger chunks for financial documents
    chunk_overlap=200,  # More overlap to maintain context
    length_function=len,
    is_separator_regex=False,
)

chunks = text_splitter.split_documents(raw_documents)

print(f"Created {len(chunks)} text chunks.")

# Enhance chunks with better page number extraction
print("Enhancing metadata with accurate page numbers...")
enhanced_chunks = enhance_metadata_with_page_numbers(chunks)

# preparing to be added in chromadb

print("Preparing documents for ChromaDB...")
documents = []
metadata = []
ids = []

for i, chunk in enumerate(enhanced_chunks):
    documents.append(chunk.page_content)
    ids.append(f"policy_chunk_{i}")
    
    # Enhanced metadata with accurate page info and chunk number
    chunk_metadata = chunk.metadata.copy()
    chunk_metadata['chunk_id'] = i
    chunk_metadata['document_type'] = 'financial_policy'
    metadata.append(chunk_metadata)

# adding to chromadb

print("Adding documents to ChromaDB...")
collection.upsert(
    documents=documents,
    metadatas=metadata,
    ids=ids
)

print(f"Successfully added {len(documents)} chunks to the database!")

# Display page number extraction summary
print("\n📄 Page Number Extraction Summary:")
page_counts = {}
for chunk_meta in metadata:
    page_num = chunk_meta.get('actual_page', 'unknown')
    page_source = chunk_meta.get('page_source', 'unknown')
    key = f"Page {page_num} ({page_source})"
    page_counts[key] = page_counts.get(key, 0) + 1

for page_info, count in sorted(page_counts.items()):
    print(f"  {page_info}: {count} chunks")

print("Database setup complete. You can now run the chatbot with 'python financial_chatbot.py'")