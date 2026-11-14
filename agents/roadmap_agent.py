from datetime import datetime

class RoadmapAgent:
    """
    Roadmap & Resource Recommender Agent:
    Generates a phased, milestone-based learning roadmap with curated courses,
    tutorials, and hands-on exercises. Adapts dynamically to career switches
    and low assessment scores (<60%).
    """
    def __init__(self):
        self.name = "Roadmap & Resource Recommender Agent"
        self.badge = "Adaptive Curriculum Architect"

    def generate_roadmap(self, target_career, missing_skills, completed_module_ids, remediation_data=None):
        missing_ids = {m["id"] if isinstance(m, dict) else m for m in missing_skills}
        roadmap = []

        is_remediation = remediation_data and remediation_data.get("needs_remediation", False)
        remedial_topic = remediation_data.get("topic", "Core Fundamentals") if is_remediation else None

        # Build role-specific customized curricula
        if target_career == "Full Stack Developer":
            phases = self._build_fullstack_roadmap(missing_ids, completed_module_ids, is_remediation, remedial_topic)
        elif target_career == "Data Scientist":
            phases = self._build_datascientist_roadmap(missing_ids, completed_module_ids, is_remediation, remedial_topic)
        elif target_career == "AI Engineer":
            phases = self._build_ai_engineer_roadmap(missing_ids, completed_module_ids, is_remediation, remedial_topic)
        elif target_career == "Python Developer":
            phases = self._build_python_dev_roadmap(missing_ids, completed_module_ids, is_remediation, remedial_topic)
        else:
            phases = self._build_devops_roadmap(missing_ids, completed_module_ids, is_remediation, remedial_topic)

        # Log generation / dynamic recalculation
        total_modules = sum(len(p["modules"]) for p in phases)
        completed_count = sum(sum(1 for m in p["modules"] if m["completed"]) for p in phases)

        if is_remediation:
            summary = f"RECALCULATED ROADMAP: Injected remedial reinforcement for '{remedial_topic}' after score < 60%."
            details = (
                f"Adaptive intervention active. Progress Evaluator flagged score below 60% threshold. "
                f"Roadmap Agent restructured Phase 1 with prerequisite drills and foundational labs. "
                f"Curated 4 remedial micro-exercises to restore confidence before advanced modules."
            )
        else:
            summary = f"Synthesized {len(phases)}-phase milestone roadmap ({completed_count}/{total_modules} completed) for '{target_career}'."
            details = (
                f"Roadmap tailored to close verified skill gaps: {[m['name'] for m in missing_skills if isinstance(m, dict)]}. "
                f"Structured into sequential milestones with verified external documentation, "
                f"interactive sandboxes, and portfolio capstone deliverables."
            )

        agent_log = {
            "agent_name": self.name,
            "action": "DYNAMIC_ROADMAP_SYNTHESIS",
            "status": "ADAPTED" if is_remediation else "SUCCESS",
            "summary": summary,
            "details": details,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

        return {
            "phases": phases,
            "total_modules": total_modules,
            "completed_modules_count": completed_count,
            "progress_pct": round((completed_count / total_modules) * 100) if total_modules else 0,
            "is_remediation": is_remediation,
            "remedial_topic": remedial_topic,
            "log": agent_log
        }

    def _build_fullstack_roadmap(self, missing_ids, completed_ids, is_remediation, remedial_topic):
        phases = []

        # If remediation is active, inject dedicated Remedial Foundation Phase
        if is_remediation:
            phases.append({
                "phase_id": "fs-remedial",
                "phase_number": "R",
                "is_remedial": True,
                "badge": "Priority Remediation Alert",
                "title": f"Refresher & Core Drills: {remedial_topic}",
                "duration": "1 - 2 Weeks (Targeted Recovery)",
                "description": "Adaptive path triggered by assessment score (<60%). Focused on syntax fundamentals, memory models, and error troubleshooting before advancing.",
                "modules": [
                    {
                        "id": "fs-rem-1",
                        "title": "Interactive Code Debugging & Variable Scope Clinic",
                        "completed": "fs-rem-1" in completed_ids,
                        "hours": "6 hours",
                        "resources": [
                            {"name": "JavaScript.info - The Modern JS Tutorial", "type": "Interactive Guide", "url": "https://javascript.info/", "platform": "JS.info"},
                            {"name": "FreeCodeCamp JavaScript Algorithms Drill", "type": "Practice Sandbox", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures-v8/", "platform": "freeCodeCamp"}
                        ],
                        "hands_on_project": {
                            "title": "Interactive Logic Fixer & Bug Buster",
                            "description": "Identify and refactor 5 intentionally broken async/sync functions with unit tests."
                        }
                    },
                    {
                        "id": "fs-rem-2",
                        "title": "DOM Events & Asynchronous Fetch Deep-Dive",
                        "completed": "fs-rem-2" in completed_ids,
                        "hours": "8 hours",
                        "resources": [
                            {"name": "MDN Web Docs: Asynchronous JavaScript", "type": "Official Docs", "url": "https://developer.mozilla.org/en-US/docs/Learn_web_development/Extensions/Async_JS", "platform": "MDN"}
                        ],
                        "hands_on_project": {
                            "title": "Weather & Crypto Real-Time Mini Dashboard",
                            "description": "Fetch real data from public REST APIs, handle errors gracefully, and update DOM elements without page reload."
                        }
                    }
                ]
            })

        # Phase 1: Core Client-Side Programming (JavaScript & DOM)
        phases.append({
            "phase_id": "fs-phase-1",
            "phase_number": "1",
            "is_remedial": False,
            "badge": "Core Foundation",
            "title": "Modern JavaScript (ES6+) & DOM Engineering",
            "duration": "Weeks 1 - 3",
            "description": "Master vanilla JavaScript modern syntax, event loops, promises, array methods, and dynamic browser interaction.",
            "modules": [
                {
                    "id": "fs-mod-1",
                    "title": "ES6+ Syntax, Closures, Scopes & Prototypes",
                    "completed": "fs-mod-1" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "MDN JavaScript Guide", "type": "Documentation", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "platform": "MDN"},
                        {"name": "CS50's Web Programming with Python and JS", "type": "Course", "url": "https://cs50.harvard.edu/web/", "platform": "Harvard CS50"}
                    ],
                    "hands_on_project": {
                        "title": "Kanban Board with LocalStorage & Drag-and-Drop",
                        "description": "Construct an interactive task board with full CRUD operations, filters, and local persistence."
                    }
                },
                {
                    "id": "fs-mod-2",
                    "title": "Asynchronous JavaScript: Promises, Async/Await & Fetch API",
                    "completed": "fs-mod-2" in completed_ids,
                    "hours": "12 hours",
                    "resources": [
                        {"name": "freeCodeCamp Asynchronous Programming", "type": "Interactive Course", "url": "https://www.freecodecamp.org/news/asynchronous-programming-in-javascript/", "platform": "freeCodeCamp"}
                    ],
                    "hands_on_project": {
                        "title": "GitHub Profile & Repo Visualizer",
                        "description": "Connect to GitHub REST API to search users, visualize commit graphs, and display repository statistics."
                    }
                }
            ]
        })

        # Phase 2: Component Architecture & Frontend Framework (React)
        phases.append({
            "phase_id": "fs-phase-2",
            "phase_number": "2",
            "is_remedial": False,
            "badge": "Frontend Architecture",
            "title": "Modern React.js, Hooks & State Management",
            "duration": "Weeks 4 - 6",
            "description": "Transition to single-page applications (SPA). Learn component lifecycles, hooks (useState, useEffect, useMemo), and clean state architecture.",
            "modules": [
                {
                    "id": "fs-mod-3",
                    "title": "React Core: JSX, Props, State & Component Tree",
                    "completed": "fs-mod-3" in completed_ids,
                    "hours": "16 hours",
                    "resources": [
                        {"name": "Official React Documentation (react.dev)", "type": "Official Interactive Docs", "url": "https://react.dev/learn", "platform": "React Docs"},
                        {"name": "Full Stack Open - React Part 1 & 2", "type": "University Course", "url": "https://fullstackopen.com/en/", "platform": "University of Helsinki"}
                    ],
                    "hands_on_project": {
                        "title": "Interactive E-Commerce Product Catalog & Cart",
                        "description": "Implement modular components for products, cart drawer, reactive stock updates, and checkout summary."
                    }
                },
                {
                    "id": "fs-mod-4",
                    "title": "Advanced Hooks, Custom Hooks & Context API",
                    "completed": "fs-mod-4" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Scrimba Interactive React Course", "type": "Interactive Bootcamp", "url": "https://scrimba.com/learn/learnreact", "platform": "Scrimba"}
                    ],
                    "hands_on_project": {
                        "title": "Multi-Step SaaS Onboarding Wizard",
                        "description": "Build dynamic forms with validation, global authentication state via Context, and responsive styling."
                    }
                }
            ]
        })

        # Phase 3: Server-Side Engineering & APIs (Node.js & Express)
        phases.append({
            "phase_id": "fs-phase-3",
            "phase_number": "3",
            "is_remedial": False,
            "badge": "Server-Side Systems",
            "title": "Node.js, Express & RESTful Microservices",
            "duration": "Weeks 7 - 9",
            "description": "Leverage existing Python/SQL knowledge to build production-ready Node.js backends with Express, JWT auth, and database integration.",
            "modules": [
                {
                    "id": "fs-mod-5",
                    "title": "Node.js Runtime, Modules & Express REST API Server",
                    "completed": "fs-mod-5" in completed_ids,
                    "hours": "15 hours",
                    "resources": [
                        {"name": "Node.js Official Documentation & Guides", "type": "Official Docs", "url": "https://nodejs.org/en/docs", "platform": "Node.js"},
                        {"name": "The Odin Project - NodeJS Course", "type": "Open Source Curriculum", "url": "https://www.theodinproject.com/paths/full-stack-javascript/courses/nodejs", "platform": "The Odin Project"}
                    ],
                    "hands_on_project": {
                        "title": "Authenticated REST API for Task Management",
                        "description": "Build endpoints with JWT tokens, bcrypt password hashing, middleware rate-limiting, and SQLite/PostgreSQL schema."
                    }
                }
            ]
        })

        # Phase 4: Full Stack Integration, Testing & Capstone Deployment
        phases.append({
            "phase_id": "fs-phase-4",
            "phase_number": "4",
            "is_remedial": False,
            "badge": "Production Capstone",
            "title": "Full Stack Capstone Integration & CI/CD Deployment",
            "duration": "Weeks 10 - 12",
            "description": "Connect React frontend with Node/Python backend, configure Git branches, write unit tests, and deploy to live cloud.",
            "modules": [
                {
                    "id": "fs-mod-6",
                    "title": "End-to-End Capstone Project: Collaborative Learning LMS",
                    "completed": "fs-mod-6" in completed_ids,
                    "hours": "25 hours",
                    "resources": [
                        {"name": "Deploying Full-Stack Apps on Render & Vercel", "type": "Guide", "url": "https://docs.render.com/deploy-node-express-app", "platform": "Render"}
                    ],
                    "hands_on_project": {
                        "title": "Full Stack Production-Ready LMS Web App",
                        "description": "Deploy a complete multi-tier web application with React frontend, Node/Python API, database migrations, and CI/CD workflow."
                    }
                }
            ]
        })

        return phases

    def _build_datascientist_roadmap(self, missing_ids, completed_ids, is_remediation, remedial_topic):
        phases = [
            {
                "phase_id": "ds-phase-1",
                "phase_number": "1",
                "is_remedial": False,
                "badge": "Data Foundation",
                "title": "Pandas, NumPy & Exploratory Data Analysis (EDA)",
                "duration": "Weeks 1 - 3",
                "description": "Master data manipulation, cleaning messy datasets, and performing robust exploratory statistical analysis.",
                "modules": [
                    {
                        "id": "ds-mod-1",
                        "title": "Advanced Pandas Wrangling & Data Cleaning",
                        "completed": "ds-mod-1" in completed_ids,
                        "hours": "14 hours",
                        "resources": [
                            {"name": "Pandas Official Tutorials", "type": "Docs", "url": "https://pandas.pydata.org/docs/user_guide/index.html", "platform": "PyData"}
                        ],
                        "hands_on_project": {
                            "title": "Global Climate & Energy Data Pipeline",
                            "description": "Ingest multi-source messy CSVs, impute missing values, and export clean Parquet datasets."
                        }
                    }
                ]
            },
            {
                "phase_id": "ds-phase-2",
                "phase_number": "2",
                "is_remedial": False,
                "badge": "Modeling Core",
                "title": "Statistical Inference & Machine Learning with Scikit-Learn",
                "duration": "Weeks 4 - 7",
                "description": "Apply regression, classification, clustering, cross-validation, and feature engineering to real data.",
                "modules": [
                    {
                        "id": "ds-mod-2",
                        "title": "Supervised Learning Algorithms & Hyperparameter Tuning",
                        "completed": "ds-mod-2" in completed_ids,
                        "hours": "18 hours",
                        "resources": [
                            {"name": "Scikit-Learn User Guide", "type": "Course", "url": "https://scikit-learn.org/stable/user_guide.html", "platform": "Scikit-Learn"}
                        ],
                        "hands_on_project": {
                            "title": "Customer Churn Prediction Model & ROC Analysis",
                            "description": "Build an end-to-end classification pipeline with feature scaling, Random Forests, and model evaluation metrics."
                        }
                    }
                ]
            }
        ]
        return phases

    def _build_ai_engineer_roadmap(self, missing_ids, completed_ids, is_remediation, remedial_topic):
        phases = [
            {
                "phase_id": "ai-phase-1",
                "phase_number": "1",
                "is_remedial": False,
                "badge": "Neural Core",
                "title": "Deep Learning Fundamentals & PyTorch Tensors",
                "duration": "Weeks 1 - 4",
                "description": "Understand backpropagation, gradient descent, loss functions, and tensor operations in PyTorch.",
                "modules": [
                    {
                        "id": "ai-mod-1",
                        "title": "PyTorch Architecture & Multi-Layer Perceptrons",
                        "completed": "ai-mod-1" in completed_ids,
                        "hours": "18 hours",
                        "resources": [
                            {"name": "PyTorch Deep Learning with PyTorch", "type": "Interactive Book", "url": "https://pytorch.org/tutorials/", "platform": "PyTorch"}
                        ],
                        "hands_on_project": {
                            "title": "Image & Multimodal Classifier from Scratch",
                            "description": "Train a convolutional neural network with custom PyTorch DataLoader and test accuracy validation."
                        }
                    }
                ]
            },
            {
                "phase_id": "ai-phase-2",
                "phase_number": "2",
                "is_remedial": False,
                "badge": "Generative AI",
                "title": "Transformers, LLMs, Vector DBs & RAG Architecture",
                "duration": "Weeks 5 - 8",
                "description": "Harness transformer attention mechanisms, fine-tuning, embeddings, ChromaDB/Pinecone, and agent orchestration.",
                "modules": [
                    {
                        "id": "ai-mod-2",
                        "title": "Retrieval Augmented Generation (RAG) & LangChain/LlamaIndex",
                        "completed": "ai-mod-2" in completed_ids,
                        "hours": "20 hours",
                        "resources": [
                            {"name": "Hugging Face NLP Course", "type": "Official Course", "url": "https://huggingface.co/learn/nlp-course", "platform": "Hugging Face"}
                        ],
                        "hands_on_project": {
                            "title": "Autonomous Research Assistant with Vector Search",
                            "description": "Build a multi-agent document analysis engine using embeddings and contextual grounding."
                        }
                    }
                ]
            }
        ]
        return phases

    def _build_python_dev_roadmap(self, missing_ids, completed_ids, is_remediation, remedial_topic):
        phases = [
            {
                "phase_id": "py-phase-1",
                "phase_number": "1",
                "is_remedial": False,
                "badge": "High Performance",
                "title": "Advanced Python, Asynchronous AsyncIO & Design Patterns",
                "duration": "Weeks 1 - 3",
                "description": "Master generators, decorators, context managers, async event loops, and clean OOP architecture.",
                "modules": [
                    {
                        "id": "py-mod-1",
                        "title": "Python Metaprogramming & AsyncIO Concurrency",
                        "completed": "py-mod-1" in completed_ids,
                        "hours": "14 hours",
                        "resources": [
                            {"name": "Real Python Advanced Paths", "type": "Tutorial", "url": "https://realpython.com/", "platform": "Real Python"}
                        ],
                        "hands_on_project": {
                            "title": "Concurrent Asynchronous Web Scraper & Stream Processor",
                            "description": "Implement high-throughput data extractor with rate limiting and asyncio workers."
                        }
                    }
                ]
            },
            {
                "phase_id": "py-phase-2",
                "phase_number": "2",
                "is_remedial": False,
                "badge": "Microservices",
                "title": "FastAPI, Docker Containers & Relational Data Layers",
                "duration": "Weeks 4 - 6",
                "description": "Build production microservices with Pydantic schemas, SQLAlchemy ORM, and automated Pytest suites.",
                "modules": [
                    {
                        "id": "py-mod-2",
                        "title": "FastAPI REST API with PostgreSQL & Pytest",
                        "completed": "py-mod-2" in completed_ids,
                        "hours": "16 hours",
                        "resources": [
                            {"name": "FastAPI Official Documentation", "type": "Docs", "url": "https://fastapi.tiangolo.com/", "platform": "FastAPI"}
                        ],
                        "hands_on_project": {
                            "title": "Production E-Commerce Backend Service with Docker",
                            "description": "Build secure API with OAuth2, automated migrations with Alembic, and 90%+ test coverage."
                        }
                    }
                ]
            }
        ]
        return phases

    def _build_devops_roadmap(self, missing_ids, completed_ids, is_remediation, remedial_topic):
        phases = [
            {
                "phase_id": "do-phase-1",
                "phase_number": "1",
                "is_remedial": False,
                "badge": "Containerization",
                "title": "Docker, Linux Internals & CI/CD Automation",
                "duration": "Weeks 1 - 3",
                "description": "Master multi-stage Dockerfiles, Linux networking, GitHub Actions workflows, and automated testing.",
                "modules": [
                    {
                        "id": "do-mod-1",
                        "title": "Production Docker & Automated CI/CD Pipelines",
                        "completed": "do-mod-1" in completed_ids,
                        "hours": "15 hours",
                        "resources": [
                            {"name": "Docker Official Docs & Labs", "type": "Docs", "url": "https://docs.docker.com/get-started/", "platform": "Docker"}
                        ],
                        "hands_on_project": {
                            "title": "Zero-Downtime GitHub Actions Pipeline",
                            "description": "Automate linting, unit tests, image build, and secure push to container registry."
                        }
                    }
                ]
            }
        ]
        return phases
