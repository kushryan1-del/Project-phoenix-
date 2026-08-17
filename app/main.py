from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from .db import BASE_DIR, db, get_settings, init_db, next_id
from .pricing import calculate_price

app = FastAPI(title="Project Phoenix", version="0.1.0")
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")
app.mount("/assets", StaticFiles(directory=BASE_DIR / "assets"), name="assets")
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")

PROJECT_STATUSES = ["Lead", "Site Visit Scheduled", "Estimating", "Proposal Sent", "Awarded", "Contracted", "Materials Ordered", "Scheduled", "In Production", "Substantial Completion", "Final Payment Due", "Closed", "Cancelled", "On Hold"]
LEAD_STATUSES = ["New", "Contacted", "Site Visit Scheduled", "Estimating", "Proposal Sent", "Follow-Up", "Won", "Lost", "Not Qualified", "On Hold"]
PRIORITIES = ["Low", "Normal", "High", "Urgent"]
PROJECT_TYPES = ["Bathroom", "Kitchen", "Interior Doors", "Exterior Doors", "Windows", "Deck", "Painting", "Drywall", "Flooring", "Trim & Finish Carpentry", "Roofing", "Siding", "Plumbing", "Electrical", "General Repair", "Other"]


@app.on_event("startup")
def startup() -> None:
    init_db()


def render(request: Request, template: str, **context):
    base = {"request": request, "settings": get_settings(), "nav": request.url.path}
    base.update(context)
    return templates.TemplateResponse(template, base)


@app.get("/health")
def health():
    return {"status": "ok", "app": "Project Phoenix", "version": "0.1.0"}


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    with db() as conn:
        customer_count = conn.execute("SELECT COUNT(*) c FROM customers").fetchone()["c"]
        open_leads = conn.execute("SELECT COUNT(*) c FROM leads WHERE lead_status NOT IN ('Lost','Not Qualified','Won')").fetchone()["c"]
        active_projects = conn.execute("SELECT COUNT(*) c FROM projects WHERE project_status NOT IN ('Closed','Cancelled')").fetchone()["c"]
        pipeline = conn.execute("SELECT COALESCE(SUM(estimated_value),0) v FROM leads WHERE lead_status NOT IN ('Lost','Not Qualified','Won')").fetchone()["v"]
        contracted = conn.execute("SELECT COALESCE(SUM(contract_amount + approved_change_orders),0) v FROM projects WHERE project_status NOT IN ('Lead','Cancelled')").fetchone()["v"]
        due_followups = conn.execute("SELECT * FROM leads WHERE next_follow_up_date IS NOT NULL AND next_follow_up_date <= ? AND lead_status NOT IN ('Lost','Not Qualified','Won') ORDER BY next_follow_up_date LIMIT 6", (date.today().isoformat(),)).fetchall()
        recent_projects = conn.execute("SELECT p.*, c.first_name, c.last_name FROM projects p JOIN customers c ON c.customer_id=p.customer_id ORDER BY p.created_at DESC LIMIT 6").fetchall()
    return render(request, "dashboard.html", customer_count=customer_count, open_leads=open_leads, active_projects=active_projects, pipeline=pipeline, contracted=contracted, due_followups=due_followups, recent_projects=recent_projects)


@app.get("/customers", response_class=HTMLResponse)
def customers(request: Request):
    with db() as conn:
        rows = conn.execute("SELECT * FROM customers ORDER BY last_name, first_name").fetchall()
    return render(request, "customers.html", customers=rows)


@app.post("/customers")
def create_customer(
    first_name: str = Form(...), last_name: str = Form(...), phone: str = Form(...),
    email: str = Form(""), billing_address: str = Form(...), customer_type: str = Form("Residential"),
    preferred_contact: str = Form("Phone"), referral_source: str = Form(""),
):
    cid = next_id("CUS", 3)
    with db() as conn:
        conn.execute("INSERT INTO customers(customer_id, customer_type, first_name, last_name, phone, email, preferred_contact, billing_address, referral_source) VALUES (?,?,?,?,?,?,?,?,?)",
                     (cid, customer_type, first_name.strip(), last_name.strip(), phone.strip(), email.strip() or None, preferred_contact, billing_address.strip(), referral_source.strip() or None))
    return RedirectResponse("/customers", status_code=303)


@app.get("/leads", response_class=HTMLResponse)
def leads(request: Request):
    with db() as conn:
        rows = conn.execute("SELECT l.*, COALESCE(c.first_name || ' ' || c.last_name, '') customer_name FROM leads l LEFT JOIN customers c ON c.customer_id=l.customer_id ORDER BY lead_date DESC, created_at DESC").fetchall()
        customers = conn.execute("SELECT customer_id, first_name, last_name FROM customers ORDER BY last_name, first_name").fetchall()
    return render(request, "leads.html", leads=rows, customers=customers, lead_statuses=LEAD_STATUSES, priorities=PRIORITIES, project_types=PROJECT_TYPES)


@app.post("/leads")
def create_lead(
    customer_id: str = Form(""), project_type: str = Form(...), description: str = Form(""),
    lead_status: str = Form("New"), priority: str = Form("Normal"), estimated_value: float = Form(0),
    next_follow_up_date: str = Form(""), referral_source: str = Form(""),
):
    lid = next_id("LEAD", 3)
    with db() as conn:
        conn.execute("INSERT INTO leads(lead_id, customer_id, lead_date, project_type, description, lead_status, priority, estimated_value, next_follow_up_date, referral_source) VALUES (?,?,?,?,?,?,?,?,?,?)",
                     (lid, customer_id or None, date.today().isoformat(), project_type, description.strip() or None, lead_status, priority, max(0, estimated_value), next_follow_up_date or None, referral_source.strip() or None))
    return RedirectResponse("/leads", status_code=303)


@app.get("/projects", response_class=HTMLResponse)
def projects(request: Request):
    with db() as conn:
        rows = conn.execute("SELECT p.*, c.first_name, c.last_name, (p.contract_amount+p.approved_change_orders) current_contract_value FROM projects p JOIN customers c ON c.customer_id=p.customer_id ORDER BY p.created_at DESC").fetchall()
        customers = conn.execute("SELECT customer_id, first_name, last_name FROM customers ORDER BY last_name, first_name").fetchall()
        leads = conn.execute("SELECT lead_id, project_type, description FROM leads WHERE lead_status NOT IN ('Lost','Not Qualified') ORDER BY created_at DESC").fetchall()
    return render(request, "projects.html", projects=rows, customers=customers, leads=leads, project_statuses=PROJECT_STATUSES, project_types=PROJECT_TYPES)


@app.post("/projects")
def create_project(
    customer_id: str = Form(...), lead_id: str = Form(""), project_name: str = Form(...), project_address: str = Form(...),
    city: str = Form(...), state: str = Form("PA"), zip_code: str = Form(...), project_type: str = Form(...),
    project_status: str = Form("Lead"), planned_start: str = Form(""), scope_summary: str = Form(""),
):
    pid = next_id("RHI", 3)
    with db() as conn:
        exists = conn.execute("SELECT 1 FROM customers WHERE customer_id=?", (customer_id,)).fetchone()
        if not exists:
            raise HTTPException(status_code=400, detail="Customer not found")
        conn.execute("INSERT INTO projects(project_id, customer_id, lead_id, project_name, project_address, city, state, zip_code, project_type, project_status, planned_start, scope_summary) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                     (pid, customer_id, lead_id or None, project_name.strip(), project_address.strip(), city.strip(), state.strip().upper() or "PA", zip_code.strip(), project_type, project_status, planned_start or None, scope_summary.strip() or None))
        if lead_id:
            conn.execute("UPDATE leads SET lead_status='Won', modified_at=CURRENT_TIMESTAMP WHERE lead_id=?", (lead_id,))
    return RedirectResponse(f"/projects/{pid}", status_code=303)


@app.get("/projects/{project_id}", response_class=HTMLResponse)
def project_detail(request: Request, project_id: str):
    with db() as conn:
        project = conn.execute("SELECT p.*, c.first_name, c.last_name, c.phone, c.email, (p.contract_amount+p.approved_change_orders) current_contract_value FROM projects p JOIN customers c ON c.customer_id=p.customer_id WHERE p.project_id=?", (project_id,)).fetchone()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        estimates = conn.execute("SELECT * FROM estimates WHERE project_id=? ORDER BY estimate_version DESC", (project_id,)).fetchall()
        payments = conn.execute("SELECT * FROM payments WHERE project_id=? ORDER BY payment_date DESC", (project_id,)).fetchall()
        paid = conn.execute("SELECT COALESCE(SUM(amount),0) v FROM payments WHERE project_id=?", (project_id,)).fetchone()["v"]
    return render(request, "project_detail.html", project=project, estimates=estimates, payments=payments, paid=paid)


@app.get("/estimates", response_class=HTMLResponse)
def estimates(request: Request):
    with db() as conn:
        rows = conn.execute("SELECT e.*, p.project_name FROM estimates e JOIN projects p ON p.project_id=e.project_id ORDER BY e.created_at DESC").fetchall()
        projects = conn.execute("SELECT project_id, project_name FROM projects WHERE project_status NOT IN ('Closed','Cancelled') ORDER BY created_at DESC").fetchall()
    return render(request, "estimates.html", estimates=rows, projects=projects)


@app.post("/estimates")
def create_estimate(
    project_id: str = Form(...), material_cost: float = Form(0), labor_hours: float = Form(0), labor_cost: float = Form(0),
    subcontractor_cost: float = Form(0), permit_cost: float = Form(0), disposal_cost: float = Form(0), equipment_cost: float = Form(0),
    delivery_cost: float = Form(0), other_direct_cost: float = Form(0), target_gross_margin: float = Form(0.30), notes: str = Form(""),
):
    settings = get_settings()
    result = calculate_price(material_cost=material_cost, labor_cost=labor_cost, subcontractor_cost=subcontractor_cost, permit_cost=permit_cost,
                             disposal_cost=disposal_cost, equipment_cost=equipment_cost, delivery_cost=delivery_cost, other_direct_cost=other_direct_cost,
                             material_tax_rate=float(settings.get("material_tax_rate", "0.06")), target_gross_margin=target_gross_margin)
    eid = next_id("EST", 4)
    with db() as conn:
        row = conn.execute("SELECT COALESCE(MAX(estimate_version),0)+1 v FROM estimates WHERE project_id=?", (project_id,)).fetchone()
        version = row["v"]
        conn.execute("INSERT INTO estimates(estimate_id, project_id, estimate_version, material_cost, material_tax, labor_hours, labor_cost, subcontractor_cost, permit_cost, disposal_cost, equipment_cost, delivery_cost, other_direct_cost, total_direct_cost, target_gross_margin, sell_price, gross_profit, gross_margin, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     (eid, project_id, version, material_cost, result.material_tax, labor_hours, labor_cost, subcontractor_cost, permit_cost, disposal_cost, equipment_cost, delivery_cost, other_direct_cost, result.total_direct_cost, target_gross_margin, result.sell_price, result.gross_profit, result.gross_margin, notes.strip() or None))
        conn.execute("UPDATE projects SET project_status=CASE WHEN project_status='Lead' THEN 'Estimating' ELSE project_status END, modified_at=CURRENT_TIMESTAMP WHERE project_id=?", (project_id,))
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


class PricingRequest(BaseModel):
    material_cost: float = Field(default=0, ge=0)
    labor_cost: float = Field(default=0, ge=0)
    subcontractor_cost: float = Field(default=0, ge=0)
    permit_cost: float = Field(default=0, ge=0)
    disposal_cost: float = Field(default=0, ge=0)
    equipment_cost: float = Field(default=0, ge=0)
    delivery_cost: float = Field(default=0, ge=0)
    other_direct_cost: float = Field(default=0, ge=0)
    target_gross_margin: float = Field(default=0.30, ge=0, lt=1)


@app.post("/api/pricing")
def api_pricing(payload: PricingRequest):
    settings = get_settings()
    return calculate_price(**payload.model_dump(), material_tax_rate=float(settings.get("material_tax_rate", "0.06"))).as_dict()
