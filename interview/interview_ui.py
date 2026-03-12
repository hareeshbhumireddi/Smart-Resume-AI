"""
Interview Assistant - Streamlit UI
Features: Question Generator, Mock Interview, Answer Evaluation,
          Readiness Score, Resume Section Analyzer, Summary Generator,
          Company-Specific Prep, Follow-Up Questions, Performance Analytics
"""
import json
import random
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from interview.interview_data import (
    init_interview_tables, get_questions_for_skills, get_questions_for_role,
    COMPANY_QUESTIONS, GENERAL_QUESTIONS, SKILL_QUESTIONS, ROLE_QUESTIONS,
    evaluate_answer, save_interview_session, save_interview_answer,
    get_user_interview_stats,
)


def _card(content_html):
    st.markdown(
        f"<div style='background:#1e1e1e;border-radius:12px;padding:1.2rem 1.4rem;"
        f"margin:0.6rem 0;border:1px solid rgba(76,175,80,0.2);'>{content_html}</div>",
        unsafe_allow_html=True,
    )


def render_interview_assistant():
    """Main entry point for the Interview Assistant page."""
    init_interview_tables()

    st.markdown("""
    <div style='background:linear-gradient(135deg,#1b5e20,#2e7d32);padding:1.5rem 2rem;
    border-radius:14px;margin-bottom:1.5rem;'>
    <h1 style='color:white;margin:0;'>🎤 Interview Assistant</h1>
    <p style='color:#c8e6c9;margin:0.4rem 0 0;'>AI-powered interview preparation & mock interview simulator</p>
    </div>
    """, unsafe_allow_html=True)

    tabs = st.tabs([
        "🤔 Question Generator",
        "🎯 Mock Interview",
        "🏢 Company Prep",
        "📄 Resume Section Analyzer",
        "✍️ AI Summary Generator",
        "📊 Performance Analytics",
    ])

    with tabs[0]:
        _render_question_generator()
    with tabs[1]:
        _render_mock_interview()
    with tabs[2]:
        _render_company_prep()
    with tabs[3]:
        _render_section_analyzer()
    with tabs[4]:
        _render_summary_generator()
    with tabs[5]:
        _render_performance_analytics()


# ── TAB 1: Question Generator ──────────────────────────────────────────────────

def _render_question_generator():
    st.subheader("AI Interview Question Generator")
    st.write("Enter your target role and/or skills to get tailored interview questions.")

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        role_input = st.text_input(
            "Target Job Role",
            placeholder="e.g. Software Engineer, Data Scientist",
            key="iq_role",
        )
    with col2:
        skills_input = st.text_input(
            "Your Skills (comma-separated)",
            placeholder="e.g. Python, React, AWS",
            key="iq_skills",
        )
    with col3:
        num_q = st.number_input("# Questions", min_value=3, max_value=20, value=8, key="iq_num")

    if st.button("Generate Questions ✨", type="primary", key="iq_gen"):
        if not role_input.strip() and not skills_input.strip():
            st.warning("Please enter a role or at least one skill.")
            return
        skills = [s.strip() for s in skills_input.split(",") if s.strip()]

        if role_input.strip():
            questions = get_questions_for_role(role_input.strip(), skills)
        else:
            questions = get_questions_for_skills(skills)

        random.shuffle(questions)
        selected = questions[:num_q]

        st.session_state["generated_questions"] = selected
        st.session_state["iq_skills_list"] = skills

    if "generated_questions" in st.session_state:
        qs = st.session_state["generated_questions"]
        st.success(f"Generated {len(qs)} questions!")
        for i, q in enumerate(qs, 1):
            _card(f"<b>Q{i}.</b> {q}")

        st.markdown("---")
        st.subheader("🔁 Generate Follow-up Question")
        selected_q = st.selectbox("Select a question to get a follow-up:", qs, key="followup_sel")
        if st.button("Generate Follow-up", key="gen_followup"):
            followups = _generate_followups(selected_q)
            st.info("**Follow-up Questions:**")
            for fq in followups:
                _card(fq)


def _generate_followups(question: str) -> list:
    q_lower = question.lower()
    followups = []

    if "time you" in q_lower or "example" in q_lower:
        followups = [
            "What would you do differently if you faced the same situation today?",
            "What was the biggest lesson you took from that experience?",
            "How did that experience shape your professional approach?",
        ]
    elif "design" in q_lower or "system" in q_lower:
        followups = [
            "How would you scale this system to handle 10x traffic?",
            "What are the main failure points and how would you handle them?",
            "How would you monitor and alert on this system in production?",
        ]
    elif "explain" in q_lower or "difference" in q_lower:
        followups = [
            "Can you give a real-world example where this concept applies?",
            "What are the performance implications of this approach?",
            "When would you choose NOT to use this?",
        ]
    else:
        followups = [
            "Can you go deeper on that point?",
            "How would this change in a high-scale production environment?",
            "What trade-offs did you consider?",
        ]

    return followups


# ── TAB 2: Mock Interview ──────────────────────────────────────────────────────

def _render_mock_interview():
    st.subheader("Mock Interview Simulator")

    # Setup
    if "mock_started" not in st.session_state or not st.session_state.mock_started:
        _mock_setup()
    else:
        _mock_session()


def _mock_setup():
    st.markdown("**Configure your Mock Interview**")
    col1, col2 = st.columns(2)
    with col1:
        interview_type = st.selectbox(
            "Interview Type",
            ["Role-Based", "Skills-Based", "Behavioral", "Technical", "Mixed"],
            key="mock_type",
        )
        target_role = st.text_input(
            "Target Job Role *", placeholder="e.g. Software Engineer, Data Scientist, Frontend Developer",
            key="mock_role"
        )
    with col2:
        num_questions = st.slider("Number of Questions", 3, 10, 5, key="mock_num")
        skills_input = st.text_input(
            "Your Skills (optional)", placeholder="Python, SQL, React", key="mock_skills"
        )

    # Show role hint
    if target_role:
        role_lower = target_role.lower()
        matched_roles = [r for r in ROLE_QUESTIONS.keys() if any(word in role_lower for word in r.split())]
        if matched_roles:
            st.info(f"✅ Found questions for: **{matched_roles[0].title()}** role")
        else:
            st.info(f"ℹ️ Will use general + skills-based questions for this role")

    if st.button("Start Mock Interview 🎤", type="primary", key="start_mock"):
        if not target_role.strip():
            st.warning("Please enter your target job role.")
            return
        skills = [s.strip() for s in skills_input.split(",") if s.strip()]

        questions = _build_mock_questions(interview_type, target_role, skills, num_questions)
        user_id = st.session_state.get("user_id", 0)
        sid = save_interview_session(user_id, interview_type, "", target_role, skills)

        st.session_state.mock_started = True
        st.session_state.mock_questions = questions
        st.session_state.mock_current = 0
        st.session_state.mock_answers = []
        st.session_state.mock_session_id = sid
        st.session_state.mock_scores = []
        st.rerun()


def _build_mock_questions(interview_type, role, skills, num):
    pool = []
    if interview_type == "Role-Based":
        pool.extend(get_questions_for_role(role, skills))
    elif interview_type in ["Skills-Based", "Technical"]:
        pool.extend(get_questions_for_role(role, skills))
    elif interview_type == "Behavioral":
        pool.extend(GENERAL_QUESTIONS)
        # Add role behavioral questions
        for key, qs in ROLE_QUESTIONS.items():
            if any(word in role.lower() for word in key.split()):
                pool.extend(qs[:4])
    elif interview_type == "Mixed":
        pool.extend(get_questions_for_role(role, skills))
        pool.extend(GENERAL_QUESTIONS)
    if not pool:
        pool = list(GENERAL_QUESTIONS)
    random.shuffle(pool)
    return list(dict.fromkeys(pool))[:num]


def _mock_session():
    questions = st.session_state.mock_questions
    current = st.session_state.mock_current
    total = len(questions)

    if current >= total:
        _mock_results()
        return

    # Progress
    progress = current / total
    st.progress(progress)
    st.markdown(f"**Question {current + 1} of {total}**")

    q = questions[current]
    _card(f"<h3 style='color:#4CAF50;margin:0;'>Q{current+1}.</h3><p style='color:white;font-size:1.1rem;margin:0.4rem 0 0;'>{q}</p>")

    answer = st.text_area(
        "Your Answer",
        height=180,
        placeholder="Type your answer here... Use the STAR method: Situation, Task, Action, Result",
        key=f"mock_answer_{current}",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("⏭️ Skip", key=f"skip_{current}"):
            st.session_state.mock_answers.append({"q": q, "a": "", "score": 0, "feedback": "Skipped"})
            st.session_state.mock_scores.append(0)
            st.session_state.mock_current += 1
            st.rerun()
    with col2:
        if st.button("Submit Answer →", type="primary", key=f"submit_{current}"):
            evaluation = evaluate_answer(q, answer)
            save_interview_answer(
                st.session_state.mock_session_id, q, answer,
                evaluation["score"], evaluation["feedback"]
            )
            st.session_state.mock_answers.append({
                "q": q, "a": answer,
                "score": evaluation["score"],
                "feedback": evaluation["feedback"],
            })
            st.session_state.mock_scores.append(evaluation["score"])
            st.session_state.mock_current += 1

            # Show feedback briefly
            if evaluation["score"] >= 70:
                st.success(f"✅ Score: {evaluation['score']}/100 — {evaluation['feedback']}")
            elif evaluation["score"] >= 40:
                st.warning(f"⚠️ Score: {evaluation['score']}/100 — {evaluation['feedback']}")
            else:
                st.error(f"❌ Score: {evaluation['score']}/100 — {evaluation['feedback']}")

            import time
            time.sleep(1.5)
            st.rerun()


def _mock_results():
    scores = st.session_state.mock_scores
    answers = st.session_state.mock_answers
    avg = sum(scores) / len(scores) if scores else 0

    st.balloons()
    st.markdown("## 🏁 Mock Interview Complete!")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Score", f"{avg:.0f}/100")
    with col2:
        st.metric("Questions Answered", f"{sum(1 for a in answers if a['a'])}/{len(answers)}")
    with col3:
        readiness = "🟢 Interview Ready" if avg >= 70 else "🟡 Almost Ready" if avg >= 50 else "🔴 More Practice Needed"
        st.metric("Readiness", readiness)

    # Radar chart
    categories = ["Technical Knowledge", "Communication", "Structure", "Confidence", "Depth"]
    base = avg / 100
    values = [
        min(100, avg + random.randint(-10, 10)),
        min(100, avg * 0.9 + random.randint(-5, 5)),
        min(100, avg * 1.05 + random.randint(-8, 8)),
        min(100, avg * 0.85 + random.randint(-10, 10)),
        min(100, avg * 0.95 + random.randint(-7, 7)),
    ]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values + [values[0]], theta=categories + [categories[0]], fill="toself", name="Score", line_color="#4CAF50"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white", height=350)
    st.plotly_chart(fig, width='stretch')

    st.markdown("### 📋 Answer Review")
    for i, item in enumerate(answers, 1):
        with st.expander(f"Q{i}: {item['q'][:60]}... — Score: {item['score']}/100"):
            st.markdown(f"**Your Answer:** {item['a'] or '_Skipped_'}")
            st.markdown(f"**Feedback:** {item['feedback']}")

    if st.button("🔄 Start New Interview", type="primary"):
        for k in ["mock_started", "mock_questions", "mock_current", "mock_answers", "mock_scores", "mock_session_id"]:
            st.session_state.pop(k, None)
        st.rerun()


# ── TAB 3: Company Prep ────────────────────────────────────────────────────────

def _render_company_prep():
    st.subheader("Company-Specific Interview Preparation")

    company = st.selectbox("Select Company", list(COMPANY_QUESTIONS.keys()), key="company_sel")
    q_type = st.radio("Question Type", ["Behavioral", "Technical", "Both"], horizontal=True, key="cq_type")

    if st.button("Load Questions", type="primary", key="load_company_qs"):
        cq = COMPANY_QUESTIONS[company]
        all_q = []
        if q_type in ["Behavioral", "Both"]:
            all_q.extend([(q, "Behavioral") for q in cq.get("Behavioral", [])])
        if q_type in ["Technical", "Both"]:
            all_q.extend([(q, "Technical") for q in cq.get("Technical", [])])
        st.session_state["company_questions"] = all_q
        st.session_state["company_name"] = company
        st.session_state["company_scores"] = {}

    # Show questions + answer boxes if loaded
    if st.session_state.get("company_questions"):
        all_q = st.session_state["company_questions"]
        cname = st.session_state.get("company_name", company)
        scores = st.session_state.get("company_scores", {})

        st.success(f"**{cname} Interview Questions** — {len(all_q)} questions")

        for i, (q, qtype) in enumerate(all_q, 1):
            badge_color = "#1565C0" if qtype == "Technical" else "#4a148c"
            score_info = scores.get(i, None)

            # Score color indicator
            if score_info:
                sc = score_info["score"]
                sc_color = "#4CAF50" if sc >= 70 else "#FFA500" if sc >= 40 else "#FF4444"
                score_badge = f"<span style='float:right;background:{sc_color};color:white;border-radius:12px;padding:2px 10px;font-size:0.78rem;font-weight:700;'>{sc}/100</span>"
            else:
                score_badge = ""

            with st.expander(f"Q{i}. {q[:60]}...", expanded=(score_info is None)):
                _card(
                    f"{score_badge}<span style='background:{badge_color};color:white;border-radius:6px;padding:2px 8px;font-size:0.8rem;'>{qtype}</span>"
                    f"<p style='color:white;margin:0.6rem 0 0;font-size:1rem;'><b>Q{i}.</b> {q}</p>"
                )

                # Answer text box
                ans_key = f"cp_answer_{cname}_{i}"
                user_ans = st.text_area(
                    "Your Answer",
                    placeholder="Type your answer here... Use STAR method: Situation → Task → Action → Result",
                    height=130,
                    key=ans_key,
                    label_visibility="collapsed",
                )

                col_a, col_b = st.columns([1, 3])
                with col_a:
                    if st.button("✅ Evaluate", key=f"eval_cp_{cname}_{i}", type="primary"):
                        if not user_ans or len(user_ans.strip()) < 15:
                            st.warning("Please write at least a sentence before evaluating.")
                        else:
                            result = evaluate_answer(q, user_ans)
                            st.session_state["company_scores"][i] = result
                            scores = st.session_state["company_scores"]
                            sc = result["score"]
                            fb = result["feedback"]
                            if sc >= 70:
                                st.success(f"🟢 **Score: {sc}/100** — {fb}")
                            elif sc >= 40:
                                st.warning(f"🟡 **Score: {sc}/100** — {fb}")
                            else:
                                st.error(f"🔴 **Score: {sc}/100** — {fb}")
                            if result.get("keywords_found"):
                                st.caption(f"✨ Strong keywords: {', '.join(result['keywords_found'][:6])}")

                with col_b:
                    if score_info:
                        sc = score_info["score"]
                        sc_color = "#4CAF50" if sc >= 70 else "#FFA500" if sc >= 40 else "#FF4444"
                        st.markdown(
                            f"<div style='padding:6px 14px;background:{sc_color}22;border:1px solid {sc_color}44;"
                            f"border-radius:8px;color:{sc_color};font-size:0.85rem;margin-top:4px;'"
                            f">Last score: <b>{sc}/100</b> — {score_info['feedback']}</div>",
                            unsafe_allow_html=True
                        )

        # Overall Readiness from answered questions
        answered = [v for v in scores.values()]
        if answered:
            avg = sum(v["score"] for v in answered) / len(answered)
            readiness_label = "🟢 Interview Ready" if avg >= 70 else "🟡 Almost Ready" if avg >= 50 else "🔴 Needs Practice"
            pct = len(answered) / len(all_q) * 100

            st.markdown("---")
            st.markdown("### 📊 Your Readiness Summary")
            c1, c2, c3 = st.columns(3)
            c1.metric("Questions Answered", f"{len(answered)}/{len(all_q)}")
            c2.metric("Average Score", f"{avg:.0f}/100")
            c3.metric("Readiness", readiness_label)

            # Progress bar
            st.markdown(f"**Completion:** {pct:.0f}%")
            st.progress(pct / 100)

            if len(answered) == len(all_q):
                if avg >= 70:
                    st.success("🎉 All questions answered! You're ready to ace this interview!")
                elif avg >= 50:
                    st.warning("💪 Good effort! Review your lower-scored answers and try again.")
                else:
                    st.error("📚 Keep practicing! Focus on structuring answers with STAR method.")

    # Readiness Score Calculator
    st.markdown("---")
    st.subheader("📊 Interview Readiness Score")
    col1, col2 = st.columns(2)
    with col1:
        resume_score = st.slider("Resume ATS Score", 0, 100, 65, key="ready_resume")
        skills_match = st.slider("Skills Match %", 0, 100, 70, key="ready_skills")
    with col2:
        mock_score = st.slider("Mock Interview Avg Score", 0, 100,
                               int(sum(st.session_state.get("mock_scores", [50])) /
                                   max(len(st.session_state.get("mock_scores", [1])), 1)),
                               key="ready_mock")
        prep_hours = st.slider("Prep Hours Invested", 0, 50, 10, key="ready_hours")

    if st.button("Calculate Readiness", key="calc_readiness"):
        readiness = (resume_score * 0.25 + skills_match * 0.30 +
                     mock_score * 0.35 + min(prep_hours * 2, 100) * 0.10)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=readiness,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Interview Readiness Score", "font": {"color": "white", "size": 16}},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#4CAF50" if readiness >= 70 else "#FFA500" if readiness >= 50 else "#FF4444"},
                "steps": [
                    {"range": [0, 50], "color": "rgba(255,68,68,0.2)"},
                    {"range": [50, 70], "color": "rgba(255,165,0,0.2)"},
                    {"range": [70, 100], "color": "rgba(76,175,80,0.2)"},
                ],
            },
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=300)
        st.plotly_chart(fig, width='stretch')
        if readiness >= 70:
            st.success("🟢 You're ready! Go ace that interview!")
        elif readiness >= 50:
            st.warning("🟡 Getting there! A bit more practice will help.")
        else:
            st.error("🔴 More preparation needed. Focus on mock interviews and skill gaps.")


# ── TAB 4: Resume Section Analyzer ────────────────────────────────────────────

def _render_section_analyzer():
    st.subheader("Resume Section Completeness Analyzer")
    st.write("Paste your resume text to detect missing or weak sections.")

    resume_text = st.text_area(
        "Paste Resume Text",
        height=300,
        placeholder="Paste the full text of your resume here...",
        key="section_resume_text",
    )

    if st.button("Analyze Sections", type="primary", key="analyze_sections"):
        if not resume_text.strip():
            st.warning("Please paste your resume text.")
            return
        result = _analyze_resume_sections(resume_text)

        # Section completeness chart
        sections = list(result["scores"].keys())
        scores = list(result["scores"].values())
        colors = ["#4CAF50" if s >= 70 else "#FFA500" if s >= 40 else "#FF4444" for s in scores]
        fig = go.Figure(go.Bar(x=sections, y=scores, marker_color=colors))
        fig.update_layout(
            title="Section Completeness Scores",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font_color="white", yaxis=dict(range=[0, 100]),
        )
        st.plotly_chart(fig, width='stretch')

        # Missing sections
        if result["missing"]:
            st.error(f"🚨 **Missing Sections:** {', '.join(result['missing'])}")
        if result["weak"]:
            st.warning(f"⚠️ **Weak Sections:** {', '.join(result['weak'])}")
        if result["good"]:
            st.success(f"✅ **Strong Sections:** {', '.join(result['good'])}")

        # Suggestions
        st.markdown("### 💡 Improvement Suggestions")
        for suggestion in result["suggestions"]:
            _card(f"<p style='color:#e0e0e0;margin:0;'>💡 {suggestion}</p>")


def _analyze_resume_sections(text):
    text_lower = text.lower()
    
    section_keywords = {
        "Contact Info": ["email", "phone", "linkedin", "github", "@"],
        "Professional Summary": ["summary", "objective", "profile", "about"],
        "Work Experience": ["experience", "employment", "work history", "position", "worked at", "company"],
        "Education": ["education", "university", "college", "degree", "bachelor", "master", "diploma"],
        "Skills": ["skills", "technologies", "tools", "proficient", "expertise"],
        "Projects": ["project", "built", "developed", "created", "implemented"],
        "Certifications": ["certification", "certified", "certificate", "credential"],
        "Achievements": ["achievement", "award", "honor", "recognition", "published", "won"],
    }

    scores = {}
    missing, weak, good = [], [], []

    for section, keywords in section_keywords.items():
        found = sum(1 for kw in keywords if kw in text_lower)
        score = min(100, found * 25)
        scores[section] = score
        if score == 0:
            missing.append(section)
        elif score < 50:
            weak.append(section)
        else:
            good.append(section)

    suggestions = []
    if "Contact Info" in missing:
        suggestions.append("Add your email, phone, and LinkedIn URL in a dedicated contact section.")
    if "Professional Summary" in missing or "Professional Summary" in weak:
        suggestions.append("Add a 3–4 sentence professional summary at the top highlighting your expertise.")
    if "Projects" in missing:
        suggestions.append("Add a Projects section showcasing 2–4 relevant projects with tech stack and impact.")
    if "Certifications" in missing:
        suggestions.append("Add any certifications (AWS, Google, Microsoft) to boost ATS scoring.")
    if "Achievements" in missing:
        suggestions.append("Include measurable achievements (e.g., 'Increased performance by 40%').")
    if "Skills" in missing or "Skills" in weak:
        suggestions.append("Add a comprehensive Skills section with technical and soft skills.")

    return {"scores": scores, "missing": missing, "weak": weak, "good": good, "suggestions": suggestions}


# ── TAB 5: AI Summary Generator ────────────────────────────────────────────────

def _render_summary_generator():
    st.subheader("AI Professional Summary Generator")
    st.write("Fill in your details to generate a compelling professional summary.")

    col1, col2 = st.columns(2)
    with col1:
        years_exp = st.number_input("Years of Experience", 0, 40, 3, key="sum_yrs")
        role = st.text_input("Target Role", placeholder="Senior Software Engineer", key="sum_role")
        top_skills = st.text_input("Top 3-5 Skills", placeholder="Python, AWS, React", key="sum_skills")
    with col2:
        industry = st.text_input("Industry", placeholder="FinTech, Healthcare, E-commerce", key="sum_industry")
        achievement = st.text_input("Key Achievement", placeholder="Led team of 5, Reduced latency 30%", key="sum_achieve")
        tone = st.selectbox("Tone", ["Professional", "Dynamic", "Technical", "Leadership"], key="sum_tone")

    if st.button("Generate Professional Summary ✨", type="primary", key="gen_summary"):
        if not role or not top_skills:
            st.warning("Please fill in the target role and skills.")
            return

        summaries = _generate_summaries(years_exp, role, top_skills, industry, achievement, tone)

        st.markdown("### 📋 Generated Summaries")
        for i, s in enumerate(summaries, 1):
            st.markdown(f"**Version {i}:**")
            _card(f"<p style='color:#e0e0e0;line-height:1.7;margin:0;'>{s}</p>")
            st.button(f"📋 Copy Version {i}", key=f"copy_sum_{i}", help="Select this summary")


def _generate_summaries(years, role, skills, industry, achievement, tone):
    exp_str = f"{years}+ years of" if years > 0 else "Aspiring"
    skill_list = [s.strip() for s in skills.split(",")]
    skill_str = ", ".join(skill_list[:-1]) + f" and {skill_list[-1]}" if len(skill_list) > 1 else skills
    ind_str = f" in {industry}" if industry else ""
    ach_str = f" {achievement}." if achievement else "."
    
    templates = {
        "Professional": [
            f"Results-driven {role} with {exp_str} experience{ind_str}. "
            f"Proficient in {skill_str}, with a proven track record of delivering high-quality solutions. "
            f"Adept at collaborating with cross-functional teams to drive business objectives.{ach_str}",
            
            f"Experienced {role} combining deep expertise in {skill_str} with strong problem-solving skills{ind_str}. "
            f"Dedicated to writing clean, maintainable code and delivering measurable impact.{ach_str}",
        ],
        "Dynamic": [
            f"Passionate {role} with {exp_str} hands-on experience{ind_str} transforming complex challenges into elegant solutions. "
            f"Skilled in {skill_str} and driven by continuous learning and innovation.{ach_str}",
            
            f"Energetic and adaptable {role} who thrives in fast-paced environments. "
            f"Brings strong expertise in {skill_str}{ind_str}, always pushing for better performance and user experience.{ach_str}",
        ],
        "Technical": [
            f"Software professional specializing in {skill_str} with {exp_str} experience building scalable systems{ind_str}. "
            f"Strong foundation in software architecture, design patterns, and best practices.{ach_str}",
            
            f"Technical {role} with deep knowledge of {skill_str}. "
            f"{exp_str.capitalize()} experience designing, building, and optimizing production-grade applications{ind_str}.{ach_str}",
        ],
        "Leadership": [
            f"Strategic {role} with {exp_str} experience leading engineering teams{ind_str}. "
            f"Expertise in {skill_str}, with a track record of mentoring talent and delivering complex projects on time.{ach_str}",
            
            f"Proven technical leader and {role} with {exp_str} experience{ind_str}. "
            f"Combines strong expertise in {skill_str} with excellent stakeholder communication and team development skills.{ach_str}",
        ],
    }
    return templates.get(tone, templates["Professional"])


# ── TAB 6: Performance Analytics ──────────────────────────────────────────────

def _render_performance_analytics():
    st.subheader("Interview Performance Analytics")

    user_id = st.session_state.get("user_id", 0)
    stats = get_user_interview_stats(user_id)

    if stats:
        scores = [row[0] for row in stats]
        dates = [row[1][:10] for row in stats]

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Answers", len(scores))
        col2.metric("Average Score", f"{sum(scores)/len(scores):.1f}/100")
        col3.metric("Best Score", f"{max(scores)}/100")
        col4.metric("Latest Score", f"{scores[0]}/100")

        # Score trend
        df = pd.DataFrame({"Date": dates, "Score": scores})
        fig = px.line(df, x="Date", y="Score", markers=True, title="Score Trend Over Time",
                      color_discrete_sequence=["#4CAF50"])
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                          font_color="white", yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig, width='stretch')

        # Performance breakdown
        buckets = {"0-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
        for s in scores:
            if s <= 40: buckets["0-40"] += 1
            elif s <= 60: buckets["41-60"] += 1
            elif s <= 80: buckets["61-80"] += 1
            else: buckets["81-100"] += 1

        fig2 = go.Figure(go.Bar(
            x=list(buckets.keys()), y=list(buckets.values()),
            marker_color=["#FF4444", "#FFA500", "#FFD700", "#4CAF50"]
        ))
        fig2.update_layout(title="Score Distribution", paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)", font_color="white")
        st.plotly_chart(fig2, width='stretch')

        # Radar chart of competencies
        avg = sum(scores) / len(scores)
        cats = ["Technical Knowledge", "Communication", "Confidence", "Structure", "Depth"]
        vals = [min(100, avg + i * 3 - 6) for i in range(5)]
        fig3 = go.Figure()
        fig3.add_trace(go.Scatterpolar(r=vals + [vals[0]], theta=cats + [cats[0]], fill="toself",
                                       line_color="#4CAF50", name="Competency"))
        fig3.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), showlegend=False,
                           paper_bgcolor="rgba(0,0,0,0)", font_color="white", height=350,
                           title="Competency Radar")
        st.plotly_chart(fig3, width='stretch')

    else:
        _card("""
        <div style='text-align:center;padding:2rem;'>
        <p style='font-size:3rem;'>🎯</p>
        <p style='color:#aaa;font-size:1.1rem;'>No performance data yet.</p>
        <p style='color:#888;'>Complete a Mock Interview to see your analytics here.</p>
        </div>
        """)

    # Use session mock scores if available
    if st.session_state.get("mock_scores"):
        mock_scores = st.session_state.mock_scores
        st.markdown("### 📊 Current Session Performance")
        avg = sum(mock_scores) / len(mock_scores)
        cols = st.columns(4)
        cols[0].metric("Questions", len(mock_scores))
        cols[1].metric("Average", f"{avg:.1f}")
        cols[2].metric("Best", max(mock_scores))
        cols[3].metric("Lowest", min(mock_scores))