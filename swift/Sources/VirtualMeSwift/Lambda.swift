import AWSLambdaRuntime
import AWSLambdaEvents
import SotoBedrockAgentRuntime
import SotoBedrockRuntime
import SotoCore
import Foundation
import Logging

// Shared AWS client (reused across invocations)
let awsClient = AWSClient()

@main
struct VirtualMeLambda {
    static func main() async throws {
        let dependencies = Dependencies.production(awsClient: awsClient)
        let handler = ChatHandler(dependencies: dependencies)

        let runtime = LambdaRuntime { (event: APIGatewayV2Request, context: LambdaContext) async throws -> APIGatewayV2Response in
            try await handler.handle(event: event)
        }
        try await runtime.run()
    }
}

func isMetaQuestion(_ question: String) -> Bool {
    MetaDetection.triggers.contains { question.lowercased().contains($0) }
}

