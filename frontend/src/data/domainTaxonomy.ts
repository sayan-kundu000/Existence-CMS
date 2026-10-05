/**
 * Comprehensive Domain Taxonomy covering Engineering, Computer Science & AI,
 * Medical & Healthcare, Business & Finance, Legal & Compliance, Natural Sciences,
 * Social Sciences, Humanities, Design, and Emerging Interdisciplinary Fields.
 */

export interface DomainItem {
  id: string;
  name: string;
  field:
    | 'Engineering'
    | 'Computer Science & AI'
    | 'Medical & Healthcare'
    | 'Business & Finance'
    | 'Legal & Compliance'
    | 'Natural Sciences & Math'
    | 'Social Sciences & Humanities'
    | 'Interdisciplinary & Emerging';
  subfield?: string;
  keywords: string[];
}

export const DOMAIN_FIELDS = [
  'All Fields',
  'Engineering',
  'Computer Science & AI',
  'Medical & Healthcare',
  'Business & Finance',
  'Legal & Compliance',
  'Natural Sciences & Math',
  'Social Sciences & Humanities',
  'Interdisciplinary & Emerging'
] as const;

export type DomainField = (typeof DOMAIN_FIELDS)[number];

export const DOMAIN_TAXONOMY: DomainItem[] = [
  // ─────────────────────────────────────────────────────────────
  // 1. ALL ENGINEERING DISCIPLINES
  // ─────────────────────────────────────────────────────────────
  {
    id: 'mech-eng',
    name: 'Mechanical Engineering',
    field: 'Engineering',
    subfield: 'Mechanical & Machinery',
    keywords: ['thermodynamics', 'cad', 'solidworks', 'fluid mechanics', 'fea', 'dynamics', 'automotive', 'hvac']
  },
  {
    id: 'aero-eng',
    name: 'Aerospace & Aeronautical Engineering',
    field: 'Engineering',
    subfield: 'Aviation & Spacecraft',
    keywords: ['aerodynamics', 'propulsion', 'avionics', 'orbital mechanics', 'cfd', 'flight dynamics', 'satellites']
  },
  {
    id: 'petro-eng',
    name: 'Petroleum & Gas Engineering',
    field: 'Engineering',
    subfield: 'Energy & Extraction',
    keywords: ['drilling', 'reservoir engineering', 'refining', 'lng', 'upstream', 'downstream', 'pipeline', 'petrochemicals']
  },
  {
    id: 'agri-eng',
    name: 'Agricultural & Biosystems Engineering',
    field: 'Engineering',
    subfield: 'Agriculture & Food Systems',
    keywords: ['precision agriculture', 'irrigation', 'harvesting tech', 'agritech', 'soil science', 'bioresource', 'crop monitoring']
  },
  {
    id: 'biotech-eng',
    name: 'Biotechnology & Bioengineering',
    field: 'Engineering',
    subfield: 'Biological & Genetic',
    keywords: ['crispr', 'bioprocessing', 'genetic engineering', 'fermentation', 'synthetic biology', 'bioinformatics', 'cloning']
  },
  {
    id: 'biomed-eng',
    name: 'Biomedical & Medical Device Engineering',
    field: 'Engineering',
    subfield: 'Healthcare Technology',
    keywords: ['prosthetics', 'implants', 'mri', 'biosensors', 'tissue engineering', 'medical imaging', 'biomechanics']
  },
  {
    id: 'mining-eng',
    name: 'Mining & Mineral Engineering',
    field: 'Engineering',
    subfield: 'Extraction & Earth Moving',
    keywords: ['mineral extraction', 'open-pit', 'underground mining', 'mineral processing', 'ore geology', 'blasting', 'tunneling']
  },
  {
    id: 'metallurgy-eng',
    name: 'Metallurgical & Materials Engineering',
    field: 'Engineering',
    subfield: 'Materials & Alloys',
    keywords: ['alloys', 'crystallography', 'heat treatment', 'corrosion', 'smelting', 'nanomaterials', 'composites', 'metallography']
  },
  {
    id: 'chem-eng',
    name: 'Chemical & Process Engineering',
    field: 'Engineering',
    subfield: 'Chemical & Industrial',
    keywords: ['distillation', 'reaction kinetics', 'polymer science', 'catalysis', 'transport phenomena', 'process control']
  },
  {
    id: 'civil-eng',
    name: 'Civil & Structural Engineering',
    field: 'Engineering',
    subfield: 'Infrastructure & Construction',
    keywords: ['bridges', 'dams', 'reinforced concrete', 'structural analysis', 'bim', 'earthquake engineering', 'geotechnical']
  },
  {
    id: 'elec-eng',
    name: 'Electrical Engineering & Power Systems',
    field: 'Engineering',
    subfield: 'Power & Electromagnetics',
    keywords: ['power grid', 'high voltage', 'transformers', 'generators', 'smart grid', 'renewable energy', 'inverters']
  },
  {
    id: 'ece-eng',
    name: 'Electronics & Communication Engineering (ECE)',
    field: 'Engineering',
    subfield: 'Hardware & Telecomm',
    keywords: ['vlsi', 'pcb design', 'rf engineering', 'fpga', 'signal processing', 'microcontrollers', 'semiconductors', '5g']
  },
  {
    id: 'robotics-eng',
    name: 'Robotics, Mechatronics & Automation',
    field: 'Engineering',
    subfield: 'Robotics & Control',
    keywords: ['ros', 'actuators', 'kinematics', 'plc', 'scada', 'industrial automation', 'servo systems', 'computer vision']
  },
  {
    id: 'marine-eng',
    name: 'Marine, Ocean & Naval Engineering',
    field: 'Engineering',
    subfield: 'Maritime & Naval',
    keywords: ['ship design', 'hydrodynamics', 'offshore structures', 'naval architecture', 'subsea engineering', 'propulsion']
  },
  {
    id: 'nuclear-eng',
    name: 'Nuclear & Radiation Engineering',
    field: 'Engineering',
    subfield: 'Nuclear & Radiation',
    keywords: ['nuclear fission', 'fusion reactors', 'radiation shielding', 'reactor physics', 'radioisotopes', 'tokamak']
  },
  {
    id: 'enviro-eng',
    name: 'Environmental & Ecological Engineering',
    field: 'Engineering',
    subfield: 'Sustainability & Ecology',
    keywords: ['water treatment', 'air quality', 'carbon capture', 'waste management', 'remediation', 'lca', 'sustainability']
  },
  {
    id: 'industrial-eng',
    name: 'Industrial & Systems Engineering',
    field: 'Engineering',
    subfield: 'Operations & Optimization',
    keywords: ['six sigma', 'lean manufacturing', 'operations research', 'queuing theory', 'ergonomics', 'supply chain', 'kaizen']
  },
  {
    id: 'geo-eng',
    name: 'Geotechnical & Geological Engineering',
    field: 'Engineering',
    subfield: 'Earth & Soil',
    keywords: ['soil mechanics', 'foundation design', 'slope stability', 'tunneling', 'seismology', 'retaining walls']
  },
  {
    id: 'nano-eng',
    name: 'Nanotechnology & Molecular Engineering',
    field: 'Engineering',
    subfield: 'Nanoscale Science',
    keywords: ['carbon nanotubes', 'graphene', 'quantum dots', 'nanofabrication', 'afm', 'molecular assembly']
  },
  {
    id: 'auto-eng',
    name: 'Automotive & EV Powertrain Engineering',
    field: 'Engineering',
    subfield: 'Vehicles & Mobility',
    keywords: ['battery management system', 'bms', 'electric vehicles', 'powertrain', 'can bus', 'telematics', 'chassis']
  },

  // ─────────────────────────────────────────────────────────────
  // 2. COMPUTER SCIENCE, AI & SOFTWARE
  // ─────────────────────────────────────────────────────────────
  {
    id: 'aiml',
    name: 'AIML (Artificial Intelligence & Machine Learning)',
    field: 'Computer Science & AI',
    subfield: 'Machine Learning',
    keywords: ['numpy', 'scipy', 'pandas', 'scikit-learn', 'tensorflow', 'pytorch', 'deep learning', 'keras', 'mlops']
  },
  {
    id: 'nlp-llm',
    name: 'Natural Language Processing & LLMs',
    field: 'Computer Science & AI',
    subfield: 'Language Models',
    keywords: ['transformers', 'bert', 'gpt', 'tokenization', 'huggingface', 'rag', 'langchain', 'vector database']
  },
  {
    id: 'comp-vision',
    name: 'Computer Vision & Spatial Computing',
    field: 'Computer Science & AI',
    subfield: 'Visual AI',
    keywords: ['opencv', 'yolo', 'image segmentation', 'cnn', 'object detection', 'point clouds', 'nerf', 'augmented reality']
  },
  {
    id: 'data-science',
    name: 'Data Science & Predictive Analytics',
    field: 'Computer Science & AI',
    subfield: 'Data & Analytics',
    keywords: ['statistical modeling', 'a/b testing', 'data wrangling', 'sql', 'spark', 'tableau', 'powerbi', 'eda']
  },
  {
    id: 'software-eng',
    name: 'Software Engineering & System Architecture',
    field: 'Computer Science & AI',
    subfield: 'Software Architecture',
    keywords: ['microservices', 'design patterns', 'oop', 'domain-driven design', 'clean architecture', 'refactoring', 'ci/cd']
  },
  {
    id: 'fullstack-web',
    name: 'Full-Stack Web Engineering',
    field: 'Computer Science & AI',
    subfield: 'Web & Applications',
    keywords: ['react', 'next.js', 'typescript', 'node.js', 'fastapi', 'tailwind css', 'graphql', 'rest api', 'websockets']
  },
  {
    id: 'cloud-devops',
    name: 'Cloud Computing & DevOps / SRE',
    field: 'Computer Science & AI',
    subfield: 'Infrastructure & Cloud',
    keywords: ['aws', 'kubernetes', 'docker', 'terraform', 'azure', 'gcp', 'observability', 'prometheus', 'grafana', 'helm']
  },
  {
    id: 'cybersecurity',
    name: 'Cybersecurity, Cryptography & Infosec',
    field: 'Computer Science & AI',
    subfield: 'Security & Forensics',
    keywords: ['penetration testing', 'zero trust', 'cryptography', 'owasp', 'soc2', 'siem', 'malware analysis', 'firewalls']
  },
  {
    id: 'embedded-iot',
    name: 'Embedded Systems & Internet of Things (IoT)',
    field: 'Computer Science & AI',
    subfield: 'Hardware & Firmware',
    keywords: ['rtos', 'arm cortex', 'c++', 'arduino', 'raspberry pi', 'zigbee', 'mqtt', 'firmware', 'esp32']
  },
  {
    id: 'blockchain-web3',
    name: 'Blockchain, Web3 & Distributed Ledgers',
    field: 'Computer Science & AI',
    subfield: 'Decentralized Tech',
    keywords: ['solidity', 'ethereum', 'smart contracts', 'defi', 'zero knowledge proofs', 'evm', 'consensus algorithms', 'hyperledger']
  },
  {
    id: 'quantum-comp',
    name: 'Quantum Computing & Quantum Algorithms',
    field: 'Computer Science & AI',
    subfield: 'Quantum Information',
    keywords: ['qiskit', 'qubits', 'quantum circuits', 'shor algorithm', 'quantum superposition', 'entanglement', 'cirq']
  },
  {
    id: 'game-dev',
    name: 'Game Development & Real-Time Graphics',
    field: 'Computer Science & AI',
    subfield: 'Gaming & Virtual Worlds',
    keywords: ['unity', 'unreal engine', 'c#', 'shaders', 'vulkan', 'directx', 'physics engine', '3d modeling']
  },
  {
    id: 'bioinformatics',
    name: 'Bioinformatics & Computational Biology',
    field: 'Computer Science & AI',
    subfield: 'Genomics & Algorithms',
    keywords: ['blast', 'next-generation sequencing', 'alphafold', 'fasta', 'phylogenetics', 'genomics', 'molecular docking']
  },

  // ─────────────────────────────────────────────────────────────
  // 3. MEDICAL & HEALTHCARE FIELDS
  // ─────────────────────────────────────────────────────────────
  {
    id: 'gen-med',
    name: 'General Medicine & Internal Medicine',
    field: 'Medical & Healthcare',
    subfield: 'Clinical Practice',
    keywords: ['diagnosis', 'clinical pathology', 'triage', 'patient assessment', 'chronic disease', 'pharmacotherapy']
  },
  {
    id: 'surgery',
    name: 'General & Minimally Invasive Surgery',
    field: 'Medical & Healthcare',
    subfield: 'Surgical Disciplines',
    keywords: ['laparoscopy', 'suturing', 'aseptic technique', 'trauma surgery', 'intraoperative care', 'robotic surgery']
  },
  {
    id: 'cardiology',
    name: 'Cardiology & Cardiovascular Sciences',
    field: 'Medical & Healthcare',
    subfield: 'Heart & Vascular',
    keywords: ['ecg', 'echocardiogram', 'cardiac catheterization', 'arrhythmia', 'angioplasty', 'hemodynamics']
  },
  {
    id: 'neurology',
    name: 'Neurology & Neurosurgery',
    field: 'Medical & Healthcare',
    subfield: 'Brain & Nervous System',
    keywords: ['eeg', 'mri neuroimaging', 'neuroplasticity', 'stroke management', 'neuropathy', 'craniotomy']
  },
  {
    id: 'oncology',
    name: 'Oncology & Cancer Therapeutics',
    field: 'Medical & Healthcare',
    subfield: 'Cancer Biology',
    keywords: ['chemotherapy', 'immunotherapy', 'car-t', 'radiation oncology', 'tumor markers', 'biopsy', 'carcinogenesis']
  },
  {
    id: 'radiology',
    name: 'Radiology & Nuclear Medicine',
    field: 'Medical & Healthcare',
    subfield: 'Diagnostics & Imaging',
    keywords: ['ct scan', 'x-ray', 'pet scan', 'ultrasound', 'dicom', 'radiopharmaceuticals', 'interventional radiology']
  },
  {
    id: 'pharma-trials',
    name: 'Pharmacology, Toxicology & Clinical Trials',
    field: 'Medical & Healthcare',
    subfield: 'Drug Development',
    keywords: ['pharmacokinetics', 'pharmacodynamics', 'fda approvals', 'gcp', 'phase i-iv trials', 'drug discovery']
  },
  {
    id: 'public-health',
    name: 'Public Health & Epidemiology',
    field: 'Medical & Healthcare',
    subfield: 'Population Health',
    keywords: ['biostatistics', 'disease surveillance', 'vaccination', 'who protocols', 'health policy', 'sanitation']
  },
  {
    id: 'psychiatry',
    name: 'Psychiatry & Clinical Psychology',
    field: 'Medical & Healthcare',
    subfield: 'Mental Health',
    keywords: ['dsm-5', 'psychopharmacology', 'cbt', 'neuropsychology', 'psychotherapy', 'trauma therapy']
  },
  {
    id: 'immunology',
    name: 'Immunology & Infectious Diseases',
    field: 'Medical & Healthcare',
    subfield: 'Immunity & Pathogens',
    keywords: ['antibodies', 'elisa', 'virology', 'bacteriology', 'autoimmune diseases', 'pathogen surveillance']
  },
  {
    id: 'dentistry',
    name: 'Dentistry & Maxillofacial Sciences',
    field: 'Medical & Healthcare',
    subfield: 'Dental & Oral',
    keywords: ['endodontics', 'orthodontics', 'periodontics', 'oral surgery', 'dental prosthetics', 'maxillofacial']
  },

  // ─────────────────────────────────────────────────────────────
  // 4. BUSINESS, FINANCE & MANAGEMENT
  // ─────────────────────────────────────────────────────────────
  {
    id: 'corp-strategy',
    name: 'Corporate Strategy & Executive Management',
    field: 'Business & Finance',
    subfield: 'Strategic Planning',
    keywords: ['okrs', 'swot', 'market entry', 'competitive moat', 'business models', 'board governance', 'm&a strategy']
  },
  {
    id: 'finance-ib',
    name: 'Corporate Finance & Investment Banking',
    field: 'Business & Finance',
    subfield: 'Finance & Banking',
    keywords: ['dcf modeling', 'lbo', 'equity research', 'valuation', 'capital markets', 'ipo', 'underwriting', 'm&a']
  },
  {
    id: 'quant-finance',
    name: 'Quantitative Finance & Algorithmic Trading',
    field: 'Business & Finance',
    subfield: 'Quant & Trading',
    keywords: ['black-scholes', 'derivatives', 'monte carlo', 'portfolio optimization', 'high frequency trading', 'volatility']
  },
  {
    id: 'accounting-tax',
    name: 'Accounting, Auditing & Taxation',
    field: 'Business & Finance',
    subfield: 'Accounting & Compliance',
    keywords: ['gaap', 'ifrs', 'forensic audit', 'corporate tax', 'balance sheet', 'p&l', 'statutory compliance']
  },
  {
    id: 'marketing-growth',
    name: 'Marketing, Digital Growth & Brand Strategy',
    field: 'Business & Finance',
    subfield: 'Marketing & Brand',
    keywords: ['seo', 'sem', 'cac/ltv', 'conversion rate optimization', 'content marketing', 'brand positioning', 'crm']
  },
  {
    id: 'product-mgmt',
    name: 'Product Management & Innovation',
    field: 'Business & Finance',
    subfield: 'Product & UX',
    keywords: ['agile', 'scrum', 'user stories', 'roadmapping', 'prds', 'product-market fit', 'kpis', 'design thinking']
  },
  {
    id: 'supply-chain',
    name: 'Supply Chain, Logistics & Procurement',
    field: 'Business & Finance',
    subfield: 'Operations & Distribution',
    keywords: ['erp', 'sap', 'inventory management', 'freight logistics', 'cold chain', 'vendor management', 'just-in-time']
  },
  {
    id: 'vc-pe',
    name: 'Venture Capital & Private Equity',
    field: 'Business & Finance',
    subfield: 'Investing & Capital',
    keywords: ['term sheets', 'due diligence', 'cap table', 'angel investing', 'seed funding', 'exit strategy', 'deal sourcing']
  },
  {
    id: 'hr-talent',
    name: 'Human Resource Management & Talent Strategy',
    field: 'Business & Finance',
    subfield: 'People & Culture',
    keywords: ['talent acquisition', 'compensation & benefits', 'hris', 'de&i', 'performance appraisal', 'organizational psychology']
  },
  {
    id: 'revops-sales',
    name: 'Revenue Operations (RevOps) & Enterprise Sales',
    field: 'Business & Finance',
    subfield: 'Sales & Growth',
    keywords: ['salesforce', 'pipeline forecasting', 'hubspot', 'b2b sales', 'account-based marketing', 'sales enablement']
  },

  // ─────────────────────────────────────────────────────────────
  // 5. LEGAL & COMPLIANCE FIELDS
  // ─────────────────────────────────────────────────────────────
  {
    id: 'corp-law',
    name: 'Corporate Law & Governance',
    field: 'Legal & Compliance',
    subfield: 'Corporate Practice',
    keywords: ['contracts', 'due diligence', 'shareholders agreement', 'board resolutions', 'joint ventures', 'sebi', 'sec']
  },
  {
    id: 'ip-law',
    name: 'Intellectual Property (IP) Law & Patents',
    field: 'Legal & Compliance',
    subfield: 'IP & Inventions',
    keywords: ['patent drafting', 'trademarks', 'copyrights', 'trade secrets', 'prior art search', 'uspto', 'wipo', 'infringement']
  },
  {
    id: 'cyber-law',
    name: 'Cyber Law, Data Privacy & Regulatory Compliance',
    field: 'Legal & Compliance',
    subfield: 'Tech & Privacy Law',
    keywords: ['gdpr', 'ccpa', 'hipaa', 'digital personal data protection', 'cyber forensics', 'data sovereignty', 'incident response']
  },
  {
    id: 'dispute-arb',
    name: 'Litigation, Dispute Resolution & Arbitration',
    field: 'Legal & Compliance',
    subfield: 'Court & ADR',
    keywords: ['arbitration', 'mediation', 'cross-examination', 'brief writing', 'pleadings', 'appellate law', 'contracts dispute']
  },
  {
    id: 'tax-law',
    name: 'Taxation Law, Customs & Tariffs',
    field: 'Legal & Compliance',
    subfield: 'Taxation & Trade',
    keywords: ['direct tax', 'indirect tax', 'gst', 'transfer pricing', 'double taxation treaty', 'customs duties', 'irs code']
  },
  {
    id: 'env-law',
    name: 'Environmental, Energy & Climate Law',
    field: 'Legal & Compliance',
    subfield: 'Environment & Climate',
    keywords: ['esg compliance', 'carbon credits', 'environmental impact assessment', 'clean air act', 'paris agreement']
  },
  {
    id: 'labor-law',
    name: 'Labor, Employment & Workplace Law',
    field: 'Legal & Compliance',
    subfield: 'Workplace & Unions',
    keywords: ['collective bargaining', 'severance', 'workplace discrimination', 'occupational safety', 'flsa', 'posh']
  },

  // ─────────────────────────────────────────────────────────────
  // 6. NATURAL SCIENCES & MATHEMATICS
  // ─────────────────────────────────────────────────────────────
  {
    id: 'physics',
    name: 'Theoretical, Experimental & Applied Physics',
    field: 'Natural Sciences & Math',
    subfield: 'Physics',
    keywords: ['quantum mechanics', 'electromagnetism', 'statistical physics', 'optics', 'lasers', 'particle physics', 'relativity']
  },
  {
    id: 'chemistry',
    name: 'Organic, Inorganic & Analytical Chemistry',
    field: 'Natural Sciences & Math',
    subfield: 'Chemistry',
    keywords: ['nmr spectroscopy', 'mass spectrometry', 'chromatography', 'synthesis', 'crystallography', 'electrochemistry']
  },
  {
    id: 'math-stats',
    name: 'Pure & Applied Mathematics / Statistics',
    field: 'Natural Sciences & Math',
    subfield: 'Mathematics',
    keywords: ['linear algebra', 'multivariable calculus', 'probability theory', 'bayesian inference', 'differential equations', 'topology']
  },
  {
    id: 'earth-climate',
    name: 'Earth, Atmospheric & Climate Sciences',
    field: 'Natural Sciences & Math',
    subfield: 'Geosciences',
    keywords: ['meteorology', 'geophysics', 'paleoclimatology', 'oceanography', 'gis', 'remote sensing', 'hydrology']
  },
  {
    id: 'astronomy',
    name: 'Astronomy, Astrophysics & Space Sciences',
    field: 'Natural Sciences & Math',
    subfield: 'Astronomy',
    keywords: ['cosmology', 'exoplanets', 'stellar evolution', 'telescope data', 'gravitational waves', 'astrometry']
  },

  // ─────────────────────────────────────────────────────────────
  // 7. SOCIAL SCIENCES, HUMANITIES & DESIGN
  // ─────────────────────────────────────────────────────────────
  {
    id: 'ui-ux-design',
    name: 'UI/UX Design, Ergonomics & Spatial Interaction',
    field: 'Social Sciences & Humanities',
    subfield: 'Design',
    keywords: ['figma', 'wireframing', 'user research', 'usability testing', 'design systems', 'micro-interactions', 'accessibility']
  },
  {
    id: 'economics-pol',
    name: 'Economics, Public Policy & Geopolitics',
    field: 'Social Sciences & Humanities',
    subfield: 'Policy & Economics',
    keywords: ['macroeconomics', 'microeconomics', 'econometrics', 'foreign policy', 'public administration', 'game theory']
  },
  {
    id: 'psychology-cog',
    name: 'Cognitive Science & Behavioral Psychology',
    field: 'Social Sciences & Humanities',
    subfield: 'Behavior & Cognition',
    keywords: ['perception', 'decision making', 'behavioral economics', 'memory systems', 'cognitive biases', 'psychometrics']
  },
  {
    id: 'creative-media',
    name: 'Media Production, Journalism & Creative Direction',
    field: 'Social Sciences & Humanities',
    subfield: 'Media & Creative',
    keywords: ['video editing', 'broadcast journalism', 'storytelling', 'sound design', 'cinematography', 'creative writing']
  },
  {
    id: 'architecture-plan',
    name: 'Architecture, Urban Planning & Interior Design',
    field: 'Social Sciences & Humanities',
    subfield: 'Spatial Architecture',
    keywords: ['autocad', 'revit', 'urban zoning', 'sustainable architecture', 'spatial design', 'landscape architecture']
  },

  // ─────────────────────────────────────────────────────────────
  // 8. INTERDISCIPLINARY & EMERGING FIELDS
  // ─────────────────────────────────────────────────────────────
  {
    id: 'neurotech-bci',
    name: 'Neurotechnology & Brain-Computer Interfaces (BCI)',
    field: 'Interdisciplinary & Emerging',
    subfield: 'Neurotech',
    keywords: ['neural decoding', 'eeg processing', 'neural interfaces', 'neuromorphic computing', 'optogenetics']
  },
  {
    id: 'climate-cleantech',
    name: 'Climate Tech, Green Hydrogen & Clean Energy',
    field: 'Interdisciplinary & Emerging',
    subfield: 'Clean Tech',
    keywords: ['photovoltaics', 'electrolyzers', 'fuel cells', 'smart grid', 'carbon sequestration', 'circular economy']
  },
  {
    id: 'space-tech',
    name: 'Space Tech, Satellite Systems & Propulsion',
    field: 'Interdisciplinary & Emerging',
    subfield: 'Space Exploration',
    keywords: ['cubesats', 'ion thrusters', 'reusable launch vehicles', 'lunar landing', 'telemetry', 'payload engineering']
  },
  {
    id: 'autonomous-systems',
    name: 'Autonomous Systems & Self-Driving Mobility',
    field: 'Interdisciplinary & Emerging',
    subfield: 'Mobility & Autonomy',
    keywords: ['lidar', 'sensor fusion', 'path planning', 'simulations', 'carla', 'v2x', 'slam', 'adas']
  },
  {
    id: 'fintech-defi',
    name: 'FinTech, InsurTech & Open Banking',
    field: 'Interdisciplinary & Emerging',
    subfield: 'Financial Tech',
    keywords: ['upi', 'payment gateways', 'algorithmic risk', 'automated underwriting', 'neobanking', 'aml compliance']
  }
];

export const getDomainByName = (name: string): DomainItem | undefined => {
  const norm = name.trim().toLowerCase();
  return DOMAIN_TAXONOMY.find((d) => d.name.toLowerCase() === norm);
};

export const filterDomainsByQuery = (
  query: string,
  fieldFilter: DomainField = 'All Fields'
): DomainItem[] => {
  const cleanQ = query.trim().toLowerCase();
  return DOMAIN_TAXONOMY.filter((item) => {
    if (fieldFilter !== 'All Fields' && item.field !== fieldFilter) {
      return false;
    }
    if (!cleanQ) return true;
    return (
      item.name.toLowerCase().includes(cleanQ) ||
      item.field.toLowerCase().includes(cleanQ) ||
      (item.subfield && item.subfield.toLowerCase().includes(cleanQ)) ||
      item.keywords.some((k) => k.toLowerCase().includes(cleanQ))
    );
  });
};
