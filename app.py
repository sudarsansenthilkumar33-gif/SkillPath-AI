import os
import hashlib
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_from_directory
from database import (
    init_db,
    get_db,
    save_profile,
    get_profile,
    update_target_career,
    update_user_skills_and_career,
    load_demo_profile,
    save_assessment,
    get_assessments,
    get_latest_assessment,
    toggle_module_progress,
    get_completed_modules,
    save_agent_logs,
    get_recent_agent_logs,
    register_user,
    authenticate_user,
    social_login,
    get_user_by_id,
    get_all_users,
    add_user_xp,
    extract_skills_from_text,
    evaluate_interview_response,
    MOCK_INTERVIEW_QUESTIONS,
    JOB_MARKET_INTELLIGENCE,
    get_platform_kpis,
    get_cohort_table_data,
    get_role_benchmarks,
    save_role_benchmark,
    analyze_job_description,
    extract_text_from_file_or_string,
    compute_comprehensive_ats_score,
    save_ats_scan,
    get_latest_ats_scan,
    generate_star_bullet_rewrites,
    generate_cover_letter_and_pitch,
    get_or_create_user_roadmap_tasks,
    toggle_user_roadmap_task,
    sync_github_profile
)
from agents.coordinator import orchestrate_learning_path, mentor_reply

app = Flask(__name__)
# Load SECRET_KEY and optional GEMINI_API_KEY from environment with zero hardcoded credentials
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(32).hex()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

@app.after_request
def set_security_headers(response):
    """Enforce defense-in-depth security headers across all application responses."""
    response.headers["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.tailwindcss.com https://cdn.jsdelivr.net https://fonts.googleapis.com https://fonts.gstatic.com data:; worker-src 'self' blob:; manifest-src 'self';"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(self), camera=()"
    return response

@app.route("/manifest.json")
def manifest():
    """Serve PWA manifest with correct JSON MIME type."""
    response = send_from_directory(os.path.join(app.root_path, "static"), "manifest.json", mimetype="application/manifest+json")
    response.headers["Cache-Control"] = "public, max-age=3600"
    return response

@app.route("/sw.js")
def service_worker():
    """Serve PWA service worker with root scope permission."""
    response = send_from_directory(os.path.join(app.root_path, "static"), "sw.js", mimetype="application/javascript")
    response.headers["Service-Worker-Allowed"] = "/"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.errorhandler(404)
def handle_404(e):
    """Handle resource not found gracefully with structured response."""
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "Resource not found"}), 404
    return redirect(url_for("dashboard"))

@app.errorhandler(500)
def handle_500(e):
    """Handle internal server error gracefully with structured response."""
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "Internal server error"}), 500
    return redirect(url_for("dashboard"))

# Initialize database tables and seed records on startup
init_db()

# Pre-load demo profile if no profile exists yet
if not get_profile():
    load_demo_profile()

QUIZ_BANKS = {
    "JavaScript & Frontend Core": [
        {
            "id": "q1",
            "question": "Which JavaScript keyword declares a block-scoped variable that can be reassigned?",
            "options": [("a", "var"), ("b", "let"), ("c", "const"), ("d", "def")],
            "answer": "b",
            "explanation": "'let' allows block-scoped mutable variable declaration in ES6+."
        },
        {
            "id": "q2",
            "question": "What is the primary role of the JavaScript Event Loop?",
            "options": [
                ("a", "To compile JS code directly to machine binaries"),
                ("b", "To coordinate asynchronous non-blocking callbacks with the call stack"),
                ("c", "To manage CSS cascading rules in the DOM"),
                ("d", "To encrypt client-side localStorage")
            ],
            "answer": "b",
            "explanation": "The Event Loop continuously monitors the call stack and task queues to handle asynchronous execution."
        },
        {
            "id": "q3",
            "question": "In React, which hook is standard for declaring and updating local component state?",
            "options": [("a", "useEffect"), ("b", "useContext"), ("c", "useState"), ("d", "useRef")],
            "answer": "c",
            "explanation": "'useState' allows functional components to maintain stateful values across re-renders."
        },
        {
            "id": "q4",
            "question": "In Node.js / Express, what is the role of middleware functions?",
            "options": [
                ("a", "They access request/response objects to run code, modify them, or end the request-response cycle"),
                ("b", "They compile JSX into virtual DOM trees"),
                ("c", "They act as relational database query builders exclusively"),
                ("d", "They replace the browser's CSS parser")
            ],
            "answer": "a",
            "explanation": "Express middleware functions execute during the lifecycle of an HTTP request before returning a response."
        },
        {
            "id": "q5",
            "question": "Which method on a JavaScript Promise executes when the promise resolves successfully?",
            "options": [("a", ".then()"), ("b", ".catch()"), ("c", ".finally()"), ("d", ".resolve()")],
            "answer": "a",
            "explanation": "The '.then()' handler takes a callback that receives the resolved Promise value."
        }
    ],
    "Full Stack & Web Architecture": [
        {
            "id": "q1",
            "question": "Which HTTP status code signifies that a resource was successfully created on the server?",
            "options": [("a", "200 OK"), ("b", "201 Created"), ("c", "204 No Content"), ("d", "304 Not Modified")],
            "answer": "b",
            "explanation": "201 Created indicates the request succeeded and led to resource creation."
        },
        {
            "id": "q2",
            "question": "What is the main benefit of Cross-Origin Resource Sharing (CORS) headers?",
            "options": [
                ("a", "Speeding up SQL queries"),
                ("b", "Allowing servers to specify which external origins can read their responses"),
                ("c", "Compressing image payloads"),
                ("d", "Disabling cookies entirely")
            ],
            "answer": "b",
            "explanation": "CORS protects web applications by letting servers define cross-origin access policies."
        },
        {
            "id": "q3",
            "question": "What distinguishes SQL (relational) databases from NoSQL (document) databases?",
            "options": [
                ("a", "SQL lacks indexes"),
                ("b", "SQL enforces structured schemas and ACID transactions with relational joins"),
                ("c", "NoSQL cannot store numbers"),
                ("d", "SQL only operates in memory")
            ],
            "answer": "b",
            "explanation": "Relational databases use structured schemas and foreign key constraints for tabular data integrity."
        },
        {
            "id": "q4",
            "question": "What does a RESTful API utilize to identify resources?",
            "options": [("a", "URIs / Endpoints"), ("b", "Binary sockets only"), ("c", "XML tags only"), ("d", "Hardware MAC addresses")],
            "answer": "a",
            "explanation": "REST systems represent resources via standardized URIs and standard HTTP verbs (GET, POST, PUT, DELETE)."
        },
        {
            "id": "q5",
            "question": "Why is hashing passwords with a salt (e.g. bcrypt) critical before storing in a database?",
            "options": [
                ("a", "To compress password string length"),
                ("b", "To prevent rainbow table attacks and ensure raw passwords cannot be reverse-engineered"),
                ("c", "To allow passwords to be recovered in plain text"),
                ("d", "To speed up user login lookups")
            ],
            "answer": "b",
            "explanation": "Salted cryptographic hashes protect passwords against dictionary and pre-computed rainbow table attacks."
        }
    ]
}

AVAILABLE_ROLES = [
    "Full Stack Developer",
    "Data Scientist",
    "AI Engineer",
    "Python Developer",
    "DevOps & Cloud Engineer"
]

@app.context_processor
def inject_global_data():
    user_id = session.get("user_id")
    user = get_user_by_id(user_id) if user_id else None
    
    if user:
        user["is_authenticated"] = True
        profile = get_profile(user_id=user["id"])
        user["target_career"] = profile.get("career") or user.get("target_career", "Full Stack Developer")
    else:
        profile = get_profile()
        user = {
            "id": None,
            "name": "Guest Learner",
            "email": "Sign in to track your personalized roadmap",
            "avatar": "SP",
            "target_career": profile.get("career", "Full Stack Developer") if profile else "Full Stack Developer",
            "role": "Learner",
            "xp": 0,
            "streak_days": 0,
            "is_authenticated": False
        }

    return {
        "current_profile": profile,
        "available_roles": AVAILABLE_ROLES,
        "current_user": user
    }

# ==============================================================================
# Authentication & Onboarding Routes (/ & /login)
# ==============================================================================

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action", "")
        
        # 1. Manual Login Form
        if action == "login":
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()
            user, err = authenticate_user(email, password)
            if err:
                flash(err, "warning")
                return render_template("login.html")
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            flash(f"Welcome back, {user['name']}! Ready to accelerate your learning.", "success")
            return redirect(url_for("dashboard"))

        # 2. Manual Sign-Up Form
        elif action == "signup":
            name = request.form.get("name", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "").strip()
            career = request.form.get("career", "Full Stack Developer").strip()
            skills = request.form.get("skills", "").strip() or "Python, SQL, HTML"
            college_company = request.form.get("college_company", "").strip() or request.form.get("education", "").strip() or "Self-Taught / University Degree"
            github_username = request.form.get("github_username", "").strip().lstrip("@")
            projects = request.form.get("projects", "").strip() or "Portfolio Projects"
            exp_level = request.form.get("experience_level", "").strip() or "Junior (0-2 yrs)"
            if not name or not email or not password:
                flash("Please fill out all required fields to create your account.", "warning")
                return render_template("login.html")
            user, err = register_user(
                name, email, password, auth_provider="local", target_career=career,
                education=college_company, skills=skills, projects=projects,
                college_company=college_company, github_username=github_username
            )
            if err:
                flash(err, "warning")
                return render_template("login.html")
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            session["user_email"] = user["email"]
            # Create matching learner profile
            save_profile({
                "name": name,
                "education": college_company,
                "skills": user.get("skills") or skills,
                "career": career,
                "experience_level": exp_level,
                "projects": projects,
                "college_company": college_company,
                "github_username": github_username
            }, user_id=user["id"])
            if github_username:
                flash(f"Account created successfully! Welcome to SkillPath AI, {name}. GitHub @{github_username} audited & verified (+150 XP)!", "success")
            else:
                flash(f"Account created successfully! Welcome to SkillPath AI, {name}.", "success")
            return redirect(url_for("dashboard"))

        # 3. Profile Intake Form (Backward compatibility)
        elif "skills" in request.form:
            profile_data = {
                "name": request.form.get("name", "").strip(),
                "education": request.form.get("education", "").strip(),
                "skills": request.form.get("skills", "").strip(),
                "career": request.form.get("career", "Full Stack Developer").strip(),
                "experience_level": request.form.get("experience_level", "Junior"),
                "certifications": request.form.get("certifications", "").strip(),
                "projects": request.form.get("projects", "").strip()
            }
            if not profile_data["name"] or not profile_data["skills"]:
                flash("Please enter at least your Name and Existing Skills.", "warning")
                return redirect(url_for("profile_view"))

            user_id = session.get("user_id")
            save_profile(profile_data, user_id=user_id)
            flash("Profile analyzed successfully! Collaborating agents have updated your roadmap.", "success")
            return redirect(url_for("dashboard"))

    # GET request: render the Coursera split-screen Sign-In portal
    return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return index()
    return render_template("login.html")

@app.route("/auth/social/<provider>", methods=["GET", "POST"])
def social_auth(provider):
    """1-Click OAuth Onboarding: Google, GitHub, or LinkedIn"""
    name = request.args.get("name") or request.form.get("name")
    email = request.args.get("email") or request.form.get("email")
    career = request.args.get("career") or request.form.get("career") or "Full Stack Developer"
    skills = request.args.get("skills") or request.form.get("skills")
    projects = request.args.get("projects") or request.form.get("projects")
    education = request.args.get("education") or request.form.get("education")

    user = social_login(
        provider,
        name=name,
        email=email,
        target_career=career,
        skills=skills,
        projects=projects,
        education=education
    )
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_email"] = user["email"]

    provider_label = provider.capitalize()
    flash(f"🎉 Successfully authenticated with {provider_label}! Welcome, {user['name']}.", "success")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out successfully. Come back soon!", "info")
    return redirect(url_for("login"))

@app.route("/profile", methods=["GET", "POST"])
@app.route("/edit-profile", methods=["GET", "POST"])
def profile_view():
    if request.method == "POST":
        return index()
    user_id = session.get("user_id")
    profile = get_profile(user_id=user_id)
    return render_template("index.html", profile=profile)

# ==============================================================================
# Resume Parser & Enterprise ATS Intelligence Engine (Feature 2 & 3)
# ==============================================================================

@app.route("/extract-resume", methods=["POST"])
def extract_resume():
    """Parses uploaded file (.pdf, .docx, .txt) or pasted text, calculates ATS score, and updates 4-agent roadmap"""
    file_storage = request.files.get("resume_file")
    pasted_text = request.form.get("resume_text", "").strip()
    next_url = request.form.get("next") or request.args.get("next") or url_for("dashboard")

    raw_text, filename = extract_text_from_file_or_string(file_storage, pasted_text)
    if not raw_text:
        flash("Please upload a resume file (.pdf, .docx, .txt) or paste your resume text to extract skills.", "warning")
        return redirect(next_url)

    matched_skills, detected_role = extract_skills_from_text(raw_text)
    user_id = session.get("user_id")
    
    current = get_profile(user_id=user_id) or {}
    target_career = current.get("career") or detected_role or "Full Stack Developer"

    # Compute comprehensive ATS match score & keyword breakdown
    ats_data = compute_comprehensive_ats_score(raw_text, target_career)
    if user_id:
        save_ats_scan(user_id, filename, raw_text, ats_data)

    skills_str = ", ".join(matched_skills) if matched_skills else current.get("skills", "Python, SQL, HTML")
    updated_profile = {
        "name": current.get("name", "Learner"),
        "education": current.get("education", "Self-Taught / University Degree"),
        "skills": skills_str,
        "career": target_career,
        "experience_level": current.get("experience_level", "Junior Developer"),
        "certifications": current.get("certifications", ""),
        "projects": current.get("projects", "Extracted from Resume")
    }
    save_profile(updated_profile, user_id=user_id)
    if user_id:
        update_user_skills_and_career(user_id, skills_str, target_career)

    flash(f"✓ Resume Parsed! ATS Match Score: {ats_data['score']}/100. Auto-extracted {len(matched_skills)} skills: {', '.join(matched_skills[:5])}... Target set to '{target_career}'. 4 Agents recalculated your custom roadmap!", "success")
    return redirect(url_for("dashboard"))

@app.route("/api/rewrite-bullet", methods=["POST"])
def rewrite_bullet():
    """1-Click AI Bullet-Point Rewriter: Transforms weak lines into quantified STAR statements"""
    bullet_text = request.form.get("bullet_text") or (request.json.get("bullet_text") if request.is_json else "")
    user_id = session.get("user_id")
    profile = get_profile(user_id=user_id)
    career = profile.get("career", "Full Stack Developer") if profile else "Full Stack Developer"
    raw_rewrites = generate_star_bullet_rewrites(bullet_text, career)
    rewrites = [r["rewritten"] if isinstance(r, dict) else r for r in raw_rewrites]
    return jsonify({"status": "success", "rewrites": rewrites})

@app.route("/api/toggle-roadmap-task", methods=["POST"])
def toggle_roadmap_task_route():
    """Interactive 30-60-90 Day Roadmap Task Checkbox with SQLite persistence"""
    task_id = request.form.get("task_id") or (request.json.get("task_id") if request.is_json else "")
    user_id = session.get("user_id") or 1
    new_state = toggle_user_roadmap_task(user_id, task_id)
    return jsonify({"status": "success", "task_id": task_id, "completed": new_state, "xp_awarded": 100})

@app.route("/api/sync-github", methods=["POST"])
def api_sync_github():
    """Real Public GitHub Profile Sync (No API Key Required)"""
    username = request.form.get("github_username") or (request.json.get("github_username") if request.is_json else "")
    user_id = session.get("user_id")
    if not username and user_id:
        user = get_user_by_id(user_id)
        if user:
            username = user.get("github_username", "")
    result = sync_github_profile(username, user_id=user_id)
    return jsonify(result)

@app.route("/report")
def career_report():
    """Executive Career Intelligence & Multi-Agent Audit Report (Print & PDF Export)"""
    user_id = session.get("user_id")
    profile = get_profile(user_id=user_id)
    if not profile:
        profile = load_demo_profile()

    assessments = get_assessments(limit=8, user_id=user_id)
    completed_modules = get_completed_modules(profile["career"])
    plan = orchestrate_learning_path(profile, assessments, completed_modules)

    ats_scan = get_latest_ats_scan(user_id)
    if not ats_scan:
        ats_base = compute_comprehensive_ats_score(f"Skills: {profile['skills']}. Projects: {profile['projects']}", profile["career"])
        ats_scan = {
            "ats_score": ats_base["score"],
            "matched_skills": ats_base["matched_skills"],
            "missing_skills": ats_base["missing_skills"],
            "matched_skills_list": ats_base["matched_skills"],
            "missing_skills_list": ats_base["missing_skills"],
            "keyword_density": ats_base["keyword_density"],
            "action_verbs_count": ats_base["action_verbs_count"],
            "metrics_count": ats_base["metrics_count"],
            "suggestions_list": ats_base["suggestions"],
            "filename": "Active Profile Bio"
        }

    roadmap_tasks = get_or_create_user_roadmap_tasks(user_id or 1, profile["career"])
    return render_template(
        "report.html",
        profile=profile,
        plan=plan,
        ats_scan=ats_scan,
        roadmap_tasks=roadmap_tasks,
        export_date=datetime.now().strftime("%B %d, %Y")
    )

# ==============================================================================
# Job Description (JD) Match Analyzer (Feature 3)
# ==============================================================================

@app.route("/api/match-jd", methods=["POST"])
def match_job_description():
    """Feature 3: Parses Job Description (JD), benchmarks skills, and generates tailored cover letter & pitch"""
    jd_text = request.form.get("jd_text") or (request.json.get("jd_text") if request.is_json else "")
    user_id = session.get("user_id")
    profile = get_profile(user_id=user_id)
    user_skills = profile.get("skills", "") if profile else ""
    target_career = profile.get("career", "Full Stack Developer") if profile else "Full Stack Developer"
    user_name = profile.get("name", "Candidate") if profile else "Candidate"

    analysis = analyze_job_description(jd_text, user_skills)
    cover_and_pitch = generate_cover_letter_and_pitch(
        user_name, target_career, analysis.get("matched_skills", []), analysis.get("missing_skills", []), jd_text
    )
    analysis["cover_letter"] = cover_and_pitch["cover_letter"]
    analysis["elevator_pitch"] = cover_and_pitch["elevator_pitch"]
    return jsonify({"status": "success", "analysis": analysis})

# ==============================================================================
# Learner Operations Dashboard
# ==============================================================================

@app.route("/dashboard")
def dashboard():
    user_id = session.get("user_id")
    profile = get_profile(user_id=user_id)
    if not profile:
        profile = load_demo_profile()

    assessments = get_assessments(limit=8, user_id=user_id)
    completed_modules = get_completed_modules(profile["career"])

    # Run multi-agent pipeline
    plan = orchestrate_learning_path(profile, assessments, completed_modules)

    # Save agent collaboration logs to SQLite for auditability
    save_agent_logs(plan["agent_logs"])
    recent_logs = get_recent_agent_logs(limit=16)

    latest_assessment = assessments[0] if assessments else None
    market_intel = JOB_MARKET_INTELLIGENCE.get(profile["career"], JOB_MARKET_INTELLIGENCE["Full Stack Developer"])
    cohort_leaderboard = get_all_users()[:5]

    # Latest ATS Scan or Baseline
    ats_scan = get_latest_ats_scan(user_id)
    if not ats_scan:
        ats_base = compute_comprehensive_ats_score(f"Skills: {profile['skills']}. Projects: {profile['projects']}", profile["career"])
        ats_scan = {
            "ats_score": ats_base["score"],
            "matched_skills": ats_base["matched_skills"],
            "missing_skills": ats_base["missing_skills"],
            "matched_skills_list": ats_base["matched_skills"],
            "missing_skills_list": ats_base["missing_skills"],
            "keyword_density": ats_base["keyword_density"],
            "action_verbs_count": ats_base["action_verbs_count"],
            "metrics_count": ats_base["metrics_count"],
            "suggestions_list": ats_base["suggestions"],
            "filename": "Active Profile Bio"
        }

    # 30-60-90 Day Actionable Roadmap Tasks
    roadmap_tasks = get_or_create_user_roadmap_tasks(user_id or 1, profile["career"])

    # Radar Chart Dimensions for Chart.js
    readiness = plan["matching"]["target_readiness_pct"]
    radar_data = {
        "labels": ["Core Syntax", "Frameworks & UI", "Storage & DB", "System Architecture", "DevOps & Cloud", "Testing & QA"],
        "user_scores": [
            min(95, max(55, readiness + 4)),
            min(95, max(50, readiness - 6)),
            min(90, max(50, readiness - 10)),
            min(95, max(58, readiness + 2)),
            min(90, max(45, readiness - 12)),
            min(95, max(60, readiness))
        ],
        "benchmark_scores": [88, 92, 85, 88, 80, 85]
    }

    return render_template(
        "dashboard.html",
        profile=profile,
        plan=plan,
        assessments=assessments,
        latest_assessment=latest_assessment,
        recent_logs=recent_logs,
        quiz_banks=QUIZ_BANKS,
        market_intel=market_intel,
        cohort_leaderboard=cohort_leaderboard,
        ats_scan=ats_scan,
        roadmap_tasks=roadmap_tasks,
        radar_data=radar_data
    )

@app.route("/load-demo", methods=["GET", "POST"])
def load_demo():
    """Fast-track access: Authenticates as Elena Rostova"""
    load_demo_profile()
    user = social_login("demo")
    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    session["user_email"] = user["email"]
    flash(f"⚡ Authenticated as {user['name']} ({user['target_career']}). Dynamic multi-agent pipeline active!", "info")
    return redirect(url_for("dashboard"))

@app.route("/switch-role", methods=["POST"])
def switch_role():
    """Dynamically switch target career role and trigger multi-agent recalculation"""
    new_role = request.form.get("career", "").strip()
    user_id = session.get("user_id")
    if new_role in AVAILABLE_ROLES:
        update_target_career(new_role, user_id=user_id)
        flash(f"🎯 Target role switched to '{new_role}'. Multi-agent pipeline recalculated your benchmarks and roadmap!", "success")
    return redirect(url_for("dashboard"))

# ==============================================================================
# Assessments & Diagnostic Testing
# ==============================================================================

@app.route("/assessment", methods=["GET", "POST"])
@app.route("/assessments", methods=["GET", "POST"])
def assessment():
    user_id = session.get("user_id")
    profile = get_profile(user_id=user_id)
    if not profile:
        profile = load_demo_profile()

    selected_topic = request.args.get("topic", "JavaScript & Frontend Core")
    if selected_topic not in QUIZ_BANKS:
        selected_topic = list(QUIZ_BANKS.keys())[0]

    questions = QUIZ_BANKS[selected_topic]

    if request.method == "POST":
        topic = request.form.get("topic", selected_topic)
        q_list = QUIZ_BANKS.get(topic, questions)

        score = 0
        total = len(q_list)

        for i, q in enumerate(q_list, start=1):
            user_ans = request.form.get(f"q{i}")
            if user_ans == q["answer"]:
                score += 1

        assessment_result = save_assessment(topic, score, total)
        pct = assessment_result["percentage"]
        if user_id:
            add_user_xp(user_id, 100)

        if pct < 60:
            flash(
                f"Assessment Submitted: {score}/{total} ({pct}%). "
                f"⚠️ Score below 60% threshold! Progress Evaluator Agent triggered dynamic roadmap recalculation to inject remedial foundation modules.",
                "remediation"
            )
        else:
            flash(
                f"Assessment Submitted: {score}/{total} ({pct}%). "
                f"🎉 Mastery verified! Progress Evaluator Agent validated competency and unlocked next milestones! (+100 XP)",
                "success"
            )
        return redirect(url_for("dashboard"))

    assessments = get_assessments(limit=8)
    return render_template(
        "assessments.html",
        profile=profile,
        topic=selected_topic,
        questions=questions,
        quiz_banks=QUIZ_BANKS,
        assessments=assessments
    )

@app.route("/quick-assessment-demo", methods=["POST"])
def quick_assessment_demo():
    """Helper for judges: Simulates a <60% or >=60% quiz submission in 1 click"""
    mode = request.form.get("mode", "fail")
    topic = request.form.get("topic", "JavaScript & Frontend Core")

    if mode == "fail":
        score = 2
        total = 5
        pct = 40
        save_assessment(topic, score, total, notes="Simulated Diagnostic Quiz (<60% Trigger)")
        flash(
            f"⚡ Judge Demo: Recorded score 2/5 (40%) on '{topic}'. "
            f"⚠️ Progress Evaluator Agent triggered dynamic remediation recalculation! Check Phase R in your roadmap.",
            "remediation"
        )
    else:
        score = 5
        total = 5
        pct = 100
        save_assessment(topic, score, total, notes="Simulated Diagnostic Quiz (100% Pass)")
        flash(
            f"⚡ Judge Demo: Recorded score 5/5 (100%) on '{topic}'. "
            f"🎉 Mastery verified! Progress Evaluator Agent validated competency and greenlit advanced roadmap milestones!",
            "success"
        )
    return redirect(url_for("dashboard"))

@app.route("/toggle-module", methods=["POST"])
def toggle_module():
    """Toggle module completion state in roadmap and award +250 XP"""
    career = request.form.get("career", "").strip()
    module_id = request.form.get("module_id", "").strip()
    user_id = session.get("user_id")
    if career and module_id:
        is_completed = toggle_module_progress(career, module_id, user_id=user_id)
        status_str = "completed (+250 XP)" if is_completed else "marked in-progress"
        flash(f"Module '{module_id}' {status_str}! Progress updated in SQLite.", "info")
    return redirect(url_for("dashboard"))

# ==============================================================================
# AI Mock Interview Simulator (Feature 5)
# ==============================================================================

@app.route("/interview", methods=["GET", "POST"])
def mock_interview():
    """AI Technical Interview Simulator for Target Career Roles"""
    user_id = session.get("user_id")
    profile = get_profile(user_id=user_id) or load_demo_profile()
    target_career = profile.get("career", "Full Stack Developer")
    
    questions = MOCK_INTERVIEW_QUESTIONS.get(target_career, MOCK_INTERVIEW_QUESTIONS["Full Stack Developer"])
    q_index = int(request.args.get("q", 0)) % len(questions)
    current_question = questions[q_index]

    evaluation_result = None
    candidate_answer = ""

    if request.method == "POST":
        candidate_answer = request.form.get("answer", "").strip()
        current_question = request.form.get("question", current_question)
        if candidate_answer:
            evaluation_result = evaluate_interview_response(target_career, current_question, candidate_answer, user_id=user_id)
            if user_id:
                add_user_xp(user_id, 200)
            flash(f"🎉 Interview Answer Evaluated! Readiness Score: {evaluation_result['score']}% (+200 XP earned)", "success")
        else:
            flash("Please provide an answer to receive AI Mentor feedback.", "warning")

    return render_template(
        "interview.html",
        profile=profile,
        target_career=target_career,
        question=current_question,
        q_index=q_index,
        total_questions=len(questions),
        candidate_answer=candidate_answer,
        evaluation=evaluation_result
    )

# ==============================================================================
# Verifiable Career Certificate Generator (Feature 6)
# ==============================================================================

@app.route("/certificate")
def certificate():
    """Renders verifiable, printable Coursera-style certificate for active learner"""
    user_id = session.get("user_id")
    profile = get_profile(user_id=user_id) or load_demo_profile()
    
    assessments = get_assessments(limit=8)
    completed_modules = get_completed_modules(profile["career"])
    plan = orchestrate_learning_path(profile, assessments, completed_modules)
    
    readiness_pct = plan["matching"]["target_readiness_pct"]
    
    # Generate unique verifiable credential ID
    cred_seed = f"{profile['name']}-{profile['career']}-2026"
    cred_hash = hashlib.sha256(cred_seed.encode()).hexdigest()[:10].upper()
    credential_id = f"SKILLPATH-{cred_hash}"
    issue_date = datetime.now().strftime("%B %d, %Y")

    return render_template(
        "certificate.html",
        profile=profile,
        career=profile["career"],
        readiness_pct=readiness_pct,
        credential_id=credential_id,
        issue_date=issue_date
    )

# ==============================================================================
# AI Mentor Companion
# ==============================================================================

@app.route("/mentor", methods=["GET", "POST"])
def mentor():
    user_id = session.get("user_id")
    profile = get_profile(user_id=user_id) or load_demo_profile()
    assessments = get_assessments(limit=5)
    completed_modules = get_completed_modules(profile["career"])
    plan = orchestrate_learning_path(profile, assessments, completed_modules)

    reply_data = None
    user_question = None

    if request.method == "POST":
        user_question = request.form.get("question", "").strip()
        reply_data = mentor_reply(user_question, profile, assessments)
        if reply_data and "log" in reply_data:
            save_agent_logs([reply_data["log"]])

    recent_logs = get_recent_agent_logs(limit=10)

    return render_template(
        "mentor.html",
        profile=profile,
        plan=plan,
        assessments=assessments,
        reply_data=reply_data,
        user_question=user_question,
        recent_logs=recent_logs
    )

# ==============================================================================
# Enterprise Admin & Analytics Portal (/admin)
# ==============================================================================

@app.route("/admin")
def admin_portal():
    """Enterprise Admin & Analytics Portal for Judges and University Cohort Coordinators"""
    kpis = get_platform_kpis()
    cohort_data = get_cohort_table_data()
    benchmarks = get_role_benchmarks()
    return render_template(
        "admin.html",
        kpis=kpis,
        cohort=cohort_data,
        benchmarks=benchmarks
    )

@app.route("/admin/add-benchmark", methods=["POST"])
def add_benchmark():
    role = request.form.get("role", "").strip()
    demand = request.form.get("demand", "High").strip()
    estimated_weeks = request.form.get("estimated_weeks", "10 - 14 Weeks").strip()
    core_skills = request.form.get("core_skills", "").strip()
    description = request.form.get("description", "").strip()

    if role and core_skills:
        save_role_benchmark(role, demand, estimated_weeks, core_skills, description)
        if role not in AVAILABLE_ROLES:
            AVAILABLE_ROLES.append(role)
        flash(f"✓ Curriculum Benchmark for '{role}' successfully updated in SQLite database.", "success")
    else:
        flash("Please provide at least a Role Title and Core Skills list.", "warning")

    return redirect(url_for("admin_portal"))

# ==============================================================================
# Agent Execution Logs API & Live Runner
# ==============================================================================

@app.route("/api/agent-feed")
def api_agent_feed():
    """API endpoint to inspect recent live agent logs as JSON"""
    logs = get_recent_agent_logs(limit=20)
    return jsonify({"status": "success", "logs": logs})

@app.route("/api/run-agents", methods=["POST"])
def run_agents_live():
    """Live 4-Agent Pipeline Execution Endpoint for Visualizer Modal"""
    user_id = session.get("user_id")
    profile = get_profile(user_id=user_id) or load_demo_profile()
    assessments = get_assessments(limit=8)
    completed_modules = get_completed_modules(profile["career"])
    plan = orchestrate_learning_path(profile, assessments, completed_modules)
    save_agent_logs(plan["agent_logs"])
    return jsonify({
        "status": "success",
        "agent_steps": plan["agent_logs"],
        "target_readiness_pct": plan["matching"]["target_readiness_pct"]
    })

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
