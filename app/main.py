from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
from library.helpers import *
from library.basemap_gen import *
from routers import twoforms, unsplash, accordion


app = FastAPI()


templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
# app.mount("/images", StaticFiles(directory="images"), name="images")

app.include_router(unsplash.router)
app.include_router(twoforms.router)
app.include_router(accordion.router)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = openfile("home.md")
    return templates.TemplateResponse("page.html", {"request": request, "data": data})


@app.get("/page/{page_name}", response_class=HTMLResponse)
async def show_page(request: Request, page_name: str):
    data = openfile(page_name+".md")
    return templates.TemplateResponse("page.html", {"request": request, "data": data})

if __name__ == '__main__':
    # the workers main function is called and then 5 seconds sleep
    worker = PlotGenerator(interval=5)
    worker.start()

    uvicorn.run(app, host="0.0.0.0", port=8501, debug=True)
    worker.terminate()
