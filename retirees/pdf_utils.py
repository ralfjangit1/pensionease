"""
PDF generation for retiree certificates and reports, using ReportLab.
Each function returns raw PDF bytes so views can stream them directly
as an HttpResponse without touching the filesystem.
"""
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER

GREEN = colors.HexColor("#123A2A")
GOLD = colors.HexColor("#B8935A")


def _base_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="OrgName", parent=styles["Title"], fontSize=16,
        textColor=GREEN, alignment=TA_CENTER, spaceAfter=2,
    ))
    styles.add(ParagraphStyle(
        name="OrgSub", parent=styles["Normal"], fontSize=8.5,
        textColor=colors.grey, alignment=TA_CENTER, spaceAfter=14,
    ))
    styles.add(ParagraphStyle(
        name="DocTitle", parent=styles["Heading2"], fontSize=13,
        textColor=colors.black, alignment=TA_CENTER, spaceBefore=6, spaceAfter=14,
    ))
    return styles


def generate_certificate_pdf(retiree, document_type_label, certificate_no, computation=None):
    """Builds a one-page certificate PDF for a single retiree."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter,
        topMargin=0.9 * inch, bottomMargin=0.9 * inch,
        leftMargin=1 * inch, rightMargin=1 * inch,
    )
    styles = _base_styles()
    story = []

    story.append(Paragraph("PensionEase Administration", styles["OrgName"]))
    story.append(Paragraph("OFFICE OF RETIREMENT SERVICES", styles["OrgSub"]))
    story.append(HRFlowable(width="100%", color=GOLD, thickness=1))
    story.append(Spacer(1, 10))
    story.append(Paragraph(document_type_label, styles["DocTitle"]))

    rows = [
        ["Retiree Name", retiree.full_name()],
        ["Employee ID", retiree.employee_id],
        ["Position", retiree.position],
        ["Department", retiree.department or "—"],
        ["Years of Service", f"{retiree.years_of_service()} years"],
        ["Date Retired", retiree.date_retired.strftime("%B %d, %Y")],
    ]
    if computation:
        rows.append(["Monthly Pension", f"PHP {computation.net_monthly_pension:,.2f}"])
    rows.append(["Certificate No.", certificate_no])

    table = Table(rows, colWidths=[2.2 * inch, 3.3 * inch])
    table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, colors.HexColor("#DCD3BE")),
    ]))
    story.append(table)
    story.append(Spacer(1, 50))

    sig_table = Table(
        [["_____________________________", "_____________________________"],
         ["Pension Officer", "Department Head"]],
        colWidths=[2.6 * inch, 2.6 * inch],
    )
    sig_table.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TEXTCOLOR", (0, 1), (-1, 1), colors.grey),
        ("TOPPADDING", (0, 1), (-1, 1), 2),
    ]))
    story.append(sig_table)

    doc.build(story)
    return buffer.getvalue()


def generate_retiree_list_report_pdf(retirees):
    """Builds a tabular report PDF listing all retirees."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                             topMargin=0.75 * inch, bottomMargin=0.75 * inch)
    styles = _base_styles()
    story = [
        Paragraph("PensionEase Administration", styles["OrgName"]),
        Paragraph("RETIREE MASTER LIST", styles["OrgSub"]),
        HRFlowable(width="100%", color=GOLD, thickness=1),
        Spacer(1, 12),
    ]

    data = [["Employee ID", "Name", "Position", "Date Retired", "Status"]]
    for r in retirees:
        data.append([
            r.employee_id, r.full_name(), r.position,
            r.date_retired.strftime("%b %d, %Y"), r.get_status_display(),
        ])

    table = Table(data, colWidths=[1.1 * inch, 1.9 * inch, 1.5 * inch, 1.2 * inch, 0.9 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#DCD3BE")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7F3E9")]),
    ]))
    story.append(table)
    doc.build(story)
    return buffer.getvalue()
