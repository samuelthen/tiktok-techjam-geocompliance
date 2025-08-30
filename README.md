# TikTok Geo-Compliance Co-pilot

AI-powered geo-specific regulatory compliance analysis system for TikTok features.

## Overview

This prototype system utilizes LLM capabilities to flag features that require geo-specific compliance logic, turning regulatory detection from a blind spot into a traceable, auditable output.

**Key Features:**
- Automated compliance analysis for TikTok features
- Distinguishes between legal compliance requirements vs business decisions
- Evidence-based reasoning with regulatory document references
- Clean web interface for feature analysis
- Audit-ready transparency with detailed reporting

## Problem Statement

As TikTok operates globally, every product feature must dynamically satisfy dozens of geographic regulations – from Brazil's data localization to GDPR. This system helps answer:

- "Does this feature require dedicated logic to comply with region-specific legal obligations?"
- "How many features have we rolled out to ensure compliance with this regulation?"

## Quick Start

### Prerequisites

- Python 3.8+
- RAGFlow instance with regulatory documents loaded
- OpenAI API access (optional, for reranking)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/samuelthen/tiktok-techjam-geocompliance
   cd tiktok-techjam-geocompliance
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Create a `.env` file in the project root:
   ```env
   # RAGFlow Configuration (Required)
   RAGFLOW_API_KEY=your_ragflow_api_key
   RAGFLOW_BASE_URL=http://your-ragflow-instance:9380
   RAGFLOW_ASSISTANT_ID=your_assistant_id
   
   # OpenAI Configuration (Optional - for evidence reranking)
   OPENAI_API_KEY=your_openai_api_key
   ```

4. **Run the application**
   ```bash
   streamlit run fixed_tiktok_app.py
   ```

5. **Access the app**
   
   Open your browser to `http://localhost:8501`

## Configuration Details

### RAGFlow Setup

This system requires a RAGFlow instance with regulatory compliance documents loaded. The RAGFlow assistant should be trained on:

- Digital Services Act (DSA)
- California Kids Act / SB976
- Florida/Utah Minor Protection Laws
- NCMEC reporting requirements
- GDPR
- Data localization laws by region

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `RAGFLOW_API_KEY` | API key for RAGFlow instance | Yes |
| `RAGFLOW_BASE_URL` | Base URL of your RAGFlow deployment | Yes |
| `RAGFLOW_ASSISTANT_ID` | ID of the compliance-trained assistant | Yes |
| `OPENAI_API_KEY` | OpenAI API key for evidence reranking | No |

## Usage

1. **Enter Feature Description**: Describe a TikTok feature in the text input
2. **Click Analyze**: The system will analyze for geo-compliance requirements
3. **Review Results**: 
   - Classification (YES/NO/UNCERTAIN)
   - Confidence score (1-10)
   - Detailed reasoning
   - Applicable regulations
   - Supporting evidence chunks

### Example Inputs

✅ **Requires Compliance Logic:**
- "Feature reads user location to enforce France's copyright rules (download blocking)"
- "Age gates specific to Indonesia's Child Protection Law"

❌ **Business Decision (No Compliance):**
- "Geofences feature rollout in US for market testing"

❓ **Needs Human Review:**
- "Video filter feature available globally except KR" (no legal reason specified)

## System Architecture

```
User Input → Streamlit Frontend → RAGFlow Client → RAGFlow API → LLM Analysis
                    ↓
Evidence Reranker ← RAGFlow Response ← Regulatory Documents
                    ↓
Results Display ← Processed Response ← Confidence Scoring
```

## Files Structure

```
techjam/
├── fixed_tiktok_app.py      # Main Streamlit application
├── ragflow_client.py        # RAGFlow integration client
├── reranking_utils.py       # Evidence reranking utilities
├── requirements.txt         # Python dependencies
├── .env                     # Environment configuration
├── TikTok_logo.svg.png     # Application logo
└── README.md               # This file
```

## Development

### Key Components

1. **RAGFlowClient** (`ragflow_client.py`)
   - Manages RAGFlow API connections
   - Handles compliance analysis prompts
   - Processes structured LLM responses

2. **EvidenceReranker** (`reranking_utils.py`)
   - Re-ranks evidence chunks using OpenAI
   - Improves relevance scoring
   - Optional enhancement for better results

3. **Streamlit App** (`fixed_tiktok_app.py`)
   - User interface and experience
   - TikTok-themed styling
   - Real-time analysis display

### Customization

To adapt for different compliance domains:

1. **Update prompts** in `ragflow_client.py` (lines 71-88)
2. **Modify evidence processing** in `process_compliance_response()`
3. **Adjust UI styling** in the Streamlit app CSS section

## Troubleshooting

### Common Issues

**"RAGFlow connection failed"**
- Verify `RAGFLOW_BASE_URL` is accessible
- Check `RAGFLOW_API_KEY` is valid
- Ensure RAGFlow instance is running

**"Assistant not found"**
- Verify `RAGFLOW_ASSISTANT_ID` exists
- Check assistant has regulatory documents loaded
- Confirm API key has access to the assistant

**Empty or poor responses**
- Ensure regulatory documents are properly indexed
- Check assistant training on compliance topics
- Verify prompt formatting in RAGFlow

### Performance Tips

1. **RAGFlow Optimization**
   - Index regulatory documents with proper chunking
   - Use semantic search for better retrieval
   - Configure appropriate similarity thresholds

2. **Evidence Reranking**
   - Enable OpenAI reranking for improved relevance
   - Adjust `max_chunks` parameter for performance
   - Monitor API usage for cost optimization

## Legal & Compliance Notes

⚠️ **Important**: This is a prototype system for demonstration purposes. For production compliance systems:

- Implement proper audit logging
- Add human review workflows for uncertain cases
- Ensure regulatory document sources are authoritative
- Validate all compliance decisions with legal teams
- Implement proper access controls and data governance

## Contributing

This project was developed for the TikTok Tech Jam hackathon. Features and improvements welcome!

## License

[Specify your license here]
