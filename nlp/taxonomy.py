"""
Skill Taxonomy and Extraction Dictionary
Curated catalog of 250+ technical and soft skills across 7 major categories,
with disambiguation patterns and alias mappings.
"""

from typing import Dict, List, Any, Optional

# Primary skill definition structure:
# name: canonical display name
# category: classification bucket
# is_tech: boolean
# aliases: alternative forms or abbreviations
# regex_pattern: optional custom boundary regex (for single letters like C, R, Go)

SKILL_TAXONOMY: List[Dict[str, Any]] = [
    # =========================================================================
    # 1. PROGRAMMING LANGUAGES
    # =========================================================================
    {"name": "Python", "category": "Languages", "is_tech": True, "aliases": ["python3", "python2", "py"]},
    {"name": "JavaScript", "category": "Languages", "is_tech": True, "aliases": ["js", "es6", "ecmascript"]},
    {"name": "TypeScript", "category": "Languages", "is_tech": True, "aliases": ["ts"]},
    {"name": "Java", "category": "Languages", "is_tech": True, "aliases": ["java 11", "java 17", "java 21", "core java"]},
    {"name": "C++", "category": "Languages", "is_tech": True, "aliases": ["cpp", "cplusplus", "c/c++"], "regex": r"(?:\bc\+\+\b|\bcpp\b)"},
    {"name": "C#", "category": "Languages", "is_tech": True, "aliases": ["csharp", "c-sharp", ".net c#"], "regex": r"(?:\bc#\b|\bcsharp\b)"},
    {"name": "Go", "category": "Languages", "is_tech": True, "aliases": ["golang"], "regex": r"(?:\bgolang\b|\bgo\s+(?:language|code|developer|backend)\b)"},
    {"name": "Rust", "category": "Languages", "is_tech": True, "aliases": ["rustlang"], "regex": r"(?:\brust\b|\brustlang\b)"},
    {"name": "SQL", "category": "Languages", "is_tech": True, "aliases": ["structured query language", "pl/sql", "t-sql"]},
    {"name": "Ruby", "category": "Languages", "is_tech": True, "aliases": ["ruby on rails", "mri ruby"]},
    {"name": "PHP", "category": "Languages", "is_tech": True, "aliases": ["php8", "php7"]},
    {"name": "Kotlin", "category": "Languages", "is_tech": True, "aliases": ["kotlin/android"]},
    {"name": "Swift", "category": "Languages", "is_tech": True, "aliases": ["swiftui", "swift/ios"]},
    {"name": "Scala", "category": "Languages", "is_tech": True, "aliases": []},
    {"name": "R", "category": "Languages", "is_tech": True, "aliases": ["r-project", "r programming"], "regex": r"(?:\br\s+(?:programming|language|scripting|studio)\b|\bdata analysis with r\b)"},
    {"name": "Bash", "category": "Languages", "is_tech": True, "aliases": ["shell", "bash scripting", "zsh", "sh"]},
    {"name": "HTML5", "category": "Languages", "is_tech": True, "aliases": ["html"]},
    {"name": "CSS3", "category": "Languages", "is_tech": True, "aliases": ["css", "scss", "sass", "less"]},
    {"name": "C", "category": "Languages", "is_tech": True, "aliases": ["c language", "ansi c"], "regex": r"(?:\bc\s+(?:language|programming|developer)\b|\bansi\s+c\b)"},
    {"name": "Solidity", "category": "Languages", "is_tech": True, "aliases": ["smart contracts"]},
    {"name": "Dart", "category": "Languages", "is_tech": True, "aliases": ["dart/flutter"]},
    {"name": "Verilog", "category": "Languages", "is_tech": True, "aliases": ["verilog-hdl", "verilog hdl"]},
    {"name": "SystemVerilog", "category": "Languages", "is_tech": True, "aliases": ["sv", "systemverilog", "system-verilog"]},
    {"name": "VHDL", "category": "Languages", "is_tech": True, "aliases": ["vhdl-ams"]},

    # =========================================================================
    # 2. FRAMEWORKS & LIBRARIES
    # =========================================================================
    {"name": "React", "category": "Frameworks", "is_tech": True, "aliases": ["reactjs", "react.js", "react native"]},
    {"name": "Next.js", "category": "Frameworks", "is_tech": True, "aliases": ["nextjs", "next.js"]},
    {"name": "Node.js", "category": "Frameworks", "is_tech": True, "aliases": ["nodejs", "node"]},
    {"name": "Vue.js", "category": "Frameworks", "is_tech": True, "aliases": ["vue", "vuejs", "vue3", "nuxt", "nuxtjs"]},
    {"name": "Angular", "category": "Frameworks", "is_tech": True, "aliases": ["angularjs", "angular 2+"]},
    {"name": "FastAPI", "category": "Frameworks", "is_tech": True, "aliases": ["fast-api"]},
    {"name": "Django", "category": "Frameworks", "is_tech": True, "aliases": ["django rest framework", "drf"]},
    {"name": "Flask", "category": "Frameworks", "is_tech": True, "aliases": []},
    {"name": "Spring Boot", "category": "Frameworks", "is_tech": True, "aliases": ["spring", "spring framework", "spring-boot"]},
    {"name": "Express.js", "category": "Frameworks", "is_tech": True, "aliases": ["expressjs", "express"]},
    {"name": "NestJS", "category": "Frameworks", "is_tech": True, "aliases": ["nest.js"]},
    {"name": ".NET Core", "category": "Frameworks", "is_tech": True, "aliases": ["dotnet", ".net", "asp.net", "asp.net core"]},
    {"name": "Ruby on Rails", "category": "Frameworks", "is_tech": True, "aliases": ["rails"]},
    {"name": "Tailwind CSS", "category": "Frameworks", "is_tech": True, "aliases": ["tailwind"]},
    {"name": "Bootstrap", "category": "Frameworks", "is_tech": True, "aliases": []},
    {"name": "Svelte", "category": "Frameworks", "is_tech": True, "aliases": ["sveltekit"]},
    {"name": "GraphQL", "category": "Frameworks", "is_tech": True, "aliases": ["apollo", "relay"]},
    {"name": "REST API", "category": "Frameworks", "is_tech": True, "aliases": ["restful", "rest api design"]},
    {"name": "gRPC", "category": "Frameworks", "is_tech": True, "aliases": ["protobuf", "protocol buffers"]},
    {"name": "Kafka", "category": "Frameworks", "is_tech": True, "aliases": ["apache kafka"]},
    {"name": "RabbitMQ", "category": "Frameworks", "is_tech": True, "aliases": ["amqp"]},

    # =========================================================================
    # 3. CLOUD & DEVOPS
    # =========================================================================
    {"name": "AWS", "category": "Cloud/DevOps", "is_tech": True, "aliases": ["amazon web services", "ec2", "s3", "lambda", "rds", "cloudformation"]},
    {"name": "Azure", "category": "Cloud/DevOps", "is_tech": True, "aliases": ["microsoft azure", "azure devops"]},
    {"name": "Google Cloud", "category": "Cloud/DevOps", "is_tech": True, "aliases": ["gcp", "google cloud platform", "bigquery cloud"]},
    {"name": "Docker", "category": "Cloud/DevOps", "is_tech": True, "aliases": ["docker-compose", "containerization"]},
    {"name": "Kubernetes", "category": "Cloud/DevOps", "is_tech": True, "aliases": ["k8s", "kubectl", "eks", "gke", "aks"]},
    {"name": "Terraform", "category": "Cloud/DevOps", "is_tech": True, "aliases": ["infrastructure as code", "iac", "terragrunt"]},
    {"name": "CI/CD", "category": "Cloud/DevOps", "is_tech": True, "aliases": ["continuous integration", "continuous delivery", "cicd"]},
    {"name": "GitHub Actions", "category": "Cloud/DevOps", "is_tech": True, "aliases": ["github action", "gh actions"]},
    {"name": "GitLab CI", "category": "Cloud/DevOps", "is_tech": True, "aliases": ["gitlab-ci"]},
    {"name": "Jenkins", "category": "Cloud/DevOps", "is_tech": True, "aliases": []},
    {"name": "Ansible", "category": "Cloud/DevOps", "is_tech": True, "aliases": []},
    {"name": "Prometheus", "category": "Cloud/DevOps", "is_tech": True, "aliases": ["grafana", "monitoring"]},
    {"name": "Helm", "category": "Cloud/DevOps", "is_tech": True, "aliases": ["helm charts"]},
    {"name": "Linux", "category": "Cloud/DevOps", "is_tech": True, "aliases": ["ubuntu", "debian", "centos", "rhel", "unix"]},
    {"name": "Serverless", "category": "Cloud/DevOps", "is_tech": True, "aliases": ["aws lambda", "cloud functions"]},
    {"name": "OpenTelemetry", "category": "Cloud/DevOps", "is_tech": True, "aliases": ["otel", "observability", "datadog", "new relic"]},

    # =========================================================================
    # 4. DATABASES & STORAGE
    # =========================================================================
    {"name": "PostgreSQL", "category": "Databases", "is_tech": True, "aliases": ["postgres", "postgresql 14", "postgresql 15", "psql"]},
    {"name": "MySQL", "category": "Databases", "is_tech": True, "aliases": ["mariadb"]},
    {"name": "MongoDB", "category": "Databases", "is_tech": True, "aliases": ["mongo", "nosql mongodb"]},
    {"name": "Redis", "category": "Databases", "is_tech": True, "aliases": ["redis cache", "in-memory"]},
    {"name": "Elasticsearch", "category": "Databases", "is_tech": True, "aliases": ["elastic search", "opensearch", "elk stack"]},
    {"name": "Cassandra", "category": "Databases", "is_tech": True, "aliases": ["apache cassandra"]},
    {"name": "DynamoDB", "category": "Databases", "is_tech": True, "aliases": ["aws dynamodb"]},
    {"name": "Snowflake", "category": "Databases", "is_tech": True, "aliases": ["snowflake warehouse"]},
    {"name": "BigQuery", "category": "Databases", "is_tech": True, "aliases": ["google bigquery"]},
    {"name": "SQLite", "category": "Databases", "is_tech": True, "aliases": []},
    {"name": "Neo4j", "category": "Databases", "is_tech": True, "aliases": ["graph database"]},
    {"name": "ClickHouse", "category": "Databases", "is_tech": True, "aliases": ["clickhouse olap"]},

    # =========================================================================
    # 5. DATA & AI/ML
    # =========================================================================
    {"name": "Machine Learning", "category": "AI/ML", "is_tech": True, "aliases": ["ml", "applied ml", "machine learning algorithms"]},
    {"name": "Deep Learning", "category": "AI/ML", "is_tech": True, "aliases": ["neural networks", "dnn", "cnn", "rnn"]},
    {"name": "PyTorch", "category": "AI/ML", "is_tech": True, "aliases": ["torch"]},
    {"name": "TensorFlow", "category": "AI/ML", "is_tech": True, "aliases": ["tf", "keras"]},
    {"name": "Pandas", "category": "AI/ML", "is_tech": True, "aliases": ["python pandas"]},
    {"name": "NumPy", "category": "AI/ML", "is_tech": True, "aliases": []},
    {"name": "Scikit-Learn", "category": "AI/ML", "is_tech": True, "aliases": ["sklearn", "scikit learn"]},
    {"name": "NLP", "category": "AI/ML", "is_tech": True, "aliases": ["natural language processing", "text processing"]},
    {"name": "LLMs", "category": "AI/ML", "is_tech": True, "aliases": ["large language models", "gpt", "gpt-4", "claude", "gemini", "fine-tuning"]},
    {"name": "Generative AI", "category": "AI/ML", "is_tech": True, "aliases": ["genai", "generative-ai", "rag", "retrieval augmented generation"]},
    {"name": "LangChain", "category": "AI/ML", "is_tech": True, "aliases": ["langgraph", "llamaindex"]},
    {"name": "Computer Vision", "category": "AI/ML", "is_tech": True, "aliases": ["opencv", "object detection", "image segmentation"]},
    {"name": "Apache Spark", "category": "AI/ML", "is_tech": True, "aliases": ["spark", "pyspark"]},
    {"name": "Airflow", "category": "AI/ML", "is_tech": True, "aliases": ["apache airflow", "etl pipelines"]},
    {"name": "dbt", "category": "AI/ML", "is_tech": True, "aliases": ["data build tool"]},
    {"name": "Vector Databases", "category": "AI/ML", "is_tech": True, "aliases": ["pinecone", "chromadb", "weaviate", "qdrant", "milvus", "pgvector"]},
    {"name": "Databricks", "category": "AI/ML", "is_tech": True, "aliases": ["mlflow", "delta lake"]},

    # =========================================================================
    # 6. DEVELOPER TOOLS & ARCHITECTURES
    # =========================================================================
    {"name": "Git", "category": "Tools", "is_tech": True, "aliases": ["github", "gitlab", "version control", "git flow"]},
    {"name": "Microservices", "category": "Tools", "is_tech": True, "aliases": ["microservice architecture", "distributed systems"]},
    {"name": "System Design", "category": "Tools", "is_tech": True, "aliases": ["high level design", "low level design", "hld/lld", "scalable architecture"]},
    {"name": "Scrapy", "category": "Tools", "is_tech": True, "aliases": ["web scraping", "scrapy spiders", "web crawler"]},
    {"name": "BeautifulSoup", "category": "Tools", "is_tech": True, "aliases": ["bs4", "beautifulsoup4"]},
    {"name": "Selenium", "category": "Tools", "is_tech": True, "aliases": ["playwright", "puppeteer"]},
    {"name": "JIRA", "category": "Tools", "is_tech": True, "aliases": ["confluence", "atlassian"]},
    {"name": "Postman", "category": "Tools", "is_tech": True, "aliases": ["api testing", "swagger", "openapi"]},
    {"name": "Unit Testing", "category": "Tools", "is_tech": True, "aliases": ["pytest", "jest", "junit", "tdd", "mocking"]},
    {"name": "Agile", "category": "Tools", "is_tech": False, "aliases": ["scrum", "kanban", "sprint planning"]},
    {"name": "Data Structures & Algorithms", "category": "Tools", "is_tech": True, "aliases": ["dsa", "data structures", "algorithms", "leetcode"]},
    {"name": "Object-Oriented Design", "category": "Tools", "is_tech": True, "aliases": ["ood", "oop", "solid principles", "design patterns"]},
    {"name": "Low-Level Design", "category": "Tools", "is_tech": True, "aliases": ["lld", "detailed class design"]},
    {"name": "High-Level Design", "category": "Tools", "is_tech": True, "aliases": ["hld", "distributed system architecture"]},
    {"name": "Multithreading & Concurrency", "category": "Tools", "is_tech": True, "aliases": ["multithreading", "concurrency", "thread safety", "async programming"]},

    # =========================================================================
    # 7. VLSI & HARDWARE DESIGN
    # =========================================================================
    {"name": "RTL Design", "category": "VLSI/Hardware", "is_tech": True, "aliases": ["rtl", "register transfer level", "rtl coding"]},
    {"name": "UVM", "category": "VLSI/Hardware", "is_tech": True, "aliases": ["universal verification methodology", "uvm testbench", "ovm"]},
    {"name": "Physical Design", "category": "VLSI/Hardware", "is_tech": True, "aliases": ["pd", "place and route", "p&r", "floorplanning", "physical verification"]},
    {"name": "Static Timing Analysis", "category": "VLSI/Hardware", "is_tech": True, "aliases": ["sta", "timing closure", "primetime", "tempus"]},
    {"name": "ASIC Design", "category": "VLSI/Hardware", "is_tech": True, "aliases": ["asic", "soc design", "application specific integrated circuit"]},
    {"name": "FPGA", "category": "VLSI/Hardware", "is_tech": True, "aliases": ["xilinx", "altera", "vivado", "quartus", "fpga design"]},
    {"name": "DFT", "category": "VLSI/Hardware", "is_tech": True, "aliases": ["design for testability", "scan insertion", "atpg", "mbist", "bist"]},
    {"name": "Synopsys Tools", "category": "VLSI/Hardware", "is_tech": True, "aliases": ["synopsys", "design compiler", "icc2", "fusion compiler", "primetime"]},
    {"name": "Cadence Tools", "category": "VLSI/Hardware", "is_tech": True, "aliases": ["cadence", "innovus", "virtuoso", "genus", "spectre"]},
    {"name": "CMOS & Semiconductor", "category": "VLSI/Hardware", "is_tech": True, "aliases": ["vlsi", "cmos", "semiconductor", "finfet", "5nm", "7nm", "silicon design"]},
    {"name": "ModelSim / Questa", "category": "VLSI/Hardware", "is_tech": True, "aliases": ["modelsim", "questasim", "vcs", "ncsim"]},
    {"name": "Computer Architecture", "category": "VLSI/Hardware", "is_tech": True, "aliases": ["risc-v", "arm architecture", "cache hierarchy", "axi", "ahb bus"]},

    # =========================================================================
    # 8. CONSULTING & BUSINESS STRATEGY
    # =========================================================================
    {"name": "Technology Consulting", "category": "Consulting", "is_tech": False, "aliases": ["it consulting", "tech advisory", "digital consulting", "tech strategy"]},
    {"name": "Management Consulting", "category": "Consulting", "is_tech": False, "aliases": ["strategy consulting", "business consulting", "strategic advisory"]},
    {"name": "Business Analysis", "category": "Consulting", "is_tech": False, "aliases": ["business requirements", "brd", "functional requirements", "requirement analysis"]},
    {"name": "ERP & SAP", "category": "Consulting", "is_tech": True, "aliases": ["sap", "sap s/4hana", "sap ecc", "enterprise resource planning", "sap abap", "sap fico", "oracle erp"]},
    {"name": "Solution Architecture", "category": "Consulting", "is_tech": True, "aliases": ["solution design", "technical architecture", "enterprise solutions"]},
    {"name": "Digital Transformation", "category": "Consulting", "is_tech": False, "aliases": ["process reengineering", "transformation roadmap", "operating model"]},
    {"name": "Client Advisory & Delivery", "category": "Consulting", "is_tech": False, "aliases": ["client engagement", "executive presentations", "stakeholder engagement", "c-level advisory"]},
    {"name": "Financial Modeling", "category": "Consulting", "is_tech": False, "aliases": ["cost-benefit analysis", "business case development", "roi analysis"]},

    # =========================================================================
    # 9. SOFT SKILLS & LEADERSHIP
    # =========================================================================
    {"name": "Communication", "category": "Soft Skills", "is_tech": False, "aliases": ["verbal communication", "written communication", "presentation skills"]},
    {"name": "Problem Solving", "category": "Soft Skills", "is_tech": False, "aliases": ["troubleshooting", "analytical thinking", "critical thinking"]},
    {"name": "Leadership", "category": "Soft Skills", "is_tech": False, "aliases": ["team leadership", "mentorship", "guiding junior engineers"]},
    {"name": "Collaboration", "category": "Soft Skills", "is_tech": False, "aliases": ["cross-functional collaboration", "team player", "interpersonal skills"]},
    {"name": "Adaptability", "category": "Soft Skills", "is_tech": False, "aliases": ["fast learner", "flexibility", "growth mindset"]},
    {"name": "Ownership", "category": "Soft Skills", "is_tech": False, "aliases": ["self-starter", "autonomous", "proactive", "accountability"]},
    {"name": "Stakeholder Management", "category": "Soft Skills", "is_tech": False, "aliases": ["client facing", "cross-functional alignment"]},
]

# Quick lookup by normalized name
SKILL_BY_NAME: Dict[str, Dict[str, Any]] = {
    s["name"].lower(): s for s in SKILL_TAXONOMY
}
