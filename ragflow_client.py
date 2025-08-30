from ragflow_sdk import RAGFlow
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class RAGFlowClient:
    def __init__(self):
        self.api_key = os.getenv('RAGFLOW_API_KEY')
        self.base_url = os.getenv('RAGFLOW_BASE_URL', 'http://localhost')
        self.assistant_id = os.getenv('RAGFLOW_ASSISTANT_ID')
        self.rag_client = None
        self.assistant = None
        
        try:
            # Initialize RAGFlow client
            self.rag_client = RAGFlow(api_key=self.api_key, base_url=self.base_url)
            
            # Try to get the existing assistant by ID
            chats = self.rag_client.list_chats(id=self.assistant_id)
            if chats:
                self.assistant = chats[0]
                print(f"✅ Connected to RAGFlow assistant: {self.assistant.name}")
            else:
                print(f"⚠️  Assistant with ID {self.assistant_id} not found")
                
        except Exception as e:
            print(f"⚠️  RAGFlow connection failed: {e}")
            self.rag_client = None
            self.assistant = None
    
    def create_chat_session(self) -> Optional[str]:
        """Create a new chat session using RAGFlow SDK"""
        if not self.assistant:
            return None
            
        try:
            session_name = f"Compliance Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            session = self.assistant.create_session(name=session_name)
            print(f"✅ Created session: {session.id}")
            return session
        except Exception as e:
            print(f"Error creating chat session: {e}")
            return None
    
    def analyze_feature(self, feature_description: str, session = None) -> Dict[str, Any]:
        """Analyze a feature for compliance using the RAGFlow assistant"""
        
        print(f"🔍 Analyzing feature: {feature_description[:100]}...")
        
        # Try RAGFlow integration first
        if not session:
            print("📝 Creating new chat session...")
            session = self.create_chat_session()
        
        # If RAGFlow connection fails, return error
        if not session:
            print("❌ No session available")
            return {
                'answer': 'Error: Could not create RAGFlow session',
                'evidence': [],
                'session_id': 'no_session',
                'feature_input': feature_description,
                'timestamp': datetime.now().isoformat(),
                'mode': 'error'
            }
        
        try:
            compliance_prompt = f"""Analyze this TikTok feature for geo-specific compliance needs: {feature_description}

IMPORTANT: Only flag features that require geo-specific logic due to LEGAL/REGULATORY requirements, NOT business decisions.

Examples:
✅ LEGAL: "Age gates for Indonesia Child Protection Law" - requires compliance logic
✅ LEGAL: "Location-based content blocking for France copyright rules" - requires compliance logic  
❌ BUSINESS: "Geofence rollout in US for market testing" - business decision, not legal requirement
❓ UNCLEAR: "Feature disabled in KR" without specifying legal reason - needs human review

ALWAYS respond in this exact format:
CLASSIFICATION: [YES/NO/UNCERTAIN]
CONFIDENCE: [1-10]
REASONING: [detailed explanation - distinguish between legal compliance vs business decisions]  
REGULATIONS: [specific laws that apply, or "None identified" if business-driven]
EVIDENCE: [quote relevant chunks]

Focus on: DSA, California Kids Act, Florida/Utah Minor Protection, NCMEC reporting requirements, GDPR, data localization laws."""

            print(f"📤 Sending prompt to RAGFlow session {session.id}...")
            print(f"Prompt preview: {compliance_prompt[:200]}...")

            # Use streaming mode as it works better with RAGFlow SDK
            response_iter = session.ask(compliance_prompt, stream=True)
            
            print("📥 Receiving streaming response...")
            
            # Collect the full response from the generator
            full_content = ""
            evidence_chunks = []
            last_message = None
            message_count = 0
            
            for message in response_iter:
                message_count += 1
                last_message = message
                print(f"📨 Message #{message_count}: {type(message)}")
                
                # Debug message type
                if hasattr(message, 'content'):
                    full_content = message.content  # This gets the complete content
                    print(f"✅ Content length: {len(full_content)} chars")
                    if len(full_content) < 200:
                        print(f"Content preview: {full_content}")
                else:
                    print(f"⚠️  Unexpected message type: {type(message)}")
                    print(f"Message attributes: {dir(message)}")
                    print(f"Message: {message}")
                    continue
                
            print(f"🏁 Finished processing {message_count} messages")
            answer = full_content.strip()
            print(f"📝 Final answer length: {len(answer)} chars")
            
            # Process reference chunks from the final message
            if last_message and hasattr(last_message, 'reference') and last_message.reference:
                for ref in last_message.reference:
                    # Handle both dict and object formats for references
                    if isinstance(ref, dict):
                        evidence_chunks.append({
                            'content': ref.get('content', ''),
                            'source': ref.get('document_name', 'Unknown'),
                            'chunk_id': ref.get('id', ''),
                            'similarity_score': ref.get('similarity', 0.0)
                        })
                    else:
                        # Object format
                        evidence_chunks.append({
                            'content': getattr(ref, 'content', ''),
                            'source': getattr(ref, 'document_name', 'Unknown'),
                            'chunk_id': getattr(ref, 'id', ''),
                            'similarity_score': getattr(ref, 'similarity', 0.0)
                        })
            
            # If we got an empty response, return error
            if not answer:
                print("⚠️  RAGFlow returned empty response")
                return {
                    'answer': 'Error: RAGFlow returned empty response',
                    'evidence': [],
                    'session_id': session.id,
                    'feature_input': feature_description,
                    'timestamp': datetime.now().isoformat(),
                    'mode': 'error'
                }
            
            return {
                'answer': answer,
                'evidence': evidence_chunks,
                'session_id': session.id,
                'feature_input': feature_description,
                'timestamp': datetime.now().isoformat(),
                'mode': 'ragflow'
            }
            
        except Exception as e:
            print(f"❌ RAGFlow SDK error: {e}")
            return {
                'answer': 'Error: RAGFlow connection failed',
                'evidence': [],
                'session_id': 'error',
                'feature_input': feature_description,
                'timestamp': datetime.now().isoformat(),
                'mode': 'error'
            }
    
    
    def process_compliance_response(self, response_text: str, evidence_chunks: List[Dict]) -> Dict[str, Any]:
        """Parse structured response from LLM"""
        lines = response_text.split('\n')
        parsed = {
            'classification': 'UNCERTAIN',
            'confidence': 'N/A',
            'reasoning': '',
            'regulations': ''
        }
        
        current_section = None
        content_buffer = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('CLASSIFICATION:'):
                if current_section and content_buffer:
                    parsed[current_section] = ' '.join(content_buffer).strip()
                current_section = 'classification'
                parsed['classification'] = line.split(':', 1)[1].strip()
                content_buffer = []
            elif line.startswith('CONFIDENCE:'):
                if current_section and content_buffer:
                    parsed[current_section] = ' '.join(content_buffer).strip()
                current_section = 'confidence'
                parsed['confidence'] = line.split(':', 1)[1].strip()
                content_buffer = []
            elif line.startswith('REASONING:'):
                if current_section and content_buffer:
                    parsed[current_section] = ' '.join(content_buffer).strip()
                current_section = 'reasoning'
                parsed['reasoning'] = line.split(':', 1)[1].strip()
                content_buffer = []
            elif line.startswith('REGULATIONS:'):
                if current_section and content_buffer:
                    parsed[current_section] = ' '.join(content_buffer).strip()
                current_section = 'regulations'
                parsed['regulations'] = line.split(':', 1)[1].strip()
                content_buffer = []
            elif line.startswith('EVIDENCE:'):
                if current_section and content_buffer:
                    parsed[current_section] = ' '.join(content_buffer).strip()
                current_section = None
                content_buffer = []
            elif current_section and line:
                content_buffer.append(line)
        
        # Handle last section
        if current_section and content_buffer:
            parsed[current_section] = ' '.join(content_buffer).strip()
        
        # Create audit record
        audit_record = {
            'timestamp': datetime.now().isoformat(),
            'classification': parsed['classification'],
            'confidence_score': parsed['confidence'],
            'reasoning': parsed['reasoning'],
            'applicable_regulations': parsed['regulations'],
            'evidence_sources': [
                {
                    'regulation_document': chunk['source'],
                    'relevant_text': chunk['content'][:300] + ('...' if len(chunk['content']) > 300 else ''),
                    'similarity_score': chunk['similarity_score'],
                    'chunk_reference': chunk['chunk_id']
                }
                for chunk in evidence_chunks
            ],
            'total_evidence_chunks': len(evidence_chunks)
        }
        
        return audit_record