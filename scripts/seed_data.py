"""
Comprehensive Job Market Data Seeder
Seeds high-fidelity job market intelligence data covering all 7 skill categories:
- Languages, Frameworks, Cloud/DevOps, Databases, AI/ML, Tools, Soft Skills.
Simulates real-world postings from leading global tech companies across major tech hubs.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import logging
from datetime import datetime, timedelta
from database.connection import init_db, session_scope
from crawler.pipelines import pipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("job_crawler.seeder")

SEED_JOBS = [
    # 1. AI & Machine Learning
    {
        "job_title": "Senior Staff Machine Learning Engineer (LLMs & Foundation Models)",
        "company": "Anthropic AI",
        "location_raw": "San Francisco, CA",
        "city": "San Francisco",
        "country": "USA",
        "is_remote": True,
        "salary_min": 240000,
        "salary_max": 320000,
        "salary_currency": "USD",
        "experience_level": "Senior",
        "source_portal": "Anthropic Careers",
        "job_url": "https://anthropic.com/careers/staff-mle-llm",
        "description_raw": """
        Anthropic is hiring a Senior Staff Machine Learning Engineer to scale our RLHF and LLM pre-training pipelines.
        Requirements:
        - 6+ years of production experience in Machine Learning and Deep Learning with Python and PyTorch.
        - Deep hands-on expertise with LLMs, Transformers, Attention mechanisms, and RLHF.
        - Experience with distributed training on GPU clusters using Ray, DeepSpeed, or Megatron.
        - Strong foundation in System Design, Algorithms, and Mathematics.
        - Proficiency with Hugging Face, Weights & Biases, and Vector Databases (Pinecone, Milvus).
        Preferred Qualifications:
        - Experience with C++, CUDA kernel programming, and Triton.
        - Publications at NeurIPS, ICML, or ICLR.
        - Familiarity with Kubernetes, Docker, and AWS / GCP cloud environments.
        - Excellent written communication, problem solving, and mentorship.
        """
    },
    {
        "job_title": "Generative AI Solutions Architect",
        "company": "Amazon Web Services",
        "location_raw": "Seattle, WA",
        "city": "Seattle",
        "country": "USA",
        "is_remote": False,
        "salary_min": 185000,
        "salary_max": 245000,
        "salary_currency": "USD",
        "experience_level": "Senior",
        "source_portal": "Amazon Jobs",
        "job_url": "https://amazon.jobs/genai-solutions-architect",
        "description_raw": """
        Join AWS to architect Generative AI enterprise solutions using Bedrock and SageMaker.
        Qualifications:
        - 5+ years designing enterprise cloud architectures on AWS (EC2, S3, IAM, Lambda, Bedrock).
        - Hands-on development in Python and TypeScript.
        - Solid understanding of Retrieval-Augmented Generation (RAG), LangChain, LlamaIndex, and ChromaDB.
        - Strong background in Cloud Security, compliance, and API integration.
        - Outstanding presentation skills, stakeholder management, and customer empathy.
        Bonus points:
        - AWS Certified Solutions Architect Professional.
        - Experience with Terraform, Docker, and Bedrock agents.
        """
    },
    {
        "job_title": "Computer Vision & Autonomous Systems Engineer",
        "company": "Waymo",
        "location_raw": "Mountain View, CA",
        "city": "San Francisco",
        "country": "USA",
        "is_remote": False,
        "salary_min": 190000,
        "salary_max": 260000,
        "salary_currency": "USD",
        "experience_level": "Mid-Level",
        "source_portal": "Waymo Careers",
        "job_url": "https://waymo.com/careers/cv-engineer",
        "description_raw": """
        Develop perception models for autonomous vehicles.
        Requirements:
        - M.S. or Ph.D. in Computer Science or Robotics.
        - 3+ years coding in modern C++ and Python.
        - Expertise in Computer Vision, OpenCV, PyTorch, and TensorFlow.
        - Real-time sensor fusion (LiDAR, Radar, Camera).
        - Experience with Linux, Git, and CI/CD pipelines.
        Nice to have:
        - CUDA optimization, TensorRT, ROS/ROS2.
        - Experience with multi-task learning.
        """
    },

    # 2. Backend Engineering & Microservices
    {
        "job_title": "Principal Backend Engineer (Distributed Systems)",
        "company": "Stripe",
        "location_raw": "New York, NY",
        "city": "New York",
        "country": "USA",
        "is_remote": True,
        "salary_min": 220000,
        "salary_max": 290000,
        "salary_currency": "USD",
        "experience_level": "Lead",
        "source_portal": "Stripe Careers",
        "job_url": "https://stripe.com/jobs/principal-backend",
        "description_raw": """
        Scale global financial payments infrastructure processing billions daily.
        Requirements:
        - 8+ years building mission-critical distributed systems.
        - Advanced proficiency in Go, Java, or Ruby.
        - Deep understanding of ACID transactions, PostgreSQL, Redis, and Kafka.
        - Proven track record with high-throughput low-latency Microservices and System Design.
        - Master of concurrency, thread safety, and idempotent API design.
        Nice to have:
        - Familiarity with Kubernetes, Envoy, and gRPC.
        - Strong background in observability using Datadog and Grafana.
        - Passion for developer tooling and engineering excellence.
        """
    },
    {
        "job_title": "Senior Backend Developer (Python & FastAPI)",
        "company": "Spotify",
        "location_raw": "Stockholm, Sweden",
        "city": "Stockholm",
        "country": "Europe",
        "is_remote": True,
        "salary_min": 110000,
        "salary_max": 145000,
        "salary_currency": "USD",
        "experience_level": "Senior",
        "source_portal": "Spotify Jobs",
        "job_url": "https://spotify.com/jobs/senior-backend-python",
        "description_raw": """
        Build high-performance recommendation and audio streaming backend APIs.
        What you'll need:
        - 5+ years of software development experience with Python, FastAPI, and Django.
        - Experience designing RESTful and GraphQL APIs.
        - Strong relational database modeling with PostgreSQL and NoSQL with Cassandra or MongoDB.
        - Hands-on cloud experience with GCP (Google Cloud Platform) or AWS.
        - Thorough unit testing with pytest and test-driven development.
        What's a plus:
        - Knowledge of Apache Kafka, Docker, and Kubernetes.
        - Mentoring junior engineers and agile sprint planning.
        """
    },
    {
        "job_title": "Backend Software Engineer (Golang & Kafka)",
        "company": "Uber",
        "location_raw": "Bengaluru, India",
        "city": "Bengaluru",
        "country": "India",
        "is_remote": False,
        "salary_min": 45000,
        "salary_max": 70000,
        "salary_currency": "USD",
        "experience_level": "Mid-Level",
        "source_portal": "Uber Careers",
        "job_url": "https://uber.com/careers/backend-golang-blr",
        "description_raw": """
        Join Uber's Marketplace Dynamics team in Bengaluru.
        Basic Qualifications:
        - 3+ years writing concurrent, robust code in Go (Golang) or Java.
        - Deep familiarity with Kafka message brokers, Redis caching, and MySQL / PostgreSQL.
        - Experience building scalable microservices deployed on Docker and Kubernetes.
        - Solid understanding of data structures, algorithms, and complexity analysis.
        Desired Skills:
        - Distributed tracing with Jaeger, OpenTelemetry, Prometheus.
        - Prior experience with dispatch, geospatial routing, or pricing systems.
        - Effective verbal and written communication skills.
        """
    },

    # 3. Full Stack & Frontend Engineering
    {
        "job_title": "Lead Full Stack Developer (Next.js, TypeScript & Node)",
        "company": "Vercel",
        "location_raw": "San Francisco, CA",
        "city": "San Francisco",
        "country": "USA",
        "is_remote": True,
        "salary_min": 175000,
        "salary_max": 230000,
        "salary_currency": "USD",
        "experience_level": "Lead",
        "source_portal": "Vercel Careers",
        "job_url": "https://vercel.com/careers/lead-fullstack",
        "description_raw": """
        Create developer tools and web infrastructure for millions of creators worldwide.
        Must have:
        - 6+ years building full-stack web applications.
        - Mastery of TypeScript, JavaScript, React, Next.js, and Node.js.
        - Deep knowledge of modern CSS, Tailwind CSS, Responsive Design, and Web Performance Core Vitals.
        - Backend API integration using GraphQL, REST, and Prisma with PostgreSQL.
        - Excellent product intuition and UI/UX design collaboration.
        Nice to have:
        - Experience with Serverless Edge functions, Redis, and WebSockets.
        - Open-source contributions and technical blogging.
        """
    },
    {
        "job_title": "Senior Frontend Engineer (React & State Architecture)",
        "company": "Airbnb",
        "location_raw": "San Francisco, CA",
        "city": "San Francisco",
        "country": "USA",
        "is_remote": True,
        "salary_min": 165000,
        "salary_max": 215000,
        "salary_currency": "USD",
        "experience_level": "Senior",
        "source_portal": "Airbnb Careers",
        "job_url": "https://airbnb.com/careers/senior-frontend",
        "description_raw": """
        Build magical booking and host exploration experiences for Airbnb.
        Requirements:
        - 5+ years of experience in Frontend Web Development.
        - Expert knowledge of React, Redux / Zustand, TypeScript, and HTML5 / CSS3.
        - Experience with Webpack, Vite, Jest, and Cypress automated testing.
        - Commitment to web accessibility (a11y) and cross-browser responsiveness.
        - Strong ownership, communication, and cross-team alignment.
        Bonus:
        - Experience with React Native or design systems (Storybook).
        """
    },
    {
        "job_title": "Full Stack Engineer (Vue.js & Python)",
        "company": "GitLab",
        "location_raw": "London, UK",
        "city": "London",
        "country": "UK",
        "is_remote": True,
        "salary_min": 115000,
        "salary_max": 155000,
        "salary_currency": "USD",
        "experience_level": "Mid-Level",
        "source_portal": "GitLab Careers",
        "job_url": "https://gitlab.com/careers/fullstack-engineer",
        "description_raw": """
        GitLab is fully remote. Help us advance the all-in-one DevSecOps platform.
        Requirements:
        - 3+ years full-stack development experience.
        - Proficiency in Vue.js, JavaScript, and modern HTML/CSS.
        - Solid backend experience in Ruby on Rails or Python.
        - Experience with PostgreSQL, Redis, and GitLab CI/CD.
        - Async communication, remote discipline, and collaboration.
        """
    },

    # 4. Data Engineering & Big Data
    {
        "job_title": "Staff Data Engineer (Snowflake & Spark Lakehouse)",
        "company": "Snowflake Computing",
        "location_raw": "San Mateo, CA",
        "city": "San Francisco",
        "country": "USA",
        "is_remote": False,
        "salary_min": 200000,
        "salary_max": 270000,
        "salary_currency": "USD",
        "experience_level": "Senior",
        "source_portal": "Snowflake Careers",
        "job_url": "https://snowflake.com/careers/staff-data-engineer",
        "description_raw": """
        Architect large-scale petabyte data pipelines.
        Requirements:
        - 7+ years of experience in data engineering and data warehousing.
        - Mastery of SQL, Python, and Apache Spark / PySpark.
        - Extensive experience with Snowflake, BigQuery, or Databricks.
        - Workflow orchestration with Apache Airflow, dbt, and Kafka.
        - Data modeling (Star schema, Data Vault) and data governance.
        Nice to have:
        - Experience with AWS S3, Terraform, and Docker.
        - Knowledge of real-time stream processing with Apache Flink.
        """
    },
    {
        "job_title": "Senior Analytics Engineer (dbt & BigQuery)",
        "company": "Canva",
        "location_raw": "Sydney, Australia",
        "city": "Sydney",
        "country": "Australia",
        "is_remote": True,
        "salary_min": 130000,
        "salary_max": 170000,
        "salary_currency": "USD",
        "experience_level": "Senior",
        "source_portal": "Canva Careers",
        "job_url": "https://canva.com/careers/analytics-engineer",
        "description_raw": """
        Shape data-driven decisions for 170+ million active monthly Canva creators.
        What we expect:
        - 4+ years working as an Analytics Engineer or Data Engineer.
        - Deep expertise in SQL and data transformation using dbt.
        - Experience with Google Cloud BigQuery and Looker / Tableau.
        - Git version control, CI/CD, and automated data testing with Great Expectations.
        - Excellent stakeholder communication and business problem solving.
        """
    },
    {
        "job_title": "Lead Data Platform Engineer",
        "company": "Zomato",
        "location_raw": "Gurugram, India",
        "city": "Delhi NCR",
        "country": "India",
        "is_remote": False,
        "salary_min": 40000,
        "salary_max": 65000,
        "salary_currency": "USD",
        "experience_level": "Lead",
        "source_portal": "Zomato Careers",
        "job_url": "https://zomato.com/careers/lead-data-platform",
        "description_raw": """
        Power food delivery logistics intelligence across 1000+ Indian cities.
        Requirements:
        - 6+ years in distributed big data engineering with Python, Scala, and SQL.
        - Experience with Apache Kafka, Spark Streaming, and Presto / Trino.
        - Storage management on AWS S3, Delta Lake, and PostgreSQL.
        - Containerization using Docker and orchestration with Kubernetes.
        - Mentorship, technical roadmap planning, and team leadership.
        """
    },

    # 5. Cloud Architecture, DevOps & SRE
    {
        "job_title": "Senior DevOps / SRE Engineer (Kubernetes & Terraform)",
        "company": "Datadog",
        "location_raw": "Paris, France",
        "city": "Paris",
        "country": "Europe",
        "is_remote": True,
        "salary_min": 105000,
        "salary_max": 140000,
        "salary_currency": "USD",
        "experience_level": "Senior",
        "source_portal": "Datadog Careers",
        "job_url": "https://datadog.com/careers/sr-sre-paris",
        "description_raw": """
        Maintain 99.999% reliability across millions of cloud instances worldwide.
        Requirements:
        - 5+ years of experience in Site Reliability Engineering or DevOps.
        - Deep hands-on experience with Kubernetes, Docker, and Linux kernel internals.
        - Infrastructure as Code (IaC) with Terraform and Ansible.
        - Multi-cloud administration across AWS, Azure, and GCP.
        - Strong scripting skills in Python, Go, or Bash.
        - Observability tools: Prometheus, Grafana, Datadog.
        Desired:
        - Chaos engineering and incident postmortem leadership.
        """
    },
    {
        "job_title": "Cloud Platform Architect",
        "company": "Microsoft",
        "location_raw": "Redmond, WA",
        "city": "Seattle",
        "country": "USA",
        "is_remote": True,
        "salary_min": 210000,
        "salary_max": 280000,
        "salary_currency": "USD",
        "experience_level": "Lead",
        "source_portal": "Microsoft Careers",
        "job_url": "https://microsoft.com/careers/cloud-platform-architect",
        "description_raw": """
        Shape next-generation enterprise hybrid cloud platforms on Azure.
        Basic Qualifications:
        - 8+ years leading enterprise cloud infrastructure architecture.
        - Deep mastery of Microsoft Azure services (AKS, CosmosDB, Azure DevOps).
        - Experience in zero-trust network security, IAM, and compliance frameworks.
        - CI/CD automation with GitHub Actions and Terraform.
        - Outstanding executive presentation and stakeholder negotiation.
        """
    },
    {
        "job_title": "DevOps Engineer (CI/CD Automation)",
        "company": "Swiggy",
        "location_raw": "Bengaluru, India",
        "city": "Bengaluru",
        "country": "India",
        "is_remote": False,
        "salary_min": 35000,
        "salary_max": 55000,
        "salary_currency": "USD",
        "experience_level": "Mid-Level",
        "source_portal": "Swiggy Careers",
        "job_url": "https://swiggy.com/careers/devops-blr",
        "description_raw": """
        Join India's leading on-demand convenience platform.
        Requirements:
        - 3+ years managing CI/CD pipelines with Jenkins and GitLab CI.
        - Hands-on experience with AWS, Docker, and Kubernetes.
        - Scripting proficiency with Python, Bash, and Linux systems.
        - Experience with monitoring using Prometheus, Grafana, and ELK Stack.
        """
    },

    # 6. Mobile & Cross-Platform Development
    {
        "job_title": "Senior iOS Engineer (Swift & SwiftUI)",
        "company": "Apple",
        "location_raw": "Cupertino, CA",
        "city": "San Francisco",
        "country": "USA",
        "is_remote": False,
        "salary_min": 175000,
        "salary_max": 235000,
        "salary_currency": "USD",
        "experience_level": "Senior",
        "source_portal": "Apple Jobs",
        "job_url": "https://apple.com/jobs/senior-ios-swift",
        "description_raw": """
        Innovate user interactions across iOS, iPadOS, and watchOS.
        Qualifications:
        - 5+ years of native iOS app development with Swift and Objective-C.
        - Deep mastery of SwiftUI, UIKit, Combine, and Core Data.
        - Solid understanding of MVC / MVVM architectures and memory profiling with Instruments.
        - RESTful API integration and offline data synchronization.
        - High attention to animation smoothness and UI polishing.
        """
    },
    {
        "job_title": "Mobile Developer (Flutter & React Native)",
        "company": "Revolut",
        "location_raw": "London, UK",
        "city": "London",
        "country": "UK",
        "is_remote": True,
        "salary_min": 95000,
        "salary_max": 135000,
        "salary_currency": "USD",
        "experience_level": "Mid-Level",
        "source_portal": "Revolut Careers",
        "job_url": "https://revolut.com/careers/mobile-flutter",
        "description_raw": """
        Build high-security global financial services mobile apps.
        Requirements:
        - 3+ years building cross-platform apps using Flutter / Dart or React Native.
        - Experience with state management (Bloc, Provider, Redux).
        - Integration with backend REST and GraphQL microservices.
        - Mobile CI/CD with Fastlane and GitHub Actions.
        - Strict attention to biometric authentication and app security.
        """
    },

    # 7. Cyber Security & AppSec
    {
        "job_title": "Staff Security Engineer (Cloud & Application Security)",
        "company": "Cloudflare",
        "location_raw": "Austin, TX",
        "city": "Austin",
        "country": "USA",
        "is_remote": True,
        "salary_min": 195000,
        "salary_max": 255000,
        "salary_currency": "USD",
        "experience_level": "Senior",
        "source_portal": "Cloudflare Careers",
        "job_url": "https://cloudflare.com/careers/staff-security",
        "description_raw": """
        Protect millions of Internet domains against state-sponsored attacks and DDoS.
        Requirements:
        - 6+ years in application security, penetration testing, and cloud infrastructure defense.
        - In-depth knowledge of OWASP Top 10, cryptographic primitives, and secure code review.
        - Scripting and tooling in Python, Go, and Rust.
        - Hands-on security auditing on AWS and Kubernetes.
        - Experience with SIEM tools, Splunk, and incident response.
        - Industry certifications: CISSP, OSCP, or CEH preferred.
        """
    },

    # 8. QA, Testing & SDET
    {
        "job_title": "Senior SDET / Test Automation Lead (Playwright & Python)",
        "company": "Atlassian",
        "location_raw": "Bengaluru, India",
        "city": "Bengaluru",
        "country": "India",
        "is_remote": True,
        "salary_min": 35000,
        "salary_max": 52000,
        "salary_currency": "USD",
        "experience_level": "Senior",
        "source_portal": "Atlassian Careers",
        "job_url": "https://atlassian.com/careers/sdet-blr",
        "description_raw": """
        Ensure flawless quality across Jira and Confluence cloud platforms.
        Requirements:
        - 5+ years of software test automation experience.
        - Expertise with Python or Java, and frameworks like Playwright, Selenium, and Cypress.
        - API testing with Postman and pytest.
        - Performance and load testing using JMeter or Locust.
        - Deep integration with CI/CD pipelines (Jenkins, Bitbucket Pipelines).
        - Strong analytical troubleshooting and defect tracking.
        """
    },

    # 9. Data Science & Business Intelligence
    {
        "job_title": "Senior Data Scientist (Product & Growth Analytics)",
        "company": "Netflix",
        "location_raw": "Los Gatos, CA",
        "city": "San Francisco",
        "country": "USA",
        "is_remote": True,
        "salary_min": 210000,
        "salary_max": 285000,
        "salary_currency": "USD",
        "experience_level": "Senior",
        "source_portal": "Netflix Jobs",
        "job_url": "https://netflix.com/jobs/sr-data-scientist-growth",
        "description_raw": """
        Drive user acquisition, retention algorithms, and global streaming engagement.
        Requirements:
        - 5+ years applying statistical modeling, A/B testing, and machine learning to product problems.
        - Proficiency in Python (pandas, numpy, scikit-learn, scipy) and advanced SQL.
        - Deep understanding of causal inference, experimental design, and hypothesis testing.
        - Experience with data visualization in Tableau, Plotly, or Streamlit.
        - Superb stakeholder storytelling and business acumen.
        Preferred:
        - Experience with PySpark and Snowflake.
        """
    },

    # 10. Germany & European Tech Scene
    {
        "job_title": "Senior Cloud Infrastructure Engineer",
        "company": "SAP",
        "location_raw": "Berlin, Germany",
        "city": "Berlin",
        "country": "Europe",
        "is_remote": False,
        "salary_min": 90000,
        "salary_max": 125000,
        "salary_currency": "EUR",
        "experience_level": "Senior",
        "source_portal": "SAP Careers",
        "job_url": "https://sap.com/careers/cloud-infra-berlin",
        "description_raw": """
        Build enterprise cloud foundation services for Fortune 500 customers.
        Requirements:
        - 5+ years in Linux cloud engineering with Kubernetes and Docker.
        - Proficiency with Go, Python, and Terraform.
        - Good understanding of PostgreSQL, Redis, and network security.
        - German or English fluent communication.
        """
    }
]


def seed_database():
    logger.info("Initializing database schema...")
    init_db()

    logger.info(f"Processing and inserting {len(SEED_JOBS)} high-fidelity seed jobs...")
    saved_count = 0
    dup_count = 0

    with session_scope() as session:
        for idx, job_data in enumerate(SEED_JOBS, start=1):
            posting_time = datetime.utcnow() - timedelta(days=idx % 14, hours=idx * 2)
            job_data["posting_date"] = posting_time
            job_data["raw_html"] = f"<html><body><h1>{job_data['job_title']}</h1><p>{job_data['description_raw']}</p></body></html>"

            status, result = pipeline.process_item(job_data, session=session)
            if status == "saved":
                saved_count += 1
                logger.info(f"[{saved_count}/{len(SEED_JOBS)}] Saved: {job_data['job_title']} ({job_data['company']})")
            elif status == "duplicate":
                dup_count += 1
                logger.info(f"Duplicate skipped: {job_data['job_title']}")
            else:
                logger.warning(f"Failed item: {result}")

    logger.info("=" * 60)
    logger.info(f"Data seeding complete! Saved: {saved_count}, Duplicates: {dup_count}")
    logger.info("=" * 60)


if __name__ == "__main__":
    seed_database()
