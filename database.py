import sqlite3
import os
import re
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from werkzeug.security import generate_password_hash, check_password_hash

if os.environ.get("VERCEL"):
    DB_DIR = "/tmp"
    DB_PATH = "/tmp/skillpath.db"
else:
    DB_DIR = os.path.join(os.path.dirname(__file__), "database")
    DB_PATH = os.path.join(DB_DIR, "students.db")

_BENCHMARKS_CACHE: Optional[List[Dict[str, Any]]] = None

@contextmanager
def get_db():
    os.makedirs(DB_DIR, exist_ok=True)
    con = sqlite3.connect(DB_PATH, timeout=30.0)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()

def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    with get_db() as con:
        # 1. Profile table
        con.execute("""
            CREATE TABLE IF NOT EXISTS profile (
                id INTEGER PRIMARY KEY CHECK (id=1),
                name TEXT NOT NULL,
                education TEXT,
                skills TEXT,
                career TEXT,
                experience_level TEXT DEFAULT 'Junior',
                certifications TEXT DEFAULT '',
                projects TEXT DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cols = [r["name"] for r in con.execute("PRAGMA table_info(profile)").fetchall()]
        if "experience_level" not in cols:
            con.execute("ALTER TABLE profile ADD COLUMN experience_level TEXT DEFAULT 'Junior'")
        if "certifications" not in cols:
            con.execute("ALTER TABLE profile ADD COLUMN certifications TEXT DEFAULT ''")
        if "projects" not in cols:
            con.execute("ALTER TABLE profile ADD COLUMN projects TEXT DEFAULT ''")
        if "updated_at" not in cols:
            con.execute("ALTER TABLE profile ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

        # 2. Assessments table
        con.execute("""
            CREATE TABLE IF NOT EXISTS assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                percentage INTEGER NOT NULL DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'Passed',
                notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        a_cols = [r["name"] for r in con.execute("PRAGMA table_info(assessments)").fetchall()]
        if "percentage" not in a_cols:
            con.execute("ALTER TABLE assessments ADD COLUMN percentage INTEGER DEFAULT 0")
        if "status" not in a_cols:
            con.execute("ALTER TABLE assessments ADD COLUMN status TEXT DEFAULT 'Passed'")
        if "notes" not in a_cols:
            con.execute("ALTER TABLE assessments ADD COLUMN notes TEXT DEFAULT ''")

        # 3. Module progress table
        con.execute("""
            CREATE TABLE IF NOT EXISTS module_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                career TEXT NOT NULL,
                module_id TEXT NOT NULL,
                completed INTEGER DEFAULT 0,
                completed_at TIMESTAMP,
                UNIQUE(career, module_id)
            )
        """)

        # 4. Agent logs table
        con.execute("""
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                action TEXT NOT NULL,
                status TEXT NOT NULL,
                summary TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 5. Users table (Gamified with XP, Streaks, Skills & Bio)
        con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT DEFAULT '',
                auth_provider TEXT DEFAULT 'local',
                avatar TEXT DEFAULT '',
                target_career TEXT DEFAULT 'Full Stack Developer',
                role TEXT DEFAULT 'Learner',
                education TEXT DEFAULT 'Self-Taught / University Degree',
                skills TEXT DEFAULT 'Python, SQL, HTML',
                projects TEXT DEFAULT '',
                certifications TEXT DEFAULT '',
                xp INTEGER DEFAULT 750,
                streak_days INTEGER DEFAULT 4,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        u_cols = [r["name"] for r in con.execute("PRAGMA table_info(users)").fetchall()]
        if "education" not in u_cols:
            con.execute("ALTER TABLE users ADD COLUMN education TEXT DEFAULT 'Self-Taught / University Degree'")
        if "skills" not in u_cols:
            con.execute("ALTER TABLE users ADD COLUMN skills TEXT DEFAULT 'Python, SQL, HTML'")
        if "projects" not in u_cols:
            con.execute("ALTER TABLE users ADD COLUMN projects TEXT DEFAULT ''")
        if "certifications" not in u_cols:
            con.execute("ALTER TABLE users ADD COLUMN certifications TEXT DEFAULT ''")
        if "xp" not in u_cols:
            con.execute("ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 750")
        if "streak_days" not in u_cols:
            con.execute("ALTER TABLE users ADD COLUMN streak_days INTEGER DEFAULT 4")

        # 6. Role Benchmarks table
        con.execute("""
            CREATE TABLE IF NOT EXISTS role_benchmarks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT UNIQUE NOT NULL,
                demand TEXT DEFAULT 'High',
                estimated_weeks TEXT DEFAULT '10 - 14 Weeks',
                core_skills TEXT NOT NULL,
                description TEXT DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 7. Mock Interviews table
        con.execute("""
            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                role TEXT NOT NULL,
                question TEXT NOT NULL,
                user_answer TEXT NOT NULL,
                readiness_score INTEGER NOT NULL DEFAULT 75,
                feedback TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 8. Certificates table
        con.execute("""
            CREATE TABLE IF NOT EXISTS certificates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                learner_name TEXT NOT NULL,
                career TEXT NOT NULL,
                readiness_pct INTEGER NOT NULL,
                credential_id TEXT UNIQUE NOT NULL,
                verification_code TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Performance Indexes for SQLite efficiency
        con.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_users_xp ON users(xp);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_module_progress_career ON module_progress(career, module_id);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_assessments_topic ON assessments(topic);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_assessments_percentage ON assessments(percentage);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_agent_logs_created ON agent_logs(created_at);")
        con.execute("CREATE INDEX IF NOT EXISTS idx_role_benchmarks_role ON role_benchmarks(role);")

        # Seed initial cohort users if none exist
        user_count = con.execute("SELECT COUNT(*) as cnt FROM users").fetchone()["cnt"]
        if user_count == 0:
            default_pass = generate_password_hash("pass123")
            admin_pass = generate_password_hash("admin123")
            initial_users = [
                ("elena.rostova@berkeleysystems.org", "Elena Rostova", default_pass, "local", "ER", "Full Stack Developer", "Learner", "B.S. EECS (UC Berkeley)", "Python, SQL, HTML, CSS", "RESTful Microservices, Real-time Dashboard", "AWS Certified Developer", 1350, 6),
                ("sarah.jenkins@stanford.edu", "Sarah Jenkins", default_pass, "google", "SJ", "Data Scientist", "Learner", "M.S. Applied Statistics", "Python, SQL, Pandas, NumPy", "Customer Churn Predictor", "Google Data Analytics", 1600, 7),
                ("priya.sharma@techcorp.io", "Priya Sharma", default_pass, "github", "PS", "AI Engineer", "Learner", "B.Tech Computer Engineering", "Python, PyTorch, LangChain", "Enterprise RAG Assistant", "DeepLearning.AI", 950, 3),
                ("david.miller@cloudops.net", "David Miller", default_pass, "linkedin", "DM", "DevOps & Cloud Engineer", "Learner", "B.S. Information Systems", "Linux, Docker, AWS", "Kubernetes Multi-Node Cluster", "AWS Solutions Architect", 1400, 6),
                ("marcus.vance@mit.edu", "Dr. Marcus Vance", admin_pass, "local", "MV", "AI Engineer", "Admin", "Ph.D. Computer Science (MIT)", "Python, PyTorch, Transformers, Agentic AI", "Autonomous Multi-Agent Harness", "IEEE Senior Fellow", 2800, 14)
            ]
            con.executemany("""
                INSERT INTO users (email, name, password_hash, auth_provider, avatar, target_career, role, education, skills, projects, certifications, xp, streak_days)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, initial_users)

        # Seed curriculum benchmarks if none exist
        bench_count = con.execute("SELECT COUNT(*) as cnt FROM role_benchmarks").fetchone()["cnt"]
        if bench_count == 0:
            initial_benchmarks = [
                ("Full Stack Developer", "Very High", "10 - 14 Weeks", "JavaScript, React, Node.js, HTML/CSS, SQL, REST APIs, Git", "Full lifecycle client and server applications, scalable database schemas, and microservice APIs."),
                ("Data Scientist", "High", "12 - 16 Weeks", "Python, SQL, Pandas, NumPy, Scikit-Learn, Data Visualization, Statistics", "Statistical computing, exploratory data analysis, and predictive machine learning models."),
                ("AI Engineer", "Explosive", "14 - 18 Weeks", "Python, PyTorch, LangChain, Transformers, LLM Fine-Tuning, Vector DBs, Prompt Engineering", "Autonomous agent workflows, neural network fine-tuning, and retrieval-augmented generation."),
                ("Python Developer", "High", "8 - 12 Weeks", "Python, Django/Flask, PostgreSQL, Celery, Docker, Pytest, Asyncio", "Robust backend services, asynchronous job workers, and automated test-driven development."),
                ("DevOps & Cloud Engineer", "High", "12 - 16 Weeks", "Linux, Docker, Kubernetes, AWS/GCP, Terraform, CI/CD, Prometheus", "Cloud infrastructure automation, container orchestration, and continuous integration pipelines.")
            ]
            con.executemany("""
                INSERT INTO role_benchmarks (role, demand, estimated_weeks, core_skills, description)
                VALUES (?, ?, ?, ?, ?)
            """, initial_benchmarks)

# ==============================================================================
# Profile Persistence
# ==============================================================================

def save_profile(p, user_id=None):
    uid = user_id or p.get("user_id")
    if uid:
        with get_db() as con:
            con.execute("""
                UPDATE users SET
                    name = ?,
                    education = ?,
                    skills = ?,
                    target_career = ?,
                    projects = ?,
                    certifications = ?,
                    last_login = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                p.get("name", "Learner"),
                p.get("education", "Self-Taught / Degree"),
                p.get("skills", ""),
                p.get("career", "Full Stack Developer"),
                p.get("projects", ""),
                p.get("certifications", ""),
                uid
            ))
    with get_db() as con:
        con.execute("""
            INSERT INTO profile (id, name, education, skills, career, experience_level, certifications, projects, updated_at)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                education = excluded.education,
                skills = excluded.skills,
                career = excluded.career,
                experience_level = excluded.experience_level,
                certifications = excluded.certifications,
                projects = excluded.projects,
                updated_at = CURRENT_TIMESTAMP
        """, (
            p.get("name", "Learner"),
            p.get("education", "Self-Taught / Degree"),
            p.get("skills", ""),
            p.get("career", "Full Stack Developer"),
            p.get("experience_level", "Junior"),
            p.get("certifications", ""),
            p.get("projects", "")
        ))

def get_profile(user_id=None):
    if user_id:
        user = get_user_by_id(user_id)
        if user:
            return {
                "name": user["name"],
                "education": user.get("education") or "Self-Taught / University Degree",
                "skills": user.get("skills") or "Python, SQL, HTML",
                "career": user.get("target_career") or "Full Stack Developer",
                "experience_level": "Junior Developer",
                "certifications": user.get("certifications") or "",
                "projects": user.get("projects") or "Personal Portfolio",
                "xp": user.get("xp", 750),
                "streak_days": user.get("streak_days", 4),
                "updated_at": user.get("last_login")
            }
    with get_db() as con:
        row = con.execute("SELECT name, education, skills, career, experience_level, certifications, projects, updated_at FROM profile WHERE id=1").fetchone()
    if not row:
        return None
    res = dict(row)
    res["xp"] = 1250
    res["streak_days"] = 5
    return res

def update_target_career(career_name, user_id=None):
    with get_db() as con:
        con.execute("UPDATE profile SET career = ?, updated_at = CURRENT_TIMESTAMP WHERE id = 1", (career_name,))
        if user_id:
            con.execute("UPDATE users SET target_career = ?, last_login = CURRENT_TIMESTAMP WHERE id = ?", (career_name, user_id))

def load_demo_profile():
    profile_data = {
        "name": "Elena Rostova",
        "education": "B.S. Electrical Engineering & CS (UC Berkeley)",
        "skills": "Python, SQL, HTML, CSS",
        "career": "Full Stack Developer",
        "experience_level": "Junior Developer",
        "certifications": "AWS Certified Developer, Python Institute PCAP",
        "projects": "RESTful Microservices (Python), Interactive SQL Analytics, Responsive Web App (HTML/CSS)"
    }
    save_profile(profile_data)
    with get_db() as con:
        con.execute("DELETE FROM module_progress WHERE career = 'Full Stack Developer'")
    return profile_data

# ==============================================================================
# Assessments Persistence
# ==============================================================================

def save_assessment(topic, score, total, notes=None):
    pct = round((score / total) * 100) if total else 0
    status = "Passed (>=60%)" if pct >= 60 else "Needs Practice (<60%)"
    with get_db() as con:
        cur = con.execute("""
            INSERT INTO assessments (topic, score, total, percentage, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (topic, score, total, pct, status, notes or ""))
        assessment_id = cur.lastrowid
    return {
        "id": assessment_id,
        "topic": topic,
        "score": score,
        "total": total,
        "percentage": pct,
        "status": status,
        "notes": notes
    }

def get_assessments(limit=10):
    with get_db() as con:
        rows = con.execute("""
            SELECT id, topic, score, total, percentage, status, notes, created_at
            FROM assessments
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()
    return [dict(r) for r in rows]

def get_latest_assessment():
    with get_db() as con:
        row = con.execute("""
            SELECT id, topic, score, total, percentage, status, notes, created_at
            FROM assessments
            ORDER BY id DESC
            LIMIT 1
        """).fetchone()
    return dict(row) if row else None

# ==============================================================================
# Module Progress Persistence & Gamification XP
# ==============================================================================

def toggle_module_progress(career, module_id, user_id=None):
    with get_db() as con:
        row = con.execute(
            "SELECT completed FROM module_progress WHERE career = ? AND module_id = ?",
            (career, module_id)
        ).fetchone()
        if row:
            new_state = 0 if row["completed"] else 1
            con.execute(
                "UPDATE module_progress SET completed = ?, completed_at = CURRENT_TIMESTAMP WHERE career = ? AND module_id = ?",
                (new_state, career, module_id)
            )
            if new_state and user_id:
                con.execute("UPDATE users SET xp = xp + 250 WHERE id = ?", (user_id,))
            return bool(new_state)
        else:
            con.execute(
                "INSERT INTO module_progress (career, module_id, completed, completed_at) VALUES (?, ?, 1, CURRENT_TIMESTAMP)",
                (career, module_id)
            )
            if user_id:
                con.execute("UPDATE users SET xp = xp + 250 WHERE id = ?", (user_id,))
            return True

def get_completed_modules(career):
    with get_db() as con:
        rows = con.execute(
            "SELECT module_id FROM module_progress WHERE career = ? AND completed = 1",
            (career,)
        ).fetchall()
    return {r["module_id"] for r in rows}

# ==============================================================================
# Agent Execution Logs Persistence
# ==============================================================================

def save_agent_logs(logs):
    if not logs:
        return
    with get_db() as con:
        for log in logs:
            con.execute("""
                INSERT INTO agent_logs (agent_name, action, status, summary, details)
                VALUES (?, ?, ?, ?, ?)
            """, (
                log.get("agent_name", "Agent"),
                log.get("action", "EXECUTE"),
                log.get("status", "SUCCESS"),
                log.get("summary", ""),
                log.get("details", "")
            ))

def get_recent_agent_logs(limit=25):
    with get_db() as con:
        rows = con.execute("""
            SELECT id, agent_name, action, status, summary, details, created_at
            FROM agent_logs
            ORDER BY id DESC
            LIMIT ?
        """, (limit,)).fetchall()
    return [dict(r) for r in rows]

# ==============================================================================
# User Authentication & Cohort Management
# ==============================================================================

def register_user(name: str, email: str, password: str, auth_provider: str = "local", target_career: str = "Full Stack Developer", education: str = "Self-Taught / University Degree", skills: str = "Python, SQL, HTML", projects: str = ""):
    """Register a new user in SQLite with hashed password and zero demo defaults."""
    email = email.strip().lower()
    name = name.strip()
    if not email or "@" not in email:
        return None, "Please provide a valid email address."
    if not name:
        return None, "Name is required."
    if not password or len(password) < 4:
        return None, "Password must be at least 4 characters."
    
    parts = name.split()
    avatar = (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")) if parts else "U"
    avatar = avatar.upper()
    hashed_pw = generate_password_hash(password)
    with get_db() as con:
        existing = con.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            return None, "An account with this email already exists."
        cur = con.execute("""
            INSERT INTO users (email, name, password_hash, auth_provider, avatar, target_career, role, education, skills, projects, xp, streak_days)
            VALUES (?, ?, ?, ?, ?, ?, 'Learner', ?, ?, ?, 500, 1)
        """, (email, name, hashed_pw, auth_provider, avatar, target_career, education, skills, projects))
        user_id = cur.lastrowid
        return {
            "id": user_id,
            "name": name,
            "email": email,
            "avatar": avatar,
            "target_career": target_career,
            "education": education,
            "skills": skills,
            "projects": projects,
            "auth_provider": auth_provider,
            "role": "Learner",
            "xp": 500,
            "streak_days": 1
        }, None

def authenticate_user(email: str, password: str):
    """Authenticate user credentials using secure hash comparison."""
    email = email.strip().lower()
    with get_db() as con:
        row = con.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not row:
            return None, "No account found with this email."
        user = dict(row)
        stored_hash = user.get("password_hash", "")
        valid = False
        if stored_hash.startswith("scrypt:") or stored_hash.startswith("pbkdf2:"):
            valid = check_password_hash(stored_hash, password)
        else:
            valid = (stored_hash == password)
            if valid:
                # Transparently upgrade plain password to hashed
                new_hash = generate_password_hash(password)
                con.execute("UPDATE users SET password_hash = ? WHERE id = ?", (new_hash, user["id"]))
        if not valid:
            return None, "Incorrect password. Please try again."
        con.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user["id"],))
        return user, None

def social_login(provider, name=None, email=None, target_career="Full Stack Developer", skills=None, projects=None, education=None):
    provider_defaults = {
        "google": ("Jordan Lee", "jordan.lee@googlemail.com", "JL", "Full Stack Developer", "B.S. Software Engineering", "Python, SQL, HTML, CSS", "Full Stack E-commerce, Task Manager API"),
        "github": ("Devon Archer", "devon.archer@github.com", "DA", "DevOps & Cloud Engineer", "B.S. Information Systems", "Linux, Docker, Python, Git", "Automated CI/CD Pipeline, K8s Cluster"),
        "linkedin": ("Maya Patel", "maya.patel@linkedin.com", "MP", "AI Engineer", "M.S. Artificial Intelligence", "Python, PyTorch, SQL, Pandas", "RAG Document Search, LLM Fine-Tuner"),
        "demo": ("Elena Rostova", "elena.rostova@berkeleysystems.org", "ER", "Full Stack Developer", "B.S. EECS (UC Berkeley)", "Python, SQL, HTML, CSS", "RESTful Microservices, Real-time Dashboard")
    }
    def_name, def_email, def_avatar, def_role, def_edu, def_skills, def_proj = provider_defaults.get(
        provider.lower(),
        ("Elena Rostova", f"learner_{provider}@skillpath.ai", "ER", "Full Stack Developer", "Self-Taught / Degree", "Python, SQL, HTML", "Portfolio Projects")
    )
    actual_name = name or def_name
    actual_email = (email or def_email).strip().lower()
    actual_career = target_career if (target_career != "Full Stack Developer" or not name) else (target_career or def_role)
    actual_edu = education or def_edu
    actual_skills = skills or def_skills
    actual_proj = projects or def_proj
    parts = actual_name.split()
    avatar = (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")) if parts else def_avatar
    avatar = avatar.upper()

    user = None
    with get_db() as con:
        row = con.execute("SELECT * FROM users WHERE email = ?", (actual_email,)).fetchone()
        if row:
            user = dict(row)
            updates = ["last_login = CURRENT_TIMESTAMP"]
            params = []
            if skills:
                updates.append("skills = ?")
                params.append(skills)
                user["skills"] = skills
            if projects:
                updates.append("projects = ?")
                params.append(projects)
                user["projects"] = projects
            if target_career and target_career != "Full Stack Developer":
                updates.append("target_career = ?")
                params.append(target_career)
                user["target_career"] = target_career
            params.append(user["id"])
            con.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", tuple(params))
        else:
            cur = con.execute("""
                INSERT INTO users (email, name, password_hash, auth_provider, avatar, target_career, role, education, skills, projects, xp, streak_days)
                VALUES (?, ?, 'oauth_token', ?, ?, ?, 'Learner', ?, ?, ?, 750, 3)
            """, (actual_email, actual_name, provider.lower(), avatar, actual_career, actual_edu, actual_skills, actual_proj))
            user = {
                "id": cur.lastrowid,
                "name": actual_name,
                "email": actual_email,
                "avatar": avatar,
                "target_career": actual_career,
                "education": actual_edu,
                "skills": actual_skills,
                "projects": actual_proj,
                "auth_provider": provider.lower(),
                "role": "Learner",
                "xp": 750,
                "streak_days": 3
            }

    save_profile({
        "name": user["name"],
        "education": user.get("education") or actual_edu,
        "skills": user.get("skills") or actual_skills,
        "career": user.get("target_career") or actual_career,
        "experience_level": "Junior Developer",
        "projects": user.get("projects") or actual_proj
    }, user_id=user["id"])
    return user

def update_user_skills_and_career(user_id, skills, career):
    if not user_id:
        return
    with get_db() as con:
        con.execute("UPDATE users SET skills = ?, target_career = ?, last_login = CURRENT_TIMESTAMP WHERE id = ?", (skills, career, user_id))

def analyze_job_description(jd_text, user_skills):
    """
    Feature 3: Parses Job Description (JD) text, detects required skills,
    compares against user's skills, and calculates dynamic match %.
    """
    if not jd_text:
        return {
            "match_pct": 0,
            "matched_skills": [],
            "missing_skills": [],
            "jd_skills": [],
            "detected_role": "Full Stack Developer",
            "recommendation": "Please paste a job description to analyze readiness."
        }

    jd_skills, detected_role = extract_skills_from_text(jd_text)
    if not jd_skills:
        jd_skills = ["JavaScript", "React", "Node.js", "SQL", "Git"]

    if isinstance(user_skills, str):
        user_skills_list = [s.strip().lower() for s in user_skills.split(",") if s.strip()]
    elif isinstance(user_skills, (list, set)):
        user_skills_list = [str(s).strip().lower() for s in user_skills if s]
    else:
        user_skills_list = []

    matched = []
    missing = []

    for s in jd_skills:
        s_clean = s.strip()
        if any(u in s_clean.lower() or s_clean.lower() in u for u in user_skills_list):
            matched.append(s_clean)
        else:
            missing.append(s_clean)

    match_pct = round((len(matched) / len(jd_skills)) * 100) if jd_skills else 0

    if match_pct >= 75:
        recommendation = f"Exceptional alignment! You qualify for {match_pct}% of the core stack for this {detected_role} position. Ready to apply."
    elif match_pct >= 50:
        recommendation = f"Strong baseline ({match_pct}% match). Focus on closing priority gaps in {', '.join(missing[:3])} to become a top-tier candidate."
    else:
        recommendation = f"Emerging fit ({match_pct}% match). Roadmap Agent recommends completing foundational modules for {', '.join(missing[:3])}."

    return {
        "match_pct": match_pct,
        "matched_skills": matched,
        "missing_skills": missing,
        "jd_skills": jd_skills,
        "detected_role": detected_role,
        "recommendation": recommendation
    }

def get_user_by_id(user_id):
    if not user_id:
        return None
    with get_db() as con:
        row = con.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None

def get_all_users():
    with get_db() as con:
        rows = con.execute("""
            SELECT id, name, email, auth_provider, avatar, target_career, role, xp, streak_days, created_at, last_login
            FROM users
            ORDER BY xp DESC
        """).fetchall()
    return [dict(r) for r in rows]

def add_user_xp(user_id, amount=250):
    with get_db() as con:
        con.execute("UPDATE users SET xp = xp + ? WHERE id = ?", (amount, user_id))

# ==============================================================================
# Resume Skill Auto-Extractor (Feature 2)
# ==============================================================================

CANONICAL_SKILLS = [
    # Languages
    "Python", "JavaScript", "TypeScript", "HTML", "CSS", "SQL", "Java", "C++", "C#", "Go", "Rust", "PHP", "Ruby", "Swift", "Kotlin", "R",
    # Frontend
    "React", "Vue", "Angular", "Next.js", "Tailwind CSS", "Bootstrap", "Redux", "DOM APIs", "Sass",
    # Backend & API
    "Node.js", "Express", "Django", "Flask", "FastAPI", "REST APIs", "GraphQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite",
    # AI & Data
    "PyTorch", "TensorFlow", "Scikit-Learn", "Pandas", "NumPy", "LangChain", "Transformers", "LLM Fine-Tuning", "Vector DBs", "Prompt Engineering", "OpenAI API", "HuggingFace", "Tableau", "Power BI", "Data Wrangling", "Statistics",
    # Cloud & DevOps
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform", "CI/CD", "Linux", "Git", "GitHub Actions", "Prometheus", "Nginx", "Microservices"
]

def extract_skills_from_text(raw_text):
    """
    Parses resume text or bio, matches canonical skill taxonomies,
    and returns detected skills + estimated target career role.
    """
    if not raw_text:
        return [], "Full Stack Developer"

    text_lower = raw_text.lower()
    matched_skills = []

    # Map variations to standard names
    synonyms = {
        "js": "JavaScript", "ts": "TypeScript", "py": "Python", "postgres": "PostgreSQL",
        "k8s": "Kubernetes", "rest": "REST APIs", "restful": "REST APIs", "reactjs": "React",
        "react.js": "React", "nodejs": "Node.js", "node": "Node.js", "expressjs": "Express",
        "nextjs": "Next.js", "tailwindcss": "Tailwind CSS", "sklearn": "Scikit-Learn"
    }

    for skill in CANONICAL_SKILLS:
        pattern = r"\b" + re.escape(skill.lower()) + r"\b"
        if re.search(pattern, text_lower):
            matched_skills.append(skill)

    for syn_key, target_name in synonyms.items():
        pattern = r"\b" + re.escape(syn_key) + r"\b"
        if re.search(pattern, text_lower) and target_name not in matched_skills:
            matched_skills.append(target_name)

    # Inferred target career
    detected_role = "Full Stack Developer"
    if any(k in text_lower for k in ["pytorch", "langchain", "llm", "ai engineer", "prompt"]):
        detected_role = "AI Engineer"
    elif any(k in text_lower for k in ["pandas", "numpy", "data scientist", "machine learning", "scikit"]):
        detected_role = "Data Scientist"
    elif any(k in text_lower for k in ["docker", "kubernetes", "devops", "cloud", "aws", "terraform"]):
        detected_role = "DevOps & Cloud Engineer"
    elif any(k in text_lower for k in ["django", "flask", "fastapi", "python dev"]):
        detected_role = "Python Developer"

    # Default fallback skills if too few detected
    if len(matched_skills) < 2:
        matched_skills = ["Python", "SQL", "Git", "Problem Solving"]

    return matched_skills, detected_role

# ==============================================================================
# AI Mock Interview Simulator (Feature 5)
# ==============================================================================

MOCK_INTERVIEW_QUESTIONS = {
    "Full Stack Developer": [
        "Explain the JavaScript Event Loop, Call Stack, and Task Queue. How does Node.js handle concurrent I/O operations without blocking?",
        "How would you design a scalable authentication flow between a React single-page app and an Express API (JWT vs HTTP-only Cookies)?",
        "Explain React's Virtual DOM reconciliation and why unique 'key' props are critical when rendering dynamic lists."
    ],
    "Data Scientist": [
        "What is the difference between Bias and Variance, and how do regularization techniques (L1 Lasso vs L2 Ridge) mitigate overfitting?",
        "How would you evaluate and address severe class imbalance (e.g. 99.5% negative) in a machine learning classification pipeline?",
        "Walk through the mathematical difference between PCA (dimensionality reduction) and t-SNE for unsupervised cluster visualization."
    ],
    "AI Engineer": [
        "Explain the core Self-Attention mechanism in Transformers (Query, Key, Value). Why does attention scale $O(N^2)$ with sequence length?",
        "How would you architect a production-grade Retrieval-Augmented Generation (RAG) system with hybrid search and reranking?",
        "What is Low-Rank Adaptation (LoRA), and how does it reduce memory requirements when fine-tuning large language models?"
    ],
    "Python Developer": [
        "What is Python's Global Interpreter Lock (GIL), how does it affect CPU vs I/O bound concurrency, and what are GIL-free developments?",
        "Explain how Python Generators and the 'yield' keyword achieve memory-efficient streaming over large datasets.",
        "How does Python manage object memory allocation and cycle detection using reference counting and generational garbage collection?"
    ],
    "DevOps & Cloud Engineer": [
        "Explain the relationship between Kubernetes Pods, Deployments, and Services. How does a RollingUpdate achieve zero-downtime releases?",
        "What are the operational differences between Docker bridge, host, and overlay networks in distributed clusters?",
        "Explain Terraform state locking and how remote state backends (e.g. S3 with DynamoDB) prevent concurrent corruption."
    ]
}

def evaluate_interview_response(role, question, user_answer):
    """
    Heuristic AI evaluation for candidate answers, generating
    a readiness score, constructive feedback, and identified strengths.
    """
    length = len(user_answer.strip().split())
    answer_lower = user_answer.lower()

    # Technical keywords check
    tech_terms = [
        "asynchronous", "non-blocking", "event loop", "callback", "promise", "latency",
        "concurrency", "overfitting", "regularization", "transformer", "attention",
        "gradient", "vector", "embedding", "docker", "kubernetes", "container",
        "pipeline", "scalability", "architecture", "tradeoff", "cache", "database",
        "memory", "complexity", "algorithm", "optimization"
    ]
    term_matches = sum(1 for term in tech_terms if term in answer_lower)

    # Score calculation
    base_score = min(40, length // 2)
    term_score = min(45, term_matches * 9)
    total_score = max(55, min(98, 30 + base_score + term_score))

    # Constructive feedback
    if total_score >= 85:
        feedback = (
            f"Outstanding, senior-level response for a {role}! "
            f"You clearly articulated underlying architectural trade-offs, correct terminology, "
            f"and practical real-world failure modes. Ready for live hiring manager loops."
        )
    elif total_score >= 70:
        feedback = (
            f"Solid conceptual foundation for {role}. "
            f"You demonstrated good working knowledge of the core concepts. "
            f"To reach the 90th percentile, elaborate on edge-case scenarios, performance benchmarking, "
            f"and horizontal scaling constraints."
        )
    else:
        feedback = (
            f"Promising start, but answer requires deeper technical precision for {role}. "
            f"Be sure to define specific mechanism names, time/space complexity impacts, "
            f"and step-by-step execution flows rather than high-level generalizations."
        )

    # Save interview result to SQLite
    with get_db() as con:
        con.execute("""
            INSERT INTO interviews (role, question, user_answer, readiness_score, feedback)
            VALUES (?, ?, ?, ?, ?)
        """, (role, question, user_answer, total_score, feedback))

    return {
        "score": total_score,
        "feedback": feedback,
        "terms_detected": term_matches
    }

# ==============================================================================
# Job Market Intelligence (Feature 7)
# ==============================================================================

JOB_MARKET_INTELLIGENCE = {
    "Full Stack Developer": {
        "salary_inr": "₹8.5 LPA - ₹28.0 LPA",
        "salary_usd": "$85,000 - $165,000",
        "avg_inr": "₹16.5 LPA",
        "avg_usd": "$125,000",
        "demand_trend": "+34% YoY (High Surge)",
        "open_positions": "42,000+ Active Openings",
        "top_skills": ["React 18", "Node.js", "TypeScript", "PostgreSQL", "Docker", "AWS"],
        "top_employers": ["Swiggy", "Razorpay", "Google", "Amazon", "Microsoft", "Flipkart"]
    },
    "Data Scientist": {
        "salary_inr": "₹10.0 LPA - ₹32.0 LPA",
        "salary_usd": "$95,000 - $175,000",
        "avg_inr": "₹18.2 LPA",
        "avg_usd": "$135,000",
        "demand_trend": "+28% YoY (Strong Demand)",
        "open_positions": "26,500+ Active Openings",
        "top_skills": ["Python", "SQL", "Pandas", "Scikit-Learn", "PyTorch", "Tableau"],
        "top_employers": ["Fractal Analytics", "Meta", "Netflix", "Walmart Tech", "Zomato"]
    },
    "AI Engineer": {
        "salary_inr": "₹14.0 LPA - ₹45.0 LPA",
        "salary_usd": "$125,000 - $220,000",
        "avg_inr": "₹24.5 LPA",
        "avg_usd": "$168,000",
        "demand_trend": "+62% YoY (Peak Talent War)",
        "open_positions": "19,800+ Active Openings",
        "top_skills": ["PyTorch", "LangChain", "Transformers", "Vector DBs", "LLM Fine-Tuning", "vLLM"],
        "top_employers": ["OpenAI", "Anthropic", "Google DeepMind", "Sarvam AI", "Nvidia"]
    },
    "Python Developer": {
        "salary_inr": "₹7.0 LPA - ₹24.0 LPA",
        "salary_usd": "$80,000 - $150,000",
        "avg_inr": "₹14.0 LPA",
        "avg_usd": "$115,000",
        "demand_trend": "+22% YoY (Steady Demand)",
        "open_positions": "31,000+ Active Openings",
        "top_skills": ["Python 3", "Django", "FastAPI", "PostgreSQL", "Celery", "Redis"],
        "top_employers": ["Spotify", "Uber", "Zerodha", "CRED", "Cisco"]
    },
    "DevOps & Cloud Engineer": {
        "salary_inr": "₹9.0 LPA - ₹30.0 LPA",
        "salary_usd": "$90,000 - $170,000",
        "avg_inr": "₹17.8 LPA",
        "avg_usd": "$130,000",
        "demand_trend": "+38% YoY (Critical Need)",
        "open_positions": "35,400+ Active Openings",
        "top_skills": ["Kubernetes", "Docker", "Terraform", "AWS / GCP", "CI/CD Pipelines", "Linux"],
        "top_employers": ["AWS", "Datadog", "Snowflake", "Jio", "PhonePe"]
    }
}

# ==============================================================================
# Admin & Platform-Wide Analytics
# ==============================================================================

def get_platform_kpis():
    with get_db() as con:
        user_cnt = con.execute("SELECT COUNT(*) as cnt FROM users").fetchone()["cnt"]
        remedial_cnt = con.execute("SELECT COUNT(*) as cnt FROM assessments WHERE percentage < 60").fetchone()["cnt"]
        total_tests = con.execute("SELECT COUNT(*) as cnt FROM assessments").fetchone()["cnt"]
        avg_pct_row = con.execute("SELECT AVG(percentage) as avg_p FROM assessments").fetchone()
        avg_pct = round(avg_pct_row["avg_p"]) if avg_pct_row and avg_pct_row["avg_p"] else 68

    skill_gaps = [
        {"name": "JavaScript & React", "demand_score": 94, "cohort_impact": "High"},
        {"name": "PyTorch & Generative AI", "demand_score": 88, "cohort_impact": "Explosive"},
        {"name": "Docker & Kubernetes", "demand_score": 82, "cohort_impact": "High"},
        {"name": "SQL & Relational DBs", "demand_score": 76, "cohort_impact": "Moderate"}
    ]

    return {
        "total_learners": max(user_cnt, 5),
        "avg_readiness": avg_pct,
        "remedial_interventions": max(remedial_cnt, 1),
        "total_assessments": total_tests,
        "top_skill_gaps": skill_gaps
    }

def get_cohort_table_data():
    with get_db() as con:
        users = con.execute("""
            SELECT id, name, email, auth_provider, avatar, target_career, role, skills, xp, streak_days, last_login
            FROM users
            ORDER BY xp DESC
        """).fetchall()

    benchmarks = {b["role"]: b for b in get_role_benchmarks()}
    cohort_rows = []

    for u in users:
        u_dict = dict(u)
        career = u_dict.get("target_career") or "Full Stack Developer"
        user_skills = u_dict.get("skills") or "Python, SQL, HTML"

        bench = benchmarks.get(career)
        if bench:
            core_skills = [s.strip() for s in bench["core_skills"].split(",") if s.strip()]
        else:
            core_skills = ["Python", "SQL", "JavaScript", "React", "Docker"]

        user_skills_list = [s.strip().lower() for s in user_skills.split(",") if s.strip()]
        strengths = []
        gaps = []
        for s in core_skills:
            if any(us in s.lower() or s.lower() in us for us in user_skills_list):
                strengths.append(s)
            else:
                gaps.append(s)

        pct = round((len(strengths) / len(core_skills)) * 100) if core_skills else 50
        status = "On Track" if pct >= 60 else ("Remedial Sprint" if pct < 45 else "Active Track")

        cohort_rows.append({
            "id": u_dict["id"],
            "name": u_dict["name"],
            "email": u_dict["email"],
            "avatar": u_dict["avatar"] or u_dict["name"][:2].upper(),
            "provider": u_dict["auth_provider"],
            "role": u_dict["role"],
            "target_career": career,
            "xp": u_dict.get("xp", 750),
            "streak_days": u_dict.get("streak_days", 3),
            "readiness_pct": pct,
            "strengths": strengths if strengths else ["Core Competencies"],
            "gaps": gaps if gaps else ["Mastery Achieved"],
            "status": status,
            "last_login": u_dict["last_login"][:16] if u_dict.get("last_login") else "Recently"
        })
    return cohort_rows

def get_role_benchmarks() -> List[Dict[str, Any]]:
    """Retrieve curriculum role benchmarks with in-memory caching for performance."""
    global _BENCHMARKS_CACHE
    if _BENCHMARKS_CACHE is not None:
        return [dict(b) for b in _BENCHMARKS_CACHE]
    with get_db() as con:
        rows = con.execute("""
            SELECT id, role, demand, estimated_weeks, core_skills, description, updated_at
            FROM role_benchmarks
            ORDER BY id ASC
        """).fetchall()
    _BENCHMARKS_CACHE = [dict(r) for r in rows]
    return [dict(b) for b in _BENCHMARKS_CACHE]

def save_role_benchmark(role: str, demand: str, estimated_weeks: str, core_skills: str, description: str = "") -> None:
    """Save or update curriculum role benchmark and invalidate in-memory cache."""
    global _BENCHMARKS_CACHE
    _BENCHMARKS_CACHE = None
    with get_db() as con:
        con.execute("""
            INSERT INTO role_benchmarks (role, demand, estimated_weeks, core_skills, description, updated_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(role) DO UPDATE SET
                demand = excluded.demand,
                estimated_weeks = excluded.estimated_weeks,
                core_skills = excluded.core_skills,
                description = excluded.description,
                updated_at = CURRENT_TIMESTAMP
        """, (role.strip(), demand.strip(), estimated_weeks.strip(), core_skills.strip(), description.strip()))
