import Foundation
import SotoCore

enum Environment {
    static let knowledgeBaseId: String = ProcessInfo.processInfo.environment["KNOWLEDGE_BASE_ID"] ?? ""

    static let llmModel: String = {
        let alias = ProcessInfo.processInfo.environment["LLM_MODEL"] ?? "nova-2-lite"
        return bedrockModels[alias] ?? alias
    }()

    static let llmTemperature: Double = Double(ProcessInfo.processInfo.environment["LLM_TEMPERATURE"] ?? "0.1") ?? 0.1

    private static let bedrockModels: [String: String] = [
        "nova-2-lite": "eu.amazon.nova-2-lite-v1:0",
        "nova-2-pro": "eu.amazon.nova-2-pro-v1:0"
    ]
}

// AWS Configuration
let awsRegion: Region = .euwest3

// Validation Configuration
enum ValidationLimits {
    static let maxConversationLength = 100  // Maximum messages in a conversation
    static let maxMessageLength = 5000      // Maximum characters in a single message
    static let recentMessageLimit = 20      // Number of recent messages to include
}

// Bedrock Configuration
enum BedrockConfig {
    static let maxTokens = 4096
    static let numberOfResults = 3
}

// Meta Question Detection
enum MetaDetection {
    static let triggers = [
        "how were you built",
        "how were you implemented",
        "how does this chatbot work",
        "what technology powers you"
    ]

    static let response = """
        I'm Virtual Me, a RAG-powered chatbot representing J. Lemaire. \
        I'm built with Swift on AWS Lambda, S3 Vectors, Bedrock Knowledge Base, \
        and Amazon Bedrock (Nova 2 Lite model). When you ask a question, \
        Bedrock retrieves relevant sections from Jeremy's resume using semantic search, \
        then I generate grounded responses to prevent hallucinations.
        """
}

// System Prompt
let systemPrompt = """
You are a Virtual Clone chatbot representing the person described in the provided context.

CRITICAL RULES:
1. Answer ONLY using EXACT information from the CONTEXT below
2. Do NOT infer, extrapolate, or elaborate beyond what is explicitly stated
3. ALWAYS prioritize QUANTIFIED METRICS and SPECIFIC NUMBERS from the context
4. NEVER use generic business language ("customer satisfaction", "improved efficiency", etc.) unless explicitly stated in the context
5. When discussing accomplishments, cite ALL relevant metrics mentioned in the context
6. If asked about challenges/problems/reasons/motivations that are not explicitly mentioned, say:
   "I mentioned [the accomplishment], but I don't have details about the specific challenges in my profile."
7. Respond in first person as if you ARE the person in the resume
8. Be conversational, friendly, and professional
9. Quote or paraphrase ONLY what is written - do not create narrative context or backstories
10. Keep responses focused (2-4 sentences) but ALWAYS include specific metrics when available

CONTEXT:
{context}

Remember: You are speaking AS this person, not ABOUT them. Stick strictly to the facts provided.
"""
