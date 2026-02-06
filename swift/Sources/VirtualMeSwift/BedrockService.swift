import Foundation
import SotoBedrockAgentRuntime
import SotoBedrockRuntime
import Logging

struct BedrockService {
    let agent: BedrockAgentRuntime
    let runtime: BedrockRuntime
    let logger: Logger

    func retrieveContext(for question: String) async throws -> String {
        guard !Environment.knowledgeBaseId.isEmpty else {
            throw BedrockError.missingConfig("KNOWLEDGE_BASE_ID")
        }

        logger.info("Retrieving context", metadata: [
            "question_length": "\(question.count)",
            "knowledge_base": "\(Environment.knowledgeBaseId)"
        ])

        let response: BedrockAgentRuntime.RetrieveResponse
        do {
            response = try await agent.retrieve(.init(
                knowledgeBaseId: Environment.knowledgeBaseId,
                retrievalConfiguration: .init(vectorSearchConfiguration: .init(numberOfResults: BedrockConfig.numberOfResults)),
                retrievalQuery: .init(text: question)
            ))
        } catch {
            throw BedrockError.retrievalFailed(underlyingError: error)
        }

        let context = response.retrievalResults
            .compactMap { $0.content.text }
            .joined(separator: "\n\n---\n\n")

        logger.info("Retrieved context", metadata: [
            "chunk_count": "\(response.retrievalResults.count)",
            "context_length": "\(context.count)"
        ])

        guard !context.isEmpty else {
            throw BedrockError.emptyContext
        }

        return context
    }

    func generateResponse(question: String, history: [ChatMessage], context: String) async throws -> String {
        let messages = buildMessages(question: question, history: history)
        let systemPrompt = buildSystemPrompt(context: context)

        logger.info("Generating response", metadata: [
            "model": "\(Environment.llmModel)",
            "temperature": "\(Environment.llmTemperature)",
            "message_count": "\(messages.count)"
        ])

        let response: BedrockRuntime.ConverseResponse
        do {
            response = try await runtime.converse(.init(
                inferenceConfig: .init(maxTokens: BedrockConfig.maxTokens, temperature: Float(Environment.llmTemperature)),
                messages: messages,
                modelId: Environment.llmModel,
                system: [.text(systemPrompt)]
            ))
        } catch {
            throw BedrockError.converseFailed(underlyingError: error)
        }

        guard let content = response.output.message?.content.first,
              case .text(let text) = content else {
            throw BedrockError.noResponse
        }

        return text
    }

    private func buildMessages(question: String, history: [ChatMessage]) -> [BedrockRuntime.Message] {
        var messages: [BedrockRuntime.Message] = history.dropLast().compactMap { msg in
            let role: BedrockRuntime.ConversationRole = msg.role == "ai" ? .assistant : .user
            return .init(content: [.text(msg.text)], role: role)
        }
        messages.append(.init(content: [.text("Question: \(question)")], role: .user))
        return messages
    }

    private func buildSystemPrompt(context: String) -> String {
        systemPrompt.replacingOccurrences(of: "{context}", with: context)
    }
}
