from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import database

def export_sales_report(filename):
    data = database.get_all_orders()
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 50, "Sales Report")
    y = height - 80
    c.drawString(50, y, "ID | Stock Name | Quantity | Total Price | Date")
    y -= 20
    for order in data:
        line = f"{order[0]} | {order[1]} | {order[2]} | ${order[3]:.2f} | {order[4]}"
        c.drawString(50, y, line)
        y -= 20
        if y < 50:
            c.showPage()
            y = height - 50
    c.save()
