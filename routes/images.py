from fastapi import APIRouter, UploadFile
import os

router = APIRouter()

@router.post("/image")
async def upload_image(file: UploadFile):
    DIR = './image'
    if not os.path.exists(DIR):
        os.makedirs(DIR)

    content = await file.read()
    extension_index = file.filename.rindex('.')
    # filename_extension = file.filename[extension_index+1:]
    filename = file.filename[:extension_index]

    image_extensions = ('.jpg', '.jprg', '.png', '.gif', '.bmp', '.tiff', '.svg')
    if not file.filename.lower().endswith(image_extensions):
        return { "detail": "This file is not image file." }
    
    with open(os.path.join(DIR, filename), "wb") as fp:
        fp.write(content)
    return {"filename": filename}
