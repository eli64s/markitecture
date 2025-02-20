class BaseSvgGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def render(self, content: str) -> str:
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.width} {self.height}">{content}</svg>'
