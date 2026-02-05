import Foundation

struct ChatMessage: Codable {
    let role: String
    let text: String
}

struct ChatRequest: Codable {
    let messages: [ChatMessage]
}

struct ChatResponse: Codable {
    let text: String
}

struct ErrorResponse: Codable {
    let error: String
    let details: [String]?

    init(error: String, details: [String]? = nil) {
        self.error = error
        self.details = details
    }
}
