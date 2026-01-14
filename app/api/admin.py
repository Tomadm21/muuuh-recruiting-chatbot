from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.db.database import get_db, engine, Base
from app.models.lead import Lead
from app.seeds import seed_data

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/seed_db_trigger")
async def trigger_seed():
    """Helper to seed DB via Browser."""
    try:
        seed_data()
        return {"status": "success", "message": "Database updated with 10 candidates!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/hard_reset_db")
async def hard_reset():
    """Wipes DB and Re-Seeds (Fixes Schema Issues)"""
    try:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        seed_data()
        return {"status": "success", "message": "HARD RESET COMPLETE. Tables dropped, recreated, and seeded."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.get("/", response_class=HTMLResponse)
async def admin_root(request: Request):
    return RedirectResponse(url="/admin/board")

@router.get("/board", response_class=HTMLResponse)
async def pipeline_board(request: Request, db: Session = Depends(get_db)):
    all_leads = db.query(Lead).all()
    
    stages = {
        "NEW": "New Applications",
        "SCREENING": "AI Screening",
        "QUALIFIED": "Qualified",
        "INTERVIEW": "Interview",
        "OFFER": "Offer Sent",
        "REJECTED": "Rejected"
    }
    
    leads_by_stage = {k: [] for k in stages}
    for lead in all_leads:
        status = lead.pipeline_status or "NEW"
        if status not in leads_by_stage:
            status = "NEW"
        leads_by_stage[status].append(lead)
        
    return templates.TemplateResponse(
        "admin/board.html", 
        {"request": request, "stages": stages, "leads_by_stage": leads_by_stage}
    )

@router.post("/move_lead/{lead_id}/{new_status}")
async def move_lead(lead_id: int, new_status: str, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return JSONResponse(status_code=404, content={"error": "Not found"})
    
    lead.pipeline_status = new_status
    db.commit()
    return {"status": "success"} 
    # Actually simpler to just have dashboard at /

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    # Fetch Top 10 by Qualification Score
    top_leads = db.query(Lead).filter(Lead.qualification_score > 0).order_by(Lead.qualification_score.desc()).limit(10).all()
    
    # Fetch All
    all_leads = db.query(Lead).order_by(Lead.updated_at.desc()).all()

    # --- Statistics Calculation ---
    total = len(all_leads)
    
    # 1. Funnel (New vs Screening vs Completed)
    # 0-2 = New/Started, 3-98 = In Progress, 99 = Completed
    count_new = sum(1 for l in all_leads if l.conversation_stage < 3)
    count_inprogress = sum(1 for l in all_leads if 3 <= l.conversation_stage < 99)
    count_completed = sum(1 for l in all_leads if l.conversation_stage == 99)
    
    # 2. Score Distribution (only scored ones)
    scored_leads = [l for l in all_leads if l.qualification_score > 0]
    count_high = sum(1 for l in scored_leads if l.qualification_score >= 80)
    count_mid = sum(1 for l in scored_leads if 50 <= l.qualification_score < 80)
    count_low = sum(1 for l in scored_leads if l.qualification_score < 50)
    
    # 3. Sources
    sources = {}
    for l in all_leads:
        s = l.source or "Unbekannt"
        sources[s] = sources.get(s, 0) + 1
        
    stats = {
        "funnel": [count_new, count_inprogress, count_completed],
        "scores": [count_high, count_mid, count_low],
        "sources_labels": list(sources.keys()),
        "sources_data": list(sources.values())
    }
    
    return templates.TemplateResponse(
        "admin/index.html", 
        {"request": request, "top_leads": top_leads, "leads": all_leads, "stats": stats}
    )

@router.get("/lead/{lead_id}/partial", response_class=HTMLResponse)
async def lead_detail_partial(lead_id: int, request: Request, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        return "<div style='padding:20px; text-align:center;'>Candidate not found</div>"
    return templates.TemplateResponse("admin/_lead_drawer.html", {"request": request, "lead": lead})

@router.get("/lead/{lead_id}", response_class=HTMLResponse)
async def lead_detail(request: Request, lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return templates.TemplateResponse(
        "admin/detail.html",
        {"request": request, "lead": lead}
    )
