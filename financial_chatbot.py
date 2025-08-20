"""
Financial Policy Chatbot
A RAG-based chatbot that answers questions about financial policy documents
with conversation memory and context awareness.
"""

import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

class FinancialPolicyChatbot:
    def __init__(self):
        """Initialize the chatbot with ChromaDB and OpenAI clients."""
        self.CHROMA_PATH = r"chroma_db"
        self.chroma_client = chromadb.PersistentClient(path=self.CHROMA_PATH)
        
        try:
            self.collection = self.chroma_client.get_collection(name="financial_policy")
        except Exception as e:
            print("Error: Database not found. Please run 'python fill_db.py' first to set up the database.")
            exit(1)
        
        # Initialize OpenAI client
        self.openai_client = OpenAI()
        
        # Conversation memory - stores recent conversation history
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history_length = 10  # Keep last 10 exchanges
        
        print("Financial Policy Chatbot initialized successfully!")
        print("Database contains", self.collection.count(), "document chunks.")
    
    def search_relevant_content(self, query: str, n_results: int = 3) -> Dict[str, Any]:
        """
        Search for relevant content in the financial policy document.
        
        Args:
            query: User's question
            n_results: Number of relevant chunks to retrieve
            
        Returns:
            Dictionary containing relevant documents and metadata
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
    
    def build_context_prompt(self, query: str, search_results: Dict[str, Any]) -> str:
        """
        Build a comprehensive prompt including conversation history and retrieved content.
        
        Args:
            query: Current user question
            search_results: Relevant documents from vector search
            
        Returns:
            Formatted system prompt with context
        """
        # Build conversation context
        conversation_context = ""
        if self.conversation_history:
            conversation_context = "\n\nRecent conversation history:\n"
            for i, exchange in enumerate(self.conversation_history[-5:], 1):  # Last 5 exchanges
                conversation_context += f"{i}. User: {exchange['user']}\n"
                conversation_context += f"   Assistant: {exchange['assistant']}\n"
        
        # Build document context
        document_context = ""
        if search_results['documents'] and search_results['documents'][0]:
            document_context = "\n\nRelevant information from the financial policy document:\n"
            for i, (doc, metadata) in enumerate(zip(search_results['documents'][0], search_results['metadatas'][0]), 1):
                # Use actual_page if available, otherwise fall back to page + 1
                page_num = metadata.get('actual_page')
                if page_num is None:
                    page_num = metadata.get('page', 0) + 1
                
                page_source = metadata.get('page_source', 'pdf_metadata')
                page_info = f" (Page {page_num})" if page_num else ""
                
                # Add indicator if page was extracted from footer
                if page_source == 'extracted_from_footer':
                    page_info += " ✓"
                
                document_context += f"\n--- Excerpt {i}{page_info} ---\n{doc}\n"
        
        system_prompt = f"""
You are a helpful financial policy assistant. You answer questions about financial policies, budgets, debt, infrastructure, and related topics based on the provided financial policy document.

IMPORTANT GUIDELINES:
1. Only use information from the provided document excerpts below
2. Do not use your general knowledge about finance or policies
3. If the information is not in the provided excerpts, say "I don't have that information in the policy document"
4. Reference page numbers when available
5. Consider the conversation history to provide contextual responses
6. Be precise and cite specific sections when possible

{conversation_context}

{document_context}

Current question: {query}

Please provide a clear, helpful answer based on the financial policy document provided above.
"""
        return system_prompt
    
    def get_response(self, user_query: str) -> str:
        """
        Get a response from the chatbot for the user's query.
        
        Args:
            user_query: User's question
            
        Returns:
            Chatbot's response
        """
        # Search for relevant content
        search_results = self.search_relevant_content(user_query, n_results=3)
        
        # Build context-aware prompt
        system_prompt = self.build_context_prompt(user_query, search_results)
        
        # Get response from OpenAI
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1,  # Low temperature for more consistent responses
                max_tokens=1000
            )
            
            assistant_response = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({
                "user": user_query,
                "assistant": assistant_response
            })
            
            # Keep history within limit
            if len(self.conversation_history) > self.max_history_length:
                self.conversation_history = self.conversation_history[-self.max_history_length:]
            
            return assistant_response
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def show_help(self):
        """Display help information for using the chatbot."""
        help_text = """
📋 FINANCIAL POLICY CHATBOT HELP

This chatbot can answer questions about the financial policy document.

EXAMPLE QUESTIONS:
• What is the total budget for this year?
• What are the main debt obligations?
• How much is allocated for infrastructure?
• What are the revenue sources?
• What about education funding?
• Tell me about capital expenditures

FEATURES:
•  Conversation memory - remembers recent questions
•  Page references - shows where information comes from
•  Context-aware - understands follow-up questions

COMMANDS:
• Type 'help' - Show this help message
• Type 'history' - Show recent conversation
• Type 'exit' or 'quit' - End the conversation

Just ask your question in plain English!
"""
        print(help_text)
    
    def show_history(self):
        """Display recent conversation history."""
        if not self.conversation_history:
            print("No conversation history yet.")
            return
        
        print("\n📝 RECENT CONVERSATION HISTORY:")
        print("=" * 50)
        for i, exchange in enumerate(self.conversation_history, 1):
            print(f"\n{i}.  User: {exchange['user']}")
            print(f"    Bot: {exchange['assistant'][:100]}{'...' if len(exchange['assistant']) > 100 else ''}")
        print("=" * 50)
    
    def run(self):
        """Run the interactive chatbot."""
        print("\n" + "="*60)
        print("🏛️  FINANCIAL POLICY CHATBOT")
        print("="*60)
        print("Ask me anything about the financial policy document!")
        print("Type 'help' for guidance, 'history' for recent chat, or 'exit' to quit.")
        print("-"*60)
        
        while True:
            try:
                user_input = input("\n💬 Your question: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Thank you for using the Financial Policy Chatbot!")
                    break
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                elif user_input.lower() == 'history':
                    self.show_history()
                    continue
                
                # Get and display response
                print("\n Searching policy document...")
                response = self.get_response(user_input)
                print(f"\n Response:\n{response}")
                print("-"*60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n Error: {str(e)}")


def main():
    """Main function to run the chatbot."""
    try:
        # Check if OpenAI API key is set
        if not os.getenv('OPENAI_API_KEY'):
            print(" Error: OPENAI_API_KEY not found in .env file")
            print("Please add your OpenAI API key to the .env file")
            return
        
        # Initialize and run chatbot
        chatbot = FinancialPolicyChatbot()
        chatbot.run()
        
    except Exception as e:
        print(f" Error starting chatbot: {str(e)}")
        print("Make sure you've run 'python fill_db.py' first to set up the database.")


if __name__ == "__main__":
    main()
