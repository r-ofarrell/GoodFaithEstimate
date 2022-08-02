import pendulum
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx import Document
#from dateutil.relativedelta import relativedelta
from estimate_details import Client, Therapist, Estimate
from location_of_services import address


class GfeDocument:
    def __init__(self, section1, section2, client, therapist, estimate):
        self.section1 = section1
        self.section2 = section2


        low_estimate = [
            ("Admin-\nistrative fee", "None", "None", "25", "1", "25"),
            (
                "Initial evaluation",
                "90971",
                "None",
                str(therapist.rate),
                "1",
                str(therapist.rate),
            ),
            (
                "Psycho-\ntherapy",
                str(client.services_sought),
                "None",
                str(therapist.rate),
                str(int(estimate.low_sessions)),
                str(estimate.low_estimate),
            ),
        ]

        high_estimate = [
            ("Admin-\nistrative fee", "None", "None", "25", "1", "25"),
            (
                "Initial evaluation",
                "90971",
                "None",
                str(therapist.rate),
                "1",
                str(therapist.rate),
            ),
            (
                "Psycho-\ntherapy",
                str(client.services_sought),
                "None",
                str(therapist.rate),
                str(int(estimate.high_sessions)),
                str(estimate.high_estimate),
            ),
        ]

        document = Document()

        heading = document.add_heading(
            "Life Resources Good Faith Estimate", level=1
        )
        heading.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        document.add_paragraph(
            self.create_section1(client, estimate, therapist)
        )
        document.add_page_break()
        if estimate.new_or_update == "Update":
            document.add_heading(
                "Itemized estimate for 12 session course of treatment", level=2
            )
            self.create_estimate_table(document, low_estimate[2:])
            document.add_heading(
                "Itemized estimate for 24 session course of treatment", level=2
            )
            self.create_estimate_table(document, high_estimate[2:])
            document.add_paragraph(
                f"\nEstimate range: ${int(estimate.low_estimate)}-"
                f"{int(estimate.high_estimate)}"
                "\n\nAddress where services will be provided:"
                f"\n{address(therapist.location)}"
            )
        else:
            document.add_heading(
                "Itemized estimate for 12 session course of treatment", level=2
            )
            self.create_estimate_table(document, low_estimate)
            document.add_heading(
                "Itemized estimate for 24 session course of treatment", level=2
            )
            self.create_estimate_table(document, high_estimate)
            document.add_paragraph(
                f"\nEstimate range: ${int(estimate.low_estimate) + int(therapist.rate) + 25}-"
                f"{int(estimate.high_estimate) + int(therapist.rate) + 25}"
                "\n\nAddress where services will be provided:"
                f"\n{address(therapist.location)}"
            )
        p = document.add_paragraph(self.create_other_sections(self.section2))
        p.add_run(
            "\n\nThis Good Faith Estimate is not a contract. It does not "
            "obligate you to accept the services listed above."
        ).bold = True

        document.save("prototype.docx")

    def create_section1(self, client, estimate, therapist):
        lines = []
        with open(self.section1) as section1:
            for line in section1:
                if "{full_name}" in line:
                    lines.append(
                        line.format(full_name=(client.first_name + ' ' + client.last_name).rstrip()
                    )
                        )

                elif "{date_of_birth}" in line:
                    lines.append(
                        line.format(
                            date_of_birth=client.date_of_birth
                        ).rstrip()
                        + "\n"
                    )

                elif "{date}" in line:
                    lines.append(
                        line.format(
                            date=estimate.date.strftime("%x").rstrip() + "\n"
                        )
                    )

                elif "{therapist_name}" in line:
                    lines.append(
                        line.format(therapist_name=therapist.name).rstrip()
                        + "\n"
                    )

                elif line == "\n":
                    lines.append("\n\n")

                else:
                    lines.append(line.rstrip() + " ")

        return "".join(lines)

    def create_other_sections(self, file):
        lines = []
        with open(file) as disclaimer:
            for line in disclaimer:
                if line == "\n":
                    lines.append(line.rstrip() + "\n\n")
                else:
                    lines.append(line.rstrip() + " ")

        return "".join(lines)

    def create_estimate_table(self, document_obj, itemized_list):

        table = document_obj.add_table(rows=1, cols=6)

        headers = [
            "Service",
            "Service code",
            "Diagnosis",
            "Cost",
            "Quantity",
            "Estimate",
        ]

        header_cell = table.rows[0].cells

        for index, item in enumerate(headers):
            header_cell[index].text = item

        for i in itemized_list:
            row_cells = table.add_row().cells
            for index, item in enumerate(i):
                row_cells[index].text = item

        return table


if __name__ == "__main__":
    client = Client('John', 'Doe', '06/07/1988', '90837')
    therapist = Therapist('Ryan OFarrell', 165, 'Mount Pleasant')
    estimate = Estimate(165, pendulum.now(), 'New')
    gfe = GfeDocument('gfe_introduction.txt', 'dispute.txt', client, therapist, estimate)
