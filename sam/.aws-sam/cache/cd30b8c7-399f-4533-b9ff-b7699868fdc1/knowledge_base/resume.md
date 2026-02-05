# Jeremy

Languages: English (Fluent), French (Native)

\

## SOLUTION ARCHITECT

#### System Modernization | Security & Compliance | System Integration

Solution Architect with over 20 years of experience, including 14 years at J.P. Morgan Private Bank. I specialize in designing and delivering complex software systems for highly
regulated enterprise environments where security, auditability, and reliability are critical.

\
I function as a Technical Lead, validating architectures through Proof of Concepts (POCs), auditing code (Java/Spring), and guiding technical delivery from design to production. I
combine deep legacy system knowledge with modern cloud-native expertise.

I am currently working on the AWS Solution Architect Professional certification.

### TECHNICAL SKILLS

|                         |                                                                               |
| :---------------------- | :---------------------------------------------------------------------------- |
| **Architecture**        | Domain-Driven Design (DDD), Hexagonal/Clean Architecture, Microservices.      |
| **Integration**         | Event-Driven (Kafka), Hybrid Cloud Patterns, Zero Trust Security.             |
| **Coding**              | **Java (20+ yrs)**, Spring Boot, Python, Swift. _Focus on rapid prototyping._ |
| **Cloud & Infra**       | **AWS Certified**, Kubernetes (EKS), Docker, Terraform, Ansible, F5 BIG-IP.   |
| **Security & Identity** | Cryptography (X.509), HSM, KMS, E-Signature (QuoVadis/Entrust), OWASP.        |
| **DevOps & Quality**    | CI/CD Pipelines, SonarQube, Maven, Git.                                       |
| **Observability**       | Splunk, Dynatrace, Grafana.                                                   |

### EXPERIENCE

\
**VP, SOLUTION ARCHITECT / SENIOR LEAD SOFTWARE ENGINEER** Oct 2010 -- Dec 2024

**J.P. Morgan Private Bank** , Geneva, Switzerland

**Technical Lead for the International Private Bank**. I drove the architecture and technical delivery for the end-to-end digital platform. I ensured the architecture followed strict security rules across multiple jurisdictions, specifically Switzerland and Asia, which enforced the most stringent regulatory standards.

##### Client Authentication Domain Owner

- **Directed the global overhaul of the Client Authentication ecosystem**, replacing legacy infrastructure with high-availability architecture. This modernization guaranteed compliance with strict multi-jurisdictional requirements (MAS Singapore, Swiss Banking Secrecy) and laid the critical technical foundation enabling the complete relaunch of the secure web and mobile platforms.

- **Mobile Security Engineering**: When the vendor failed to provide a mobile SDK, I reverse-engineered their proprietary JavaScript cryptographic algorithm and re-implemented the logic in native Swift (iOS) and Java (Android). This unblocked the launch of the mobile channel.

- **Vendor Security Auditing**: Identified a critical security vulnerability in an external MFA solution during acceptance testing. As a vendor patch was not available prior to the critical go-live, I assumed responsibility for hardening the deployment artifact myself, eliminating the vulnerability. This intervention ensured the release proceeded securely, preventing a potential breach of Swiss Banking Secrecy and avoiding significant reputational repercussions.

##### Digital Platform Architecture & Modernization

- **Architected the Service Oriented Architecture (SOA)**: Decoupled the frontend from the backend via RESTful APIs, enforcing strict JSON contract versioning to ensure
  zero-breakage deployments. Established the Stateless Architecture standard to facilitate the future move to Cloud/Kubernetes.

- **Global Entitlement Framework**: Architected an access control layer to manage fine-grained feature visibility. This enabled granular rollout strategies (Canary/Pilot) and the dynamic activation of specific features by country, region or user.

- **Client Service Optimization (View-As)**: Implemented the impersonation functionality within the dedicated banker application. This allows bankers to view the interface exactly as the client sees it, ensuring personalized guidance and precise assistance.

- **Project Ownership**: Provided full project ownership across complex, cross-functional initiatives, leading offshore teams, reviewing vendor contracts (Legal), and securing final architectural and security approval from Risk & Control, and Infrastructure stakeholders.

##### Cloud Native Engineering & Optimization

- **Implementation of Hybrid Cloud Strategy (AWS Migration)**: Engineered the on-premise SQL Server 'Always Encrypted' solution with local KMS (Switzerland) for sensitive data
  encryption. This validated the 'Keys-at-Home' model, enabling the future migration of all compute resources to AWS.

- **Resource & Dependency Optimization**: Rationalized Maven dependency trees to minimize security exposure. Fine-tuned Kubernetes CPU/Memory requests and limits during the
  CloudFoundry/K8s migration, minimizing cluster capacity requirements and reducing infrastructure costs.

- **Infrastructure Optimization**: Led the rationalization of legacy Virtual Machine (VM) workloads, migrating services to containerized environments to achieve cost savings.

##### System Integration & Compliance

- **Qualified Digital Signatures (Hybrid SaaS)**: Architected and delivered a regulatory compliant digital signature solution (QuoVadis) for non-repudiable transactions exceeding $10M each. This integration was critical for expanding into restricted Middle Eastern markets while preserving Swiss Banking Secrecy.

- **Secure Messaging & WeChat Integration**: Led the technical integration of the 'Moxo' platform to capture and secure client communications (Asia) performed via WeChat (unmonitored channel). Validated the vendor's WeChat bridging capabilities and guided the technical implementation to overcome API limitations, ensuring seamless ingestion of external messages into the bank's compliance archive.

- **System Integration (Engage Project)**: Developed backend services for the direct investment platform, integrating Apache Kafka consumers to handle document distribution and asynchronous client notifications.

- Managed end-to-end deployment orchestration, collaborating with infrastructure teams to provision backend, web, and database instances across multiple data centers.

\
**Environment**: Java 17, Spring Boot, AWS, Kubernetes, Kafka, MS SQL Server (Encrypted), Splunk, Dynatrace, ReactJS, Swift, Linux, Maven, Git

\
**IT ARCHITECT** Aug 2007 -- Sep 2010
**Carlson Wagonlit Travel.** www.carlsonwagonlit.com, Paris, France

##### Global leader specializing in business travel management. CWT is a Carlson company

- Defined the Java/J2EE reference architecture and promoted the use of automated testing (Selenium) and Continuous Integration (CI).

- Stabilized the "Harp" global booking platform by migrating the persistence layer from a legacy proprietary framework to iBatis, which eliminated critical performance overheads.

##### EARLY CAREER 2000 - 2007

- **Business Propulsion Systems** (Toronto) | _2005 – 2007_
  _FinTech: SOX Compliance Workflows_

- **Blast Radius** (Toronto) | _2004 – 2005_
  _Web Agency: High-Traffic Web Portals_

- **Taleo** (Québec) | _2002 – 2004_
  _HR Tech: Talent Management Solution_

- **Vanilla Technology** (Paris) | _2000 – 2002_
  _Finance: OTC Trading Platform_

### EDUCATION

M.Sc. Computer Science _Université Polytechnique Hauts-de-France_, 2000

### CERTIFICATIONS 2025

AWS Certified Solutions Architect, AWS Certified Security Specialty

Machine Learning Specialization, _Stanford Online_

Deep Learning Specialization, _DeepLearning.AI_

Generative AI with Large Language Models, _DeepLearning.AI_

### PORTFOLIO

**Generative AI Prototype**: Built a modular RAG pipeline using LangChain4j, implementing Fusion retrieval patterns. The system is architected as a Model Context Protocol (MCP) server to enable standardized integration with LLM agents.
**Serverless development**: Serverless Apple Wallet Pass Generator (AWS)
Serverless Apple Wallet Pass Generator (AWS)
The Architecture: Built a stateless backend using AWS Lambda and API Gateway. The system performs real-time User-Agent detection to serve native Apple Wallet passes (.pkpass) to iOS devices and standard vCards (.vcf) to Android users.

Key Innovation: Unlike static vCards, the Apple Wallet implementation allows for remote updates (push notifications), ensuring contacts always have the latest information without re-scanning.

Try here: pass.lemaire.tel.

The Architecture: Built a stateless backend using AWS Lambda and API Gateway. The system performs real-time User-Agent detection to serve native Apple Wallet passes (.pkpass) to iOS devices and standard vCards (.vcf) to Android users. Key Innovation: Unlike static vCards, the Apple Wallet implementation allows for remote updates (push notifications), ensuring contacts always have the latest information without re-scanning. Try here: pass.lemaire.tel.
Skills: Amazon Web Services (AWS) · Terraform · Python (Programming Language) · iOS · AWS Lambda

A production-ready "Virtual Clone" chatbot that uses **Retrieval Augmented Generation (RAG)** to answer questions accurately based on your personal data (resume, bio, etc.). Built with AWS Lambda, AWS Bedrock (Nova 2 Lite), LangChain, LangGraph, and DynamoDB for persistent vector storage. Supports local development with LM Studio.

- **RAG Architecture**: Grounds all responses in your provided knowledge base (no hallucinations!)
- **Serverless**: Cost-effective AWS Lambda + API Gateway architecture
- **Cold Start Optimized**: Strategic code organization minimizes Lambda initialization time
- **UI**: Modern, responsive chat interface using Deep Chat web component
- **Infrastructure as Code**: Complete Terraform configuration for reproducible deployments
- **Production Ready**: Pydantic validation, structured logging, retry logic, and timeout handling
