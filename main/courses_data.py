"""Course and mentorship program catalog modeled on WsCube Tech's career tracks."""

COURSE_CATEGORIES = [
    {
        'slug': 'digital-marketing',
        'name': 'Digital Marketing',
        'icon': 'fas fa-bullhorn',
        'nav_badge': '',
        'description': 'Master AI-powered SEO, Answer Engine Optimization, Performance Ads, and Marketing Automation.',
    },
    {
        'slug': 'data-science-analytics',
        'name': 'Data Science & Analytics',
        'icon': 'fas fa-chart-bar',
        'nav_badge': 'New',
        'description': 'Hands-on mastery in Excel, SQL, Power BI, Python, Machine Learning, and GenAI analytics.',
    },
    {
        'slug': 'ai-programs',
        'name': 'AI Programs',
        'icon': 'fas fa-robot',
        'nav_badge': 'New',
        'description': 'Build production Generative AI apps, RAG pipelines, and autonomous agentic workflows.',
    },
    {
        'slug': 'full-stack-ai',
        'name': 'Full Stack with AI Engineering',
        'icon': 'fas fa-laptop-code',
        'nav_badge': '',
        'description': 'End-to-end web engineering with React, Node.js, databases, System Design, DSA, and AI integration.',
    },
    {
        'slug': 'cyber-security',
        'name': 'Cyber Security',
        'icon': 'fas fa-shield-alt',
        'nav_badge': 'New',
        'description': 'Practical Ethical Hacking, Penetration Testing, VAPT reporting, and SOC L1 threat defense.',
    },
    {
        'slug': 'cloud-computing',
        'name': 'Cloud Computing',
        'icon': 'fas fa-cloud',
        'nav_badge': 'New',
        'description': 'Master AWS, Microsoft Azure, Terraform, Docker, Kubernetes, CI/CD pipelines, and cloud security.',
    },
]

CATEGORIES_BY_SLUG = {c['slug']: c for c in COURSE_CATEGORIES}

COURSES = [
    # ---------------- 1. Digital Marketing ----------------
    {
        'slug': 'digital-marketing-mentorship',
        'title': 'Digital Marketing Mentorship Program with AI',
        'short_title': 'Digital Marketing with AI',
        'category': 'digital-marketing',
        'category_name': 'Digital Marketing',
        'badge': 'Bestseller',
        'duration': '24 Weeks (6 Months)',
        'hours': '160+ Hrs Live',
        'mode': 'Live Online Cohort',
        'projects': '24+ Projects',
        'level': 'Beginner to Pro',
        'icon': 'fas fa-bullhorn',
        'summary': 'A comprehensive 6-month mentorship cohort covering Digital Marketing foundations, high-converting WordPress websites, SEO & AEO, Social Media, Performance Ads, and AI Marketing Automation.',
        'capstone': 'Plan, launch, and optimize a live multi-channel acquisition funnel for a D2C/SaaS brand with Google Ads, Meta Ads, GA4 tracking, and n8n CRM lead-nurturing workflows.',
        'highlights': [
            '160+ hours of live mentor-led sessions with agency & growth leads',
            '24+ real brand campaigns, SEO audits, and live ad budget simulations',
            'Dedicated AI Mindset & n8n marketing automation workflows',
            'Portfolio showcase, agency freelancing playbook & placement support',
        ],
        'tools': ['WordPress', 'GA4', 'Google Tag Manager', 'Google Ads', 'Meta Ads', 'SEMrush', 'Ahrefs', 'n8n', 'HubSpot'],
        'roles': ['Digital Marketing Manager', 'Growth Marketer', 'Performance Marketer', 'SEO Strategist'],
        'curriculum': [
            {
                'milestone': 'Milestone 1: Digital Marketing Foundation & AI Mindset',
                'duration': 'Weeks 1–3',
                'topics': [
                    'Full-funnel marketing architecture, ICP mapping, and unit economics (CAC, LTV, ROAS)',
                    'Brand positioning, value proposition design, and competitor teardown frameworks',
                    'AI-assisted market research, customer persona synthesis, and prompt libraries',
                ],
            },
            {
                'milestone': 'Milestone 2: Website & High-Converting Landing Pages',
                'duration': 'Weeks 4–6',
                'topics': [
                    'WordPress architecture, theme customization, and landing page wireframing',
                    'Conversion Rate Optimization (CRO), persuasive copywriting, and lead-capture funnels',
                    'Core Web Vitals, mobile speed tuning, and AI-assisted design workflows',
                ],
            },
            {
                'milestone': 'Milestone 3: SEO & Answer Engine Optimization (AEO)',
                'duration': 'Weeks 7–11',
                'topics': [
                    'Search intent mapping, topical clusters, and semantic keyword research',
                    'Technical SEO: crawl budgets, XML sitemaps, canonicals, and JSON-LD Schema markup',
                    'Off-page link acquisition and Answer Engine Optimization for Google AI Overviews & LLMs',
                ],
            },
            {
                'milestone': 'Milestone 4: Social Media & Content Engine',
                'duration': 'Weeks 12–14',
                'topics': [
                    'Organic growth playbooks for Instagram, LinkedIn, and YouTube',
                    'Short-form video scripting, editorial calendars, and creator partnerships',
                    'Community management, social listening, and brand storytelling metrics',
                ],
            },
            {
                'milestone': 'Milestone 5: Performance Marketing & Paid Acquisition',
                'duration': 'Weeks 15–20',
                'topics': [
                    'Google Search, Display, YouTube, and Performance Max campaign engineering',
                    'Meta Ads Manager: Advantage+, custom/lookalike audiences, and creative testing sprints',
                    'GA4 event tracking, Google Tag Manager, Meta Pixel/CAPI, and Looker Studio reporting',
                ],
            },
            {
                'milestone': 'Milestone 6: Marketing Automation, AI Agents & Capstone',
                'duration': 'Weeks 21–24',
                'topics': [
                    'Email lifecycle flows, WhatsApp/CRM automation in HubSpot, and n8n AI agents',
                    'Multi-channel capstone brand audit and budget defense before industry mentors',
                    'Resume crafting, mock growth-marketing interviews, and placement referrals',
                ],
            },
        ],
    },
    {
        'slug': 'performance-marketing-bootcamp',
        'title': 'AI-Driven Performance Marketing Bootcamp',
        'short_title': 'Performance Marketing Bootcamp',
        'category': 'digital-marketing',
        'category_name': 'Digital Marketing',
        'badge': 'Bootcamp',
        'duration': '16 Weeks (4 Months)',
        'hours': '96+ Hrs Live',
        'mode': 'Live Bootcamp',
        'projects': '12+ Live Campaigns',
        'level': 'Beginner to Intermediate',
        'icon': 'fas fa-bullseye',
        'summary': 'Deep-dive 4-month paid acquisition bootcamp focused on profitable media buying across Meta Ads, Google Ads, server-side conversion tracking, and AI creative testing.',
        'capstone': 'Build a complete multi-platform paid growth engine with GTM server-side events, 10+ ad creative variations, and an automated Looker Studio ROAS scorecard.',
        'highlights': [
            'Hands-on campaign structuring, bid strategy selection & scaling rules',
            'End-to-end GA4, Google Tag Manager & Meta Conversion API tracking',
            'AI-powered ad copy, hook testing & landing-page CRO sprints',
            'Live media-buying audits & performance-marketer interview prep',
        ],
        'tools': ['Meta Ads Manager', 'Google Ads', 'Google Tag Manager', 'GA4', 'Looker Studio', 'Meta CAPI', 'Canva AI'],
        'roles': ['Performance Marketer', 'Paid Media Specialist', 'Media Buyer', 'PPC Analyst'],
        'curriculum': [
            {
                'milestone': 'Milestone 1: Funnel Economics & Attribution Setup',
                'duration': 'Weeks 1–4',
                'topics': [
                    'MER, ROAS, CPA, AOV, and break-even cohort modeling in spreadsheets',
                    'Google Tag Manager containers, GA4 custom events, and enhanced conversions',
                    'Meta Pixel & server-side Conversion API deduplication',
                ],
            },
            {
                'milestone': 'Milestone 2: Meta Ads Architecture & Creative Sprints',
                'duration': 'Weeks 5–8',
                'topics': [
                    'CBO vs ABO testing frameworks, broad vs lookalike scaling',
                    'High-converting UGC video hooks, static carousels, and AI ad iteration',
                    'Retargeting sequences and creative fatigue diagnostics',
                ],
            },
            {
                'milestone': 'Milestone 3: Google Ads & Programmatic Demand Capture',
                'duration': 'Weeks 9–12',
                'topics': [
                    'High-intent Search keyword sculpting, negative lists, and Quality Score tuning',
                    'Shopping feeds, Performance Max asset groups, and YouTube action campaigns',
                    'Competitor auction insights and landing page A/B testing',
                ],
            },
            {
                'milestone': 'Milestone 4: Automated Reporting & Media Buying Capstone',
                'duration': 'Weeks 13–16',
                'topics': [
                    'Blended executive dashboards in Looker Studio',
                    'Budget pacing, seasonal scaling playbooks, and live account audit defense',
                ],
            },
        ],
    },
    {
        'slug': 'seo-aeo-bootcamp',
        'title': 'SEO & AI Search Optimization (AEO) Bootcamp',
        'short_title': 'SEO & AEO Bootcamp',
        'category': 'digital-marketing',
        'category_name': 'Digital Marketing',
        'badge': 'Bootcamp',
        'duration': '16 Weeks (4 Months)',
        'hours': '96+ Hrs Live',
        'mode': 'Live Bootcamp',
        'projects': '12+ Audits',
        'level': 'Beginner to Pro',
        'icon': 'fas fa-search',
        'summary': 'Master organic search growth for Google and AI Answer Engines (ChatGPT, Perplexity, AI Overviews) with technical site audits, programmatic SEO, and authority building.',
        'capstone': 'Deliver a full 50-point technical + content SEO and AEO growth roadmap for a live SaaS or e-commerce domain.',
        'highlights': [
            'Real crawl diagnostics with Screaming Frog & Google Search Console',
            'Dedicated Answer Engine Optimization (AEO) & LLM citation strategies',
            'Local SEO, International hreflang & E-commerce faceted navigation',
            'Client-ready audit templates & technical SEO interview prep',
        ],
        'tools': ['Google Search Console', 'Screaming Frog', 'Ahrefs', 'SEMrush', 'Schema.org', 'GA4', 'ChatGPT / Perplexity'],
        'roles': ['SEO Specialist', 'Technical SEO Analyst', 'Organic Growth Lead', 'Content Strategist'],
        'curriculum': [
            {
                'milestone': 'Milestone 1: Search Intent & Topical Authority Architecture',
                'duration': 'Weeks 1–4',
                'topics': [
                    'How search engines crawl, render, index, and rank pages',
                    'Keyword clustering, SERP intent dissection, and hub-and-spoke site maps',
                    'Programmatic SEO templates and E-E-A-T editorial briefs',
                ],
            },
            {
                'milestone': 'Milestone 2: Technical SEO, Speed & Structured Data',
                'duration': 'Weeks 5–8',
                'topics': [
                    'Log-file analysis, robots.txt, canonical chains, and orphan-page fixes',
                    'Core Web Vitals (LCP, INP, CLS) optimization and JS rendering audits',
                    'JSON-LD Schema markup for products, FAQs, articles, and organizations',
                ],
            },
            {
                'milestone': 'Milestone 3: Answer Engine Optimization (AEO) & Off-Page PR',
                'duration': 'Weeks 9–12',
                'topics': [
                    'Optimizing entity authority and structured answers for AI Overviews & LLMs',
                    'Digital PR, broken-link outreach, and toxic-backlink disavow workflows',
                    'Local SEO, Google Business Profile optimization, and citation consistency',
                ],
            },
            {
                'milestone': 'Milestone 4: Organic Revenue Attribution & Capstone',
                'duration': 'Weeks 13–16',
                'topics': [
                    'Mapping organic traffic to pipeline revenue in GA4 and Looker Studio',
                    'Full live-domain SEO + AEO audit presentation and mock interviews',
                ],
            },
        ],
    },

    # ---------------- 2. Data Science & Analytics ----------------
    {
        'slug': 'data-analytics-mentorship',
        'title': 'Data Analytics Mentorship Program with GenAI',
        'short_title': 'Data Analytics with GenAI',
        'category': 'data-science-analytics',
        'category_name': 'Data Science & Analytics',
        'badge': 'Bestseller',
        'duration': '24 Weeks (6 Months)',
        'hours': '150+ Hrs Live',
        'mode': 'Live Online Cohort',
        'projects': '14+ Projects',
        'level': 'Beginner to Job-Ready',
        'icon': 'fas fa-chart-line',
        'summary': 'A 6-month structured mentorship program taking you from zero to job-ready Data Analyst using Advanced Excel, MySQL, Power BI, Tableau, Python, Statistics, and GenAI.',
        'capstone': 'Build an end-to-end enterprise retail & supply-chain analytics suite combining MySQL ETL, Python EDA, and a multi-page Power BI executive dashboard.',
        'highlights': [
            '150+ hours of live coding & dashboard workshops with practicing analysts',
            '14+ real-world datasets across fintech, e-commerce, healthcare & SaaS',
            'GenAI Copilot workflows for SQL tuning, DAX debugging & insight summaries',
            'Internship readiness, GitHub portfolio & mock analyst interviews',
        ],
        'tools': ['Microsoft Excel', 'MySQL', 'Power BI', 'Tableau', 'Python', 'Pandas', 'Seaborn', 'ChatGPT / GenAI'],
        'roles': ['Data Analyst', 'BI Developer', 'Product Analyst', 'MIS & Reporting Specialist'],
        'curriculum': [
            {
                'milestone': 'Milestone 1: Excel Mastery & Financial/KPI Modeling',
                'duration': 'Weeks 1–4',
                'topics': [
                    'Data cleaning, XLOOKUP, INDEX-MATCH, and dynamic array formulas',
                    'Power Query transformations, Pivot tables, and automated KPI trackers',
                    'Retail profitability & inventory variance dashboard project',
                ],
            },
            {
                'milestone': 'Milestone 2: Relational Databases & Advanced SQL',
                'duration': 'Weeks 5–9',
                'topics': [
                    'ER modeling, normalization, multi-table JOINs, and subqueries in MySQL',
                    'CTEs, window functions (RANK, DENSE_RANK, LAG/LEAD), and query indexing',
                    'E-commerce customer retention, RFM segmentation & cohort SQL project',
                ],
            },
            {
                'milestone': 'Milestone 3: Power BI & Enterprise Visual Storytelling',
                'duration': 'Weeks 10–14',
                'topics': [
                    'Star-schema data modeling, relationships, and Power Query M scripts',
                    'DAX time-intelligence, CALCULATE context, and row-level security (RLS)',
                    'Publishing interactive executive dashboards to Power BI Service',
                ],
            },
            {
                'milestone': 'Milestone 4: Tableau & Executive Dashboards',
                'duration': 'Weeks 15–17',
                'topics': [
                    'Calculated fields, LOD expressions, parameters, and dual-axis storytelling',
                    'Supply-chain & logistics SLA bottleneck explorer in Tableau',
                ],
            },
            {
                'milestone': 'Milestone 5: Python, Pandas & Applied Statistics',
                'duration': 'Weeks 18–21',
                'topics': [
                    'NumPy, Pandas DataFrames, regex cleaning & automated CSV/API ingestion',
                    'Hypothesis testing, A/B test significance, and EDA with Matplotlib/Seaborn',
                ],
            },
            {
                'milestone': 'Milestone 6: GenAI Analytics Workflows & Capstone',
                'duration': 'Weeks 22–24',
                'topics': [
                    'AI-assisted SQL generation, Python notebook automation, and executive briefs',
                    'End-to-end capstone defense, resume polish & mock SQL/BI interviews',
                ],
            },
        ],
    },
    {
        'slug': 'data-science-ml',
        'title': 'Data Science & Machine Learning Mentorship Program',
        'short_title': 'Data Science & ML',
        'category': 'data-science-analytics',
        'category_name': 'Data Science & Analytics',
        'badge': 'Trending',
        'duration': '32 Weeks (8 Months)',
        'hours': '200+ Hrs Live',
        'mode': 'Live Cohort + Internship Prep',
        'projects': '16+ Projects',
        'level': 'Beginner to Advanced',
        'icon': 'fas fa-brain',
        'summary': 'An intensive 8-month Data Science & ML career track covering Python, SQL, Statistical Modeling, Supervised & Unsupervised ML, Deep Learning, NLP, and MLOps deployment.',
        'capstone': 'Train, evaluate, and deploy a production churn-prediction and recommendation API with FastAPI, Docker, and drift-monitoring dashboards.',
        'highlights': [
            '200+ hours of live mentorship with senior Data Scientists',
            '16+ end-to-end projects spanning churn, fraud detection, NLP & vision',
            'Production model deployment with FastAPI, Streamlit & cloud containers',
            'Dedicated DSA/SQL coding rounds & placement support',
        ],
        'tools': ['Python', 'SQL', 'NumPy', 'Pandas', 'Scikit-learn', 'XGBoost', 'TensorFlow', 'FastAPI', 'Docker'],
        'roles': ['Data Scientist', 'Machine Learning Engineer', 'Applied AI Scientist', 'Quantitative Analyst'],
        'curriculum': [
            {
                'milestone': 'Milestone 1: Python Engineering & SQL for Data Science',
                'duration': 'Weeks 1–6',
                'topics': [
                    'Clean Python, OOP, vectorized NumPy operations & functional pipelines',
                    'Window-function SQL aggregations for feature table extraction',
                    'Healthcare patient-flow & clinic bottleneck analysis lab',
                ],
            },
            {
                'milestone': 'Milestone 2: Probability, Statistics & EDA',
                'duration': 'Weeks 7–11',
                'topics': [
                    'Distributions, Central Limit Theorem, Bayes theorem & confidence intervals',
                    'Parametric/non-parametric hypothesis testing and A/B experiment design',
                    'Feature scaling, encoding, imputation & imbalance handling (SMOTE)',
                ],
            },
            {
                'milestone': 'Milestone 3: Classical & Ensemble Machine Learning',
                'duration': 'Weeks 12–18',
                'topics': [
                    'Linear/Logistic Regression, Regularization, SVM & Decision Trees',
                    'Bagging & Boosting: Random Forest, XGBoost, LightGBM & SHAP explainability',
                    'K-Means, DBSCAN, PCA, and collaborative-filtering recommenders',
                ],
            },
            {
                'milestone': 'Milestone 4: Deep Learning & Computer Vision',
                'duration': 'Weeks 19–23',
                'topics': [
                    'Backpropagation, optimizers, dropout & batch normalization in TensorFlow',
                    'CNNs, transfer learning (ResNet/EfficientNet), and image classification',
                ],
            },
            {
                'milestone': 'Milestone 5: Natural Language Processing & Transformers',
                'duration': 'Weeks 24–27',
                'topics': [
                    'Tokenization, TF-IDF, word embeddings & sequence models',
                    'Fine-tuning HuggingFace transformers for text classification & NER',
                ],
            },
            {
                'milestone': 'Milestone 6: MLOps Deployment & Capstone Defense',
                'duration': 'Weeks 28–32',
                'topics': [
                    'Experiment tracking, FastAPI model serving & Docker containerization',
                    'End-to-end ML capstone defense and mock data-science interviews',
                ],
            },
        ],
    },
    {
        'slug': 'business-analytics',
        'title': 'Business Analytics Mentorship Program with GenAI',
        'short_title': 'Business Analytics with GenAI',
        'category': 'data-science-analytics',
        'category_name': 'Data Science & Analytics',
        'badge': 'Job-Ready',
        'duration': '20 Weeks (5 Months)',
        'hours': '120+ Hrs Live',
        'mode': 'Live Online Cohort',
        'projects': '12+ Case Studies',
        'level': 'Beginner Friendly',
        'icon': 'fas fa-briefcase',
        'summary': 'Built for aspiring Business & Product Analysts: master KPI tree framing, Advanced Excel, SQL, Power BI, Looker Studio, and GenAI executive storytelling.',
        'capstone': 'Present a complete SaaS/marketplace growth & pricing optimization case study backed by SQL cohort analysis and live BI scorecards.',
        'highlights': [
            'Structured around real product, pricing & operations case interviews',
            'Hands-on SQL, Excel, Power BI & Looker Studio without heavy coding',
            '12+ boardroom-ready case studies & stakeholder PRDs',
            'Mock guesstimates, root-cause analysis (RCA) & BA interviews',
        ],
        'tools': ['Advanced Excel', 'SQL', 'Power BI', 'Google Sheets', 'Looker Studio', 'Mixpanel', 'GenAI'],
        'roles': ['Business Analyst', 'Product Analyst', 'Operations Analyst', 'Strategy Associate'],
        'curriculum': [
            {
                'milestone': 'Milestone 1: Business Framing & KPI Architecture',
                'duration': 'Weeks 1–4',
                'topics': [
                    'North-star metrics, driver trees, and SaaS/marketplace unit economics',
                    'Root-Cause Analysis (RCA) and guesstimate problem solving',
                ],
            },
            {
                'milestone': 'Milestone 2: Financial & Scenario Modeling in Excel',
                'duration': 'Weeks 5–8',
                'topics': [
                    'Dynamic lookups, sensitivity tables, Solver optimization & forecasting',
                    'Automated weekly business review (WBR) workbooks',
                ],
            },
            {
                'milestone': 'Milestone 3: Product & Cohort SQL',
                'duration': 'Weeks 9–13',
                'topics': [
                    'Funnel drop-off, retention cohorts, LTV/CAC & churn segmentation queries',
                    'Joining CRM, payment, and clickstream tables cleanly',
                ],
            },
            {
                'milestone': 'Milestone 4: Power BI & Looker Studio Scorecards',
                'duration': 'Weeks 14–17',
                'topics': [
                    'Executive drill-through views, DAX KPI cards, and automated alerts',
                    'Connecting GA4, Google Sheets, and relational data sources',
                ],
            },
            {
                'milestone': 'Milestone 5: GenAI Insights & Case Interview Capstone',
                'duration': 'Weeks 18–20',
                'topics': [
                    'Automated executive memos and stakeholder presentation practice',
                    'Live BA/PA mock interviews and resume portfolio review',
                ],
            },
        ],
    },

    # ---------------- 3. AI Programs ----------------
    {
        'slug': 'ai-genai-certification',
        'title': 'Professional Certification in AI & GenAI',
        'short_title': 'Professional Cert. in AI & GenAI',
        'category': 'ai-programs',
        'category_name': 'AI Programs',
        'badge': 'New',
        'duration': '20 Weeks (5 Months)',
        'hours': '120+ Hrs Live',
        'mode': 'Live Mentorship',
        'projects': '12+ AI Workflows',
        'level': 'Beginner to Intermediate',
        'icon': 'fas fa-robot',
        'summary': 'Master applied Artificial Intelligence and Generative AI—from prompt engineering and multimodal LLM APIs to production RAG knowledge assistants, fine-tuning, and evaluation.',
        'capstone': 'Ship a multi-document Enterprise Knowledge Assistant with hybrid vector search, cited answers, streaming UI, and automated quality evals.',
        'highlights': [
            '120+ hours of live hands-on AI engineering & product labs',
            'Build 12+ real GenAI tools across text, voice, vision & documents',
            'Production RAG, vector databases, guardrails & hallucination evals',
            'Career mentoring for GenAI Engineer & AI Consultant roles',
        ],
        'tools': ['Python', 'OpenAI & Gemini APIs', 'LangChain', 'LlamaIndex', 'Chroma / Pinecone', 'FastAPI', 'Streamlit'],
        'roles': ['GenAI Developer', 'AI Solutions Engineer', 'Applied AI Specialist', 'AI Product Builder'],
        'curriculum': [
            {
                'milestone': 'Milestone 1: Foundations of Modern AI & LLMs',
                'duration': 'Weeks 1–4',
                'topics': [
                    'Neural foundations, transformer attention, tokenization & context limits',
                    'Structured prompting, JSON schema outputs & reasoning techniques',
                    'Evaluating open-weights vs frontier commercial models',
                ],
            },
            {
                'milestone': 'Milestone 2: Python for AI & Multimodal APIs',
                'duration': 'Weeks 5–8',
                'topics': [
                    'Async API clients, streaming responses, function/tool calling & retries',
                    'Multimodal pipelines: PDF parsing, vision extraction & audio transcription',
                ],
            },
            {
                'milestone': 'Milestone 3: Production Retrieval-Augmented Generation (RAG)',
                'duration': 'Weeks 9–13',
                'topics': [
                    'Document chunking strategies, embeddings & vector indexing (Pinecone/Chroma)',
                    'Hybrid BM25 + semantic search, reranking & inline source citations',
                ],
            },
            {
                'milestone': 'Milestone 4: Fine-Tuning, Guardrails & Evals',
                'duration': 'Weeks 14–17',
                'topics': [
                    'LoRA/PEFT fine-tuning concepts and synthetic dataset curation',
                    'Prompt-injection defense, PII redaction, cost routing & RAGAS evaluation',
                ],
            },
            {
                'milestone': 'Milestone 5: Live AI Product Launch & Capstone',
                'duration': 'Weeks 18–20',
                'topics': [
                    'Deploying your GenAI application with FastAPI + modern web UI',
                    'Demo day presentation & technical AI engineering mock interviews',
                ],
            },
        ],
    },
    {
        'slug': 'agentic-ai-automation',
        'title': 'Agentic AI & Workflow Automation Mentorship',
        'short_title': 'Agentic AI & Automation',
        'category': 'ai-programs',
        'category_name': 'AI Programs',
        'badge': 'Hot Track',
        'duration': '16 Weeks (4 Months)',
        'hours': '100+ Hrs Live',
        'mode': 'Live Hands-On Cohort',
        'projects': '10+ AI Agents',
        'level': 'All Levels',
        'icon': 'fas fa-network-wired',
        'summary': 'Design and deploy autonomous multi-step AI agents and enterprise workflow automations using n8n, Make, LangGraph, webhooks, and custom Python/API connectors.',
        'capstone': 'Architect an autonomous Sales & Support Operations Agent that qualifies leads, drafts personalized proposals, updates CRM/Sheets, and escalates edge cases.',
        'highlights': [
            'Combine no-code orchestration (n8n) with custom Python agent code',
            '10+ deployable business agents for ops, support, research & content',
            'Human-in-the-loop approvals, memory persistence & error recovery',
            'Freelance & AI automation agency blueprint included',
        ],
        'tools': ['n8n', 'LangGraph', 'MCP / Tool Calling', 'REST Webhooks', 'Google Workspace APIs', 'Python', 'Supabase'],
        'roles': ['AI Automation Engineer', 'Agentic Systems Builder', 'AI Ops Consultant', 'No-Code AI Architect'],
        'curriculum': [
            {
                'milestone': 'Milestone 1: APIs, Webhooks & Automation Architecture',
                'duration': 'Weeks 1–4',
                'topics': [
                    'REST APIs, JSON transformations, OAuth2 & webhook event triggers',
                    'Self-hosting and designing fault-tolerant n8n workflows',
                ],
            },
            {
                'milestone': 'Milestone 2: Single-Agent Tool Use & Memory',
                'duration': 'Weeks 5–8',
                'topics': [
                    'Function calling, structured output validation & database memory',
                    'Connecting agents to Google Sheets, Gmail, Slack, Notion & CRMs',
                ],
            },
            {
                'milestone': 'Milestone 3: Multi-Agent Orchestration with LangGraph',
                'duration': 'Weeks 9–12',
                'topics': [
                    'Supervisor, planner-executor & reflection agent patterns',
                    'Human-in-the-loop checkpoints, retry policies & observability',
                ],
            },
            {
                'milestone': 'Milestone 4: Enterprise Agent Capstone & Deployment',
                'duration': 'Weeks 13–16',
                'topics': [
                    'Security boundaries, rate-limit handling & cost monitoring',
                    'Shipping and presenting a production automation suite',
                ],
            },
        ],
    },

    # ---------------- 4. Full Stack with AI Engineering ----------------
    {
        'slug': 'full-stack-web-development',
        'title': 'Full Stack Web Development with AI Engineering',
        'short_title': 'Full Stack with AI Engg.',
        'category': 'full-stack-ai',
        'category_name': 'Full Stack with AI Engineering',
        'badge': 'Bestseller',
        'duration': '32 Weeks (8 Months)',
        'hours': '210+ Hrs Live',
        'mode': 'Live Cohort + Code Reviews',
        'projects': '14+ Production Apps',
        'level': 'Beginner to Advanced',
        'icon': 'fas fa-laptop-code',
        'summary': 'Our flagship 8-month Software Engineering cohort uniting Frontend, React/Next.js, Node.js, SQL/NoSQL, System Design, DSA, Cloud DevOps, and AI feature engineering.',
        'capstone': 'Architect and deploy a multi-tenant AI SaaS workspace with role-based auth, Stripe billing, real-time notifications, and streaming AI assistants.',
        'highlights': [
            '210+ hours of live coding, architecture reviews & debugging clinics',
            '14+ deployed apps including AI SaaS, e-commerce & real-time platforms',
            'Includes Data Structures & Algorithms (DSA) + System Design track',
            'CI/CD cloud deployment, Git workflows & placement support',
        ],
        'tools': ['HTML5 / CSS3', 'Tailwind CSS', 'TypeScript', 'React.js', 'Next.js', 'Node.js', 'PostgreSQL', 'MongoDB', 'Docker', 'OpenAI API'],
        'roles': ['Full Stack Engineer', 'Software Development Engineer (SDE)', 'Frontend / React Engineer', 'Backend Engineer'],
        'curriculum': [
            {
                'milestone': 'Milestone 1: Semantic Web, Responsive CSS & JavaScript ES6+',
                'duration': 'Weeks 1–5',
                'topics': [
                    'HTML5 accessibility, Flexbox, CSS Grid, Tailwind CSS & fluid design systems',
                    'JavaScript engine internals, closures, async/await, Fetch & DOM mastery',
                ],
            },
            {
                'milestone': 'Milestone 2: TypeScript, React.js & Modern Frontend',
                'duration': 'Weeks 6–11',
                'topics': [
                    'Component architecture, custom hooks, React Router & Redux Toolkit',
                    'TypeScript type safety, form validation, caching & performance profiling',
                ],
            },
            {
                'milestone': 'Milestone 3: Backend Engineering, REST/GraphQL & Databases',
                'duration': 'Weeks 12–18',
                'topics': [
                    'Node.js, Express, JWT/session authentication, RBAC & security hardening',
                    'PostgreSQL schema design, migrations, indexing & MongoDB aggregations',
                ],
            },
            {
                'milestone': 'Milestone 4: AI Engineering in Web Applications',
                'duration': 'Weeks 19–22',
                'topics': [
                    'Integrating streaming LLM chat, semantic search & AI copilots in Next.js/Node',
                    'Background job queues, rate limiting & token-usage metering',
                ],
            },
            {
                'milestone': 'Milestone 5: DSA & Scalable System Design',
                'duration': 'Weeks 23–27',
                'topics': [
                    'Arrays, trees, graphs, dynamic programming & interview problem solving',
                    'Caching (Redis), load balancing, WebSockets & microservices patterns',
                ],
            },
            {
                'milestone': 'Milestone 6: Docker, Cloud CI/CD & Capstone Launch',
                'duration': 'Weeks 28–32',
                'topics': [
                    'Automated testing, Docker Compose, GitHub Actions & cloud hosting',
                    'Production SaaS capstone defense & SDE mock technical interviews',
                ],
            },
        ],
    },
    {
        'slug': 'mern-stack-development',
        'title': 'MERN Stack Development with GenAI',
        'short_title': 'MERN Stack with GenAI',
        'category': 'full-stack-ai',
        'category_name': 'Full Stack with AI Engineering',
        'badge': 'Popular',
        'duration': '24 Weeks (6 Months)',
        'hours': '160+ Hrs Live',
        'mode': 'Live Mentorship',
        'projects': '10+ Full-Stack Apps',
        'level': 'Beginner to Job-Ready',
        'icon': 'fas fa-layer-group',
        'summary': 'Specialize deeply in MongoDB, Express.js, React.js, and Node.js across 6 months—building real-time, payment-enabled, AI-augmented full-stack web products.',
        'capstone': 'Build and deploy a full-featured collaborative project management & e-commerce platform with AI smart-search, Razorpay/Stripe checkout, and WebSockets.',
        'highlights': [
            '10+ full-stack JavaScript applications pushed to GitHub & cloud',
            'Master Redux Toolkit, JWT auth, file uploads & WebSocket real-time chat',
            'Add GenAI smart assistants & content generators to MERN apps',
            'Weekly 1-on-1 code reviews & MERN developer mock interviews',
        ],
        'tools': ['MongoDB', 'Express.js', 'React.js', 'Node.js', 'Redux Toolkit', 'Socket.io', 'JWT Auth', 'Tailwind CSS', 'LLM APIs'],
        'roles': ['MERN Stack Developer', 'React.js Developer', 'Node.js Backend Developer', 'JavaScript Engineer'],
        'curriculum': [
            {
                'milestone': 'Milestone 1: JavaScript Deep Dive & Responsive UI',
                'duration': 'Weeks 1–5',
                'topics': [
                    'Scopes, prototypes, event loop, promises & modular ES6+ JavaScript',
                    'Responsive Tailwind CSS UI systems & accessible component design',
                ],
            },
            {
                'milestone': 'Milestone 2: React.js & State Architecture',
                'duration': 'Weeks 6–11',
                'topics': [
                    'Hooks, Context API, Redux Toolkit, RTK Query & protected routing',
                    'Optimistic UI updates, infinite scroll & bundle optimization',
                ],
            },
            {
                'milestone': 'Milestone 3: Node.js, Express & MongoDB Engineering',
                'duration': 'Weeks 12–17',
                'topics': [
                    'Mongoose schemas, aggregation pipelines, indexing & transactions',
                    'JWT refresh tokens, cookies, CORS, Helmet & cloud media uploads',
                ],
            },
            {
                'milestone': 'Milestone 4: Real-Time Features, Payments & GenAI',
                'duration': 'Weeks 18–21',
                'topics': [
                    'WebSockets with Socket.io and Stripe/Razorpay webhook integration',
                    'Embedding AI chat, summarization & semantic search into MERN backends',
                ],
            },
            {
                'milestone': 'Milestone 5: Testing, Cloud Deployment & Capstone',
                'duration': 'Weeks 22–24',
                'topics': [
                    'API integration tests, cloud hosting & production monitoring',
                    'Capstone demo & full-stack technical interview preparation',
                ],
            },
        ],
    },

    # ---------------- 5. Cyber Security ----------------
    {
        'slug': 'ethical-hacking-bootcamp',
        'title': 'Ethical Hacking & Penetration Testing Bootcamp',
        'short_title': 'Ethical Hacking & Pentesting',
        'category': 'cyber-security',
        'category_name': 'Cyber Security',
        'badge': 'Job-Ready',
        'duration': '24 Weeks (6 Months)',
        'hours': '150+ Hrs Live',
        'mode': 'Live Hands-On Labs',
        'projects': '20+ Security Labs',
        'level': 'Beginner to Pro',
        'icon': 'fas fa-user-secret',
        'summary': 'A 6-month offensive security mentorship program covering Networking, Linux, OSINT, Network & Web Application Pentesting, Active Directory, and professional VAPT reporting.',
        'capstone': 'Perform a simulated black-box & gray-box penetration test on a multi-host lab network and deliver an executive + remediation VAPT report.',
        'highlights': [
            '20+ guided attack & defense labs in isolated virtual environments',
            'Deep mastery of OWASP Top 10, Burp Suite Pro workflows & API testing',
            'Network scanning, Metasploit, Wireshark & Active Directory fundamentals',
            'Prepares you for Junior Pentester, VAPT & Security Analyst roles',
        ],
        'tools': ['Kali Linux', 'Nmap', 'Burp Suite', 'Metasploit', 'Wireshark', 'OWASP ZAP', 'ffuf', 'Hydra'],
        'roles': ['Ethical Hacker', 'Penetration Tester', 'VAPT Security Analyst', 'AppSec Engineer'],
        'curriculum': [
            {
                'milestone': 'Milestone 1: Networking Internals & Linux Security',
                'duration': 'Weeks 1–4',
                'topics': [
                    'TCP/IP, OSI layers, subnetting, DNS, TLS handshakes & HTTP internals',
                    'Kali Linux mastery, Bash scripting, permissions & process auditing',
                ],
            },
            {
                'milestone': 'Milestone 2: OSINT, Reconnaissance & Scanning',
                'duration': 'Weeks 5–8',
                'topics': [
                    'Passive/active footprinting, subdomain enumeration & asset discovery',
                    'Nmap scripting engine (NSE), service fingerprinting & banner analysis',
                ],
            },
            {
                'milestone': 'Milestone 3: System, Network & Wireless Exploitation',
                'duration': 'Weeks 9–12',
                'topics': [
                    'Vulnerability validation, Metasploit modules & safe exploit chaining',
                    'Linux/Windows privilege escalation & Wireshark packet forensics',
                ],
            },
            {
                'milestone': 'Milestone 4: Web Application & API Penetration Testing',
                'duration': 'Weeks 13–17',
                'topics': [
                    'OWASP Top 10: SQLi, XSS, CSRF, SSRF, IDOR & broken access control',
                    'Intercepting & fuzzing REST/GraphQL APIs and JWT flaws in Burp Suite',
                ],
            },
            {
                'milestone': 'Milestone 5: Active Directory & Cloud Security Basics',
                'duration': 'Weeks 18–20',
                'topics': [
                    'Kerberos, BloodHound path mapping & lateral-movement defense',
                    'Cloud IAM misconfigurations and S3/storage hardening',
                ],
            },
            {
                'milestone': 'Milestone 6: VAPT Reporting, CTF & Placement Prep',
                'duration': 'Weeks 21–24',
                'topics': [
                    'Writing CVSS-scored executive & developer-ready VAPT reports',
                    'Live CTF capstone challenge & security analyst mock interviews',
                ],
            },
        ],
    },
    {
        'slug': 'soc-analyst-certification',
        'title': 'SOC Analyst Certification (L1 & Threat Defense)',
        'short_title': 'SOC Analyst (L1)',
        'category': 'cyber-security',
        'category_name': 'Cyber Security',
        'badge': 'Certification',
        'duration': '20 Weeks (5 Months)',
        'hours': '120+ Hrs Live',
        'mode': 'Live Mentorship + Labs',
        'projects': '14+ Incident Drills',
        'level': 'Beginner to Job-Ready',
        'icon': 'fas fa-shield-virus',
        'summary': 'Become a blue-team SOC Analyst (L1) through hands-on SIEM monitoring, Windows/Linux log forensics, phishing triage, MITRE ATT&CK mapping, and incident response.',
        'capstone': 'Investigate a simulated multi-stage ransomware & credential-dumping attack in SIEM logs, build detection rules, and author a complete Incident Response report.',
        'highlights': [
            '14+ realistic blue-team alert triage & incident response simulations',
            'Hands-on SIEM log correlation, Splunk/Wazuh queries & Sigma rules',
            'Map attacker TTPs using the MITRE ATT&CK framework',
            'Dedicated L1/L2 SOC shift interview scenarios & resume reviews',
        ],
        'tools': ['Splunk / SIEM', 'Wazuh', 'Wireshark', 'MITRE ATT&CK', 'Sysmon', 'YARA', 'VirusTotal'],
        'roles': ['SOC Analyst (L1)', 'Cyber Defense Analyst', 'Incident Response Associate', 'Threat Intelligence Analyst'],
        'curriculum': [
            {
                'milestone': 'Milestone 1: Blue-Team Foundations & SOC Operations',
                'duration': 'Weeks 1–4',
                'topics': [
                    'SOC tiers (L1/L2/L3), alert lifecycle, SLA triage & ticketing workflows',
                    'Cyber Kill Chain, MITRE ATT&CK tactics & defense-in-depth architecture',
                ],
            },
            {
                'milestone': 'Milestone 2: Endpoint & Network Log Forensics',
                'duration': 'Weeks 5–8',
                'topics': [
                    'Windows Event IDs, Sysmon telemetry, PowerShell logging & Linux auth logs',
                    'Deep packet inspection in Wireshark to spot C2 beacons & exfiltration',
                ],
            },
            {
                'milestone': 'Milestone 3: SIEM Engineering & Detection Rules',
                'duration': 'Weeks 9–13',
                'topics': [
                    'Log ingestion, Splunk/SIEM search pipelines & dashboard building',
                    'Writing correlation alerts, Sigma rules & tuning false positives',
                ],
            },
            {
                'milestone': 'Milestone 4: Phishing, Malware Triage & Threat Intel',
                'duration': 'Weeks 14–17',
                'topics': [
                    'Email header/SPF/DKIM/DMARC analysis & malicious attachment sandboxing',
                    'IOC enrichment, YARA scanning & threat-hunting hypotheses',
                ],
            },
            {
                'milestone': 'Milestone 5: Incident Response Drills & Career Prep',
                'duration': 'Weeks 18–20',
                'topics': [
                    'NIST incident containment, eradication & post-incident lessons learned',
                    'Live SOC shift capstone & blue-team technical mock interviews',
                ],
            },
        ],
    },

    # ---------------- 6. Cloud Computing ----------------
    {
        'slug': 'cloud-computing-aws-azure',
        'title': 'Cloud Computing & Multi-Cloud Mentorship Program (AWS & Azure)',
        'short_title': 'Cloud Computing (AWS & Azure)',
        'category': 'cloud-computing',
        'category_name': 'Cloud Computing',
        'badge': 'New',
        'duration': '24 Weeks (6 Months)',
        'hours': '150+ Hrs Live',
        'mode': 'Live Online Cohort',
        'projects': '14+ Cloud Labs',
        'level': 'Beginner to Job-Ready',
        'icon': 'fas fa-cloud',
        'summary': 'A comprehensive 6-month multi-cloud mentorship program covering Linux & Cloud Networking, AWS Core Architecture, Microsoft Azure, Terraform IaC, Serverless, and Cloud Security.',
        'capstone': 'Design, provision with Terraform, and deploy a fault-tolerant, auto-scaling multi-AZ web architecture across AWS & Azure with centralized CloudWatch logging and FinOps cost alerts.',
        'highlights': [
            '150+ hours of live cloud architecture & lab walkthroughs',
            '14+ hands-on labs spanning VPC networking, EC2, S3, RDS & Azure AD',
            'Infrastructure as Code (IaC) automation using Terraform',
            'Prepares you for AWS Solutions Architect & Azure Administrator roles',
        ],
        'tools': ['AWS', 'Microsoft Azure', 'Terraform', 'Docker', 'Linux', 'VPC & IAM', 'AWS Lambda', 'CloudWatch'],
        'roles': ['Cloud Engineer', 'AWS Solutions Architect', 'Azure Cloud Administrator', 'Cloud Support Engineer'],
        'curriculum': [
            {
                'milestone': 'Milestone 1: Cloud Foundations, Linux & Virtual Networking',
                'duration': 'Weeks 1–4',
                'topics': [
                    'IaaS/PaaS/SaaS, shared responsibility model & global region/AZ design',
                    'Linux administration, SSH hardening, systemd services & Bash scripting',
                    'CIDR subnetting, DNS routing, load balancers & firewall security groups',
                ],
            },
            {
                'milestone': 'Milestone 2: AWS Core Infrastructure & Storage',
                'duration': 'Weeks 5–9',
                'topics': [
                    'IAM least-privilege policies, EC2 Auto Scaling & Application Load Balancers',
                    'S3 lifecycle policies, EBS snapshots, EFS & managed RDS PostgreSQL/MySQL',
                    'Private/public VPC peering, NAT gateways & Bastion host architectures',
                ],
            },
            {
                'milestone': 'Milestone 3: Microsoft Azure & Multi-Cloud Services',
                'duration': 'Weeks 10–13',
                'topics': [
                    'Azure Resource Groups, VNets, Virtual Machines & Entra ID (Azure AD)',
                    'Azure Blob Storage, App Service & hybrid identity synchronization',
                ],
            },
            {
                'milestone': 'Milestone 4: Infrastructure as Code with Terraform',
                'duration': 'Weeks 14–17',
                'topics': [
                    'HCL syntax, remote state locking, reusable modules & workspaces',
                    'Provisioning reproducible staging & production cloud environments',
                ],
            },
            {
                'milestone': 'Milestone 5: Serverless, Containers, Cloud Security & FinOps',
                'duration': 'Weeks 18–21',
                'topics': [
                    'AWS Lambda, API Gateway, ECS containers & event-driven queues (SQS/SNS)',
                    'KMS encryption, CloudTrail auditing, GuardDuty & FinOps cost optimization',
                ],
            },
            {
                'milestone': 'Milestone 6: Multi-Cloud Capstone & Architect Interview Prep',
                'duration': 'Weeks 22–24',
                'topics': [
                    'End-to-end highly available cloud deployment & disaster recovery drill',
                    'AWS/Azure certification exam prep & cloud architect mock interviews',
                ],
            },
        ],
    },
    {
        'slug': 'cloud-devops-engineering',
        'title': 'Cloud & DevOps Engineering Mentorship Program',
        'short_title': 'Cloud & DevOps Engineering',
        'category': 'cloud-computing',
        'category_name': 'Cloud Computing',
        'badge': 'Job-Ready',
        'duration': '24 Weeks (6 Months)',
        'hours': '160+ Hrs Live',
        'mode': 'Live Cohort + Labs',
        'projects': '12+ CI/CD Pipelines',
        'level': 'Beginner to Pro',
        'icon': 'fas fa-server',
        'summary': 'Master modern DevOps and SRE engineering across Linux, Git, Docker, Kubernetes, CI/CD automation (GitHub Actions & Jenkins), Terraform, Ansible, and Prometheus/Grafana observability.',
        'capstone': 'Build a zero-downtime GitOps CI/CD pipeline deploying containerized microservices to a managed Kubernetes cluster with Terraform IaC and Grafana SLA alerting.',
        'highlights': [
            '160+ hours of live production-grade DevOps & Kubernetes labs',
            '12+ automated CI/CD, Docker, Terraform & observability pipelines',
            'Hands-on EKS/AKS Kubernetes deployments, Helm charts & ingress TLS',
            'Mock SRE / DevOps interviews & architecture troubleshooting drills',
        ],
        'tools': ['AWS & Azure', 'Docker', 'Kubernetes', 'Terraform', 'GitHub Actions', 'Jenkins', 'Ansible', 'Prometheus & Grafana'],
        'roles': ['DevOps Engineer', 'Site Reliability Engineer (SRE)', 'Cloud Infrastructure Engineer', 'Platform Engineer'],
        'curriculum': [
            {
                'milestone': 'Milestone 1: Linux, Git Workflows & Shell Automation',
                'duration': 'Weeks 1–4',
                'topics': [
                    'Git branching strategies, rebase workflows & pull-request automation',
                    'Linux process internals, Nginx reverse proxies, SSL/TLS & Bash/Python scripts',
                ],
            },
            {
                'milestone': 'Milestone 2: Docker Containers & Multi-Service Apps',
                'duration': 'Weeks 5–8',
                'topics': [
                    'Multi-stage Dockerfiles, image security scanning & layer caching',
                    'Docker Compose networks, volumes & container registry management',
                ],
            },
            {
                'milestone': 'Milestone 3: Kubernetes Orchestration (K8s / EKS / AKS)',
                'duration': 'Weeks 9–13',
                'topics': [
                    'Pods, Deployments, Services, ConfigMaps, Secrets & StatefulSets',
                    'Helm charts, Horizontal Pod Autoscaling (HPA) & Ingress controllers',
                ],
            },
            {
                'milestone': 'Milestone 4: CI/CD Pipelines (GitHub Actions & Jenkins)',
                'duration': 'Weeks 14–17',
                'topics': [
                    'Automated lint, test, container build & blue-green/canary rollouts',
                    'Jenkinsfile declarative pipelines & artifact security gates',
                ],
            },
            {
                'milestone': 'Milestone 5: Terraform & Ansible Configuration Management',
                'duration': 'Weeks 18–20',
                'topics': [
                    'Provisioning Kubernetes clusters & VPCs cleanly with Terraform',
                    'Server hardening & fleet configuration via Ansible playbooks',
                ],
            },
            {
                'milestone': 'Milestone 6: Observability, SRE & Capstone',
                'duration': 'Weeks 21–24',
                'topics': [
                    'Prometheus metrics, Grafana dashboards, Loki logs & incident runbooks',
                    'Full GitOps DevOps capstone & SRE/DevOps mock technical interviews',
                ],
            },
        ],
    },
]

COURSES_BY_SLUG = {c['slug']: c for c in COURSES}

_CATEGORY_IMAGES = {
    'digital-marketing': 'images/courses/digital-marketing.png',
    'data-science-analytics': 'images/courses/data-analytics.png',
    'ai-programs': 'images/courses/ai-genai.png',
    'full-stack-ai': 'images/courses/full-stack-ai.png',
    'cyber-security': 'images/courses/cyber-security.png',
    'cloud-computing': 'images/courses/cloud-computing.png',
}

_COURSE_IMAGES = {
    'seo-aeo-bootcamp': 'images/courses/seo-aeo.png',
    'data-science-ml': 'images/courses/data-science-ml.png',
}

_CATEGORY_PROJECTS = {
    'digital-marketing': [
        ('Live SEO + AEO Growth Audit', 'Full 50-point technical crawl, schema markup, and LLM Answer Engine strategy on a real web domain.', 'Search & AI'),
        ('High-ROAS Meta & Google Ads Funnel', 'End-to-end audience matrix, creative sprint variations, and server-side GA4/CAPI conversion tracking.', 'Paid Media'),
        ('n8n + HubSpot AI CRM Engine', 'Automated WhatsApp, email nurturing, and lead-scoring pipeline built without brittle manual steps.', 'Automation'),
    ],
    'data-science-analytics': [
        ('Executive Revenue & Cohort Power BI Suite', 'Multi-page interactive DAX dashboard tracking retention, churn drivers, and unit economics.', 'BI & Viz'),
        ('SQL + Python Data Warehouse Pipeline', 'Normalized PostgreSQL analytics schema with automated cleaning, anomaly detection, and KPI exports.', 'Data Ops'),
        ('Predictive ML Forecasting & GenAI Copilot', 'Deployed scikit-learn churn/demand predictor paired with natural-language insight summaries.', 'ML & GenAI'),
    ],
    'ai-programs': [
        ('Enterprise Hybrid RAG Knowledge Assistant', 'Production Q&A system combining vector + BM25 search, reranking, and strict source citations.', 'RAG & LLMs'),
        ('Autonomous Multi-Agent Research & Ops Crew', 'Tool-calling agentic workflow with memory, guardrail validation, and webhook integrations.', 'Agentic AI'),
        ('Full-Stack FastAPI AI SaaS Product', 'Streaming LLM backend with latency observability, evaluation suite, and live cloud deployment.', 'Production AI'),
    ],
    'full-stack-ai': [
        ('AI-Powered SaaS Web Platform', 'Responsive React/Next.js frontend backed by Node.js/REST/GraphQL APIs, Redis caching, and Auth.', 'Full Stack'),
        ('Real-Time Collaborative Workspace', 'WebSocket live updates, role-based permissions, Stripe billing simulation, and PostgreSQL schema.', 'System Design'),
        ('Dockerized CI/CD Cloud Deployment', 'Automated GitHub Actions test & build pipeline shipping a zero-downtime cloud web application.', 'DevOps Ready'),
    ],
    'cyber-security': [
        ('OWASP Web & API Penetration Test Report', 'Exploiting and patching IDOR, SQLi, XSS, and JWT flaws in Burp Suite with executive VAPT PDF report.', 'Offensive Sec'),
        ('Active Directory & Network Compromise Lab', 'Internal enumeration, privilege escalation defense, and hardening checklist across Linux/Windows hosts.', 'Red & Blue'),
        ('SOC L1 SIEM Detection & Incident Playbook', 'Splunk/Wazuh correlation rules, phishing triage, MITRE ATT&CK mapping, and containment runbook.', 'SOC Defense'),
    ],
    'cloud-computing': [
        ('Multi-AZ Highly Available Cloud Architecture', 'VPC subnetting, Application Load Balancers, Auto Scaling, RDS, and least-privilege IAM on AWS & Azure.', 'Cloud Infra'),
        ('Reusable Terraform IaC Modules', 'Version-controlled Infrastructure as Code provisioning isolated staging and production cloud stacks.', 'IaC Automation'),
        ('Zero-Downtime Kubernetes GitOps Pipeline', 'Dockerized microservices deployed onto managed K8s/EKS with Helm, HPA scaling, and Grafana alerts.', 'Cloud DevOps'),
    ],
}

_COMPARISON_ROWS = [
    ('Live 2-Way Mentor Classes (Not Just Videos)', 'Live interactive cohorts + real-time code/campaign reviews', 'Mostly pre-recorded videos with delayed replies'),
    ('Curriculum Updated for AI & 2026 Hiring', 'Built around GenAI tools, AEO, RAG & modern production stacks', 'Outdated slides from 3+ years ago'),
    ('Line-by-Line Capstone Feedback', 'Reviewed personally by working engineers & domain directors', 'Generic automated quiz certificates'),
    ('Small Cohort Size for Personal Attention', 'Max 25 learners/batch with dedicated doubt clinics', 'Crowded 200+ webinars where questions get lost'),
    ('Real IT Company Exposure', 'Mentors lead live client projects at BunShai TECHNOHUB', 'Purely academic theory instructors'),
    ('Verified Portfolio + Career Prep', '10–24+ real deliverables, GitHub/portfolio audit & mock interviews', 'No tailored interview or portfolio defense'),
    ('Transparent Downloadable Syllabus', 'Instant structured milestone PDF before you enroll', 'Vague topic bullet points only'),
]


def _enrich_catalog():
    for cat in COURSE_CATEGORIES:
        cat.setdefault('image', _CATEGORY_IMAGES.get(cat['slug'], 'images/site/tech-studio.png'))

    for c in COURSES:
        cat_slug = c['category']
        c.setdefault('image', _COURSE_IMAGES.get(c['slug'], _CATEGORY_IMAGES.get(cat_slug, 'images/site/tech-studio.png')))
        c.setdefault('rating', '4.9/5')
        c.setdefault('cohort_size', 'Max 25 Learners / Batch')
        top_tools = ', '.join(c.get('tools', [])[:4])
        c.setdefault('why_us', [
            {
                'icon': 'fas fa-chalkboard-teacher',
                'title': 'Practicing Industry Mentors, Not Just Trainers',
                'desc': f"Learn directly from specialists shipping live {c['category_name']} work at BunShai TECHNOHUB — not script-reading lecturers.",
            },
            {
                'icon': 'fas fa-robot',
                'title': 'AI-First Toolchain Built Into Every Milestone',
                'desc': f"Master {top_tools} alongside modern AI workflows so you work 3x faster than traditionally trained candidates.",
            },
            {
                'icon': 'fas fa-layer-group',
                'title': f"{c['projects']} Reviewed Portfolio Deliverables",
                'desc': 'Graduate with verified capstones, architecture docs, and live demos recruiters can inspect in 30 seconds.',
            },
            {
                'icon': 'fas fa-user-tie',
                'title': '1:1 Mock Interviews & Placement Support',
                'desc': f"Targeted resume reviews, LinkedIn positioning, and technical/case mocks tailored for {c['roles'][0]} interviews.",
            },
        ])
        c.setdefault('comparison_rows', _COMPARISON_ROWS)
        c.setdefault('build_projects', [
            {'title': t, 'desc': d, 'tag': tag}
            for t, d, tag in _CATEGORY_PROJECTS.get(cat_slug, _CATEGORY_PROJECTS['full-stack-ai'])
        ])
        c.setdefault('faqs', [
            {
                'q': f"Can a beginner join {c['title']}?",
                'a': f"Yes! This track is rated '{c['level']}' and starts cleanly from core fundamentals before advancing to production capstones across {c['duration']}.",
            },
            {
                'q': 'What if I miss a live mentorship session?',
                'a': 'Every live class is recorded in HD and uploaded the same day along with slides, datasets/code repositories, and weekly live doubt-clearing clinics.',
            },
            {
                'q': 'Why choose BunShai TECHNOHUB instead of a cheaper recorded course?',
                'a': f"Recorded videos leave you stuck on errors with an empty portfolio. Here you build {c['projects']} real projects with max 25 peers per cohort, get personal feedback from working {c['category_name']} practitioners, and practice real mock interviews.",
            },
            {
                'q': 'Will I receive an industry-recognized certificate and placement guidance?',
                'a': 'Yes. Upon completing your milestone deliverables and flagship capstone defense, you earn a verifiable BunShai TECHNOHUB Certification plus resume, GitHub/portfolio, and interview preparation.',
            },
            {
                'q': 'How do I inspect the week-by-week syllabus before enrolling?',
                'a': "Click 'Download Full Syllabus (PDF)' anywhere on this page to instantly unlock and download the complete milestone-by-milestone PDF syllabus.",
            },
        ])
        c.setdefault('video_chapters', [
            {'time': '00:00', 'title': f"{c['duration']} Roadmap", 'desc': f"{c['hours']} structured into practical weekly sprints from basics to capstone."},
            {'time': '00:15', 'title': f"{c['projects']} Real Projects", 'desc': c['capstone']},
            {'time': '00:30', 'title': 'Modern Tools & AI Stack', 'desc': f"Hands-on mastery of {', '.join(c.get('tools', [])[:6])}."},
            {'time': '00:45', 'title': 'Career Launch & Placement', 'desc': f"Direct readiness for {', '.join(c.get('roles', [])[:3])} roles."},
        ])


_enrich_catalog()


def get_courses_by_category():
    grouped = []
    for cat in COURSE_CATEGORIES:
        cat_courses = [c for c in COURSES if c['category'] == cat['slug']]
        grouped.append({**cat, 'courses': cat_courses})
    return grouped


NAV_COURSE_GROUPS = get_courses_by_category()
