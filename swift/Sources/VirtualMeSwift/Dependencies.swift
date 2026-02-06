import Foundation
import SotoBedrockAgentRuntime
import SotoBedrockRuntime
import SotoCore
import Logging
import AWSLambdaEvents

struct Dependencies {
    let bedrockService: BedrockService
    let logger: Logger
    let validator: RequestValidator

    static func production(awsClient: AWSClient) -> Dependencies {
        let logger = Logger(label: "virtual-me")
        return Dependencies(
            bedrockService: BedrockService(
                agent: BedrockAgentRuntime(client: awsClient, region: awsRegion),
                runtime: BedrockRuntime(client: awsClient, region: awsRegion),
                logger: logger
            ),
            logger: logger,
            validator: RequestValidator(
                maxConversationLength: ValidationLimits.maxConversationLength,
                maxMessageLength: ValidationLimits.maxMessageLength
            )
        )
    }
}

struct ChatHandler {
    let dependencies: Dependencies

    func handle(event: APIGatewayV2Request) async throws -> APIGatewayV2Response {
        guard let body = event.body else {
            return errorResponse(from: ValidationError.missingBody)
        }

        do {
            let request: ChatRequest
            do {
                request = try JSONDecoder().decode(ChatRequest.self, from: Data(body.utf8))
            } catch {
                throw ValidationError.invalidJSON(underlyingError: error)
            }

            try dependencies.validator.validate(request)

            let recentMessages = request.recentMessages(limit: ValidationLimits.recentMessageLimit)
            guard let question = request.lastMessageText else {
                throw ValidationError.emptyMessages
            }

            dependencies.logger.info("Processing request", metadata: [
                "question_length": "\(question.count)",
                "message_count": "\(recentMessages.count)"
            ])

            let answer: String
            if isMetaQuestion(question) {
                answer = MetaDetection.response
            } else {
                let context = try await dependencies.bedrockService.retrieveContext(for: question)
                answer = try await dependencies.bedrockService.generateResponse(question: question, history: recentMessages, context: context)
            }

            dependencies.logger.info("Generated response", metadata: ["response_length": "\(answer.count)"])

            let responseBody = try JSONEncoder().encode(ChatResponse(text: answer))
            return APIGatewayV2Response(
                statusCode: .ok,
                headers: ["Content-Type": "application/json"],
                body: String(data: responseBody, encoding: .utf8)
            )
        } catch {
            dependencies.logger.error("Request failed", metadata: [
                "error": "\(error)",
                "error_type": "\(type(of: error))"
            ])
            return errorResponse(from: error)
        }
    }
}
