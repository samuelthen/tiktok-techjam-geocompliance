"""
OpenAI-powered evidence reranking utility
Reranks evidence chunks by relevance using OpenAI GPT
"""

import openai
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
import json

load_dotenv()

class EvidenceReranker:
    def __init__(self):
        self.api_key = os.getenv('OPEN_AI_KEY')
        if self.api_key:
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None
            
    def rerank_evidence(self, query: str, evidence_chunks: List[Dict], max_chunks: int = 5) -> List[Dict]:
        """
        Rerank evidence chunks using OpenAI for relevance to the compliance query
        """
        if not self.client or not evidence_chunks:
            return evidence_chunks[:max_chunks]
            
        try:
            # Prepare evidence for ranking
            evidence_text = []
            for i, chunk in enumerate(evidence_chunks):
                evidence_text.append(f"Evidence {i+1}: {chunk.get('content', '')[:500]}...")
            
            ranking_prompt = f"""You are an expert compliance analyst. Rank the following evidence chunks by their relevance to this TikTok feature compliance query: "{query}"

Consider:
1. Direct regulatory applicability
2. Specificity to the feature described
3. Legal precedence and importance
4. Clarity of compliance requirements

Evidence to rank:
{chr(10).join(evidence_text)}

Respond with only a JSON array of numbers representing the ranking order (most relevant first).
For example: [3, 1, 5, 2, 4] means Evidence 3 is most relevant, then Evidence 1, etc.
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": ranking_prompt}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            ranking_text = response.choices[0].message.content.strip()
            
            # Parse the ranking
            try:
                ranking = json.loads(ranking_text)
                
                # Reorder evidence based on ranking
                reranked_evidence = []
                for rank in ranking[:max_chunks]:
                    if 1 <= rank <= len(evidence_chunks):
                        chunk = evidence_chunks[rank - 1].copy()
                        chunk['ai_relevance_score'] = len(ranking) - ranking.index(rank)
                        reranked_evidence.append(chunk)
                
                return reranked_evidence
                
            except (json.JSONDecodeError, IndexError):
                print("Failed to parse ranking, using original order")
                return evidence_chunks[:max_chunks]
                
        except Exception as e:
            print(f"Reranking failed: {e}")
            return evidence_chunks[:max_chunks]
    
    def get_relevance_explanation(self, query: str, evidence_chunk: Dict) -> str:
        """
        Get an AI explanation of why this evidence is relevant
        """
        if not self.client:
            return "Relevance assessment not available"
            
        try:
            explanation_prompt = f"""Explain in 1-2 sentences why this evidence is relevant to the TikTok compliance query: "{query}"

Evidence: {evidence_chunk.get('content', '')[:300]}

Be specific about which regulations or compliance requirements it addresses."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": explanation_prompt}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Explanation generation failed: {e}")
            return f"Related to {evidence_chunk.get('source', 'compliance requirements')}"