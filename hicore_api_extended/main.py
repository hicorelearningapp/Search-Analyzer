from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import (
    session_routes,
    search_routes,
    proposal_routes,
    methodology_routes,
    review_routes,
    visualization_routes,
    synthesis_routes,
    compare_routes,
    misc_routes,
    search_analyzer_routes
)

app = FastAPI(title="HICORE Research API (Extended)", description="Extended research & document processing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

# Include Routers
app.include_router(session_routes.router)
app.include_router(search_routes.router)
app.include_router(proposal_routes.router)
app.include_router(methodology_routes.router)
app.include_router(review_routes.router)
app.include_router(visualization_routes.router)
app.include_router(synthesis_routes.router)
app.include_router(compare_routes.router)
app.include_router(misc_routes.router)
app.include_router(search_analyzer_routes.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
