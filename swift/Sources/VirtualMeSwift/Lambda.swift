import AWSLambdaRuntime
import AWSLambdaEvents
import SotoBedrockAgentRuntime
import SotoBedrockRuntime
import SotoCore
import Foundation
import Logging

// Shared clients (reused across invocations)
let awsClient = AWSClient()
let bedrockAgent = BedrockAgentRuntime(client: awsClient, region: awsRegion)
let bedrock = BedrockRuntime(client: awsClient, region: awsRegion)
let logger = Logger(label: "virtual-me")

@main
struct VirtualMeLambda {
    static func main() async throws {
        let runtime = LambdaRuntime { (event: APIGatewayV2Request, context: LambdaContext) async throws -> APIGatewayV2Response in
            try await handleRequest(event: event)
        }
        try await runtime.run()
    }
}

func handleRequest(event: APIGatewayV2Request) async throws -> APIGatewayV2Response {
    // API Gateway handles OPTIONS requests automatically via CORS configuration
    
    guard let body = event.body else {
        return errorResponse(400, "Missing request body")
    }

    do {
        let request = try JSONDecoder().decode(ChatRequest.self, from: Data(body.utf8))

        guard let question = request.messages.suffix(20).last?.text else {
            return errorResponse(400, "No messages found")
        }

        logger.info("Processing: \(question.prefix(100))...")

        let answer = isMetaQuestion(question) ? getMetaResponse() : try await retrieveAndGenerate(question)

        logger.info("Response: \(answer.count) chars")

        let responseBody = try JSONEncoder().encode(ChatResponse(text: answer))
        return APIGatewayV2Response(
            statusCode: .ok,
            headers: ["Content-Type": "application/json"],
            body: String(data: responseBody, encoding: .utf8)
        )
    } catch {
        logger.error("Error: \(error)")
        return errorResponse(500, "Internal server error")
    }
}

func retrieveAndGenerate(_ question: String) async throws -> String {
    guard !Environment.knowledgeBaseId.isEmpty else {
        throw BedrockError.missingConfig("KNOWLEDGE_BASE_ID")
    }

    // Retrieve context
    let retrieveResponse = try await bedrockAgent.retrieve(.init(
        knowledgeBaseId: Environment.knowledgeBaseId,
        retrievalConfiguration: .init(vectorSearchConfiguration: .init(numberOfResults: 3)),
        retrievalQuery: .init(text: question)
    ))

    let context = retrieveResponse.retrievalResults
        .compactMap { $0.content.text }
        .joined(separator: "\n\n---\n\n")

    logger.info("Retrieved \(retrieveResponse.retrievalResults.count) chunks")

    guard !context.isEmpty else {
        return "I don't have enough information in my knowledge base to answer that question."
    }

    // Generate response
    let prompt = systemPrompt.replacingOccurrences(of: "{context}", with: context)

    logger.info("Model: \(Environment.llmModel)")

    let response = try await bedrock.converse(.init(
        inferenceConfig: .init(maxTokens: maxTokens, temperature: Float(Environment.llmTemperature)),
        messages: [.init(content: [.text("\(prompt)\n\nQuestion: \(question)")], role: .user)],
        modelId: Environment.llmModel
    ))

    guard let content = response.output.message?.content.first,
          case .text(let text) = content else {
        throw BedrockError.noResponse
    }

    return text
}

func isMetaQuestion(_ question: String) -> Bool {
    ["how were you built", "how were you implemented", "how does this chatbot work", "what technology powers you"]
        .contains { question.lowercased().contains($0) }
}

func getMetaResponse() -> String {
    """
    I'm Virtual Me, a RAG-powered chatbot representing J. Lemaire. \
    I'm built with Swift on AWS Lambda, S3 Vectors, Bedrock Knowledge Base, \
    and Amazon Bedrock (Nova 2 Lite model). When you ask a question, \
    Bedrock retrieves relevant sections from Jeremy's resume using semantic search, \
    then I generate grounded responses to prevent hallucinations.
    """
}

func errorResponse(_ code: Int, _ message: String) -> APIGatewayV2Response {
    let body = try? JSONEncoder().encode(ErrorResponse(error: message))
    return APIGatewayV2Response(
        statusCode: .init(code: code),
        headers: ["Content-Type": "application/json"],
        body: body.flatMap { String(data: $0, encoding: .utf8) } ?? "{\"error\":\"\(message)\"}"
    )
}

enum BedrockError: Error, LocalizedError {
    case missingConfig(String)
    case noResponse

    var errorDescription: String? {
        switch self {
        case .missingConfig(let key): return "Missing config: \(key)"
        case .noResponse: return "No response from Bedrock"
        }
    }
}
