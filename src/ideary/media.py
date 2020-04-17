import io


def get_media_content_stream(file_id):
    from src.ideary.storage import read_image
    content = read_image(file_id=file_id)['content']
    buf = io.BytesIO()
    buf.write(content)
    buf.seek(0)
    return buf