from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import User
from diagrams.aws.network import CloudFront, Route53, APIGateway
from diagrams.aws.compute import Lambda
from diagrams.aws.storage import S3
from diagrams.aws.ml import Bedrock
from diagrams.aws.management import Cloudwatch
from diagrams.aws.devtools import XRay

with Diagram("RAG Chatbot Architecture", show=False, direction="LR", graph_attr={"bgcolor": "white"}):
    user = User("User (Web Browser with Deep Chat UI)")

    with Cluster("AWS Cloud", graph_attr={"bgcolor": "white", "style": ""}):
        with Cluster("CDN Layer", graph_attr={"bgcolor": "white"}):
            cloudfront = CloudFront("Amazon CloudFront")
            s3_frontend = S3("Amazon S3 (Static Frontend)")
            cloudfront >> Edge(label="Serves static content") >> s3_frontend

        with Cluster("DNS & API Layer", graph_attr={"bgcolor": "white"}):
            route53 = Route53("Amazon Route 53")
            api_gateway = APIGateway("Amazon API Gateway")

        with Cluster("Compute Layer", graph_attr={"bgcolor": "white"}):
            lambda_function = Lambda("AWS Lambda (Swift Runtime)")

        with Cluster("AI Layer", graph_attr={"bgcolor": "white"}):
            bedrock = Bedrock("Amazon Bedrock (Nova 2 Lite)")
            bedrock_kb = Bedrock("Bedrock Knowledge Base")

        with Cluster("Storage Layer", graph_attr={"bgcolor": "white"}):
            s3_vectors = S3("S3 Vectors (Vector Store)")
            s3_kb = S3("S3 (Knowledge Base)")

        with Cluster("Monitoring Layer", graph_attr={"bgcolor": "white"}):
            cloudwatch = Cloudwatch("Amazon CloudWatch")
            xray = XRay("AWS X-Ray")

    # Connections
    user >> Edge(label="Accesses frontend") >> cloudfront
    user >> Edge(label="Sends /chat POST request") >> route53 >> api_gateway
    api_gateway >> Edge(label="Invokes") >> lambda_function

    lambda_function >> Edge(label="Retrieve & Generate") >> bedrock_kb
    bedrock_kb >> Edge(label="Vector search") >> s3_vectors
    bedrock_kb >> Edge(label="LLM inference") >> bedrock
    s3_kb >> Edge(label="Ingestion") >> bedrock_kb

    lambda_function >> Edge(label="Logs") >> cloudwatch
    lambda_function >> Edge(label="Traces") >> xray
