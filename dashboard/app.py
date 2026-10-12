"""
Job Market Skill Demand Intelligence & Crawler Analytics Dashboard
Interactive, high-fidelity Streamlit platform for labor market analytics, skill demand ranking,
role-skill matrices, compensation telemetry, and crawler operations.
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from database.connection import get_session, get_active_db_type, init_db
from database.repository import (
    get_market_overview_stats,
    get_top_in_demand_skills,
    get_role_wise_skill_matrix,
    get_emerging_technologies,
    get_city_wise_opportunities,
    get_salary_trends_by_role,
    get_skill_cooccurrence_matrix,
    get_crawler_runs_summary,
    get_recent_crawl_logs,
)
from database.models import Job, Skill, JobSkill
from crawler.engine import crawl_engine, ADAPTER_REGISTRY
from nlp.analytics import calculate_skill_associations

# Ensure database tables exist
init_db()

# -----------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Job Market Skill Demand Intelligence Platform",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-Aesthetic Theme Injection
st.markdown("""
<style>
    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(10px);
        margin-bottom: 12px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.2);
        border-color: rgba(59, 130, 246, 0.3);
    }
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #f8fafc;
        margin: 0;
    }
    .metric-badge {
        font-size: 0.75rem;
        padding: 3px 8px;
        border-radius: 9999px;
        font-weight: 600;
        display: inline-block;
        margin-top: 6px;
    }
    .badge-blue { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
    .badge-green { background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
    .badge-purple { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.3); }
    .badge-orange { background: rgba(249, 115, 22, 0.2); color: #fb923c; border: 1px solid rgba(249, 115, 22, 0.3); }
    
    /* Job Card */
    .job-card {
        background: rgba(30, 41, 59, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 10px;
        padding: 16px 20px;
        margin-bottom: 14px;
        transition: border-color 0.2s ease;
    }
    .job-card:hover {
        border-color: rgba(59, 130, 246, 0.4);
    }
    .job-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #38bdf8;
        margin-bottom: 4px;
    }
    .job-meta {
        font-size: 0.85rem;
        color: #94a3b8;
        margin-bottom: 10px;
    }
    .skill-tag {
        display: inline-block;
        font-size: 0.72rem;
        padding: 3px 7px;
        border-radius: 6px;
        margin: 2px 4px 2px 0;
        font-weight: 500;
    }
    .skill-req {
        background: rgba(59, 130, 246, 0.25);
        color: #93c5fd;
        border: 1px solid rgba(59, 130, 246, 0.4);
    }
    .skill-pref {
        background: rgba(100, 116, 139, 0.25);
        color: #cbd5e1;
        border: 1px solid rgba(148, 163, 184, 0.3);
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------------------------------------------
st.sidebar.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&auto=format&fit=crop&q=80", use_container_width=True)
st.sidebar.title("Job Intelligence")
st.sidebar.markdown(f"**Database:** `{get_active_db_type().upper()}`")

navigation_option = st.sidebar.radio(
    "Navigation Menu",
    [
        "📊 Market Overview",
        "🎯 Skill Demand Rankings",
        "🧬 Role-Skill Matrix & Co-occurrence",
        "🚀 Emerging Tech & Momentum",
        "💰 Salaries & Global Hubs",
        "🕷️ Crawler Operations & Telemetry",
        "🔍 Job Search & Intelligence Explorer"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Quick Crawl Launcher")
quick_source = st.sidebar.selectbox("Source", list(ADAPTER_REGISTRY.keys()), index=0)
quick_pages = st.sidebar.slider("Max Pages", 1, 5, 2)
if st.sidebar.button("🚀 Run Live Crawl", use_container_width=True):
    with st.spinner(f"Crawling {quick_source} ({quick_pages} pages)..."):
        res = crawl_engine.execute_crawl(source_name=quick_source, max_pages=quick_pages)
        if res.get("status") == "completed":
            st.sidebar.success(f"Extracted {res.get('jobs_extracted', 0)} jobs! ({res.get('duplicates_skipped', 0)} skipped)")
        else:
            st.sidebar.error(f"Crawl finished with issue: {res.get('error')}")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Job Demand Intelligence Platform v1.0.0\nFully Ethical & Polite Crawling")


# -----------------------------------------------------------------------------
# VIEW 1: MARKET OVERVIEW
# -----------------------------------------------------------------------------
if navigation_option == "📊 Market Overview":
    st.title("📊 Labor Market Intelligence Overview")
    st.markdown("Real-time aggregated telemetry across tech job postings, engineering roles, and skills demand.")

    with get_session() as sess:
        overview = get_market_overview_stats(sess)
        top_skills = get_top_in_demand_skills(sess, limit=10)
        locations = get_city_wise_opportunities(sess, limit=10)
        jobs = sess.query(Job.role_category, Job.is_remote, Job.experience_level).all()

    # Metric Row
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Jobs Analyzed</div>
            <div class="metric-value">{overview['total_jobs']:,}</div>
            <span class="metric-badge badge-blue">Active Index</span>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Unique Skills Tracked</div>
            <div class="metric-value">{overview['total_unique_skills']:,}</div>
            <span class="metric-badge badge-purple">7 Categories</span>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Companies Monitored</div>
            <div class="metric-value">{overview['total_companies']:,}</div>
            <span class="metric-badge badge-green">Enterprise & Startups</span>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Remote Work Ratio</div>
            <div class="metric-value">{overview['remote_percentage']}%</div>
            <span class="metric-badge badge-orange">Global Workforce</span>
        </div>
        """, unsafe_allow_html=True)
    with c5:
        avg_sal_str = f"${int(overview['average_salary_usd']):,}" if overview['average_salary_usd'] else "N/A"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Market Salary</div>
            <div class="metric-value">{avg_sal_str}</div>
            <span class="metric-badge badge-blue">USD / Year</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("###")

    # Overview Visualizations
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Top Engineering Role Categories")
        if jobs:
            df_jobs = pd.DataFrame(jobs, columns=["role", "remote", "experience"])
            role_counts = df_jobs["role"].value_counts().reset_index()
            role_counts.columns = ["Role Category", "Count"]

            fig_roles = px.bar(
                role_counts,
                x="Count",
                y="Role Category",
                orientation="h",
                color="Count",
                color_continuous_scale="Viridis",
            )
            fig_roles.update_layout(
                yaxis=dict(autorange="reversed"),
                margin=dict(l=0, r=0, t=10, b=0),
                height=350,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_roles, use_container_width=True)
        else:
            st.info("No job postings available yet.")

    with col_right:
        st.subheader("Remote vs On-Site Distribution")
        if jobs:
            remote_counts = df_jobs["remote"].value_counts().reset_index()
            remote_counts["Type"] = remote_counts["remote"].map({True: "Remote / Work From Anywhere", False: "On-site / Hybrid Hub"})
            remote_counts.columns = ["remote", "Count", "Type"]

            fig_remote = px.pie(
                remote_counts,
                names="Type",
                values="Count",
                hole=0.45,
                color="Type",
                color_discrete_map={
                    "Remote / Work From Anywhere": "#38bdf8",
                    "On-site / Hybrid Hub": "#64748b"
                }
            )
            fig_remote.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=350)
            st.plotly_chart(fig_remote, use_container_width=True)
        else:
            st.info("No distribution data.")

    st.markdown("###")
    st.subheader("Leaderboard: Top 10 In-Demand Skills")
    if top_skills:
        df_top = pd.DataFrame(top_skills)
        fig_skills = px.bar(
            df_top,
            x="name",
            y="demand_count",
            color="category",
            text="demand_count",
            labels={"name": "Skill", "demand_count": "Job Postings Demand Count", "category": "Category"},
        )
        fig_skills.update_traces(textposition="outside")
        fig_skills.update_layout(height=380, margin=dict(l=0, r=0, t=20, b=20))
        st.plotly_chart(fig_skills, use_container_width=True)


# -----------------------------------------------------------------------------
# VIEW 2: SKILL DEMAND RANKINGS
# -----------------------------------------------------------------------------
elif navigation_option == "🎯 Skill Demand Rankings":
    st.title("🎯 Skill Demand & Category Rankings")
    st.markdown("Explore which technical languages, frameworks, cloud platforms, and tools dominate hiring requisitions.")

    with get_session() as sess:
        # Get unique roles & categories for filters
        distinct_roles = ["All"] + [r[0] for r in sess.query(Job.role_category).distinct().order_by(Job.role_category).all() if r[0]]
        distinct_cats = ["All"] + [c[0] for c in sess.query(Skill.category).distinct().order_by(Skill.category).all() if c[0]]

    # Filter Bar
    f1, f2, f3, f4 = st.columns([1.5, 1.5, 1, 1])
    with f1:
        sel_role = st.selectbox("Filter by Role Category", distinct_roles, index=0)
    with f2:
        sel_cat = st.selectbox("Filter by Skill Category", distinct_cats, index=0)
    with f3:
        tech_only = st.checkbox("Technical Skills Only", value=False)
    with f4:
        top_k = st.slider("Top N Skills", 10, 50, 20)

    with get_session() as sess:
        skills_data = get_top_in_demand_skills(
            session=sess,
            limit=top_k,
            role_category=sel_role,
            skill_category=sel_cat,
            is_tech_only=tech_only
        )

    if skills_data:
        df_s = pd.DataFrame(skills_data)

        tab_chart, tab_req, tab_table = st.tabs(["📊 Demand Volume & Market Share", "⚖️ Required vs Preferred Breakdown", "📋 Detailed Data Table"])

        with tab_chart:
            fig_bar = px.bar(
                df_s,
                x="demand_count",
                y="name",
                orientation="h",
                color="category",
                hover_data=["market_share_pct", "required_pct", "avg_salary"],
                labels={"demand_count": "Job Postings", "name": "Skill", "category": "Domain"},
                title=f"Top {len(df_s)} Skills for Role: {sel_role} | Domain: {sel_cat}"
            )
            fig_bar.update_layout(yaxis=dict(autorange="reversed"), height=550)
            st.plotly_chart(fig_bar, use_container_width=True)

        with tab_req:
            st.markdown("#### Must-Have Requirements vs Desired / Nice-to-Have Pluses")
            df_s["preferred_count"] = df_s["demand_count"] - df_s["required_count"]

            fig_stack = go.Figure()
            fig_stack.add_trace(go.Bar(
                name="Strictly Required",
                y=df_s["name"],
                x=df_s["required_count"],
                orientation="h",
                marker_color="#ef4444"
            ))
            fig_stack.add_trace(go.Bar(
                name="Preferred / Bonus",
                y=df_s["name"],
                x=df_s["preferred_count"],
                orientation="h",
                marker_color="#3b82f6"
            ))
            fig_stack.update_layout(
                barmode="stack",
                yaxis=dict(autorange="reversed"),
                height=550,
                xaxis_title="Number of Requisitions",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_stack, use_container_width=True)

        with tab_table:
            st.dataframe(
                df_s[[
                    "name", "category", "demand_count", "required_pct",
                    "market_share_pct", "avg_salary", "is_tech"
                ]].rename(columns={
                    "name": "Skill Name",
                    "category": "Category",
                    "demand_count": "Demand Count",
                    "required_pct": "Must-Have %",
                    "market_share_pct": "Market Share %",
                    "avg_salary": "Avg Salary (USD)",
                    "is_tech": "Tech Skill"
                }),
                use_container_width=True
            )
    else:
        st.warning("No skills matched the specified filter criteria.")


# -----------------------------------------------------------------------------
# VIEW 3: ROLE-SKILL MATRIX & CO-OCCURRENCE
# -----------------------------------------------------------------------------
elif navigation_option == "🧬 Role-Skill Matrix & Co-occurrence":
    st.title("🧬 Role-Skill Matrix & Co-occurrence Graph")
    st.markdown("Analyze how skills map across roles and which technologies appear together in the same job specifications.")

    tab_matrix, tab_cooccur = st.tabs(["🗺️ Role vs Skill Heatmap", "🕸️ Technology Co-occurrence & Pair Associations"])

    with tab_matrix:
        with get_session() as sess:
            matrix_records = get_role_wise_skill_matrix(sess, top_roles_count=8, top_skills_count=10)

        if matrix_records:
            df_mat = pd.DataFrame(matrix_records)
            pivot = df_mat.pivot_table(index="role", columns="skill", values="demand_count", fill_value=0)

            fig_heat = px.imshow(
                pivot,
                labels=dict(x="Skill", y="Role Category", color="Demand Count"),
                x=pivot.columns,
                y=pivot.index,
                color_continuous_scale="Blues",
                aspect="auto"
            )
            fig_heat.update_layout(height=520)
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Insufficient data to generate role-skill matrix.")

    with tab_cooccur:
        st.subheader("Skill Co-occurrence & Association Pairs")
        st.markdown("Shows how frequently technologies are required together (e.g. `Python` + `FastAPI` + `Docker` + `PostgreSQL`).")

        with get_session() as sess:
            cooccur_data = get_skill_cooccurrence_matrix(sess, top_n_skills=15)
            associations = calculate_skill_associations(cooccur_data)

        c_left, c_right = st.columns([1.5, 1])
        with c_left:
            st.markdown("#### Top Co-occurring Pairs (Jaccard Similarity)")
            if associations:
                df_assoc = pd.DataFrame(associations[:15])
                fig_assoc = px.bar(
                    df_assoc,
                    x="jaccard_similarity",
                    y=df_assoc.apply(lambda r: f"{r['skill_a']} + {r['skill_b']}", axis=1),
                    orientation="h",
                    color="co_occurrence",
                    color_continuous_scale="Tealgrn",
                    labels={"jaccard_similarity": "Jaccard Association Index", "y": "Skill Pair", "co_occurrence": "Joint Count"}
                )
                fig_assoc.update_layout(yaxis=dict(autorange="reversed"), height=500)
                st.plotly_chart(fig_assoc, use_container_width=True)
            else:
                st.info("No co-occurrence associations available.")

        with c_right:
            st.markdown("#### Co-occurrence Matrix")
            if cooccur_data.get("matrix"):
                df_matrix = pd.DataFrame(cooccur_data["matrix"])
                fig_m = px.imshow(
                    df_matrix,
                    color_continuous_scale="Purples",
                    aspect="auto"
                )
                fig_m.update_layout(height=500, margin=dict(l=0, r=0, t=10, b=10))
                st.plotly_chart(fig_m, use_container_width=True)


# -----------------------------------------------------------------------------
# VIEW 4: EMERGING TECH & MOMENTUM
# -----------------------------------------------------------------------------
elif navigation_option == "🚀 Emerging Tech & Momentum":
    st.title("🚀 Emerging Tech & Momentum Index")
    st.markdown("Spot emerging technology adoption across Generative AI, Cloud Native architectures, and modern engineering stacks.")

    with get_session() as sess:
        emerging = get_emerging_technologies(sess, limit=20)

    if emerging:
        df_em = pd.DataFrame(emerging)

        col_g1, col_g2 = st.columns([1.2, 1])

        with col_g1:
            st.subheader("Technology Momentum Ranking")
            fig_mom = px.scatter(
                df_em,
                x="demand_count",
                y="momentum_index",
                size="demand_count",
                color="category",
                hover_name="name",
                text="name",
                labels={
                    "demand_count": "Current Market Demand (Postings)",
                    "momentum_index": "Adoption Momentum Index",
                    "category": "Stack"
                }
            )
            fig_mom.update_traces(textposition="top center")
            fig_mom.update_layout(height=480)
            st.plotly_chart(fig_mom, use_container_width=True)

        with col_g2:
            st.subheader("Average Compensation for Emerging Stacks")
            df_em_sal = df_em.dropna(subset=["avg_salary"])
            if not df_em_sal.empty:
                fig_sal_em = px.bar(
                    df_em_sal.sort_values(by="avg_salary", ascending=True),
                    x="avg_salary",
                    y="name",
                    orientation="h",
                    color="avg_salary",
                    color_continuous_scale="Viridis",
                    labels={"avg_salary": "Avg Salary (USD)", "name": "Emerging Tech"}
                )
                fig_sal_em.update_layout(height=480, coloraxis_showscale=False)
                st.plotly_chart(fig_sal_em, use_container_width=True)
            else:
                st.info("Salary information will populate as more postings with compensation details are ingested.")
    else:
        st.info("No emerging technologies tracked yet.")


# -----------------------------------------------------------------------------
# VIEW 5: SALARIES & GLOBAL HUBS
# -----------------------------------------------------------------------------
elif navigation_option == "💰 Salaries & Global Hubs":
    st.title("💰 Compensation & Geographic Tech Hubs")
    st.markdown("Analyze salary benchmarks by role category and top hiring locations globally.")

    with get_session() as sess:
        salaries = get_salary_trends_by_role(sess)
        cities = get_city_wise_opportunities(sess, limit=15)

    c_city, c_sal = st.columns(2)

    with c_city:
        st.subheader("Top Global Hiring Hubs & Remote Volume")
        if cities:
            df_cities = pd.DataFrame(cities)
            fig_city = px.bar(
                df_cities,
                x="city",
                y=["job_count", "remote_count"],
                barmode="group",
                labels={"value": "Job Postings", "city": "City / Hub", "variable": "Category"},
                color_discrete_map={"job_count": "#3b82f6", "remote_count": "#10b981"}
            )
            fig_city.update_layout(height=420)
            st.plotly_chart(fig_city, use_container_width=True)
        else:
            st.info("No city data available.")

    with c_sal:
        st.subheader("Salary Ranges by Role (Min, Average, Max)")
        if salaries:
            df_sal = pd.DataFrame(salaries)
            fig_sal = go.Figure()
            for _, row in df_sal.iterrows():
                fig_sal.add_trace(go.Box(
                    name=row["role"],
                    q1=[row["min_salary"]],
                    median=[row["avg_salary"]],
                    q3=[row["max_salary"]],
                    lowerfence=[row["min_salary"]],
                    upperfence=[row["max_salary"]],
                    boxpoints=False
                ))
            fig_sal.update_layout(
                yaxis_title="Annual Compensation (USD)",
                height=420,
                showlegend=False
            )
            st.plotly_chart(fig_sal, use_container_width=True)
        else:
            st.info("Salary ranges require at least 2 listings per role with salary figures.")


# -----------------------------------------------------------------------------
# VIEW 6: CRAWLER OPERATIONS & TELEMETRY
# -----------------------------------------------------------------------------
elif navigation_option == "🕷️ Crawler Operations & Telemetry":
    st.title("🕷️ Live Crawler Operations & Telemetry Monitor")
    st.markdown("Trigger ethical crawler jobs, monitor live HTTP telemetry, and inspect audit logs.")

    # Trigger New Run Form
    with st.expander("🚀 Launch New Crawler Run", expanded=True):
        f_src, f_pages, f_q, f_btn = st.columns([1.5, 1, 2, 1])
        with f_src:
            sel_src = st.selectbox("Source Adapter", list(ADAPTER_REGISTRY.keys()), index=0)
        with f_pages:
            sel_p = st.number_input("Max Pages", min_value=1, max_value=20, value=2)
        with f_q:
            sel_query = st.text_input("Optional Query Filter", value="")
        with f_btn:
            st.write("###")
            trigger_crawl_btn = st.button("Start Crawl", use_container_width=True)

        if trigger_crawl_btn:
            with st.spinner(f"Crawling {sel_src}..."):
                crawl_res = crawl_engine.execute_crawl(
                    source_name=sel_src,
                    max_pages=sel_p,
                    query=sel_query
                )
                if crawl_res.get("status") == "completed":
                    st.success(f"Crawl Completed! Extracted: {crawl_res.get('jobs_extracted', 0)} jobs | Skipped duplicates: {crawl_res.get('duplicates_skipped', 0)}")
                else:
                    st.error(f"Crawl finished with status: {crawl_res.get('status')} | {crawl_res.get('error')}")
                st.rerun()

    st.markdown("###")
    st.subheader("Execution History & Telemetry")

    with get_session() as sess:
        runs = get_crawler_runs_summary(sess, limit=20)
        logs = get_recent_crawl_logs(sess, limit=50)

    if runs:
        df_runs = pd.DataFrame(runs)
        st.dataframe(
            df_runs[[
                "id", "source_name", "status", "started_at", "duration_seconds",
                "urls_discovered", "pages_crawled", "jobs_extracted",
                "duplicates_skipped", "errors_count", "http_200_count", "http_429_count"
            ]].rename(columns={
                "source_name": "Source",
                "status": "Status",
                "started_at": "Timestamp",
                "duration_seconds": "Duration (s)",
                "urls_discovered": "Discovered",
                "pages_crawled": "Pages",
                "jobs_extracted": "Jobs Saved",
                "duplicates_skipped": "Duplicates",
                "errors_count": "Errors",
                "http_200_count": "HTTP 200",
                "http_429_count": "HTTP 429",
            }),
            use_container_width=True
        )
    else:
        st.info("No crawl runs registered yet.")

    st.markdown("###")
    st.subheader("Granular Audit Logs")
    if logs:
        df_logs = pd.DataFrame(logs)
        st.dataframe(
            df_logs[["timestamp", "level", "status_code", "message", "url"]].rename(columns={
                "timestamp": "Time",
                "level": "Level",
                "status_code": "Status",
                "message": "Audit Log Message",
                "url": "Target URL"
            }),
            use_container_width=True
        )
    else:
        st.info("No audit logs available.")


# -----------------------------------------------------------------------------
# VIEW 7: JOB SEARCH & INTELLIGENCE EXPLORER
# -----------------------------------------------------------------------------
elif navigation_option == "🔍 Job Search & Intelligence Explorer":
    st.title("🔍 Job Search & Parsed Intelligence Explorer")
    st.markdown("Search across extracted job requisitions, view parsed skills, and export datasets.")

    with get_session() as sess:
        roles_list = ["All"] + [r[0] for r in sess.query(Job.role_category).distinct().order_by(Job.role_category).all() if r[0]]
        cities_list = ["All"] + [c[0] for c in sess.query(Job.city).distinct().order_by(Job.city).all() if c[0]]

    # Search Bar & Facets
    s_col1, s_col2, s_col3, s_col4 = st.columns([2, 1, 1, 1])
    with s_col1:
        keyword = st.text_input("Search Keyword (Title, Company, Skills)", "")
    with s_col2:
        filter_role = st.selectbox("Role", roles_list, index=0)
    with s_col3:
        filter_city = st.selectbox("City", cities_list, index=0)
    with s_col4:
        filter_remote = st.checkbox("Remote Only", value=False)

    with get_session() as sess:
        query = sess.query(Job)
        if keyword:
            pattern = f"%{keyword}%"
            query = query.filter(
                (Job.job_title.ilike(pattern)) |
                (Job.company.ilike(pattern)) |
                (Job.description_cleaned.ilike(pattern))
            )
        if filter_role != "All":
            query = query.filter(Job.role_category == filter_role)
        if filter_city != "All":
            query = query.filter(Job.city == filter_city)
        if filter_remote:
            query = query.filter(Job.is_remote == True)

        matched_jobs = query.order_by(Job.created_at.desc()).limit(50).all()

        st.caption(f"Showing **{len(matched_jobs)}** matching positions")

        # CSV Download Button
        if matched_jobs:
            csv_rows = []
            for j in matched_jobs:
                csv_rows.append({
                    "ID": j.id,
                    "Title": j.job_title,
                    "Company": j.company,
                    "Role Category": j.role_category,
                    "City": j.city or "",
                    "Country": j.country or "",
                    "Remote": j.is_remote,
                    "Salary Min": j.salary_min or "",
                    "Salary Max": j.salary_max or "",
                    "Experience": j.experience_level or "",
                    "Source": j.source_portal,
                    "URL": j.job_url,
                })
            df_export = pd.DataFrame(csv_rows)
            st.download_button(
                "📥 Export Filtered Jobs (CSV)",
                df_export.to_csv(index=False),
                file_name="job_market_demand.csv",
                mime="text/csv"
            )

        st.markdown("---")

        for job in matched_jobs:
            skills = (
                sess.query(Skill.name, JobSkill.is_required, Skill.category)
                .join(JobSkill, Skill.id == JobSkill.skill_id)
                .filter(JobSkill.job_id == job.id)
                .all()
            )

            remote_str = "🌐 Remote" if job.is_remote else "🏢 On-site / Hybrid"
            sal_str = f"${int(job.salary_min):,} - ${int(job.salary_max):,}" if job.salary_min and job.salary_max else "Compensation Not Disclosed"
            loc_str = f"{job.city}, {job.country}" if job.city and job.country else (job.city or job.country or "Worldwide")

            with st.container():
                st.markdown(f"""
                <div class="job-card">
                    <div class="job-title">{job.job_title}</div>
                    <div class="job-meta">
                        <strong>{job.company}</strong> &nbsp;|&nbsp; 
                        📍 {loc_str} &nbsp;|&nbsp; 
                        {remote_str} &nbsp;|&nbsp; 
                        💰 {sal_str} &nbsp;|&nbsp; 
                        🏷️ {job.role_category} &nbsp;|&nbsp; 
                        📌 Source: <em>{job.source_portal}</em>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Skill Badges
                if skills:
                    badges_html = "<div>"
                    for s_name, s_req, s_cat in skills:
                        cls = "skill-req" if s_req else "skill-pref"
                        tag_type = "★ Req" if s_req else "Pref"
                        badges_html += f'<span class="skill-tag {cls}">{s_name} ({tag_type})</span>'
                    badges_html += "</div>"
                    st.markdown(badges_html, unsafe_allow_html=True)

                with st.expander(f"View Full Description & Requisition Details"):
                    st.markdown(f"**Requisition URL:** [{job.job_url}]({job.job_url})")
                    st.text_area("Job Description", job.description_cleaned, height=160, key=f"desc_{job.id}")
                st.markdown("###")
