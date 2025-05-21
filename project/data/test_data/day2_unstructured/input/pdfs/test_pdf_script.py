from reportlab.pdfgen import canvas

def create_test_pdf(filename):
    c = canvas.Canvas(filename)
    c.drawString(100, 750, "This is a test PDF document")
    c.drawString(100, 700, "Testing our PDF parser functionality")
    c.save()

if __name__ == "__main__":
    create_test_pdf("project/data/unstructured/test.pdf") 