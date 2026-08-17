PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS app_settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS id_sequences (
  prefix TEXT NOT NULL,
  year INTEGER NOT NULL,
  last_number INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY(prefix, year)
);

CREATE TABLE IF NOT EXISTS customers (
  customer_id TEXT PRIMARY KEY,
  customer_type TEXT NOT NULL DEFAULT 'Residential',
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  company_name TEXT,
  phone TEXT NOT NULL,
  email TEXT,
  preferred_contact TEXT NOT NULL DEFAULT 'Phone',
  billing_address TEXT NOT NULL,
  referral_source TEXT,
  customer_status TEXT NOT NULL DEFAULT 'Active',
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by TEXT NOT NULL DEFAULT 'Ryan',
  modified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  modified_by TEXT NOT NULL DEFAULT 'Ryan'
);

CREATE TABLE IF NOT EXISTS leads (
  lead_id TEXT PRIMARY KEY,
  customer_id TEXT,
  lead_date TEXT NOT NULL,
  project_type TEXT NOT NULL,
  lead_status TEXT NOT NULL DEFAULT 'New',
  priority TEXT NOT NULL DEFAULT 'Normal',
  estimated_value REAL NOT NULL DEFAULT 0 CHECK(estimated_value >= 0),
  next_follow_up_date TEXT,
  description TEXT,
  referral_source TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by TEXT NOT NULL DEFAULT 'Ryan',
  modified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  modified_by TEXT NOT NULL DEFAULT 'Ryan',
  FOREIGN KEY(customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS projects (
  project_id TEXT PRIMARY KEY,
  customer_id TEXT NOT NULL,
  lead_id TEXT,
  project_name TEXT NOT NULL,
  project_address TEXT NOT NULL,
  city TEXT NOT NULL,
  state TEXT NOT NULL DEFAULT 'PA',
  zip_code TEXT NOT NULL,
  project_type TEXT NOT NULL,
  project_status TEXT NOT NULL DEFAULT 'Lead',
  contract_amount REAL NOT NULL DEFAULT 0 CHECK(contract_amount >= 0),
  approved_change_orders REAL NOT NULL DEFAULT 0 CHECK(approved_change_orders >= 0),
  planned_start TEXT,
  actual_start TEXT,
  completion_date TEXT,
  scope_summary TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by TEXT NOT NULL DEFAULT 'Ryan',
  modified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  modified_by TEXT NOT NULL DEFAULT 'Ryan',
  FOREIGN KEY(customer_id) REFERENCES customers(customer_id) ON DELETE RESTRICT,
  FOREIGN KEY(lead_id) REFERENCES leads(lead_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS estimates (
  estimate_id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  estimate_version INTEGER NOT NULL DEFAULT 1 CHECK(estimate_version >= 1),
  material_cost REAL NOT NULL DEFAULT 0 CHECK(material_cost >= 0),
  material_tax REAL NOT NULL DEFAULT 0 CHECK(material_tax >= 0),
  labor_hours REAL NOT NULL DEFAULT 0 CHECK(labor_hours >= 0),
  labor_cost REAL NOT NULL DEFAULT 0 CHECK(labor_cost >= 0),
  subcontractor_cost REAL NOT NULL DEFAULT 0 CHECK(subcontractor_cost >= 0),
  permit_cost REAL NOT NULL DEFAULT 0 CHECK(permit_cost >= 0),
  disposal_cost REAL NOT NULL DEFAULT 0 CHECK(disposal_cost >= 0),
  equipment_cost REAL NOT NULL DEFAULT 0 CHECK(equipment_cost >= 0),
  delivery_cost REAL NOT NULL DEFAULT 0 CHECK(delivery_cost >= 0),
  other_direct_cost REAL NOT NULL DEFAULT 0 CHECK(other_direct_cost >= 0),
  overhead_allocation REAL NOT NULL DEFAULT 0 CHECK(overhead_allocation >= 0),
  total_direct_cost REAL NOT NULL DEFAULT 0 CHECK(total_direct_cost >= 0),
  target_gross_margin REAL NOT NULL DEFAULT 0.30 CHECK(target_gross_margin >= 0 AND target_gross_margin < 1),
  sell_price REAL NOT NULL DEFAULT 0 CHECK(sell_price >= 0),
  gross_profit REAL NOT NULL DEFAULT 0,
  gross_margin REAL NOT NULL DEFAULT 0,
  estimate_status TEXT NOT NULL DEFAULT 'Draft',
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by TEXT NOT NULL DEFAULT 'Ryan',
  modified_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  modified_by TEXT NOT NULL DEFAULT 'Ryan',
  FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE RESTRICT,
  UNIQUE(project_id, estimate_version)
);

CREATE TABLE IF NOT EXISTS payments (
  payment_id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL,
  payment_type TEXT NOT NULL,
  payment_date TEXT NOT NULL,
  amount REAL NOT NULL CHECK(amount != 0),
  payment_method TEXT NOT NULL,
  notes TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(lead_status);
CREATE INDEX IF NOT EXISTS idx_leads_followup ON leads(next_follow_up_date);
CREATE INDEX IF NOT EXISTS idx_projects_customer ON projects(customer_id);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(project_status);
CREATE INDEX IF NOT EXISTS idx_estimates_project ON estimates(project_id);
CREATE INDEX IF NOT EXISTS idx_payments_project ON payments(project_id);
