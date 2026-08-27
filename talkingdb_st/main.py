from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from talkingdb_st import __version__
from talkingdb_st.api import crawl

OPENAPI_TAGS = [
    {
        "name": "Crawl & Train",
        "description": (
            "Fetch pages from configured seed URLs, chunk their content, "
            "and push it into package-document-search."
        ),
    },
]

app = FastAPI(
    title="TalkingDB Search Trainer",
    description=(
        "Generic crawl-and-train pipeline: fetches pages from configured "
        "seed URLs or a sitemap, chunks their content, and indexes it into "
        "package-document-search for vector and keyword search."
    ),
    version=__version__,
    openapi_tags=OPENAPI_TAGS,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(crawl.router)
app.include_router(crawl.sitemap_router)
