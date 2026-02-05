// swift-tools-version:6.0
import PackageDescription

let package = Package(
    name: "VirtualMeSwift",
    platforms: [.macOS(.v15)],
    dependencies: [
        .package(url: "https://github.com/awslabs/swift-aws-lambda-runtime.git", from: "2.5.3"),
        .package(url: "https://github.com/swift-server/swift-aws-lambda-events.git", from: "1.5.0"),
        .package(url: "https://github.com/soto-project/soto.git", from: "7.12.0")
    ],
    targets: [
        .executableTarget(
            name: "VirtualMeSwift",
            dependencies: [
                .product(name: "AWSLambdaRuntime", package: "swift-aws-lambda-runtime"),
                .product(name: "AWSLambdaEvents", package: "swift-aws-lambda-events"),
                .product(name: "SotoBedrockAgentRuntime", package: "soto"),
                .product(name: "SotoBedrockRuntime", package: "soto")
            ]
        )
    ]
)
