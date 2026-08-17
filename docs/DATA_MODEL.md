# Phoenix v0.1 Data Model

The app begins with the Master Data Dictionary entities and extends the Estimate record to match the current pricing rule.

## Core relationships
- Customer 1 → many Leads
- Customer 1 → many Projects
- Project 1 → many Estimates
- Project 1 → many Payments
- Later phases add Proposal, Contract, Invoice, Document, Warranty, Photo, Change Order and Lesson Learned relationships.

## Estimate pricing additions
The original dictionary already includes material cost, material tax, labor hours, labor cost, equipment cost, overhead allocation, sell price, gross profit and gross margin. App v0.1 adds direct-cost fields required by the updated Phoenix pricing standard:
- `subcontractor_cost`
- `permit_cost`
- `disposal_cost`
- `delivery_cost`
- `other_direct_cost`
- `total_direct_cost`
- `target_gross_margin`

These should be incorporated into the next official Data Dictionary revision.
