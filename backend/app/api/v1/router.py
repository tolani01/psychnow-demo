"""
API v1 Main Router
Combines all endpoint routers
"""
from fastapi import APIRouter
from app.api.v1 import auth, intake, consents, reports, providers, admin, websocket, telemedicine, clinical_insights, patient_portal, billing, compliance, feedback

# Create main API router
api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(consents.router, prefix="/consents", tags=["Consents"])
api_router.include_router(intake.router, prefix="/intake", tags=["Intake"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(providers.router, prefix="/provider", tags=["Providers"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])
api_router.include_router(telemedicine.router, prefix="/telemedicine", tags=["Telemedicine"])
api_router.include_router(clinical_insights.router, prefix="/clinical-insights", tags=["Clinical Insights"])
# api_router.include_router(screeners.router, prefix="/screeners", tags=["Screeners"])  # TODO: Implement screeners endpoint
api_router.include_router(patient_portal.router, prefix="/patient-portal", tags=["Patient Portal"])
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_router.include_router(compliance.router, prefix="/compliance", tags=["Compliance"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])

@api_router.get("/")
async def api_root():
    """API v1 root endpoint"""
    return {
        "message": "PsychNow API v1",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "docs": "/api/docs",
            "auth": "/api/v1/auth",
            "intake": "/api/v1/intake",
            "reports": "/api/v1/reports",
            "providers": "/api/v1/provider",
            "admin": "/api/v1/admin",
            "telemedicine": "/api/v1/telemedicine",
            "screeners": "/api/v1/screeners",
            "patient_portal": "/api/v1/patient-portal",
            "billing": "/api/v1/billing",
            "compliance": "/api/v1/compliance",
        }
    }

