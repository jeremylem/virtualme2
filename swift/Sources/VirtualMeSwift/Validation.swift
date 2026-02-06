import Foundation

struct RequestValidator {
    let maxConversationLength: Int
    let maxMessageLength: Int

    init(maxConversationLength: Int = 100, maxMessageLength: Int = 5000) {
        self.maxConversationLength = maxConversationLength
        self.maxMessageLength = maxMessageLength
    }

    func validate(_ request: ChatRequest) throws {
        guard request.messages.count <= maxConversationLength else {
            throw ValidationError.conversationTooLong(actual: request.messages.count, max: maxConversationLength)
        }

        for (index, message) in request.messages.enumerated() {
            guard message.text.count <= maxMessageLength else {
                throw ValidationError.messageTooLong(index: index, actual: message.text.count, max: maxMessageLength)
            }
        }

        guard !request.messages.isEmpty, request.messages.last?.text.isEmpty == false else {
            throw ValidationError.emptyMessages
        }
    }
}

extension ChatRequest {
    func recentMessages(limit: Int = 20) -> [ChatMessage] {
        Array(messages.suffix(limit))
    }

    var lastMessageText: String? {
        messages.last?.text
    }
}
