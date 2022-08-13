class Estimate:
    """Contains details for a Good Faith Estimate"""

    def __init__(
        self,
        rate,
        date,
        first_year_or_additional,
        low_sessions=12,
        high_sessions=24,
    ):
        self.rate = rate
        self.date = date
        self.first_year_or_additional = first_year_or_additional
        self.low_sessions = low_sessions
        self.high_sessions = high_sessions
        self.low_estimate = int(self.rate) * int(self.low_sessions)
        self.high_estimate = int(self.rate) * int(self.high_sessions)


class Client:
    """Creates a client for a Good Faith Estimate"""

    def __init__(self, first_name, last_name, date_of_birth, services_sought):
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.services_sought = services_sought


class Therapist:
    """Creates a therapist"""

    def __init__(
        self, first_name, last_name, license_type, tax_id, npi, location
    ):
        self.first_name = first_name
        self.last_name = last_name
        self.license_type = license_type
        self.tax_id = tax_id
        self.npi = npi
        self.location = location
