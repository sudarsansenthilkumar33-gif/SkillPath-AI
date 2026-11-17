from datetime import datetime
from typing import List, Dict, Any, Optional

class RoadmapAgent:
    """
    Roadmap & Resource Recommender Agent:
    Generates a phased, milestone-based learning roadmap with 9 to 12 curated,
    actionable modules across Phase 1 (Foundations & Missing Skills),
    Phase 2 (Hands-On Capstone Builds), and Phase 3 (Production Deployment & Interview Mastery).
    Adapts dynamically to career switches, custom user milestones, and low assessment scores (<60%).
    """
    def __init__(self):
        self.name = "Roadmap & Resource Recommender Agent"
        self.badge = "Adaptive Curriculum Architect"

    def generate_roadmap(self, target_career: str, missing_skills: Any, completed_module_ids: Any, remediation_data: Optional[Dict[str, Any]] = None, custom_modules: Optional[List[Dict[str, Any]]] = None):
        missing_ids = {m["id"] if isinstance(m, dict) else m for m in missing_skills} if missing_skills else set()
        completed_ids = set(completed_module_ids) if completed_module_ids else set()

        is_remediation = remediation_data and remediation_data.get("needs_remediation", False)
        remedial_topic = remediation_data.get("topic", "Core Fundamentals") if is_remediation else None

        # Build role-specific customized curricula (9 - 12 modules per role across 3 phases)
        if target_career == "Full Stack Developer":
            phases = self._build_fullstack_roadmap(missing_ids, completed_ids, is_remediation, remedial_topic)
        elif target_career == "Data Scientist":
            phases = self._build_datascientist_roadmap(missing_ids, completed_ids, is_remediation, remedial_topic)
        elif target_career == "AI Engineer":
            phases = self._build_ai_engineer_roadmap(missing_ids, completed_ids, is_remediation, remedial_topic)
        elif target_career == "Python Developer":
            phases = self._build_python_dev_roadmap(missing_ids, completed_ids, is_remediation, remedial_topic)
        else:
            phases = self._build_devops_roadmap(missing_ids, completed_ids, is_remediation, remedial_topic)

        # Inject user custom modules into corresponding phases
        if custom_modules:
            for cm in custom_modules:
                p_num = str(cm.get("phase_number", "2"))
                target_p = None
                for p in phases:
                    if str(p.get("phase_number")) == p_num:
                        target_p = p
                        break
                if not target_p and phases:
                    target_p = phases[min(1, len(phases) - 1)]

                if target_p:
                    mod_id = f"custom-mod-{cm['id']}"
                    target_p["modules"].append({
                        "id": mod_id,
                        "title": cm["title"],
                        "completed": bool(cm.get("completed", 0) or mod_id in completed_ids),
                        "hours": cm.get("hours") or "8 hours",
                        "is_custom": True,
                        "custom_id": cm["id"],
                        "resources": [
                            {"name": "Self-Directed Resource", "type": "Documentation", "url": cm.get("resource_url") or "#", "platform": "Learner Selected"}
                        ] if cm.get("resource_url") else [
                            {"name": "SkillPath Practical Milestone Lab", "type": "Self-Paced Lab", "url": "#", "platform": "SkillPath AI"}
                        ],
                        "hands_on_project": {
                            "title": f"Custom Deliverable: {cm['title']}",
                            "description": cm.get("project_desc") or "Deliverable milestone set by user to demonstrate topic mastery."
                        }
                    })

        # Calculate module counts and progress
        total_modules = sum(len(p["modules"]) for p in phases)
        completed_count = sum(sum(1 for m in p["modules"] if m["completed"]) for p in phases)

        if is_remediation:
            summary = f"RECALCULATED ROADMAP: Injected remedial reinforcement for '{remedial_topic}' after score < 60%."
            details = (
                f"Adaptive intervention active. Progress Evaluator flagged score below 60% threshold. "
                f"Roadmap Agent restructured Phase 1 with prerequisite drills and foundational labs. "
                f"Curated remedial micro-exercises to restore confidence before advanced modules."
            )
        else:
            summary = f"Synthesized {len(phases)}-phase milestone roadmap ({completed_count}/{total_modules} completed) for '{target_career}'."
            details = (
                f"Roadmap tailored to close verified skill gaps: {[m['name'] for m in missing_skills if isinstance(m, dict)]}. "
                f"Structured into sequential milestones across Foundations, Hands-On Builds, and Production Mastery."
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

    # ==========================================================================
    # 1. Full Stack Developer (10 Actionable Modules across 3 Phases)
    # ==========================================================================
    def _build_fullstack_roadmap(self, missing_ids, completed_ids, is_remediation, remedial_topic):
        phases = []

        if is_remediation:
            phases.append({
                "phase_id": "fs-remedial",
                "phase_number": "R",
                "is_remedial": True,
                "badge": "Priority Remediation Alert",
                "title": f"Refresher & Core Drills: {remedial_topic}",
                "duration": "1 - 2 Weeks (Targeted Recovery)",
                "description": "Adaptive path triggered by assessment score (<60%). Focused on syntax fundamentals, memory models, and error troubleshooting.",
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

        # Phase 1: Foundations & Missing Skills (3 Modules)
        phases.append({
            "phase_id": "fs-phase-1",
            "phase_number": "1",
            "is_remedial": False,
            "badge": "Phase 1: Foundations & Missing Skills",
            "title": "Modern JavaScript (ES6+), Asynchronous Execution & DOM Engineering",
            "duration": "Weeks 1 - 3",
            "description": "Master vanilla JavaScript modern syntax, event loops, promises, array methods, and responsive browser layout engineering.",
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
                        "title": "Interactive Kanban Board with LocalStorage & Drag-and-Drop",
                        "description": "Construct an interactive task board with full CRUD operations, state persistence, and keyboard accessibility."
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
                        "title": "GitHub Profile & Public Repository Visualizer",
                        "description": "Connect to GitHub REST API to search users, visualize commit graphs, and display repository statistics."
                    }
                },
                {
                    "id": "fs-mod-3",
                    "title": "Semantic HTML5, CSS Grid, Flexbox & Responsive Layouts",
                    "completed": "fs-mod-3" in completed_ids,
                    "hours": "10 hours",
                    "resources": [
                        {"name": "web.dev Responsive Design Patterns", "type": "Guide", "url": "https://web.dev/learn/design/", "platform": "Google Chrome"}
                    ],
                    "hands_on_project": {
                        "title": "Pixel-Perfect Accessible SaaS Landing Page",
                        "description": "Build a WCAG 2.1 AAA accessible landing page with dark/light theme switching and responsive mobile drawers."
                    }
                }
            ]
        })

        # Phase 2: Hands-On Capstone Builds (4 Modules)
        phases.append({
            "phase_id": "fs-phase-2",
            "phase_number": "2",
            "is_remedial": False,
            "badge": "Phase 2: Hands-On Capstone Builds",
            "title": "Modern React.js, Full Stack APIs & Scalable Databases",
            "duration": "Weeks 4 - 8",
            "description": "Build end-to-end full stack web applications with React component architecture, Node.js REST APIs, and relational schemas.",
            "modules": [
                {
                    "id": "fs-mod-4",
                    "title": "React.js Core: JSX, State, Hooks & Component Trees",
                    "completed": "fs-mod-4" in completed_ids,
                    "hours": "16 hours",
                    "resources": [
                        {"name": "Official React Documentation (react.dev)", "type": "Interactive Docs", "url": "https://react.dev/learn", "platform": "React Docs"}
                    ],
                    "hands_on_project": {
                        "title": "Interactive E-Commerce Product Catalog & Cart Drawer",
                        "description": "Implement modular components for products, reactive cart drawer, live inventory filters, and checkout summary."
                    }
                },
                {
                    "id": "fs-mod-5",
                    "title": "Advanced React: Context API, Redux Toolkit & Client-Side Routing",
                    "completed": "fs-mod-5" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Full Stack Open - React State Management", "type": "University Course", "url": "https://fullstackopen.com/en/", "platform": "University of Helsinki"}
                    ],
                    "hands_on_project": {
                        "title": "Multi-Step SaaS Onboarding Wizard with Global State",
                        "description": "Build multi-step interactive onboarding flow with form validation, route guards, and session state."
                    }
                },
                {
                    "id": "fs-mod-6",
                    "title": "Node.js & Express RESTful Microservices Architecture",
                    "completed": "fs-mod-6" in completed_ids,
                    "hours": "16 hours",
                    "resources": [
                        {"name": "The Odin Project - NodeJS Course", "type": "Open Source Curriculum", "url": "https://www.theodinproject.com/paths/full-stack-javascript/courses/nodejs", "platform": "The Odin Project"}
                    ],
                    "hands_on_project": {
                        "title": "Authenticated REST API with JWT, Bcrypt & Rate Limiting",
                        "description": "Build high-throughput JSON endpoints with secure authentication tokens, error middleware, and logging."
                    }
                },
                {
                    "id": "fs-mod-7",
                    "title": "PostgreSQL, Prisma ORM & Scalable Database Schemas",
                    "completed": "fs-mod-7" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Prisma ORM Getting Started Guides", "type": "Documentation", "url": "https://www.prisma.io/docs", "platform": "Prisma"}
                    ],
                    "hands_on_project": {
                        "title": "Multi-Tenant Team Collaboration Data Schema",
                        "description": "Design normalized relational schemas with foreign keys, compound indexes, and automated migration scripts."
                    }
                }
            ]
        })

        # Phase 3: Production Deployment & Interview Mastery (3 Modules)
        phases.append({
            "phase_id": "fs-phase-3",
            "phase_number": "3",
            "is_remedial": False,
            "badge": "Phase 3: Production Deployment & Interview Mastery",
            "title": "Docker Containers, Cloud CI/CD Deployment & Technical Interview Mastery",
            "duration": "Weeks 9 - 12",
            "description": "Deploy production applications to cloud environments with automated testing pipelines and conquer technical interview loops.",
            "modules": [
                {
                    "id": "fs-mod-8",
                    "title": "Containerization with Docker & GitHub Actions CI/CD",
                    "completed": "fs-mod-8" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Docker Official Documentation", "type": "Docs", "url": "https://docs.docker.com/get-started/", "platform": "Docker"}
                    ],
                    "hands_on_project": {
                        "title": "Zero-Downtime Containerized CI/CD Deployment Pipeline",
                        "description": "Author multi-stage Dockerfiles and automated GitHub Actions workflow to run unit tests and deploy artifacts."
                    }
                },
                {
                    "id": "fs-mod-9",
                    "title": "Full Stack Capstone LMS Web Application Deployment",
                    "completed": "fs-mod-9" in completed_ids,
                    "hours": "22 hours",
                    "resources": [
                        {"name": "Deploying Full-Stack Apps on Render & Vercel", "type": "Guide", "url": "https://docs.render.com/deploy-node-express-app", "platform": "Render"}
                    ],
                    "hands_on_project": {
                        "title": "Production-Ready EdTech LMS Platform with Live Database",
                        "description": "Deploy a complete multi-tier web application with React UI, Express/Python backend, SQLite/Postgres DB, and SSL."
                    }
                },
                {
                    "id": "fs-mod-10",
                    "title": "System Design, Web Security (CORS/CSRF) & Interview Mastery",
                    "completed": "fs-mod-10" in completed_ids,
                    "hours": "12 hours",
                    "resources": [
                        {"name": "OWASP Top Ten Security Vulnerabilities", "type": "Standard", "url": "https://owasp.org/www-project-top-ten/", "platform": "OWASP"}
                    ],
                    "hands_on_project": {
                        "title": "High-Availability System Design Blueprint & Mock Defense",
                        "description": "Diagram caching (Redis), horizontal scaling, CDN distribution, and defend architectural trade-offs in live mock interview."
                    }
                }
            ]
        })

        return phases

    # ==========================================================================
    # 2. Data Scientist (10 Actionable Modules across 3 Phases)
    # ==========================================================================
    def _build_datascientist_roadmap(self, missing_ids, completed_ids, is_remediation, remedial_topic):
        phases = []

        if is_remediation:
            phases.append({
                "phase_id": "ds-remedial",
                "phase_number": "R",
                "is_remedial": True,
                "badge": "Priority Remediation Alert",
                "title": f"Refresher & Core Drills: {remedial_topic}",
                "duration": "1 - 2 Weeks (Targeted Recovery)",
                "description": "Adaptive path triggered by assessment score (<60%). Focused on statistical foundations, probability, and array computing.",
                "modules": [
                    {
                        "id": "ds-rem-1",
                        "title": "Python Data Structures, NumPy Arrays & Vectorized Ops",
                        "completed": "ds-rem-1" in completed_ids,
                        "hours": "6 hours",
                        "resources": [
                            {"name": "NumPy Quickstart Tutorial", "type": "Official Tutorial", "url": "https://numpy.org/doc/stable/user/quickstart.html", "platform": "NumPy"}
                        ],
                        "hands_on_project": {
                            "title": "Vectorized Matrix Calculator & Stat Validator",
                            "description": "Implement dot products, broadcasting, and covariance matrices without external libraries."
                        }
                    }
                ]
            })

        # Phase 1: Foundations & Missing Skills (3 Modules)
        phases.append({
            "phase_id": "ds-phase-1",
            "phase_number": "1",
            "is_remedial": False,
            "badge": "Phase 1: Foundations & Missing Skills",
            "title": "Pandas, NumPy Wrangling & Exploratory Statistical Analysis (EDA)",
            "duration": "Weeks 1 - 3",
            "description": "Master data manipulation, missing value imputation, and exploratory data visualization.",
            "modules": [
                {
                    "id": "ds-mod-1",
                    "title": "Advanced Pandas Wrangling & Data Cleaning Pipelines",
                    "completed": "ds-mod-1" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Pandas Official Tutorials", "type": "Docs", "url": "https://pandas.pydata.org/docs/user_guide/index.html", "platform": "PyData"}
                    ],
                    "hands_on_project": {
                        "title": "Global Climate & Energy Multi-Source Data Pipeline",
                        "description": "Ingest multi-source messy CSVs, impute missing values, detect outliers, and export clean Parquet datasets."
                    }
                },
                {
                    "id": "ds-mod-2",
                    "title": "Exploratory Data Analysis (EDA) with Matplotlib & Seaborn",
                    "completed": "ds-mod-2" in completed_ids,
                    "hours": "12 hours",
                    "resources": [
                        {"name": "Seaborn Statistical Data Visualization", "type": "Interactive Guide", "url": "https://seaborn.pydata.org/tutorial.html", "platform": "Seaborn"}
                    ],
                    "hands_on_project": {
                        "title": "Consumer Behavior & Market Basket Distribution Dashboard",
                        "description": "Generate correlation heatmaps, violin plots, and multi-variable distribution charts to surface business insights."
                    }
                },
                {
                    "id": "ds-mod-3",
                    "title": "Applied Linear Algebra, Calculus & Inferential Statistics",
                    "completed": "ds-mod-3" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Khan Academy Statistics & Probability", "type": "Interactive Course", "url": "https://www.khanacademy.org/math/statistics-probability", "platform": "Khan Academy"}
                    ],
                    "hands_on_project": {
                        "title": "Hypothesis Testing & Statistical Significance Validator",
                        "description": "Formulate null hypotheses, run two-tailed t-tests and ANOVA, and compute p-values and confidence intervals."
                    }
                }
            ]
        })

        # Phase 2: Hands-On Capstone Builds (4 Modules)
        phases.append({
            "phase_id": "ds-phase-2",
            "phase_number": "2",
            "is_remedial": False,
            "badge": "Phase 2: Hands-On Capstone Builds",
            "title": "Supervised Learning, Feature Engineering & Advanced Modeling",
            "duration": "Weeks 4 - 8",
            "description": "Build end-to-end predictive machine learning systems with Scikit-Learn, XGBoost, and relational SQL queries.",
            "modules": [
                {
                    "id": "ds-mod-4",
                    "title": "Supervised Learning Algorithms & Cross-Validation with Scikit-Learn",
                    "completed": "ds-mod-4" in completed_ids,
                    "hours": "18 hours",
                    "resources": [
                        {"name": "Scikit-Learn User Guide", "type": "Course", "url": "https://scikit-learn.org/stable/user_guide.html", "platform": "Scikit-Learn"}
                    ],
                    "hands_on_project": {
                        "title": "Customer Churn Prediction Model & ROC-AUC Optimization",
                        "description": "Build classification pipeline with Random Forests and XGBoost, tuning hyper-parameters via StratifiedKFold."
                    }
                },
                {
                    "id": "ds-mod-5",
                    "title": "Unsupervised Learning: Clustering (K-Means, DBSCAN) & PCA",
                    "completed": "ds-mod-5" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Google Machine Learning Crash Course", "type": "Interactive Course", "url": "https://developers.google.com/machine-learning/crash-course", "platform": "Google"}
                    ],
                    "hands_on_project": {
                        "title": "Customer Segmentation Engine with PCA Dimensionality Reduction",
                        "description": "Cluster customer transaction behaviors in reduced 2D/3D space with silhouette score benchmarking."
                    }
                },
                {
                    "id": "ds-mod-6",
                    "title": "Advanced SQL for Data Science: Window Functions & CTEs",
                    "completed": "ds-mod-6" in completed_ids,
                    "hours": "12 hours",
                    "resources": [
                        {"name": "Mode Analytics SQL Tutorial for Data Analysis", "type": "Interactive Tutorial", "url": "https://mode.com/sql-tutorial/", "platform": "Mode Analytics"}
                    ],
                    "hands_on_project": {
                        "title": "Cohort Retention & Revenue Funnel Query Suite",
                        "description": "Write advanced SQL queries with RANK(), LEAD(), LAG(), and recursive CTEs to calculate monthly recurring revenue."
                    }
                },
                {
                    "id": "ds-mod-7",
                    "title": "Time Series Forecasting: ARIMA, Prophet & Exponential Smoothing",
                    "completed": "ds-mod-7" in completed_ids,
                    "hours": "16 hours",
                    "resources": [
                        {"name": "Meta Prophet Forecasting Documentation", "type": "Docs", "url": "https://facebook.github.io/prophet/", "platform": "Meta"}
                    ],
                    "hands_on_project": {
                        "title": "Retail Demand & Inventory Forecasting Engine",
                        "description": "Decompose seasonal trends, model holiday effects, and predict 90-day product demand with prediction intervals."
                    }
                }
            ]
        })

        # Phase 3: Production Deployment & Interview Mastery (3 Modules)
        phases.append({
            "phase_id": "ds-phase-3",
            "phase_number": "3",
            "is_remedial": False,
            "badge": "Phase 3: Production Deployment & Interview Mastery",
            "title": "Model Serving, A/B Testing & Data Science Case Study Interviews",
            "duration": "Weeks 9 - 12",
            "description": "Deploy models as production microservices, design controlled online experiments, and excel in technical case interviews.",
            "modules": [
                {
                    "id": "ds-mod-8",
                    "title": "Model Serving with FastAPI & Docker Containers",
                    "completed": "ds-mod-8" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "FastAPI ML Model Deployment Guide", "type": "Guide", "url": "https://fastapi.tiangolo.com/tutorial/", "platform": "FastAPI"}
                    ],
                    "hands_on_project": {
                        "title": "Real-Time Inference REST API with Pydantic Validation",
                        "description": "Package serialized Scikit-Learn models into Docker containers with health checks and sub-50ms latency."
                    }
                },
                {
                    "id": "ds-mod-9",
                    "title": "Controlled Online Experiments (A/B Testing) & Business Metrics",
                    "completed": "ds-mod-9" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Expedia & Netflix A/B Testing Case Studies", "type": "Article", "url": "https://netflixtechblog.com/", "platform": "Tech Blogs"}
                    ],
                    "hands_on_project": {
                        "title": "Statistical Power Analysis & A/B Experiment Calculator",
                        "description": "Calculate minimum sample sizes, run z-tests on conversion rates, and guard against sample ratio mismatch."
                    }
                },
                {
                    "id": "ds-mod-10",
                    "title": "Data Science System Design & Business Case Study Mastery",
                    "completed": "ds-mod-10" in completed_ids,
                    "hours": "12 hours",
                    "resources": [
                        {"name": "Designing Machine Learning Systems by Chip Huyen", "type": "Book Reference", "url": "https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/", "platform": "O'Reilly"}
                    ],
                    "hands_on_project": {
                        "title": "Real-Time Recommendation System Architecture Defense",
                        "description": "Architect two-stage retrieval and ranking pipeline and defend trade-offs in simulated hiring manager review."
                    }
                }
            ]
        })

        return phases

    # ==========================================================================
    # 3. AI Engineer (10 Actionable Modules across 3 Phases)
    # ==========================================================================
    def _build_ai_engineer_roadmap(self, missing_ids, completed_ids, is_remediation, remedial_topic):
        phases = []

        if is_remediation:
            phases.append({
                "phase_id": "ai-remedial",
                "phase_number": "R",
                "is_remedial": True,
                "badge": "Priority Remediation Alert",
                "title": f"Refresher & Core Drills: {remedial_topic}",
                "duration": "1 - 2 Weeks (Targeted Recovery)",
                "description": "Adaptive path triggered by assessment score (<60%). Focused on PyTorch tensor math, backprop mechanics, and loss landscapes.",
                "modules": [
                    {
                        "id": "ai-rem-1",
                        "title": "PyTorch Autograd & Computational Graph Walkthrough",
                        "completed": "ai-rem-1" in completed_ids,
                        "hours": "6 hours",
                        "resources": [
                            {"name": "PyTorch Autograd Mechanics", "type": "Docs", "url": "https://pytorch.org/tutorials/beginner/blitz/autograd_tutorial.html", "platform": "PyTorch"}
                        ],
                        "hands_on_project": {
                            "title": "Manual Backward Pass & Gradient Descent Verifier",
                            "description": "Implement backpropagation manually using pure Python and verify tensor gradients match PyTorch."
                        }
                    }
                ]
            })

        # Phase 1: Foundations & Missing Skills (3 Modules)
        phases.append({
            "phase_id": "ai-phase-1",
            "phase_number": "1",
            "is_remedial": False,
            "badge": "Phase 1: Foundations & Missing Skills",
            "title": "PyTorch Architecture, Neural Networks & High-Dimensional Embeddings",
            "duration": "Weeks 1 - 4",
            "description": "Understand computational graphs, gradient descent, loss functions, CNNs, and vector embedding spaces in PyTorch.",
            "modules": [
                {
                    "id": "ai-mod-1",
                    "title": "PyTorch Tensors, Autograd & Multi-Layer Perceptrons (MLPs)",
                    "completed": "ai-mod-1" in completed_ids,
                    "hours": "18 hours",
                    "resources": [
                        {"name": "PyTorch Deep Learning Tutorials", "type": "Interactive Book", "url": "https://pytorch.org/tutorials/", "platform": "PyTorch"}
                    ],
                    "hands_on_project": {
                        "title": "Multimodal Deep Classifier from Scratch in PyTorch",
                        "description": "Train custom neural network with custom Dataset, DataLoader, cross-entropy loss, and validation checkpointing."
                    }
                },
                {
                    "id": "ai-mod-2",
                    "title": "Convolutional Neural Networks (CNNs) & Sequence Modeling (RNNs)",
                    "completed": "ai-mod-2" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Stanford CS231n Convolutional Networks", "type": "University Course", "url": "https://cs231n.github.io/", "platform": "Stanford"}
                    ],
                    "hands_on_project": {
                        "title": "Transfer Learning Computer Vision Pipeline (ResNet-50)",
                        "description": "Fine-tune pretrained ResNet on custom domain imagery with data augmentation and confusion matrix analysis."
                    }
                },
                {
                    "id": "ai-mod-3",
                    "title": "Vector Embeddings, Cosine Similarity & Vector Databases",
                    "completed": "ai-mod-3" in completed_ids,
                    "hours": "12 hours",
                    "resources": [
                        {"name": "ChromaDB & Pinecone Vector Architecture Guides", "type": "Documentation", "url": "https://docs.trychroma.com/", "platform": "ChromaDB"}
                    ],
                    "hands_on_project": {
                        "title": "Semantic Document Search Engine with OpenAI Embeddings",
                        "description": "Index PDF documents, generate high-dimensional vectors, and perform sub-10ms nearest neighbor semantic queries."
                    }
                }
            ]
        })

        # Phase 2: Hands-On Capstone Builds (4 Modules)
        phases.append({
            "phase_id": "ai-phase-2",
            "phase_number": "2",
            "is_remedial": False,
            "badge": "Phase 2: Hands-On Capstone Builds",
            "title": "Transformers, RAG Architecture, LLM Fine-Tuning & Multi-Agent Workflows",
            "duration": "Weeks 5 - 8",
            "description": "Harness transformer attention mechanisms, LangChain, hybrid RAG, LoRA parameter-efficient fine-tuning, and multi-agent coordination.",
            "modules": [
                {
                    "id": "ai-mod-4",
                    "title": "Transformer Attention Mechanisms (Query, Key, Value) from Scratch",
                    "completed": "ai-mod-4" in completed_ids,
                    "hours": "18 hours",
                    "resources": [
                        {"name": "The Illustrated Transformer by Jay Alammar", "type": "Article", "url": "https://jalammar.github.io/illustrated-transformer/", "platform": "Visual Guides"},
                        {"name": "Hugging Face NLP Course", "type": "Official Course", "url": "https://huggingface.co/learn/nlp-course", "platform": "Hugging Face"}
                    ],
                    "hands_on_project": {
                        "title": "Multi-Head Self-Attention Layer Implementation in PyTorch",
                        "description": "Code scaled dot-product attention, causal masking, and positional encodings from scratch without high-level wrappers."
                    }
                },
                {
                    "id": "ai-mod-5",
                    "title": "Production RAG: Hybrid Search, Chunking Strategies & Rerankers",
                    "completed": "ai-mod-5" in completed_ids,
                    "hours": "20 hours",
                    "resources": [
                        {"name": "LangChain Official Documentation", "type": "Framework Docs", "url": "https://python.langchain.com/", "platform": "LangChain"}
                    ],
                    "hands_on_project": {
                        "title": "Enterprise Knowledge-Base Assistant with Cohere Rerank",
                        "description": "Construct recursive chunking pipeline, dense + sparse BM25 hybrid search, and cross-encoder reranking."
                    }
                },
                {
                    "id": "ai-mod-6",
                    "title": "Parameter-Efficient Fine-Tuning (PEFT, LoRA & QLoRA) on Open LLMs",
                    "completed": "ai-mod-6" in completed_ids,
                    "hours": "16 hours",
                    "resources": [
                        {"name": "Hugging Face PEFT Library Guide", "type": "Docs", "url": "https://huggingface.co/docs/peft/index", "platform": "Hugging Face"}
                    ],
                    "hands_on_project": {
                        "title": "Fine-Tuning Llama-3 / Mistral on Domain-Specific JSON Tasks",
                        "description": "Quantize 4-bit weights with bitsandbytes, configure rank-16 adapters, and evaluate perplexity on test split."
                    }
                },
                {
                    "id": "ai-mod-7",
                    "title": "Multi-Agent System Orchestration with Tool Calling & LangGraph",
                    "completed": "ai-mod-7" in completed_ids,
                    "hours": "18 hours",
                    "resources": [
                        {"name": "LangGraph Stateful Multi-Agent Guide", "type": "Documentation", "url": "https://langchain-ai.github.io/langgraph/", "platform": "LangGraph"}
                    ],
                    "hands_on_project": {
                        "title": "Autonomous Coding & Testing Multi-Agent Swarm",
                        "description": "Construct stateful cyclic graph with Researcher, Coder, and Verifier agents communicating across shared memory."
                    }
                }
            ]
        })

        # Phase 3: Production Deployment & Interview Mastery (3 Modules)
        phases.append({
            "phase_id": "ai-phase-3",
            "phase_number": "3",
            "is_remedial": False,
            "badge": "Phase 3: Production Deployment & Interview Mastery",
            "title": "High-Throughput LLM Serving, Guardrails & AI Technical Interviews",
            "duration": "Weeks 9 - 12",
            "description": "Deploy low-latency LLM serving engines with vLLM, implement safety guardrails, and master technical interview loops.",
            "modules": [
                {
                    "id": "ai-mod-8",
                    "title": "High-Throughput Serving with vLLM, PagedAttention & Streaming APIs",
                    "completed": "ai-mod-8" in completed_ids,
                    "hours": "16 hours",
                    "resources": [
                        {"name": "vLLM Documentation & Benchmarks", "type": "Serving Engine Docs", "url": "https://docs.vllm.ai/", "platform": "vLLM"}
                    ],
                    "hands_on_project": {
                        "title": "Continuous Batching Inference Server with SSE Streaming",
                        "description": "Benchmark throughput under 50 concurrent requests, optimize KV cache memory, and stream Server-Sent Events."
                    }
                },
                {
                    "id": "ai-mod-9",
                    "title": "AI Safety, Hallucination Detection & NeMo Guardrails",
                    "completed": "ai-mod-9" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "NVIDIA NeMo Guardrails Guidelines", "type": "Security Toolkit", "url": "https://github.com/NVIDIA/NeMo-Guardrails", "platform": "NVIDIA"}
                    ],
                    "hands_on_project": {
                        "title": "Enterprise RAG Defense Firewall & PII Sanitizer",
                        "description": "Enforce input jailbreak filtering, PII redaction, output hallucination checks, and token budget policies."
                    }
                },
                {
                    "id": "ai-mod-10",
                    "title": "AI Systems Architecture, Latency Economics & Mock Interview",
                    "completed": "ai-mod-10" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "OpenAI Production Best Practices & Cost Optimization", "type": "Guide", "url": "https://platform.openai.com/docs/guides/production-best-practices", "platform": "OpenAI"}
                    ],
                    "hands_on_project": {
                        "title": "End-to-End Enterprise Agent Architecture Defense",
                        "description": "Present comprehensive architecture blueprint covering caching, TTFT, cost per million tokens, and disaster recovery."
                    }
                }
            ]
        })

        return phases

    # ==========================================================================
    # 4. Python Developer (10 Actionable Modules across 3 Phases)
    # ==========================================================================
    def _build_python_dev_roadmap(self, missing_ids, completed_ids, is_remediation, remedial_topic):
        phases = []

        if is_remediation:
            phases.append({
                "phase_id": "py-remedial",
                "phase_number": "R",
                "is_remedial": True,
                "badge": "Priority Remediation Alert",
                "title": f"Refresher & Core Drills: {remedial_topic}",
                "duration": "1 - 2 Weeks (Targeted Recovery)",
                "description": "Adaptive path triggered by assessment score (<60%). Focused on OOP basics, exceptions, and collections.",
                "modules": [
                    {
                        "id": "py-rem-1",
                        "title": "Python Object-Oriented Principles & Error Handling Drills",
                        "completed": "py-rem-1" in completed_ids,
                        "hours": "6 hours",
                        "resources": [
                            {"name": "Real Python OOP In-Depth", "type": "Tutorial", "url": "https://realpython.com/python3-object-oriented-programming/", "platform": "Real Python"}
                        ],
                        "hands_on_project": {
                            "title": "Robust Custom Collection Class with Unit Tests",
                            "description": "Implement custom dunder methods (__len__, __getitem__, __iter__) with 100% test coverage."
                        }
                    }
                ]
            })

        # Phase 1: Foundations & Missing Skills (3 Modules)
        phases.append({
            "phase_id": "py-phase-1",
            "phase_number": "1",
            "is_remedial": False,
            "badge": "Phase 1: Foundations & Missing Skills",
            "title": "Advanced Python, Metaprogramming & AsyncIO Concurrency",
            "duration": "Weeks 1 - 3",
            "description": "Master generators, decorators, context managers, async event loops, and clean architecture patterns.",
            "modules": [
                {
                    "id": "py-mod-1",
                    "title": "Python Metaprogramming, Decorators & Context Managers",
                    "completed": "py-mod-1" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Fluent Python by Luciano Ramalho", "type": "Reference", "url": "https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/", "platform": "O'Reilly"}
                    ],
                    "hands_on_project": {
                        "title": "Execution Profiling Decorator & Transaction Context Manager",
                        "description": "Build reusable decorators for memoization, rate-limiting, and auto-rollback database contexts."
                    }
                },
                {
                    "id": "py-mod-2",
                    "title": "AsyncIO Event Loops, Coroutines & Non-Blocking Concurrency",
                    "completed": "py-mod-2" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Python AsyncIO Official Docs", "type": "Docs", "url": "https://docs.python.org/3/library/asyncio.html", "platform": "Python.org"}
                    ],
                    "hands_on_project": {
                        "title": "Concurrent Asynchronous Web Scraper & Stream Processor",
                        "description": "Implement high-throughput data extractor with rate limiting, semaphores, and asyncio workers."
                    }
                },
                {
                    "id": "py-mod-3",
                    "title": "Data Structures, Algorithms & Time/Space Complexity in Python",
                    "completed": "py-mod-3" in completed_ids,
                    "hours": "16 hours",
                    "resources": [
                        {"name": "Problem Solving with Algorithms and Data Structures in Python", "type": "Open Book", "url": "https://runestone.academy/ns/books/published/pythonds3/index.html", "platform": "Runestone"}
                    ],
                    "hands_on_project": {
                        "title": "LRU Cache & Trie Autocomplete System",
                        "description": "Construct high-performance LRU cache using Doubly Linked List and Hash Map, plus prefix tree search."
                    }
                }
            ]
        })

        # Phase 2: Hands-On Capstone Builds (4 Modules)
        phases.append({
            "phase_id": "py-phase-2",
            "phase_number": "2",
            "is_remedial": False,
            "badge": "Phase 2: Hands-On Capstone Builds",
            "title": "FastAPI, SQLAlchemy ORM, Celery & Asynchronous Background Workers",
            "duration": "Weeks 4 - 8",
            "description": "Build high-throughput production microservices with Pydantic validation, relational ORMs, and distributed job queues.",
            "modules": [
                {
                    "id": "py-mod-4",
                    "title": "Modern FastAPI & Pydantic v2 REST API Engineering",
                    "completed": "py-mod-4" in completed_ids,
                    "hours": "16 hours",
                    "resources": [
                        {"name": "FastAPI Official Documentation", "type": "Docs", "url": "https://fastapi.tiangolo.com/", "platform": "FastAPI"}
                    ],
                    "hands_on_project": {
                        "title": "High-Throughput E-Commerce Backend Service with OAuth2",
                        "description": "Build secure API with JWT auth, dependency injection, OpenAPI documentation, and automated validation."
                    }
                },
                {
                    "id": "py-mod-5",
                    "title": "Relational Modeling with PostgreSQL, SQLAlchemy 2.0 & Alembic",
                    "completed": "py-mod-5" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "SQLAlchemy 2.0 Unified Tutorial", "type": "Documentation", "url": "https://docs.sqlalchemy.org/en/20/tutorial/", "platform": "SQLAlchemy"}
                    ],
                    "hands_on_project": {
                        "title": "Multi-Tenant Database Engine with Schema Migrations",
                        "description": "Define declarative models with relationships, eager loading strategies, and Alembic version control."
                    }
                },
                {
                    "id": "py-mod-6",
                    "title": "Distributed Task Queues with Celery, Redis & RabbitMQ",
                    "completed": "py-mod-6" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Celery Distributed Task Queue Guide", "type": "Docs", "url": "https://docs.celeryq.dev/en/stable/", "platform": "Celery"}
                    ],
                    "hands_on_project": {
                        "title": "Asynchronous Email & Video Transcoding Pipeline",
                        "description": "Offload long-running computing jobs to distributed Celery workers with retry policies and flower monitoring."
                    }
                },
                {
                    "id": "py-mod-7",
                    "title": "Automated Testing with Pytest, Fixtures & Mocking",
                    "completed": "py-mod-7" in completed_ids,
                    "hours": "12 hours",
                    "resources": [
                        {"name": "Pytest Documentation & Best Practices", "type": "Docs", "url": "https://docs.pytest.org/en/stable/", "platform": "Pytest"}
                    ],
                    "hands_on_project": {
                        "title": "Comprehensive Test Suite with 95%+ Coverage & CI Integration",
                        "description": "Author unit and integration tests with pytest-cov, pytest-asyncio, and monkeypatching external services."
                    }
                }
            ]
        })

        # Phase 3: Production Deployment & Interview Mastery (3 Modules)
        phases.append({
            "phase_id": "py-phase-3",
            "phase_number": "3",
            "is_remedial": False,
            "badge": "Phase 3: Production Deployment & Interview Mastery",
            "title": "Docker Multi-Stage Builds, Python Internals & System Design",
            "duration": "Weeks 9 - 12",
            "description": "Optimize Python production runtime performance, understand memory management, and master senior engineering interviews.",
            "modules": [
                {
                    "id": "py-mod-8",
                    "title": "Multi-Stage Docker Packaging & Cloud Infrastructure Deployment",
                    "completed": "py-mod-8" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Dockerizing Python Applications Guide", "type": "Guide", "url": "https://testdriven.io/blog/docker-best-practices/", "platform": "TestDriven.io"}
                    ],
                    "hands_on_project": {
                        "title": "Production Distroless Docker Image with Non-Root Security",
                        "description": "Create slim container images under 80MB using multi-stage builds, Gunicorn ASGI workers, and healthchecks."
                    }
                },
                {
                    "id": "py-mod-9",
                    "title": "Python Internals: GIL, Memory Allocator, Garbage Collection & Cython",
                    "completed": "py-mod-9" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Inside the Python 3.13 GIL-Free Interpreter", "type": "Deep Dive", "url": "https://docs.python.org/3/whatsnew/3.13.html", "platform": "Python.org"}
                    ],
                    "hands_on_project": {
                        "title": "Memory Profiling & High-Performance C Extension Benchmark",
                        "description": "Profile heap memory with tracemalloc, detect reference cycles, and accelerate inner compute loop with Cython/NumPy."
                    }
                },
                {
                    "id": "py-mod-10",
                    "title": "Backend System Design & Senior Python Interview Simulator",
                    "completed": "py-mod-10" in completed_ids,
                    "hours": "12 hours",
                    "resources": [
                        {"name": "System Design Primer by Donne Martin", "type": "Open Source Repo", "url": "https://github.com/donnemartin/system-design-primer", "platform": "GitHub"}
                    ],
                    "hands_on_project": {
                        "title": "Distributed URL Shortener & Rate-Limiter System Design",
                        "description": "Architect high-availability URL shortener handling 100k RPS with Redis caching and defend scaling limits in mock interview."
                    }
                }
            ]
        })

        return phases

    # ==========================================================================
    # 5. DevOps & Cloud Engineer (10 Actionable Modules across 3 Phases)
    # ==========================================================================
    def _build_devops_roadmap(self, missing_ids, completed_ids, is_remediation, remedial_topic):
        phases = []

        if is_remediation:
            phases.append({
                "phase_id": "do-remedial",
                "phase_number": "R",
                "is_remedial": True,
                "badge": "Priority Remediation Alert",
                "title": f"Refresher & Core Drills: {remedial_topic}",
                "duration": "1 - 2 Weeks (Targeted Recovery)",
                "description": "Adaptive path triggered by assessment score (<60%). Focused on Linux permissions, bash syntax, and ports.",
                "modules": [
                    {
                        "id": "do-rem-1",
                        "title": "Linux Shell Scripting & File System Permissions Drills",
                        "completed": "do-rem-1" in completed_ids,
                        "hours": "6 hours",
                        "resources": [
                            {"name": "Linux Journey Tutorial", "type": "Interactive Guide", "url": "https://linuxjourney.com/", "platform": "Linux Journey"}
                        ],
                        "hands_on_project": {
                            "title": "Automated Server Health Check & Log Rotator",
                            "description": "Write robust Bash script monitoring disk/memory usage and rotating logs via cron."
                        }
                    }
                ]
            })

        # Phase 1: Foundations & Missing Skills (3 Modules)
        phases.append({
            "phase_id": "do-phase-1",
            "phase_number": "1",
            "is_remedial": False,
            "badge": "Phase 1: Foundations & Missing Skills",
            "title": "Linux Internals, Networking Protocols & GitOps Workflows",
            "duration": "Weeks 1 - 3",
            "description": "Master system administration, TCP/IP networking, SSH security, and trunk-based Git workflows.",
            "modules": [
                {
                    "id": "do-mod-1",
                    "title": "Linux System Administration, Systemd Services & Storage",
                    "completed": "do-mod-1" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Linux Foundation System Administration Essentials", "type": "Course", "url": "https://www.linuxfoundation.org/", "platform": "Linux Foundation"}
                    ],
                    "hands_on_project": {
                        "title": "Hardened Linux Web Server with Systemd Daemon Management",
                        "description": "Configure non-root sudo users, iptables firewall, automated updates, and custom systemd service daemons."
                    }
                },
                {
                    "id": "do-mod-2",
                    "title": "Computer Networking: DNS, TCP/IP, TLS/SSL, HTTP/2 & Reverse Proxies",
                    "completed": "do-mod-2" in completed_ids,
                    "hours": "12 hours",
                    "resources": [
                        {"name": "Nginx Official Beginner's Guide", "type": "Documentation", "url": "https://nginx.org/en/docs/beginners_guide.html", "platform": "Nginx"}
                    ],
                    "hands_on_project": {
                        "title": "Nginx Reverse Proxy with Automated Let's Encrypt SSL/TLS",
                        "description": "Configure SSL termination, rate-limiting, upstream load balancing, and gzip compression in Nginx."
                    }
                },
                {
                    "id": "do-mod-3",
                    "title": "GitOps Version Control, Branching & Conventional Commits",
                    "completed": "do-mod-3" in completed_ids,
                    "hours": "10 hours",
                    "resources": [
                        {"name": "Pro Git Book by Scott Chacon", "type": "Open Book", "url": "https://git-scm.com/book/en/v2", "platform": "Git SCM"}
                    ],
                    "hands_on_project": {
                        "title": "Automated Semantic Versioning & Release Changelog Automation",
                        "description": "Configure commitlint, husky pre-commit hooks, and semantic-release in a multi-contributor repository."
                    }
                }
            ]
        })

        # Phase 2: Hands-On Capstone Builds (4 Modules)
        phases.append({
            "phase_id": "do-phase-2",
            "phase_number": "2",
            "is_remedial": False,
            "badge": "Phase 2: Hands-On Capstone Builds",
            "title": "Docker, Kubernetes, Terraform IaC & GitHub Actions CI/CD",
            "duration": "Weeks 4 - 8",
            "description": "Deploy containerized applications to Kubernetes clusters configured with Terraform Infrastructure as Code.",
            "modules": [
                {
                    "id": "do-mod-4",
                    "title": "Production Containerization with Docker & Multi-Stage Builds",
                    "completed": "do-mod-4" in completed_ids,
                    "hours": "16 hours",
                    "resources": [
                        {"name": "Docker Best Practices Guide", "type": "Docs", "url": "https://docs.docker.com/develop/develop-images/dockerfile_best-practices/", "platform": "Docker"}
                    ],
                    "hands_on_project": {
                        "title": "Secure Microservice Docker Compose Multi-Container Stack",
                        "description": "Build networked stack connecting Web, API, Postgres, and Redis containers with persistent volume mounts."
                    }
                },
                {
                    "id": "do-mod-5",
                    "title": "Infrastructure as Code (IaC) with HashiCorp Terraform & Cloud Modules",
                    "completed": "do-mod-5" in completed_ids,
                    "hours": "18 hours",
                    "resources": [
                        {"name": "HashiCorp Terraform Tutorials", "type": "Interactive Labs", "url": "https://developer.hashicorp.com/terraform/tutorials", "platform": "HashiCorp"}
                    ],
                    "hands_on_project": {
                        "title": "Automated Multi-Tier AWS/GCP Cloud VPC & Compute Deployment",
                        "description": "Provision public/private subnets, security groups, RDS database, and remote S3 state with DynamoDB locking."
                    }
                },
                {
                    "id": "do-mod-6",
                    "title": "CI/CD Pipeline Automation with GitHub Actions & Security Auditing",
                    "completed": "do-mod-6" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "GitHub Actions Documentation", "type": "Docs", "url": "https://docs.github.com/en/actions", "platform": "GitHub"}
                    ],
                    "hands_on_project": {
                        "title": "End-to-End Build, Test, Security Scan & Auto-Deploy Workflow",
                        "description": "Integrate Trivy container vulnerability scanning, SonarQube linting, and automated cloud push."
                    }
                },
                {
                    "id": "do-mod-7",
                    "title": "Kubernetes Cluster Architecture: Pods, Deployments & Services",
                    "completed": "do-mod-7" in completed_ids,
                    "hours": "20 hours",
                    "resources": [
                        {"name": "Kubernetes Official Tutorials", "type": "Interactive Course", "url": "https://kubernetes.io/docs/tutorials/", "platform": "Kubernetes"}
                    ],
                    "hands_on_project": {
                        "title": "High-Availability K8s Deployment with HPA & Ingress Controller",
                        "description": "Deploy stateless web service with Horizontal Pod Autoscaler, readiness/liveness probes, and rolling updates."
                    }
                }
            ]
        })

        # Phase 3: Production Deployment & Interview Mastery (3 Modules)
        phases.append({
            "phase_id": "do-phase-3",
            "phase_number": "3",
            "is_remedial": False,
            "badge": "Phase 3: Production Deployment & Interview Mastery",
            "title": "Prometheus Monitoring, Cloud Security & SRE Interview Mastery",
            "duration": "Weeks 9 - 12",
            "description": "Implement full-stack observability with Prometheus/Grafana, cloud security hardening, and conquer SRE interviews.",
            "modules": [
                {
                    "id": "do-mod-8",
                    "title": "Full-Stack Observability: Prometheus Metrics, Grafana & Loki Logs",
                    "completed": "do-mod-8" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Prometheus Monitoring System Documentation", "type": "Docs", "url": "https://prometheus.io/docs/introduction/overview/", "platform": "Prometheus"}
                    ],
                    "hands_on_project": {
                        "title": "Real-Time Cluster Health & AlertManager Dashboard",
                        "description": "Scrape node and application metrics, design Grafana dashboards, and route threshold alerts to Slack/PagerDuty."
                    }
                },
                {
                    "id": "do-mod-9",
                    "title": "Zero-Trust Cloud Security Hardening, IAM & Secret Management",
                    "completed": "do-mod-9" in completed_ids,
                    "hours": "12 hours",
                    "resources": [
                        {"name": "HashiCorp Vault Security Guide", "type": "Docs", "url": "https://developer.hashicorp.com/vault", "platform": "HashiCorp"}
                    ],
                    "hands_on_project": {
                        "title": "Dynamic Ephemeral Secret Injection Engine with HashiCorp Vault",
                        "description": "Configure short-lived database credentials, TLS certificates, and IAM least-privilege role boundaries."
                    }
                },
                {
                    "id": "do-mod-10",
                    "title": "Site Reliability Engineering (SRE), Chaos Engineering & Interview",
                    "completed": "do-mod-10" in completed_ids,
                    "hours": "14 hours",
                    "resources": [
                        {"name": "Google Site Reliability Engineering (SRE) Book", "type": "Open Book", "url": "https://sre.google/sre-book/table-of-contents/", "platform": "Google"}
                    ],
                    "hands_on_project": {
                        "title": "Disaster Recovery Playbook & 99.99% Availability Architecture",
                        "description": "Formulate SLOs/SLIs, simulate pod failure chaos test, and defend multi-region failover strategy in mock interview."
                    }
                }
            ]
        })

        return phases
