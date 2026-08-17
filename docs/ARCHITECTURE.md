# Project Phoenix App Architecture — v0.1

## Goal
Turn the existing Phoenix workbooks and SOPs into one responsive RHI operating system that works on iPhone and desktop.

## Source hierarchy
1. **Master Data Dictionary** — canonical field names, IDs, relationships and controlled values.
2. **Phoenix Core 2.0** — operational register and dashboard behavior.
3. **Estimate Studio / Price Library** — estimating, assemblies and price-library concepts.
4. **Master Workbook v1.5** — workflow and document-engine logic.
5. **Scott Sears Premium Package** — visual standard for customer-facing documents.

## v0.1 foundation implemented
- SQLite relational database.
- Automatic yearly IDs: `CUS-YYYY-NNN`, `LEAD-YYYY-NNN`, `RHI-YYYY-NNN`, `EST-YYYY-NNNN`.
- Dashboard.
- Customer register and customer creation.
- Lead register and lead creation.
- Project register, project creation and project detail screen.
- Estimate Studio with corrected gross-margin pricing.
- Responsive RHI blue / gray / black / white UI using the RHI logo.

## Pricing standard
The app does **not** use a separate 30% material markup. It calculates:

`material tax = taxable material cost × 6%`

`total direct cost = materials + material tax + direct labor + subcontractors + permits + disposal + equipment/rentals + delivery + other direct job costs`

`sell price = total direct cost ÷ (1 − target gross margin)`

Default target = 30%. The interface also provides 35% and 40% options for small, complicated, uncertain or higher-risk jobs.

`overhead_allocation` is retained in the database for future internal reporting, but it is not automatically inserted into the gross-margin formula because the approved Phoenix rule is based on direct job cost.

## Next build sequence
1. Customer/project edit screens and activity history.
2. Price Library + Labor Library + reusable Assembly Builder.
3. Full estimate line-items and scope builder.
4. Proposal/contract document engine using the premium Scott Sears layout.
5. Payments and invoice engine.
6. Field Mode: Daily Job Sheets, clock-in/out, materials, photos, problems and change-order flags.
7. Change Orders.
8. Punch list and closeout engine.
9. Schedule/calendar.
10. Reports and lessons-learned feedback to assemblies.
11. Authentication, cloud PostgreSQL, file storage, backups and deployment.
