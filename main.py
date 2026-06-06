from fastapi import FastAPI

app = FastAPI()

@app.get("/sources")
def get_sources():
    return ["headhunter", "LinkedIn", "HubrCareer"]
