import pendulum
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx import Document
from estimate_details import Client, Therapist, Estimate
from location_of_services import address


class GfeDocument:
    """Creates a Good Faith Estimate form and saves it in docx."""

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
        if estimate.first_year_or_additional == "Additional year":
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
            # Takes out the initial assessment and registration fee rows when
            # the estimate is for an additional year of services.
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

    def create_section1(
        self, client: "Client", estimate: "Estimate", therapist: "Therapist"
    ) -> str:
        """Reads text from a given file and auto-populates information."""
        lines = []
        with open(self.section1) as section1:
            for line in section1:
                if "{full_name}" in line:
                    lines.append(
                        line.format(
                            full_name=(
                                client.first_name + " " + client.last_name
                            ).rstrip()
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

    def create_other_sections(self, file: str) -> str:
        """Reads text from a file to use in sections of a Good Faith Estimate"""
        lines = []
        with open(file) as disclaimer:
            for line in disclaimer:
                if line == "\n":
                    lines.append(line.rstrip() + "\n\n")
                else:
                    lines.append(line.rstrip() + " ")

        return "".join(lines)

    def create_estimate_table(
            self, document_obj: 'Document', itemized_list: list
    ) -> 'Document.add_table':
        """Creates a table of itemized services for a Good Faith Estimate."""

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
    JohnDoe = Client("John", "Doe", "06/07/1988", "90837")
    RyanO = Therapist("Ryan OFarrell", 165, "Mount Pleasant")
    JohnDoeEstimate = Estimate(165, pendulum.now(), "New")
    JohnDoeGFEDocument = GfeDocument(
        "gfe_introduction.txt", "dispute.txt", JohnDoe, RyanO, JohnDoeEstimate
    )
