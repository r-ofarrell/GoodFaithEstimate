class Estimate:
    """Contains details for a Good Faith Estimate"""
    def __init__(self, rate, date, new_or_update, low_sessions=12, high_sessions=24):
        self.rate = rate
        self.date = date
        self.new_or_update = new_or_update
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

    def __init__(self, name, rate, location):
        self.name = name
        self.rate = rate
        self.location = location
