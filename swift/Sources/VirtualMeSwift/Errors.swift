import Foundation
import AWSLambdaEvents

// MARK: - Domain Errors

enum ValidationError: Error, LocalizedError {
    case missingBody
    case invalidJSON(underlyingError: Error)
    case emptyMessages
    case conversationTooLong(actual: Int, max: Int)
    case messageTooLong(index: Int, actual: Int, max: Int)

    var errorDescription: String? {
        switch self {
        case .missingBody: return "Missing request body"
        case .invalidJSON(let error): return "Invalid JSON format: \(error.localizedDescription)"
        case .emptyMessages: return "No messages found"
        case .conversationTooLong(let actual, let max):
            return "Conversation exceeds maximum length of \(max) messages. Current: \(actual)"
        case .messageTooLong(let index, let actual, let max):
            return "Message at index \(index) exceeds maximum length of \(max) characters. Actual: \(actual)"
        }
    }

    var httpStatusCode: Int { 400 }
}

enum BedrockError: Error, LocalizedError {
    case missingConfig(String)
    case noResponse
    case emptyContext
    case retrievalFailed(underlyingError: Error)
    case converseFailed(underlyingError: Error)

    var errorDescription: String? {
        switch self {
        case .missingConfig(let key): return "Missing configuration: \(key)"
        case .noResponse: return "No response from Bedrock model"
        case .emptyContext: return "No relevant information found in knowledge base"
        case .retrievalFailed(let error): return "Failed to retrieve context: \(error.localizedDescription)"
        case .converseFailed(let error): return "Failed to generate response: \(error.localizedDescription)"
        }
    }

    var httpStatusCode: Int {
        switch self {
        case .missingConfig: return 500
        case .emptyContext: return 404
        case .noResponse, .retrievalFailed, .converseFailed: return 502
        }
    }
}

// MARK: - Error Response Builder

extension Error {
    var httpStatusCode: Int {
        switch self {
        case let error as ValidationError: return error.httpStatusCode
        case let error as BedrockError: return error.httpStatusCode
        default: return 500
        }
    }

    var userMessage: String {
        if let localized = self as? LocalizedError {
            return localized.errorDescription ?? "An unexpected error occurred"
        }
        return "An unexpected error occurred"
    }
}

func errorResponse(from error: Error) -> APIGatewayV2Response {
    let statusCode = error.httpStatusCode
    let message = error.userMessage
    let body = try? JSONEncoder().encode(ErrorResponse(error: message))
    return APIGatewayV2Response(
        statusCode: .init(code: statusCode),
        headers: ["Content-Type": "application/json"],
        body: body.flatMap { String(data: $0, encoding: .utf8) } ?? "{\"error\":\"\(message)\"}"
    )
}
