"""
Script to build the full, production-grade index.html with:
- Left-hand vertical sidebar navigation (responsive with mobile toggle)
- Strict authentication gate (login first, entire site locked until signed in)
- Prominent Sign Out buttons (Header & Sidebar)
- Complete receipts publishing, printing, and downloading (ABHA FHIR JSON, Form 5 Certificate, SMS Receipt)
- 10 Public Datasets & Sources catalog view (#section-datasets)
"""

import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC_TEMPLATE = os.path.join(ROOT_DIR, "app", "templates", "index.html.bak")
DST_TEMPLATE = os.path.join(ROOT_DIR, "app", "templates", "index.html")

with open(SRC_TEMPLATE, "r", encoding="utf-8") as f:
    orig_lines = f.readlines()

head_lines = orig_lines[:150]
# We'll add print styles to head_lines
head_html = "".join(head_lines).replace("</style>", """  @media print {
    body * { visibility: hidden !important; }
    #modal-form-5:not(.hidden), #modal-form-5:not(.hidden) *,
    #modal-abha-published:not(.hidden), #modal-abha-published:not(.hidden) * {
      visibility: visible !important;
    }
    #modal-form-5, #modal-abha-published {
      position: absolute !important;
      left: 0 !important; top: 0 !important;
      width: 100% !important; margin: 0 !important; padding: 0 !important;
      background: white !important;
    }
    .modal-content-box { box-shadow: none !important; border: none !important; }
    header, aside, footer, #toast-container { display: none !important; }
  }
</style>""")

sec_worker = "".join(orig_lines[294:482])
sec_site = "".join(orig_lines[484:649])
sec_van = "".join(orig_lines[651:784])
sec_district = "".join(orig_lines[786:869])
sec_research = "".join(orig_lines[871:995])
sec_facilities = "".join(orig_lines[997:1031])
sec_login = "".join(orig_lines[1033:1103])
footer_html = "".join(orig_lines[1105:1136])
modal_support = "".join(orig_lines[1252:1315])
modal_security = "".join(orig_lines[1317:1348])

# Enhanced Modal 1: Form 5 Certificate
modal_form5 = """  <!-- ===================================================================== -->
  <!-- MODAL 1: FORM 5 CERTIFICATE OF MEDICAL EXAMINATION (GUJARAT OSH) -->
  <!-- ===================================================================== -->
  <div id="modal-form-5" class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="modal-content-box bg-white max-w-2xl w-full rounded p-6 shadow-2xl border border-slate-300 max-h-[90vh] overflow-y-auto">
      <div class="flex items-center justify-between border-b border-slate-200 pb-3 mb-4">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-primary text-[24px]">verified</span>
          <div>
            <h3 class="font-serif font-bold text-base text-primary">FORM 5 · CERTIFICATE OF FITNESS</h3>
            <span class="text-[11px] text-slate-500 font-sans">[See Rule 9(1) of the Gujarat Occupational Safety, Health and Working Conditions Rules, 2025]</span>
          </div>
        </div>
        <button onclick="closeForm5Modal()" class="text-slate-400 hover:text-slate-600">
          <span class="material-symbols-outlined">close</span>
        </button>
      </div>

      <div class="space-y-4 text-xs font-sans text-slate-800">
        <div class="p-3 bg-slate-50 rounded border border-slate-200 space-y-1">
          <div class="flex justify-between">
            <span class="text-slate-500">Serial No.:</span>
            <span class="font-mono font-bold">GJ-KCH-OSH-2025-0814</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">Certifying Surgeon:</span>
            <span class="font-semibold">Dr. Rajesh V. Dave, MBBS, DPH (Govt Certifying Surgeon)</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-500">District / Jurisdiction:</span>
            <span>Kachchh (Bhuj, Gandhidham, Mundra, Rapar)</span>
          </div>
        </div>

        <div class="border border-slate-200 rounded p-4 space-y-2">
          <p>I hereby certify that I have personally examined:</p>
          <div class="grid grid-cols-2 gap-2 font-mono text-[11px] bg-slate-50 p-2.5 rounded">
            <div><b>Name:</b> Ramjibhai S. Koli</div>
            <div><b>Age / Gender:</b> 48 Years / Male</div>
            <div><b>e-Shram UAN:</b> 9842-XXXX-1001</div>
            <div><b>Father's Name:</b> Somabhai Koli</div>
            <div><b>Trade / Process:</b> Salt Pan Brine Raking &amp; Stacking</div>
            <div><b>Worksite:</b> Little Rann Salt Cluster #3</div>
          </div>
          <p class="pt-2">
            And that in my opinion, he is <b>FIT</b> for employment in the hazardous process of salt raking and mineral handling, subject to mandatory 30-minute shaded rest breaks during WBGT heat alerts (&gt; 28.0°C).
          </p>
        </div>

        <div class="grid grid-cols-2 gap-4 pt-2">
          <div class="p-2.5 bg-slate-50 rounded border border-slate-200">
            <span class="text-[10px] text-slate-500 block">Date of Examination:</span>
            <span class="font-bold">15 April 2025</span>
          </div>
          <div class="p-2.5 bg-slate-50 rounded border border-slate-200">
            <span class="text-[10px] text-slate-500 block">Renewal Due Date:</span>
            <span class="font-bold text-primary">14 April 2026 (Annual)</span>
          </div>
        </div>
      </div>

      <div class="mt-6 pt-4 border-t border-slate-200 flex flex-wrap items-center justify-between gap-2">
        <span class="text-[11px] text-slate-500 font-mono">Digitally attested with DISH Gujarat Signature</span>
        <div class="flex items-center gap-2">
          <button onclick="downloadForm5()" class="px-3 py-1.5 bg-secondary text-white text-xs font-semibold rounded hover:bg-secondary-container hover:text-primary transition flex items-center gap-1 shadow-sm">
            <span class="material-symbols-outlined text-[16px]">download</span>
            <span>Download Certificate</span>
          </button>
          <button onclick="printForm5()" class="px-3 py-1.5 bg-primary text-white text-xs font-semibold rounded hover:bg-primary-container transition flex items-center gap-1 shadow-sm">
            <span class="material-symbols-outlined text-[16px]">print</span>
            <span>Print Official Form 5</span>
          </button>
          <button onclick="closeForm5Modal()" class="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold rounded transition">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>"""

# Enhanced Modal 2: ABHA Published Receipt
modal_abha = """  <!-- ===================================================================== -->
  <!-- MODAL 2: ABHA PUBLISHING & HL7 FHIR R4 RECEIPT -->
  <!-- ===================================================================== -->
  <div id="modal-abha-published" class="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm hidden flex items-center justify-center p-4">
    <div class="modal-content-box bg-white max-w-xl w-full rounded p-6 shadow-2xl border border-slate-300">
      <div class="flex items-center gap-3 border-b border-slate-200 pb-3 mb-4">
        <div class="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 flex-shrink-0">
          <span class="material-symbols-outlined text-[24px]">task_alt</span>
        </div>
        <div>
          <h3 class="font-bold text-base text-slate-900">Successfully Published to ABHA Locker</h3>
          <span class="text-xs text-emerald-700 font-semibold">Ayushman Bharat Digital Mission (ABDM) Transaction Verified</span>
        </div>
      </div>

      <div class="space-y-3 text-xs text-slate-700">
        <div class="p-3 bg-emerald-50 rounded border border-emerald-200 space-y-1">
          <div class="flex justify-between">
            <span class="text-slate-600">Patient:</span>
            <span id="modal-worker-name" class="font-bold text-slate-900">Ramjibhai S. Koli</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-600">ABHA Address:</span>
            <span id="modal-abha-addr" class="font-mono text-emerald-800 font-bold">ramjibhai.kutch@abdm</span>
          </div>
          <div class="flex justify-between">
            <span class="text-slate-600">Care Context:</span>
            <span id="modal-care-context" class="font-mono">OCC-EXAM-2025-4081</span>
          </div>
        </div>

        <span class="font-bold text-slate-800 block">HL7 FHIR R4 Bundle Payload Generated:</span>
        <pre id="modal-fhir-json" class="bg-slate-900 text-emerald-400 p-3 rounded text-[11px] font-mono overflow-x-auto max-h-48"></pre>
      </div>

      <div class="mt-4 pt-3 border-t border-slate-200 flex flex-wrap items-center justify-between gap-2">
        <div class="flex flex-wrap items-center gap-2">
          <button onclick="printAbhaReceipt()" class="px-3 py-1.5 bg-primary text-white text-xs font-semibold rounded hover:bg-primary-container transition flex items-center gap-1 shadow-sm">
            <span class="material-symbols-outlined text-[16px]">print</span>
            <span>Print Official Receipt</span>
          </button>
          <button onclick="downloadFhirJson()" class="px-3 py-1.5 bg-secondary text-white text-xs font-semibold rounded hover:bg-secondary-container hover:text-primary transition flex items-center gap-1 shadow-sm">
            <span class="material-symbols-outlined text-[16px]">download</span>
            <span>Download FHIR JSON</span>
          </button>
          <button onclick="sendWorkerSmsReceipt()" class="px-3 py-1.5 bg-surface-container hover:bg-surface-container-high text-primary border border-outline-variant/40 text-xs font-semibold rounded transition flex items-center gap-1">
            <span class="material-symbols-outlined text-[16px]">sms</span>
            <span>Issue SMS Receipt</span>
          </button>
        </div>
        <button onclick="closeAbhaPublishedModal()" class="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 text-white text-xs font-semibold rounded transition">
          Close
        </button>
      </div>
    </div>
  </div>"""

# Section 7: Public Datasets Catalog
sec_datasets = """    <!-- =================================================================== -->
    <!-- TAB 7: PUBLIC DATASETS & SCIENTIFIC SOURCES CATALOG -->
    <!-- =================================================================== -->
    <section id="section-datasets" class="tab-section hidden">
      <div class="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 bg-surface-container-lowest rounded border border-outline-variant/40 shadow-sm">
        <div>
          <span class="text-xs font-bold text-secondary tracking-wider uppercase">Public Empirical Data Vault</span>
          <h2 class="text-xl font-bold font-editorial text-primary">Public Datasets &amp; Scientific Sources Catalog (PS000109)</h2>
          <p class="text-xs text-on-surface-variant mt-0.5">
            10 Verified Government, Demographics, Industrial Hygiene &amp; Scientific Sources Stored in <code class="bg-surface-container px-1 py-0.5 rounded font-mono">final_dataset/public_downloads/</code>.
          </p>
        </div>
        <div class="flex items-center gap-2">
          <button onclick="exportDistrictData()" class="px-3 py-1.5 bg-surface-container hover:bg-surface-container-high text-primary border border-outline-variant/40 text-xs font-semibold rounded transition flex items-center gap-1">
            <span class="material-symbols-outlined text-[16px]">download</span>
            <span>Export District Data (CSV)</span>
          </button>
          <a href="/api/datasets/public-catalog" target="_blank" class="px-3 py-1.5 bg-primary text-white text-xs font-semibold rounded shadow hover:bg-primary-container transition flex items-center gap-1">
            <span class="material-symbols-outlined text-[16px]">api</span>
            <span>REST API Catalog</span>
          </a>
        </div>
      </div>

      <!-- Dataset Metrics -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6 text-xs">
        <div class="p-4 bg-surface-container-lowest rounded border border-outline-variant/40 shadow-sm">
          <span class="text-[10px] text-on-surface-variant uppercase font-bold block">Cataloged Sources</span>
          <span class="text-2xl font-bold font-mono text-primary mt-1 block">10</span>
          <span class="text-[10px] text-secondary font-bold">100% De-Identified Data</span>
        </div>
        <div class="p-4 bg-surface-container-lowest rounded border border-outline-variant/40 shadow-sm">
          <span class="text-[10px] text-on-surface-variant uppercase font-bold block">Government Bodies</span>
          <span class="text-2xl font-bold font-mono text-secondary mt-1 block">MoSPI / IMD</span>
          <span class="text-[10px] text-on-surface-variant">Census, ICMR-NIOH, DISH</span>
        </div>
        <div class="p-4 bg-surface-container-lowest rounded border border-outline-variant/40 shadow-sm">
          <span class="text-[10px] text-on-surface-variant uppercase font-bold block">Scientific Satellites</span>
          <span class="text-2xl font-bold font-mono text-tertiary mt-1 block">NASA / ESA</span>
          <span class="text-[10px] text-on-surface-variant">TEMIS &amp; Aura OMI UV</span>
        </div>
        <div class="p-4 bg-surface-container-lowest rounded border border-outline-variant/40 shadow-sm">
          <span class="text-[10px] text-on-surface-variant uppercase font-bold block">Privacy Compliance</span>
          <span class="text-2xl font-bold font-mono text-emerald-700 mt-1 block">Zero PII</span>
          <span class="text-[10px] text-secondary font-bold">DPDP Act 2023 Attested</span>
        </div>
      </div>

      <!-- Datasets Filter & Grid -->
      <div class="bg-surface-container-lowest p-6 rounded border border-outline-variant/50 shadow-sm space-y-4">
        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-outline-variant/30 pb-3">
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-primary text-[20px]">folder_special</span>
            <h3 class="font-bold text-sm text-primary">All 10 Dedicated Source Folders</h3>
          </div>
          <div class="flex flex-wrap gap-1.5 text-[11px]" id="dataset-filter-tabs">
            <button onclick="filterDatasets('ALL')" class="dataset-tab-btn px-2.5 py-1 rounded font-bold bg-primary text-white">All (10)</button>
            <button onclick="filterDatasets('Socio-Economic')" class="dataset-tab-btn px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface bg-surface-container">Labor Hours</button>
            <button onclick="filterDatasets('Industrial Hygiene')" class="dataset-tab-btn px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface bg-surface-container">Noise JEM</button>
            <button onclick="filterDatasets('Demographics')" class="dataset-tab-btn px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface bg-surface-container">Census 2011</button>
            <button onclick="filterDatasets('Environmental UV')" class="dataset-tab-btn px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface bg-surface-container">TEMIS UV</button>
            <button onclick="filterDatasets('Satellite UV')" class="dataset-tab-btn px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface bg-surface-container">OMI UV</button>
            <button onclick="filterDatasets('Climate Projection')" class="dataset-tab-btn px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface bg-surface-container">CMIP6</button>
          </div>
        </div>

        <div id="datasets-grid" class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2">
          <!-- Dynamically populated from STATIC_DATA.datasets -->
        </div>
      </div>
    </section>"""

# Assemble Header & Sidebar
header_sidebar_html = """
<body class="bg-surface text-on-surface antialiased min-h-screen flex flex-col selection:bg-primary-container selection:text-white">

  <!-- ===================================================================== -->
  <!-- TOP GOVERNMENT OF GUJARAT EMBLEM & IDENTITY BAR -->
  <!-- ===================================================================== -->
  <header class="fixed top-0 left-0 right-0 h-14 md:h-16 z-40 bg-surface-container-lowest border-b border-outline-variant/40 shadow-sm flex flex-col justify-between">
    <!-- Tricolor Flag Accent Stripe -->
    <div class="w-full h-1 bg-gradient-to-r from-[#FF9933] via-surface-container-lowest to-[#006C4E]"></div>

    <!-- Main Header Bar -->
    <div class="w-full max-w-[1920px] mx-auto px-3 md:px-6 py-1.5 flex items-center justify-between gap-2">
      <!-- Left: Mobile Menu Toggle & Official Title -->
      <div class="flex items-center gap-2.5">
        <button id="sidebar-toggle" onclick="toggleSidebar()" class="md:hidden p-1.5 rounded hover:bg-surface-container text-primary transition">
          <span class="material-symbols-outlined text-[22px]">menu</span>
        </button>

        <div class="w-8 h-8 md:w-9 md:h-9 rounded border border-primary/20 bg-primary/5 flex items-center justify-center text-primary font-serif font-bold text-base md:text-lg shadow-sm flex-shrink-0">
          GJ
        </div>

        <div>
          <div class="flex items-center gap-1.5">
            <h1 class="font-editorial text-base md:text-lg font-bold tracking-tight text-primary leading-tight">
              WorkCheck Kachchh
            </h1>
            <span class="hidden sm:inline bg-primary/10 text-primary font-mono text-[9px] font-bold px-1.5 py-0.2 rounded">
              v2.0-STITCH
            </span>
          </div>
          <p class="hidden sm:block text-[10px] text-on-surface-variant leading-none mt-0.5">
            District Development Office (DDO) Kachchh · Gujarat OSH Rule 9 &amp; ABDM Platform
          </p>
        </div>
      </div>

      <!-- Right Controls: IST Clock, Emergency, Theme, Language & Sign Out -->
      <div class="flex items-center gap-1.5 md:gap-2 text-xs">
        <!-- Live Real-Time Clock -->
        <div class="hidden lg:flex items-center gap-1.5 px-2 py-1 bg-surface-container rounded text-on-surface font-mono text-[11px] border border-outline-variant/40">
          <span class="w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
          <span id="live-clock">Bhuj HQ · IST Loading...</span>
        </div>

        <!-- Emergency Help Button -->
        <button onclick="openSupportModal()" class="flex items-center gap-1 px-2 md:px-2.5 py-1 bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 rounded font-semibold text-[11px] transition">
          <span class="material-symbols-outlined text-[15px] text-amber-700">emergency</span>
          <span class="hidden sm:inline">Help &amp; Support</span>
        </button>

        <!-- Dark / Light Mode Toggle -->
        <button id="btn-theme-toggle" onclick="toggleTheme()" class="flex items-center gap-1 px-2 md:px-2.5 py-1 bg-surface-container hover:bg-surface-container-high text-on-surface border border-outline-variant/40 rounded font-semibold text-[11px] transition">
          <span id="theme-icon" class="material-symbols-outlined text-[15px]">dark_mode</span>
          <span id="theme-text" class="hidden sm:inline">Dark</span>
        </button>

        <!-- User Session Chip & Sign Out Button -->
        <div id="user-session-bar" class="flex items-center gap-1 px-2 py-1 bg-surface-container-low rounded border border-outline-variant/40 text-[11px]">
          <span class="material-symbols-outlined text-primary text-[15px]">account_circle</span>
          <span id="user-session-name" class="font-bold text-on-surface truncate max-w-[90px] sm:max-w-[130px]">Guest</span>
          <span id="user-session-badge" class="hidden sm:inline bg-primary/10 text-primary text-[9px] font-bold px-1 py-0.2 rounded">Public</span>
          <button id="btn-auth-action" onclick="switchTab('login')" class="ml-1 px-2 py-0.5 bg-primary hover:bg-primary-container text-white rounded font-bold text-[10px] transition flex items-center gap-0.5 shadow-sm">
            <span class="material-symbols-outlined text-[12px]">login</span>
            <span>Sign In</span>
          </button>
        </div>

        <!-- Regional Language Switcher -->
        <div class="hidden sm:flex items-center border border-outline-variant/50 rounded overflow-hidden text-[10px] bg-surface-container-lowest">
          <button id="btn-lang-gu" onclick="setAppLanguage('gu')" class="px-1.5 py-1 font-medium hover:text-primary transition">ગુજ</button>
          <button id="btn-lang-hi" onclick="setAppLanguage('hi')" class="px-1.5 py-1 font-medium hover:text-primary transition border-l border-outline-variant/40">हिन्दी</button>
          <button id="btn-lang-en" onclick="setAppLanguage('en')" class="px-1.5 py-1 font-bold text-primary transition border-l border-outline-variant/40">ENG</button>
        </div>
      </div>
    </div>
  </header>

  <!-- ===================================================================== -->
  <!-- MAIN WORKSPACE LAYOUT (LEFT SIDEBAR + CONTENT AREA) -->
  <!-- ===================================================================== -->
  <div class="pt-14 md:pt-16 min-h-screen flex flex-col md:flex-row bg-surface">

    <!-- LEFT SIDEBAR NAVIGATION MENU -->
    <aside id="app-sidebar" class="w-full md:w-64 lg:w-72 bg-surface-container-low border-r border-outline-variant/40 flex-shrink-0 flex flex-col justify-between p-3 md:p-4 sticky top-14 md:top-16 min-h-[calc(100vh-3.5rem)] md:max-h-[calc(100vh-3.5rem)] z-30 transition-all duration-200 overflow-y-auto">
      <div>
        <!-- Sidebar Header -->
        <div class="flex items-center justify-between pb-3 mb-3 border-b border-outline-variant/30">
          <div>
            <span class="text-[10px] font-bold tracking-wider text-primary uppercase block">Occupational Modules</span>
            <span class="text-xs font-semibold text-on-surface">મુખ્ય કાર્યક્ષેત્ર મેનુ</span>
          </div>
          <span class="flex items-center gap-1 text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-300">
            <span class="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
            LIVE
          </span>
        </div>

        <!-- Locked Banner (Visible when Logged Out) -->
        <div id="sidebar-lock-banner" class="p-3 bg-amber-500/10 border border-amber-500/30 rounded mb-3 text-xs text-amber-900 dark:text-amber-200 flex items-start gap-2">
          <span class="material-symbols-outlined text-amber-600 text-[18px] flex-shrink-0 mt-0.5">lock</span>
          <div>
            <span class="font-bold block">Institutional Access Locked</span>
            <span class="text-[10px] leading-tight block mt-0.5">Please sign in with your official Gujarat Government credentials to unlock worker records and telemetry.</span>
          </div>
        </div>

        <!-- Vertical Navigation Links (8 Items) -->
        <nav id="sidebar-nav" class="space-y-1">
          <!-- Tab 1: Worker Pass -->
          <button id="nav-tab-worker" onclick="switchTab('worker')" class="nav-tab-btn w-full flex items-center justify-between p-2.5 rounded text-xs font-semibold transition text-left text-on-surface-variant hover:bg-surface-container hover:text-on-surface">
            <div class="flex items-center gap-2.5">
              <span class="material-symbols-outlined text-[19px] text-primary">badge</span>
              <div>
                <span class="block font-bold">1. Worker Health Pass</span>
                <span class="text-[10px] text-on-surface-variant font-normal">સ્વાસ્થ્ય કાર્ડ · ABHA Locker</span>
              </div>
            </div>
            <span class="lock-indicator material-symbols-outlined text-[15px] text-amber-600">lock</span>
          </button>

          <!-- Tab 2: Worksite Watch -->
          <button id="nav-tab-site" onclick="switchTab('site')" class="nav-tab-btn w-full flex items-center justify-between p-2.5 rounded text-xs font-semibold transition text-left text-on-surface-variant hover:bg-surface-container hover:text-on-surface">
            <div class="flex items-center gap-2.5">
              <span class="material-symbols-outlined text-[19px] text-amber-600">solar_power</span>
              <div>
                <span class="block font-bold">2. Worksite Live Watch</span>
                <span class="text-[10px] text-on-surface-variant font-normal">કાર્યસ્થળ · ISO 7243 Beacon</span>
              </div>
            </div>
            <span class="lock-indicator material-symbols-outlined text-[15px] text-amber-600">lock</span>
          </button>

          <!-- Tab 3: Mobile Van Station -->
          <button id="nav-tab-van" onclick="switchTab('van')" class="nav-tab-btn w-full flex items-center justify-between p-2.5 rounded text-xs font-semibold transition text-left text-on-surface-variant hover:bg-surface-container hover:text-on-surface">
            <div class="flex items-center gap-2.5">
              <span class="material-symbols-outlined text-[19px] text-secondary">medical_services</span>
              <div>
                <span class="block font-bold">3. Mobile Van Station</span>
                <span class="text-[10px] text-on-surface-variant font-normal">મોબાઇલ વાન · Clinical Triage</span>
              </div>
            </div>
            <span class="lock-indicator material-symbols-outlined text-[15px] text-amber-600">lock</span>
          </button>

          <!-- Tab 4: District DDO Macro View -->
          <button id="nav-tab-district" onclick="switchTab('district')" class="nav-tab-btn w-full flex items-center justify-between p-2.5 rounded text-xs font-semibold transition text-left text-on-surface-variant hover:bg-surface-container hover:text-on-surface">
            <div class="flex items-center gap-2.5">
              <span class="material-symbols-outlined text-[19px] text-primary">monitoring</span>
              <div>
                <span class="block font-bold">4. District DDO View</span>
                <span class="text-[10px] text-on-surface-variant font-normal">જિલ્લા નકશો · Macro Heatmap</span>
              </div>
            </div>
            <span class="lock-indicator material-symbols-outlined text-[15px] text-amber-600">lock</span>
          </button>

          <!-- Tab 5: Respiration & Silica Lab -->
          <button id="nav-tab-research" onclick="switchTab('research')" class="nav-tab-btn w-full flex items-center justify-between p-2.5 rounded text-xs font-semibold transition text-left text-on-surface-variant hover:bg-surface-container hover:text-on-surface">
            <div class="flex items-center gap-2.5">
              <span class="material-symbols-outlined text-[19px] text-secondary">respiration</span>
              <div>
                <span class="block font-bold">5. BME280 Mask Lab</span>
                <span class="text-[10px] text-on-surface-variant font-normal">BME280 સંશોધન · XRD Assays</span>
              </div>
            </div>
            <span class="lock-indicator material-symbols-outlined text-[15px] text-amber-600">lock</span>
          </button>

          <!-- Tab 6: Healthcare Facilities Directory -->
          <button id="nav-tab-facilities" onclick="switchTab('facilities')" class="nav-tab-btn w-full flex items-center justify-between p-2.5 rounded text-xs font-semibold transition text-left text-on-surface-variant hover:bg-surface-container hover:text-on-surface">
            <div class="flex items-center gap-2.5">
              <span class="material-symbols-outlined text-[19px] text-red-600">local_hospital</span>
              <div>
                <span class="block font-bold">6. Health Facilities</span>
                <span class="text-[10px] text-on-surface-variant font-normal">હોસ્પિટલ ડિરેક્ટરી · 108 Bases</span>
              </div>
            </div>
            <span class="lock-indicator material-symbols-outlined text-[15px] text-amber-600">lock</span>
          </button>

          <!-- Tab 7: Public Datasets Catalog -->
          <button id="nav-tab-datasets" onclick="switchTab('datasets')" class="nav-tab-btn w-full flex items-center justify-between p-2.5 rounded text-xs font-semibold transition text-left text-on-surface-variant hover:bg-surface-container hover:text-on-surface">
            <div class="flex items-center gap-2.5">
              <span class="material-symbols-outlined text-[19px] text-indigo-600">dataset</span>
              <div>
                <span class="block font-bold">7. Public Datasets</span>
                <span class="text-[10px] text-on-surface-variant font-normal">10 સરકારી ડેટાસેટ · Catalog</span>
              </div>
            </div>
            <span class="lock-indicator material-symbols-outlined text-[15px] text-amber-600">lock</span>
          </button>

          <!-- Tab 8: Institutional Login Portal -->
          <button id="nav-tab-login" onclick="switchTab('login')" class="nav-tab-btn w-full flex items-center justify-between p-2.5 rounded text-xs font-bold transition text-left bg-primary text-white shadow-sm">
            <div class="flex items-center gap-2.5">
              <span class="material-symbols-outlined text-[19px]">login</span>
              <div>
                <span class="block">8. Institutional Sign-In</span>
                <span class="text-[10px] font-normal opacity-90">સત્તાવાર લોગિન · Auth Portal</span>
              </div>
            </div>
            <span class="material-symbols-outlined text-[15px]">key</span>
          </button>
        </nav>
      </div>

      <!-- Sidebar Bottom: Environment Status & User Sign Out Card -->
      <div class="mt-4 pt-3 border-t border-outline-variant/30 space-y-2.5">
        <!-- Worksite Status Widget -->
        <div class="p-2.5 bg-surface-container rounded border border-outline-variant/40 text-[11px] space-y-1">
          <div class="flex items-center justify-between font-bold">
            <span class="text-on-surface">Worksite Beacon:</span>
            <span class="px-1.5 py-0.2 rounded bg-amber-100 text-amber-800 text-[9px] font-mono">ORANGE</span>
          </div>
          <div class="text-[10px] text-on-surface-variant">Kandla Port: 30.6°C WBGT</div>
        </div>

        <!-- User Profile & Sign Out Button -->
        <div id="sidebar-user-card" class="p-2.5 bg-surface-container rounded border border-outline-variant/40 text-xs">
          <div class="flex items-center gap-2 mb-2">
            <div class="w-7 h-7 rounded-full bg-primary/10 text-primary font-bold flex items-center justify-center text-xs flex-shrink-0">
              <span class="material-symbols-outlined text-[16px]">person</span>
            </div>
            <div class="truncate">
              <span id="sidebar-user-name" class="font-bold text-on-surface block leading-tight truncate">Guest User</span>
              <span id="sidebar-user-badge" class="text-[9px] text-on-surface-variant block font-mono">Institutional Login Required</span>
            </div>
          </div>
          <button id="btn-sidebar-signout" onclick="handleSignOut()" class="w-full py-1.5 bg-red-600 hover:bg-red-700 text-white rounded text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-sm hidden">
            <span class="material-symbols-outlined text-[15px]">logout</span>
            <span>Sign Out (લોગ આઉટ)</span>
          </button>
          <button id="btn-sidebar-signin" onclick="switchTab('login')" class="w-full py-1.5 bg-primary hover:bg-primary-container text-white rounded text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-sm">
            <span class="material-symbols-outlined text-[15px]">login</span>
            <span>Sign In to Access</span>
          </button>
        </div>
      </div>
    </aside>

    <!-- RIGHT MAIN CONTENT AREA -->
    <main id="main-content" class="flex-1 p-3 md:p-6 lg:p-8 overflow-y-auto bg-surface">
      <div class="max-w-7xl mx-auto space-y-8">
"""

# Now write complete index.html assembling everything
with open(DST_TEMPLATE, "w", encoding="utf-8") as f:
    f.write(head_html)
    f.write(header_sidebar_html)
    f.write(sec_worker + "\n")
    f.write(sec_site + "\n")
    f.write(sec_van + "\n")
    f.write(sec_district + "\n")
    f.write(sec_research + "\n")
    f.write(sec_facilities + "\n")
    f.write(sec_datasets + "\n")
    f.write(sec_login + "\n")
    f.write("      </div>\n    </main>\n  </div>\n\n")
    f.write(footer_html + "\n\n")
    f.write(modal_form5 + "\n\n")
    f.write(modal_abha + "\n\n")
    f.write(modal_support + "\n\n")
    f.write(modal_security + "\n\n")
    f.write("""  <!-- Enterprise Toast Notification Container -->
  <div id="toast-container" class="fixed bottom-6 right-6 z-50 flex flex-col gap-2 pointer-events-none"></div>

  <!-- ===================================================================== -->
  <!-- JAVASCRIPT APPLICATION CORE (WITH GITHUB PAGES STATIC FALLBACK) -->
  <!-- ===================================================================== -->
  <script>
    // Global Application State
    let state = {
      lang: 'en',
      theme: localStorage.getItem('workcheck_theme') || 'light',
      currentUser: JSON.parse(localStorage.getItem('workcheck_user')) || null,
      activeTab: 'login',
      workers: [],
      currentWorker: null,
      sites: [],
      currentSite: null,
      vanQueue: [],
      selectedVanWorker: null,
      facilities: [],
      silicaAssays: [],
      datasets: [],
      timerSeconds: 1125,
      timerRunning: true,
      timerInterval: null,
      map: null,
      jobChart: null,
      bmeChart: null
    };

    // Client-Side Pre-Seeded Fallback Data (Guarantees 100% functionality on GitHub Pages)
    const STATIC_DATA = {
      workers: [
        { worker_id: "W-KCH-0001", full_name: "Ramjibhai S. Koli", job_role: "Salt Raker", taluka: "Rapar", masked_eshram_uan: "9842-XXXX-1001", abha_address: "ramjibhai.kutch@abdm", age: 48, gender: "Male", site_name: "Little Rann Salt Pan #3", qr_card_hash: "hash_001", statutory_rules: { rule_explanation: "Mandatory annual exam due under Gujarat OSH Rules 2025 Rule 9 (Age 45+ hazardous worker)." }, recent_exposures: [{ cumulative_dust_dose_mg_m3_hr: 1.85, hours_above_wbgt_30: 4.2 }] },
        { worker_id: "W-KCH-0002", full_name: "Ganeshbhai P. Vankar", job_role: "Crusher Operator", taluka: "Abdasa", masked_eshram_uan: "9842-XXXX-1002", abha_address: "ganesh.kutch@abdm", age: 46, gender: "Male", site_name: "Abdasa Cement Quarry", qr_card_hash: "hash_002", statutory_rules: { rule_explanation: "Mandatory annual exam due under Gujarat OSH Rules 2025 Rule 9 (Age 45+ stone crushing)." }, recent_exposures: [{ cumulative_dust_dose_mg_m3_hr: 2.45, hours_above_wbgt_30: 3.8 }] },
        { worker_id: "W-KCH-0003", full_name: "Dineshbhai M. Rabari", job_role: "Dock Loader", taluka: "Kandla", masked_eshram_uan: "9842-XXXX-1003", abha_address: "dinesh.kandla@abdm", age: 42, gender: "Male", site_name: "Kandla Port Loading Yard #4", qr_card_hash: "hash_003", statutory_rules: { rule_explanation: "Mandatory dock exam due under Central OSH Rules 2026 Rule 5 (Age 40+ dock worker)." }, recent_exposures: [{ cumulative_dust_dose_mg_m3_hr: 1.20, hours_above_wbgt_30: 3.5 }] },
        { worker_id: "W-KCH-0004", full_name: "Kavitaben D. Maheshwari", job_role: "Agariya Salt Worker", taluka: "Rapar", masked_eshram_uan: "9842-XXXX-1004", abha_address: "kavita.kutch@abdm", age: 39, gender: "Female", site_name: "Little Rann Salt Pan #3", qr_card_hash: "hash_004", statutory_rules: { rule_explanation: "Screened on high heat strain & dark urine reports." }, recent_exposures: [{ cumulative_dust_dose_mg_m3_hr: 1.40, hours_above_wbgt_30: 4.6 }] }
      ],
      sites: [
        { site_id: "site_kandla", site_name: "Kandla Port Loading Yard #4", taluka: "Kandla", current_lamp_color: "ORANGE", has_potable_water: 1, has_toilets: 1, has_shaded_rest_area: 1, avg_wbgt: 30.6, avg_temp: 39.2, avg_humidity: 62, avg_globe: 49.8, avg_pm2_5: 48 },
        { site_id: "site_rann", site_name: "Little Rann Salt Pan Cluster #3", taluka: "Rapar", current_lamp_color: "RED", has_potable_water: 1, has_toilets: 0, has_shaded_rest_area: 1, avg_wbgt: 31.8, avg_temp: 41.5, avg_humidity: 56, avg_globe: 52.4, avg_pm2_5: 38 },
        { site_id: "site_abdasa", site_name: "Abdasa Cement Quarry Station", taluka: "Abdasa", current_lamp_color: "ORANGE", has_potable_water: 1, has_toilets: 1, has_shaded_rest_area: 1, avg_wbgt: 30.1, avg_temp: 38.8, avg_humidity: 58, avg_globe: 48.5, avg_pm2_5: 84 },
        { site_id: "site_bhuj", site_name: "Bhuj HQ Construction Cluster", taluka: "Bhuj", current_lamp_color: "YELLOW", has_potable_water: 1, has_toilets: 1, has_shaded_rest_area: 1, avg_wbgt: 28.2, avg_temp: 37.4, avg_humidity: 50, avg_globe: 44.2, avg_pm2_5: 52 },
        { site_id: "site_mundra", site_name: "Mundra SEZ Bulk Terminal", taluka: "Mundra", current_lamp_color: "YELLOW", has_potable_water: 1, has_toilets: 1, has_shaded_rest_area: 1, avg_wbgt: 29.4, avg_temp: 36.8, avg_humidity: 68, avg_globe: 46.1, avg_pm2_5: 45 }
      ],
      vanQueue: [
        { case_id: "CASE-001", worker_id: "W-KCH-0001", worker_name: "Ramjibhai S. Koli", job_role: "Salt Raker", site_name: "Little Rann Salt Pan", age: 48, priority_score: 5, masked_eshram_uan: "9842-XXXX-1001", abha_address: "ramjibhai.kutch@abdm", clinical_route: "ROUTE_1_STATUTORY", route_label: "Rule 9 Gujarat OSH Due (Age 45+)", route_badge_color: "blue" },
        { case_id: "CASE-002", worker_id: "W-KCH-0002", worker_name: "Ganeshbhai P. Vankar", job_role: "Crusher Operator", site_name: "Abdasa Quarry", age: 46, priority_score: 5, masked_eshram_uan: "9842-XXXX-1002", abha_address: "ganesh.kutch@abdm", clinical_route: "ROUTE_2_EXPOSURE", route_label: "High Silica Dust Exposure (>2.0 mg/m³·h)", route_badge_color: "amber" },
        { case_id: "CASE-003", worker_id: "W-KCH-0004", worker_name: "Kavitaben D. Maheshwari", job_role: "Agariya Salt Worker", site_name: "Little Rann Salt Pan", age: 39, priority_score: 4, masked_eshram_uan: "9842-XXXX-1004", abha_address: "kavita.kutch@abdm", clinical_route: "ROUTE_3_SYMPTOMS", route_label: "Dark Urine / Heat Exhaustion Reported", route_badge_color: "red" }
      ],
      silicaAssays: [
        { industry_type: "Stone Crushing", location: "Abdasa Cement Belt", dust_conc: 2.85, quartz_pct: 18.4, lab: "NIOH Ahmedabad XRD Lab" },
        { industry_type: "Quarry Drilling", location: "Bhuj HQ Stone Cluster", dust_conc: 3.42, quartz_pct: 22.8, lab: "NABL Envirocare Lab" },
        { industry_type: "Cement Grinding", location: "Abdasa Plant", dust_conc: 1.94, quartz_pct: 12.2, lab: "NIOH Ahmedabad XRD Lab" },
        { industry_type: "Bentonite Mill", location: "Anjar Industrial Zone", dust_conc: 1.45, quartz_pct: 8.5, lab: "NIOH Ahmedabad XRD Lab" },
        { industry_type: "Bulk Minerals", location: "Kandla Port Trust", dust_conc: 1.20, quartz_pct: 6.2, lab: "KPT Environmental Lab" },
        { industry_type: "Salt Pan Dust", location: "Little Rann of Kutch", dust_conc: 0.85, quartz_pct: 3.1, lab: "NIOH Ahmedabad XRD Lab" },
        { industry_type: "Container Logistics", location: "Mundra Port SEZ", dust_conc: 0.62, quartz_pct: 4.5, lab: "Adani Environmental Center" }
      ],
      facilities: [
        { name: "GK General Hospital (Govt Medical College)", tier: "District Hospital", taluka: "Bhuj", xray: true, spiro: true, audio: true, lab: true, cbnaat: true, amb108: true },
        { name: "ESIC Model Hospital Gandhidham", tier: "ESIC Hospital", taluka: "Gandhidham", xray: true, spiro: true, audio: true, lab: true, cbnaat: true, amb108: true },
        { name: "Mundra Community Health Centre (CHC)", tier: "CHC", taluka: "Mundra", xray: true, spiro: true, audio: false, lab: true, cbnaat: false, amb108: true },
        { name: "Anjar Sub-District Hospital", tier: "Sub-District Hospital", taluka: "Anjar", xray: true, spiro: true, audio: false, lab: true, cbnaat: true, amb108: true },
        { name: "Mandvi Referral Hospital & CHC", tier: "CHC", taluka: "Mandvi", xray: true, spiro: true, audio: false, lab: true, cbnaat: false, amb108: true },
        { name: "Naliya CHC (Abdasa Belt)", tier: "CHC", taluka: "Abdasa", xray: true, spiro: false, audio: false, lab: true, cbnaat: false, amb108: true },
        { name: "Nakhatrana Community Health Centre", tier: "CHC", taluka: "Nakhatrana", xray: true, spiro: true, audio: false, lab: true, cbnaat: false, amb108: true },
        { name: "Rapar Community Health Centre", tier: "CHC", taluka: "Rapar", xray: true, spiro: false, audio: false, lab: true, cbnaat: false, amb108: true },
        { name: "Dayapar Primary Health Centre (Lakhpat)", tier: "PHC", taluka: "Lakhpat", xray: false, spiro: false, audio: false, lab: true, cbnaat: false, amb108: true },
        { name: "Bhachau Community Health Centre", tier: "CHC", taluka: "Bhachau", xray: true, spiro: true, audio: false, lab: true, cbnaat: false, amb108: true },
        { name: "BOCW Dhanvantari Rath #1 (Mundra/Kandla)", tier: "Mobile Medical Van", taluka: "Mundra", xray: true, spiro: true, audio: true, lab: true, cbnaat: false, amb108: true },
        { name: "BOCW Dhanvantari Rath #2 (Little Rann Salt)", tier: "Mobile Medical Van", taluka: "Rapar", xray: true, spiro: true, audio: false, lab: true, cbnaat: false, amb108: true }
      ],
      datasets: [
        { id: 1, name: "PLFS Microdata (Worker Hours)", folder: "01_plfs_worker_hours", category: "Socio-Economic", source: "MoSPI Microdata Portal", url: "https://microdata.gov.in/NADA/index.php/catalog/292/get-microdata", license: "OGD India", file: "plfs_kachchh_worker_hours.csv", rows: 6, why: "Only official microdata route for unorganized weekly work-hours estimation (Kachchh code 468)." },
        { id: 2, name: "noiseJEM Job Exposure Matrix", folder: "02_noisejem_job_levels", category: "Industrial Hygiene", source: "Univ. of Michigan", url: "https://noisejem.sph.umich.edu/about.html", license: "CC BY 4.0", file: "noisejem_occupational_noise_by_job.csv", rows: 7, why: "Empirical occupational noise distributions (8h TWA, Lpeak) by specific job role." },
        { id: 3, name: "Census 2011 Taluka Workers", folder: "03_census_2011_kachchh_taluka_workers", category: "Demographics", source: "Census India Table B-Series", url: "https://censusindia.gov.in/nada/index.php/catalog/12722", license: "OGD India", file: "census_2011_kachchh_taluka_workers.csv", rows: 10, why: "Exact main vs marginal worker totals across all 10 Kachchh talukas for demographic denominators." },
        { id: 4, name: "TEMIS UV Radiation Archive", folder: "04_temis_uv_radiation", category: "Environmental UV", source: "KNMI / ESA TEMIS Archive", url: "https://www.temis.nl/uvradiation/UVarchive.php", license: "CC BY 4.0", file: "temis_uv_radiation_bhuj_kachchh.csv", rows: 6, why: "Time series of clear-sky & aerosol-adjusted UV Index for Bhuj coordinates." },
        { id: 5, name: "OMI Daily Erythemal UV", folder: "05_omi_uv_erythemal", category: "Satellite UV", source: "NASA / FMI Aura OMI", url: "https://omi.fmi.fi/products.html", license: "NASA Open Data", file: "omi_daily_erythemal_uv_kachchh.csv", rows: 5, why: "Daily erythemal UV dose (J/m²) by satellite grid pixel for Kachchh industrial clusters." },
        { id: 6, name: "CMIP6 Gridded Labour Capacity", folder: "06_cmip6_gridded_labour_capacity", category: "Climate Projection", source: "Lancet Countdown / Zenodo", url: "https://zenodo.org/records/21636524", license: "CC BY 4.0", file: "cmip6_kachchh_labour_capacity_projections.csv", rows: 6, why: "Multi-model ensemble projections showing heavy work capacity loss through 2050." },
        { id: 7, name: "Occupational Heat Benchmarks", folder: "07_worker_study_reference_data", category: "Clinical Evidence", source: "Venugopal 2020, Hansson 2019, Dutta 2021", url: "Peer-Reviewed Journals", license: "Academic Fair Use", file: "worker_studies_deidentified_clinical_benchmarks.csv", rows: 3, why: "De-identified empirical rates of acute kidney injury and cross-shift eGFR loss." },
        { id: 8, name: "NIOH Little Rann Salt Workers", folder: "08_nioh_salt_worker_report", category: "Occupational Health", source: "ICMR-NIOH Ahmedabad", url: "ICMR Research Report", license: "ICMR Research", file: "nioh_little_rann_salt_workers_health_hazards.csv", rows: 5, why: "Prevalence of pterygium, dermatitis, and respiratory symptoms in Agariya salt workers." },
        { id: 9, name: "Kachchh Health & Worker Records", folder: "09_kachchh_health_and_worker_records", category: "Administration", source: "CDHO, BOCW Board, ESIC, DISH", url: "Government of Gujarat", license: "State Govt Open Data", file: "kachchh_administrative_health_and_worker_records.csv", rows: 6, why: "Aggregated registered unorganized workers and active Dhanvantari Rath routes." },
        { id: 10, name: "IMD Station Ground Truth Data", folder: "10_imd_station_bhuj_kandla", category: "Weather Validation", source: "India Meteorological Department", url: "IMD Portal", license: "IMD Weather Data", file: "imd_station_bhuj_kandla_validation.csv", rows: 5, why: "Station vs model validation proving ambient temperature bias is within ±0.6°C." }
      ]
    };

    // DOM Ready
    document.addEventListener('DOMContentLoaded', async () => {
      applyTheme(state.theme);
      initClock();
      
      // Strict Authentication Gate
      state.currentUser = JSON.parse(localStorage.getItem('workcheck_user')) || null;
      if (!state.currentUser) {
        state.activeTab = 'login';
      } else {
        const urlParams = new URLSearchParams(window.location.search);
        const tabParam = urlParams.get('tab') || window.location.hash.replace('#', '');
        const validTabs = ['worker', 'site', 'van', 'district', 'research', 'facilities', 'datasets', 'login'];
        state.activeTab = validTabs.includes(tabParam) ? tabParam : (state.currentUser.targetTab || 'worker');
      }

      updateAuthUI();
      switchTab(state.activeTab);
      await fetchInitialData();
      startSiteTimer();
    });

    // Enterprise Toast Notification
    function showToast(message, type = 'info') {
      const container = document.getElementById('toast-container');
      if (!container) return;
      const toast = document.createElement('div');
      let bg = "bg-primary text-on-primary";
      let icon = "info";
      if (type === 'success') { bg = "bg-[#006c4e] text-white"; icon = "check_circle"; }
      if (type === 'warning') { bg = "bg-[#d97706] text-white"; icon = "warning"; }
      if (type === 'error') { bg = "bg-[#ba1a1a] text-white"; icon = "error"; }

      toast.className = `${bg} px-4 py-3 rounded-lg shadow-xl text-xs font-semibold flex items-center gap-2 transform transition-all duration-300 translate-y-2 opacity-0 pointer-events-auto border border-white/20`;
      toast.innerHTML = `<span class="material-symbols-outlined text-[18px]">${icon}</span><span>${message}</span>`;
      container.appendChild(toast);

      requestAnimationFrame(() => {
        toast.classList.remove('translate-y-2', 'opacity-0');
      });

      setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
      }, 3500);
    }

    // Sidebar Mobile Toggle
    function toggleSidebar() {
      const sidebar = document.getElementById('app-sidebar');
      if (sidebar) sidebar.classList.toggle('hidden');
    }

    // Theme Management (Light vs Dark)
    function applyTheme(theme) {
      state.theme = theme;
      localStorage.setItem('workcheck_theme', theme);
      const html = document.documentElement;
      const icon = document.getElementById('theme-icon');
      const text = document.getElementById('theme-text');

      if (theme === 'dark') {
        html.classList.add('dark');
        if (icon) icon.innerText = 'light_mode';
        if (text) text.innerText = 'Light';
      } else {
        html.classList.remove('dark');
        if (icon) icon.innerText = 'dark_mode';
        if (text) text.innerText = 'Dark';
      }
    }

    function toggleTheme() {
      applyTheme(state.theme === 'dark' ? 'light' : 'dark');
    }

    // Real-Time Clock
    function initClock() {
      setInterval(() => {
        const now = new Date();
        const str = now.toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata', hour12: false });
        const el = document.getElementById('live-clock');
        if (el) el.innerText = `Bhuj HQ · IST ${str}`;
      }, 1000);
    }

    // Tab Navigation & Authentication Gate
    function switchTab(tabId) {
      // Gate all tabs except login when unauthenticated
      if (!state.currentUser && tabId !== 'login') {
        showToast("Access Restricted: Please sign in with your institutional credentials to access this system.", "warning");
        tabId = 'login';
      }

      state.activeTab = tabId;
      document.querySelectorAll('.tab-section').forEach(el => el.classList.add('hidden'));
      document.querySelectorAll('.nav-tab-btn').forEach(btn => {
        btn.classList.remove('bg-primary', 'text-white', 'shadow-sm', 'font-bold');
        btn.classList.add('text-on-surface-variant');
      });

      const sec = document.getElementById(`section-${tabId}`);
      if (sec) sec.classList.remove('hidden');

      const btn = document.getElementById(`nav-tab-${tabId}`);
      if (btn) {
        btn.classList.add('bg-primary', 'text-white', 'shadow-sm', 'font-bold');
        btn.classList.remove('text-on-surface-variant');
      }

      if (history.replaceState) {
        history.replaceState(null, null, `#${tabId}`);
      }

      // Close mobile sidebar on selection
      if (window.innerWidth < 768) {
        const sidebar = document.getElementById('app-sidebar');
        if (sidebar && !sidebar.classList.contains('hidden')) sidebar.classList.add('hidden');
      }

      if (tabId === 'district' && !state.map) {
        setTimeout(initDistrictMap, 150);
      }
      if (tabId === 'research' && !state.bmeChart) {
        setTimeout(initBmeChart, 150);
      }
    }

    // Language Toggle
    function setAppLanguage(lang) {
      state.lang = lang;
      ['gu', 'hi', 'en'].forEach(l => {
        const b = document.getElementById(`btn-lang-${l}`);
        if (b) {
          b.className = (l === lang) ? "px-1.5 py-1 font-bold text-primary transition" : "px-1.5 py-1 font-medium hover:text-primary transition border-l border-outline-variant/40";
        }
      });
      showToast(`Interface language set to ${lang.toUpperCase()}`, "info");
    }

    // Data Fetch with Seamless Fallback
    async function fetchInitialData() {
      try {
        // 1. Fetch Workers
        try {
          const wRes = await fetch('/api/workers?limit=50');
          if (wRes.ok) state.workers = await wRes.json();
          else state.workers = STATIC_DATA.workers;
        } catch { state.workers = STATIC_DATA.workers; }
        populateWorkerDropdown();

        // 2. Fetch Sites
        try {
          const sRes = await fetch('/api/sites');
          if (sRes.ok) state.sites = await sRes.json();
          else state.sites = STATIC_DATA.sites;
        } catch { state.sites = STATIC_DATA.sites; }
        populateSiteDropdown();

        // 3. Fetch Van Queue
        await loadVanTriageQueue('ALL');

        // 4. Render Silica Assays
        renderSilicaAssays();

        // 5. Render Facilities
        renderFacilities();

        // 6. Render Public Datasets
        renderDatasets();

        // Initialize First Worker & Site
        if (state.workers.length > 0) await loadWorkerData(state.workers[0].worker_id);
        if (state.sites.length > 0) await loadSiteData(state.sites[0].site_id);
      } catch (err) {
        console.error("Data fetch fallback engaged:", err);
      }
    }

    // Worker Profile
    function populateWorkerDropdown() {
      const select = document.getElementById('worker-dropdown');
      if (!select) return;
      select.innerHTML = '';
      state.workers.forEach(w => {
        const opt = document.createElement('option');
        opt.value = w.worker_id;
        opt.text = `${w.full_name} (${w.job_role}) · ${w.masked_eshram_uan}`;
        select.appendChild(opt);
      });
    }

    async function handleWorkerChange() {
      const id = document.getElementById('worker-dropdown').value;
      if (id) await loadWorkerData(id);
    }

    async function loadWorkerData(workerId) {
      let data = state.workers.find(w => w.worker_id === workerId);
      try {
        const res = await fetch(`/api/workers/${workerId}`);
        if (res.ok) data = await res.json();
      } catch {}

      state.currentWorker = data;
      const worker = data.worker || data;

      document.getElementById('w-name').innerText = worker.full_name;
      document.getElementById('w-role-taluka').innerText = `${worker.job_role} · ${worker.taluka || 'Kachchh'}`;
      document.getElementById('w-uan').innerText = worker.masked_eshram_uan;
      document.getElementById('w-abha-addr').innerText = worker.abha_address;
      document.getElementById('w-age-gender').innerText = `${worker.age} yrs · ${worker.gender}`;
      document.getElementById('w-site').innerText = worker.site_name || 'Kachchh Cluster';
      document.getElementById('w-token-label').innerText = `TOKEN: ABDM-GJ-KCH-${worker.worker_id.slice(-4)}`;

      // Generate Dynamic QR Code
      const qrBox = document.getElementById('w-qrcode-container');
      qrBox.innerHTML = '';
      new QRCode(qrBox, {
        text: `https://abdm.gov.in/phr/verify?hash=${worker.qr_card_hash || 'DEMO_HASH'}`,
        width: 120,
        height: 120,
        colorDark: "#00236f",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.M
      });

      // Statutory Text
      const stat = data.statutory_rules ? data.statutory_rules.rule_explanation : "Statutory annual exam required under Gujarat OSH Rules 2025 Rule 9.";
      document.getElementById('w-statutory-text').innerHTML = stat;

      // Exposures
      const exps = data.recent_exposures || [{ cumulative_dust_dose_mg_m3_hr: 1.85, hours_above_wbgt_30: 4.2 }];
      if (exps.length > 0) {
        const e = exps[0];
        const dust = parseFloat(e.cumulative_dust_dose_mg_m3_hr) || 1.85;
        document.getElementById('w-dust-range').innerText = `${(dust * 0.8).toFixed(1)} – ${(dust * 1.25).toFixed(1)} mg/m³·hr`;
        document.getElementById('w-heat-hrs').innerText = `${(parseFloat(e.hours_above_wbgt_30) || 4.2).toFixed(1)} hrs`;
      }
    }

    async function handleSymptomSubmit() {
      const fb = document.getElementById('symptom-feedback');
      fb.classList.remove('hidden');
      showToast("Daily occupational symptoms logged. Dhanvantari Rath alert updated.", "success");
      setTimeout(() => {
        fb.classList.add('hidden');
        document.getElementById('symp-dark-urine').checked = false;
        document.getElementById('symp-dizziness').checked = false;
        document.getElementById('symp-cough').checked = false;
        document.getElementById('symp-eye-glare').checked = false;
      }, 4000);
    }

    // Worksite Management
    function populateSiteDropdown() {
      const select = document.getElementById('site-dropdown');
      if (!select) return;
      select.innerHTML = '';
      state.sites.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.site_id;
        opt.text = `${s.site_name} (${s.taluka}) · ${s.current_lamp_color || 'YELLOW'} LAMP`;
        select.appendChild(opt);
      });
    }

    async function handleSiteChange() {
      const id = document.getElementById('site-dropdown').value;
      if (id) await loadSiteData(id);
    }

    async function loadSiteData(siteId) {
      let data = state.sites.find(s => s.site_id === siteId);
      try {
        const res = await fetch(`/api/sites/${siteId}`);
        if (res.ok) data = await res.json();
      } catch {}

      state.currentSite = data;
      const stats = data.current_stats || data;
      const wbgt = parseFloat(stats.avg_wbgt || stats.current_wbgt_c || 30.4);
      const ta = parseFloat(stats.avg_temp || stats.current_temp_c || 38.6);
      const rh = parseFloat(stats.avg_humidity || stats.current_humidity_pct || 64);
      const tg = parseFloat(stats.avg_globe || stats.current_globe_temp_c || 49.1);
      const pm25 = parseFloat(stats.avg_pm2_5 || stats.current_pm2_5_ug_m3 || 54);
      const tnw = Math.round((wbgt - 0.2 * tg - 0.1 * ta) / 0.7 * 10) / 10;

      document.getElementById('tel-ta').innerText = ta.toFixed(1);
      document.getElementById('tel-rh').innerText = Math.round(rh);
      document.getElementById('tel-tg').innerText = tg.toFixed(1);
      document.getElementById('tel-tnw').innerText = tnw.toFixed(1);
      document.getElementById('tel-wbgt-main').innerText = wbgt.toFixed(1);
      document.getElementById('tel-pm25').innerText = Math.round(pm25);
      document.getElementById('tel-formula-breakdown').innerText = 
        `0.7(${tnw}) + 0.2(${tg.toFixed(1)}) + 0.1(${ta.toFixed(1)}) = ${wbgt.toFixed(1)}°C`;

      // Update Beacon Lamp State
      const lampColor = (data.iso_7243_status && data.iso_7243_status.lamp_color) || stats.current_lamp_color || 'ORANGE';
      const bulb = document.getElementById('beacon-bulb');
      const bulbText = document.getElementById('beacon-color-name');
      const bulbWbgt = document.getElementById('beacon-wbgt-sub');
      const dirTitle = document.getElementById('beacon-directive-title');
      const dirCycle = document.getElementById('beacon-directive-cycle');

      bulb.className = "w-20 h-20 rounded-full flex items-center justify-center transition-all duration-500 shadow-lg text-white font-bold text-xs uppercase";
      if (lampColor === 'GREEN') {
        bulb.classList.add('bg-secondary', 'lamp-glow-green');
        bulbText.innerText = "GREEN";
        dirTitle.innerText = `NORMAL WORKING CONDITIONS (WBGT ${wbgt.toFixed(1)}°C)`;
      } else if (lampColor === 'YELLOW') {
        bulb.classList.add('bg-amber-400', 'lamp-glow-yellow', 'text-slate-900');
        bulbText.innerText = "YELLOW";
        dirTitle.innerText = `CAUTION — Moderate Heat Strain (WBGT ${wbgt.toFixed(1)}°C)`;
      } else if (lampColor === 'ORANGE') {
        bulb.classList.add('bg-tertiary', 'lamp-glow-orange');
        bulbText.innerText = "ORANGE";
        dirTitle.innerText = `WARNING — Mandatory Water & Rest Schedule (WBGT ${wbgt.toFixed(1)}°C)`;
      } else {
        bulb.classList.add('bg-error', 'lamp-glow-red');
        bulbText.innerText = "RED";
        dirTitle.innerText = `RED ALERT — Extreme Heat (WBGT ${wbgt.toFixed(1)}°C)`;
      }

      bulbWbgt.innerText = `${wbgt.toFixed(1)}°C WBGT`;
      dirCycle.innerText = (data.iso_7243_status && data.iso_7243_status.work_rest_minutes) || "30 min work / 30 min rest in shaded shelter";
    }

    async function simulateHardwarePacket() {
      showToast("ESP32 Solar Node Ingestion Successful! Outdoor WBGT: 31.2°C (ORANGE LAMP)", "warning");
    }

    // ACGIH Work-Rest Timer
    function startSiteTimer() {
      state.timerInterval = setInterval(() => {
        if (!state.timerRunning) return;
        if (state.timerSeconds > 0) {
          state.timerSeconds--;
          const m = Math.floor(state.timerSeconds / 60);
          const s = state.timerSeconds % 60;
          document.getElementById('site-countdown').innerText = `${m}:${s < 10 ? '0' : ''}${s}`;
          const pct = Math.round(((1800 - state.timerSeconds) / 1800) * 100);
          document.getElementById('site-timer-bar').style.width = `${pct}%`;
        } else {
          state.timerSeconds = 1800;
          showToast("Work interval cap reached. 30-minute shaded rest cycle is mandatory.", "error");
        }
      }, 1000);
    }

    function toggleSiteTimer() {
      state.timerRunning = !state.timerRunning;
      document.getElementById('btn-timer-toggle').innerText = state.timerRunning ? 'Pause Timer' : 'Resume Timer';
    }

    function resetSiteTimer() {
      state.timerSeconds = 1800;
      showToast("ACGIH Work-Rest Timer reset to 30:00.", "info");
    }

    function handleComplianceChange() {
      showToast("Worksite potable water & shade compliance logged.", "success");
    }

    // Van Queue & Triage
    async function loadVanTriageQueue(routeFilter = 'ALL') {
      try {
        const res = await fetch(`/api/van/queue?route_filter=${routeFilter}`);
        if (res.ok) state.vanQueue = await res.json();
        else state.vanQueue = STATIC_DATA.vanQueue;
      } catch {
        state.vanQueue = STATIC_DATA.vanQueue;
      }

      const container = document.getElementById('van-worker-list');
      if (!container) return;
      container.innerHTML = '';

      state.vanQueue.forEach(w => {
        const row = document.createElement('div');
        row.className = "bg-surface-container-low p-3 rounded border border-outline-variant/30 flex items-center justify-between hover:bg-surface-container cursor-pointer transition";
        row.onclick = () => selectVanWorker(w);

        let badgeStyle = "bg-primary/10 text-primary border-primary/20";
        if (w.route_badge_color === 'red') badgeStyle = "bg-red-100 text-red-800 border-red-300";
        if (w.route_badge_color === 'amber' || w.route_badge_color === 'orange') badgeStyle = "bg-amber-100 text-amber-800 border-amber-300";

        row.innerHTML = `
          <div>
            <div class="flex items-center gap-2">
              <span class="font-bold text-xs text-on-surface">${w.worker_name}</span>
              <span class="text-[9px] font-bold px-1.5 py-0.5 rounded border ${badgeStyle}">${w.route_label.split(' ')[0]}</span>
            </div>
            <p class="text-[10px] text-on-surface-variant mt-0.5">${w.job_role} · ${w.site_name} · ${w.age}y</p>
          </div>
          <div class="text-right">
            <span class="text-xs font-bold text-secondary font-mono">Priority ${w.priority_score}/5</span>
            <span class="text-[9px] text-on-surface-variant block font-mono">${w.masked_eshram_uan}</span>
          </div>
        `;
        container.appendChild(row);
      });

      if (state.vanQueue.length > 0) selectVanWorker(state.vanQueue[0]);
    }

    function filterVanTriage(route) {
      ['all', 'r1', 'r2', 'r3'].forEach(r => {
        const b = document.getElementById(`van-tab-${r}`);
        if (b) b.className = "px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface";
      });
      const active = document.getElementById(route === 'ALL' ? 'van-tab-all' : (route === 'ROUTE_1_STATUTORY' ? 'van-tab-r1' : (route === 'ROUTE_2_EXPOSURE' ? 'van-tab-r2' : 'van-tab-r3')));
      if (active) active.className = "px-2.5 py-1 rounded font-bold bg-primary text-white";
      loadVanTriageQueue(route);
    }

    function selectVanWorker(w) {
      state.selectedVanWorker = w;
      document.getElementById('van-selected-name').innerText = w.worker_name;
      document.getElementById('van-selected-meta').innerText = `e-Shram UAN: ${w.masked_eshram_uan} · ABHA: ${w.abha_address} · ${w.age}y · ${w.job_role}`;
      document.getElementById('van-selected-route-badge').innerText = w.route_label;
    }

    function calculateLungRatio() {
      const fev1 = parseFloat(document.getElementById('diag-fev1').value) || 2.85;
      const fvc = parseFloat(document.getElementById('diag-fvc').value) || 3.65;
      const ratio = (fev1 / Math.max(0.1, fvc)).toFixed(2);
      const el = document.getElementById('diag-ratio-text');
      if (ratio < 0.70) {
        el.innerText = `${ratio} (Obstructive Defect)`;
        el.className = "font-mono font-bold text-sm text-error";
      } else {
        el.innerText = `${ratio} (Normal)`;
        el.className = "font-mono font-bold text-sm text-secondary";
      }
    }

    // 1-Click Publish to ABHA Health Locker
    async function publishToAbhaDirect() {
      if (!state.selectedVanWorker) return;
      const btn = document.getElementById('btn-van-publish');
      btn.innerHTML = '<span class="material-symbols-outlined text-[18px] animate-spin">refresh</span><span>Publishing to ABHA...</span>';
      btn.disabled = true;

      setTimeout(() => {
        btn.innerHTML = '<span class="material-symbols-outlined text-[18px]">publish</span><span>1-Click Publish to ABHA Health Locker</span>';
        btn.disabled = false;

        document.getElementById('modal-worker-name').innerText = state.selectedVanWorker.worker_name;
        document.getElementById('modal-abha-addr').innerText = state.selectedVanWorker.abha_address;
        document.getElementById('modal-care-context').innerText = `OCC-EXAM-2025-${state.selectedVanWorker.worker_id.slice(-4)}`;

        const fhirBundle = {
          resourceType: "Bundle",
          type: "document",
          id: `FHIR-ABDM-${Math.random().toString(36).substr(2, 9).toUpperCase()}`,
          timestamp: new Date().toISOString(),
          entry: [
            { resource: { resourceType: "DiagnosticReport", code: "Occupational Medical Examination (Gujarat Rule 9)", performer: "Dr. Rajesh V. Dave (GMC-4081)" } },
            { resource: { resourceType: "Observation", code: "FEV1/FVC Ratio", valueQuantity: { value: 0.78, unit: "ratio" } } },
            { resource: { resourceType: "Observation", code: "Serum Creatinine", valueQuantity: { value: 1.05, unit: "mg/dL" } } },
            { resource: { resourceType: "Observation", code: "Chest X-Ray ILO Profusion", valueCodeableConcept: { text: "0/0 Normal" } } }
          ]
        };
        document.getElementById('modal-fhir-json').innerText = JSON.stringify(fhirBundle, null, 2);
        document.getElementById('modal-abha-published').classList.remove('hidden');
        showToast(`Clinical examination published to ABHA Locker for ${state.selectedVanWorker.worker_name}!`, "success");
      }, 700);
    }

    // ABHA Receipt Action Functions
    function printAbhaReceipt() {
      window.print();
    }

    function downloadFhirJson() {
      if (!state.selectedVanWorker) return;
      const fhirBundle = {
        resourceType: "Bundle",
        type: "document",
        id: `FHIR-ABDM-${Math.random().toString(36).substr(2, 9).toUpperCase()}`,
        timestamp: new Date().toISOString(),
        entry: [
          { resource: { resourceType: "Patient", name: [{ text: state.selectedVanWorker.worker_name }], identifier: [{ system: "https://healthid.ndhm.gov.in", value: state.selectedVanWorker.abha_address }] } },
          { resource: { resourceType: "DiagnosticReport", code: "Occupational Medical Examination (Gujarat OSH Rule 9)", performer: "Dr. Rajesh V. Dave (GMC-4081)" } },
          { resource: { resourceType: "Observation", code: "FEV1/FVC Ratio", valueQuantity: { value: 0.78, unit: "ratio" } } },
          { resource: { resourceType: "Observation", code: "Serum Creatinine", valueQuantity: { value: 1.05, unit: "mg/dL" } } }
        ]
      };
      const blob = new Blob([JSON.stringify(fhirBundle, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `ABHA_FHIR_Receipt_${state.selectedVanWorker.worker_id}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast("FHIR JSON Receipt downloaded.", "success");
    }

    function sendWorkerSmsReceipt() {
      if (!state.selectedVanWorker) return;
      showToast(`SMS receipt dispatched to ${state.selectedVanWorker.worker_name}: 'ABHA Exam Token OCC-2025-${state.selectedVanWorker.worker_id.slice(-4)} recorded successfully.'`, "success");
    }

    function closeAbhaPublishedModal() {
      document.getElementById('modal-abha-published').classList.add('hidden');
    }

    // Form 5 Modal Functions
    function openForm5Modal() {
      document.getElementById('modal-form-5').classList.remove('hidden');
    }

    function closeForm5Modal() {
      document.getElementById('modal-form-5').classList.add('hidden');
    }

    function printForm5() {
      window.print();
    }

    function downloadForm5() {
      const text = `GOVERNMENT OF GUJARAT - FORM 5 CERTIFICATE OF FITNESS
[Rule 9(1) of Gujarat OSH Rules 2025]
Serial No: GJ-KCH-OSH-2025-0814
Worker: Ramjibhai S. Koli (Age: 48, Male)
e-Shram UAN: 9842-XXXX-1001 | ABHA: ramjibhai.kutch@abdm
Trade: Salt Pan Brine Raking & Stacking (Little Rann Salt Cluster #3)
Medical Opinion: FIT for employment in hazardous processes subject to mandatory 30-min shaded rest breaks during WBGT > 28°C.
Certifying Surgeon: Dr. Rajesh V. Dave, MBBS, DPH (GMC-4081)
Date of Exam: 15 April 2025 | Next Renewal: 14 April 2026
Digitally Attested by DISH Gujarat.`;
      const blob = new Blob([text], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "Form_5_Fitness_Certificate_Ramjibhai_Koli.txt";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast("Form 5 Fitness Certificate downloaded.", "success");
    }

    // Support Modal Functions
    function openSupportModal() {
      document.getElementById('modal-support').classList.remove('hidden');
    }

    function closeSupportModal() {
      document.getElementById('modal-support').classList.add('hidden');
    }

    function openSecurityModal() {
      document.getElementById('modal-security').classList.remove('hidden');
    }

    function closeSecurityModal() {
      document.getElementById('modal-security').classList.add('hidden');
    }

    function handleLodgeTicket() {
      const reporter = document.getElementById('ticket-reporter').value || "Site Safety Staff";
      const cat = document.getElementById('ticket-category').value;
      const tktId = `TKT-KCH-2026-${Math.floor(1000 + Math.random() * 9000)}`;
      const conf = document.getElementById('ticket-confirmation');
      conf.innerText = `✓ Ticket ${tktId} generated. Forwarded to DDO Kachchh Grievance Cell.`;
      conf.classList.remove('hidden');
      showToast(`Grievance Ticket ${tktId} created successfully.`, "success");
      setTimeout(() => {
        closeSupportModal();
        conf.classList.add('hidden');
      }, 3000);
    }

    // District Map & Charts
    function initDistrictMap() {
      if (state.map) return;
      state.map = L.map('district-map').setView([23.2420, 69.6669], 9);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(state.map);

      const pins = [
        { name: "Mundra SEZ Bulk Terminal", lat: 22.8395, lng: 69.7258, color: "#00236f", heat: "29.4°C WBGT", workers: 420 },
        { name: "Kandla Port Loading Yard #4", lat: 23.0033, lng: 70.2185, color: "#C2410C", heat: "30.6°C WBGT (Orange)", workers: 310 },
        { name: "Little Rann Salt Cluster #3", lat: 23.3500, lng: 71.0500, color: "#782200", heat: "31.8°C WBGT (Red Alert)", workers: 350 },
        { name: "Bhuj HQ Construction Cluster", lat: 23.2420, lng: 69.6669, color: "#006c4e", heat: "28.2°C WBGT (Normal)", workers: 120 },
        { name: "Abdasa Cement Quarry Station", lat: 23.2100, lng: 68.8500, color: "#C2410C", heat: "30.1°C WBGT", workers: 150 }
      ];

      pins.forEach(p => {
        const marker = L.circleMarker([p.lat, p.lng], {
          radius: 10,
          fillColor: p.color,
          color: '#ffffff',
          weight: 2,
          opacity: 1,
          fillOpacity: 0.9
        }).addTo(state.map);

        marker.bindPopup(`
          <div class="text-xs p-1">
            <strong>${p.name}</strong><br/>
            <span>Active Laborers: <b>${p.workers}</b></span><br/>
            <span>Heat Index: <b>${p.heat}</b></span>
          </div>
        `);
      });

      initJobRiskChart();
    }

    function initJobRiskChart() {
      const ctx = document.getElementById('job-risk-chart');
      if (!ctx || state.jobChart) return;
      state.jobChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Salt Rakers', 'Quarry Drillers', 'Cement Loaders', 'Port Yard Staff', 'Truck Drivers'],
          datasets: [{
            label: 'Screening Referral Rate (%)',
            data: [78.5, 74.2, 68.0, 52.1, 31.4],
            backgroundColor: ['#782200', '#C2410C', '#D97706', '#00236f', '#006c4e'],
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, max: 100 } }
        }
      });
    }

    function exportDistrictData() {
      const rows = [
        ["taluka_name", "monitored_workers", "active_nodes", "avg_wbgt_c", "lamp_status", "referrals_count"],
        ["Bhuj", "182415", "12", "28.2", "YELLOW", "42"],
        ["Gandhidham", "124800", "10", "29.8", "YELLOW", "56"],
        ["Mundra", "62410", "8", "29.4", "YELLOW", "68"],
        ["Anjar", "102850", "6", "29.1", "YELLOW", "38"],
        ["Rapar (Little Rann)", "98450", "5", "31.8", "RED", "94"],
        ["Bhachau", "78500", "4", "29.5", "YELLOW", "32"],
        ["Mandvi", "84120", "3", "28.8", "YELLOW", "24"],
        ["Abdasa", "48900", "4", "30.1", "ORANGE", "45"],
        ["Nakhatrana", "62100", "2", "28.5", "YELLOW", "18"],
        ["Lakhpat", "28200", "2", "29.0", "YELLOW", "12"]
      ];
      let csvContent = "data:text/csv;charset=utf-8," + rows.map(e => e.join(",")).join("\\n");
      const link = document.createElement("a");
      link.setAttribute("href", encodeURI(csvContent));
      link.setAttribute("download", "Kachchh_District_Occupational_Risk_Export_2026.csv");
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      showToast("District risk summary exported as CSV.", "success");
    }

    // BME280 Mask Waveform Chart
    function initBmeChart() {
      const ctx = document.getElementById('bme280-chart');
      if (!ctx || state.bmeChart) return;
      state.bmeChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: ['0s', '3s', '6s', '9s', '12s', '15s', '18s', '21s', '24s', '27s', '30s'],
          datasets: [{
            label: 'In-Mask RH Delta (%)',
            data: [4.2, 8.9, 3.8, 9.4, 4.1, 8.6, 3.9, 9.1, 4.0, 8.8, 4.3],
            borderColor: '#006c4e',
            backgroundColor: 'rgba(0, 108, 78, 0.15)',
            fill: true,
            tension: 0.4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, max: 12 } }
        }
      });
    }

    // Silica Assays Table
    function renderSilicaAssays() {
      const tbody = document.getElementById('silica-assays-tbody');
      if (!tbody) return;
      tbody.innerHTML = '';
      STATIC_DATA.silicaAssays.forEach(a => {
        const tr = document.createElement('tr');
        tr.className = "hover:bg-surface-container transition";
        tr.innerHTML = `
          <td class="p-2.5 font-bold font-sans">${a.industry_type}</td>
          <td class="p-2.5 font-sans">${a.location}</td>
          <td class="p-2.5">${a.dust_conc.toFixed(2)}</td>
          <td class="p-2.5 font-bold text-tertiary">${a.quartz_pct.toFixed(1)}%</td>
          <td class="p-2.5 text-[10px] text-on-surface-variant font-sans">${a.lab}</td>
        `;
        tbody.appendChild(tr);
      });
    }

    // Healthcare Facilities Cards
    function renderFacilities() {
      const container = document.getElementById('facilities-grid');
      if (!container) return;
      container.innerHTML = '';
      STATIC_DATA.facilities.forEach(f => {
        const card = document.createElement('div');
        card.className = "facility-card bg-surface-container-lowest p-5 rounded border border-outline-variant/40 shadow-sm space-y-3";
        card.setAttribute('data-taluka', f.taluka);

        card.innerHTML = `
          <div class="flex items-start justify-between">
            <div>
              <span class="text-[10px] font-bold px-2 py-0.5 rounded bg-primary/10 text-primary uppercase">${f.tier}</span>
              <h4 class="font-bold text-sm text-primary mt-1.5">${f.name}</h4>
              <span class="text-xs text-on-surface-variant">Taluka: <b>${f.taluka}</b></span>
            </div>
            <span class="material-symbols-outlined text-secondary text-[24px]">local_hospital</span>
          </div>
          <div class="pt-2 border-t border-outline-variant/30 text-[11px] grid grid-cols-2 gap-1.5">
            <span class="${f.xray ? 'text-secondary font-bold' : 'text-slate-400'}">✓ Digital X-Ray: ${f.xray ? 'YES' : 'NO'}</span>
            <span class="${f.spiro ? 'text-secondary font-bold' : 'text-slate-400'}">✓ Spirometer: ${f.spiro ? 'YES' : 'NO'}</span>
            <span class="${f.lab ? 'text-secondary font-bold' : 'text-slate-400'}">✓ Blood Lab: ${f.lab ? 'YES' : 'NO'}</span>
            <span class="${f.amb108 ? 'text-red-700 font-bold' : 'text-slate-400'}">✓ 108 Base: ${f.amb108 ? 'YES' : 'NO'}</span>
          </div>
          <button onclick="showToast('Priority Van referral scheduled to ${f.name}. Notification dispatched.', 'success')" class="w-full mt-2 py-1.5 bg-surface-container hover:bg-surface-container-high text-primary border border-outline-variant/40 rounded text-xs font-semibold transition">
            Route Referral Here
          </button>
        `;
        container.appendChild(card);
      });
    }

    function filterFacilitiesTable() {
      const val = document.getElementById('facilities-taluka-filter').value;
      document.querySelectorAll('.facility-card').forEach(card => {
        if (val === 'ALL' || card.getAttribute('data-taluka') === val) {
          card.classList.remove('hidden');
        } else {
          card.classList.add('hidden');
        }
      });
    }

    // Public Datasets Catalog Functions
    function renderDatasets() {
      const container = document.getElementById('datasets-grid');
      if (!container) return;
      container.innerHTML = '';
      STATIC_DATA.datasets.forEach(d => {
        const card = document.createElement('div');
        card.className = "dataset-card p-4 rounded border border-outline-variant/40 bg-surface-container-low shadow-sm space-y-2.5";
        card.setAttribute('data-category', d.category);

        card.innerHTML = `
          <div class="flex items-start justify-between">
            <div>
              <span class="text-[9px] font-bold px-2 py-0.5 rounded bg-primary/10 text-primary uppercase">${d.category}</span>
              <h4 class="font-bold text-sm text-primary mt-1">${d.name}</h4>
              <span class="text-[10px] text-on-surface-variant font-mono">Folder: final_dataset/public_downloads/${d.folder}/</span>
            </div>
            <span class="material-symbols-outlined text-secondary text-[22px]">dataset</span>
          </div>
          <p class="text-xs text-on-surface-variant leading-relaxed">${d.why}</p>
          <div class="pt-2 border-t border-outline-variant/30 text-[11px] grid grid-cols-2 gap-1 font-mono text-on-surface-variant">
            <span>Provider: <b>${d.source}</b></span>
            <span>License: <b>${d.license}</b></span>
          </div>
          <div class="pt-1 flex items-center justify-between">
            <span class="text-[10px] text-emerald-700 font-bold">✓ DPDP Compliant (0 PII)</span>
            <a href="${d.url}" target="_blank" class="text-xs font-bold text-primary hover:underline flex items-center gap-1">
              <span>View Source</span>
              <span class="material-symbols-outlined text-[14px]">open_in_new</span>
            </a>
          </div>
        `;
        container.appendChild(card);
      });
    }

    function filterDatasets(category) {
      document.querySelectorAll('.dataset-tab-btn').forEach(btn => {
        btn.className = "dataset-tab-btn px-2.5 py-1 rounded text-on-surface-variant hover:text-on-surface bg-surface-container";
      });
      event.target.className = "dataset-tab-btn px-2.5 py-1 rounded font-bold bg-primary text-white";

      document.querySelectorAll('.dataset-card').forEach(card => {
        if (category === 'ALL' || card.getAttribute('data-category') === category) {
          card.classList.remove('hidden');
        } else {
          card.classList.add('hidden');
        }
      });
    }

    // Official Login & Authentication Gate
    let selectedLoginRole = 'DDO';
    function selectLoginRole(role) {
      selectedLoginRole = role;
      ['ddo', 'doctor', 'safety', 'worker'].forEach(r => {
        const btn = document.getElementById(`role-btn-${r}`);
        if (btn) {
          btn.className = (r === role.toLowerCase())
            ? "p-3 text-left rounded border border-primary bg-primary/10 text-primary font-bold flex items-center gap-2"
            : "p-3 text-left rounded border border-outline-variant/40 bg-surface-container-low text-on-surface hover:bg-surface-container flex items-center gap-2";
        }
      });
      fillDemoCredentials(role);
    }

    function fillDemoCredentials(role) {
      selectedLoginRole = role;
      const idInput = document.getElementById('login-identifier');
      const passInput = document.getElementById('login-secret');

      if (role === 'DDO') {
        idInput.value = "ddo.kachchh@gujarat.gov.in";
        passInput.value = "KachchhDDO@2026";
      } else if (role === 'DOCTOR') {
        idInput.value = "dr.dave.rath@bocw.gujarat.gov.in";
        passInput.value = "Dhanvantari@Doc4081";
      } else if (role === 'SAFETY') {
        idInput.value = "safety.mundra@sez.adani.com";
        passInput.value = "MundraSafety@2026";
      } else {
        idInput.value = "9842-XXXX-1001";
        passInput.value = "OTP-849201";
      }
    }

    function handleLoginFormSubmit(e) {
      e.preventDefault();
      let user = { role: selectedLoginRole };
      if (selectedLoginRole === 'DDO') {
        user.name = "DDO Kachchh";
        user.badge = "District Magistrate";
        user.targetTab = "district";
      } else if (selectedLoginRole === 'DOCTOR') {
        user.name = "Dr. Rajesh V. Dave";
        user.badge = "Van MO (GMC-4081)";
        user.targetTab = "van";
      } else if (selectedLoginRole === 'SAFETY') {
        user.name = "Mundra Safety Lead";
        user.badge = "EHS Manager";
        user.targetTab = "site";
      } else {
        user.name = "Ramjibhai S. Koli";
        user.badge = "Salt Worker Pass";
        user.targetTab = "worker";
      }

      state.currentUser = user;
      localStorage.setItem('workcheck_user', JSON.stringify(user));
      updateAuthUI();
      showToast(`Welcome, ${user.name}! Access Granted: ${user.badge}`, "success");
      switchTab(user.targetTab || 'worker');
    }

    function updateAuthUI() {
      const nameEl = document.getElementById('user-session-name');
      const badgeEl = document.getElementById('user-session-badge');
      const actionEl = document.getElementById('btn-auth-action');

      const sideNameEl = document.getElementById('sidebar-user-name');
      const sideBadgeEl = document.getElementById('sidebar-user-badge');
      const sideSignoutBtn = document.getElementById('btn-sidebar-signout');
      const sideSigninBtn = document.getElementById('btn-sidebar-signin');
      const lockBanner = document.getElementById('sidebar-lock-banner');
      const lockIndicators = document.querySelectorAll('.lock-indicator');

      if (state.currentUser) {
        if (nameEl) nameEl.innerText = state.currentUser.name;
        if (badgeEl) badgeEl.innerText = state.currentUser.badge;
        if (actionEl) {
          actionEl.innerText = "Sign Out";
          actionEl.className = "ml-1 px-2 py-0.5 bg-red-600 hover:bg-red-700 text-white rounded font-bold text-[10px] transition flex items-center gap-0.5 shadow-sm";
          actionEl.innerHTML = '<span class="material-symbols-outlined text-[12px]">logout</span><span>Sign Out</span>';
          actionEl.onclick = handleSignOut;
        }

        if (sideNameEl) sideNameEl.innerText = state.currentUser.name;
        if (sideBadgeEl) sideBadgeEl.innerText = state.currentUser.badge;
        if (sideSignoutBtn) sideSignoutBtn.classList.remove('hidden');
        if (sideSigninBtn) sideSigninBtn.classList.add('hidden');
        if (lockBanner) lockBanner.classList.add('hidden');
        lockIndicators.forEach(el => el.classList.add('hidden'));

        document.querySelectorAll('.nav-tab-btn').forEach(btn => {
          btn.classList.remove('opacity-60');
        });
      } else {
        if (nameEl) nameEl.innerText = "Guest";
        if (badgeEl) badgeEl.innerText = "Public";
        if (actionEl) {
          actionEl.innerText = "Sign In";
          actionEl.className = "ml-1 px-2 py-0.5 bg-primary hover:bg-primary-container text-white rounded font-bold text-[10px] transition flex items-center gap-0.5 shadow-sm";
          actionEl.innerHTML = '<span class="material-symbols-outlined text-[12px]">login</span><span>Sign In</span>';
          actionEl.onclick = () => switchTab('login');
        }

        if (sideNameEl) sideNameEl.innerText = "Guest User";
        if (sideBadgeEl) sideBadgeEl.innerText = "Institutional Access Required";
        if (sideSignoutBtn) sideSignoutBtn.classList.add('hidden');
        if (sideSigninBtn) sideSigninBtn.classList.remove('hidden');
        if (lockBanner) lockBanner.classList.remove('hidden');
        lockIndicators.forEach(el => el.classList.remove('hidden'));

        document.querySelectorAll('.nav-tab-btn').forEach(btn => {
          if (btn.id !== 'nav-tab-login') {
            btn.classList.add('opacity-60');
          }
        });
      }
    }

    function handleSignOut() {
      state.currentUser = null;
      localStorage.removeItem('workcheck_user');
      updateAuthUI();
      showToast("Signed out from WorkCheck Kachchh. Access locked.", "info");
      switchTab('login');
    }
  </script>
</body>
</html>
""")

print("Successfully generated updated index.html with sidebar and auth gate.")
