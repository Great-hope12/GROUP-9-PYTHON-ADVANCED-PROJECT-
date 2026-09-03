"""
This Calculates an estimated TRIP BUDGET from a destination  and miscellaneous
"""
from validators import validate_amount, validate_duration, validate_currency_code

class TripBudget:

    def __init__(self, destination, duration_days, currency, daily_accommodation, daily_food, daily_transportation, daily_activities, daily_miscellaneous,):
        self.destination = destination
        self.duration_days = validate_duration(duration_days)
        self.currency = validate_currency_code(currency)

        #This Stores each daily rate only after checking if its vaild
        self.daily_accommodation = validate_amount(daily_accommodation, "daily accommodation cost")
        self.daily_food = validate_amount(daily_food, "daily food cost")
        self.daily_transportation = validate_amount(daily_transportation, "daily transportation cost")
        self.daily_activities = validate_amount(daily_activities, "daily activities cost")
        self.daily_miscellaneous = validate_amount(daily_miscellaneous, "daily miscellaneous cost")

    def accommodation_cost(self):
        """Total accommodation cost for the whole trip."""
        return round(self.daily_accommodation * self.duration_days, 2)

    def food_cost(self):
        """Total food cost for the whole trip."""
        return round(self.daily_food * self.duration_days, 2)

    def transportation_cost(self):
        """Total transportation cost for the whole trip."""
        return round(self.daily_transportation * self.duration_days, 2)

    def activities_cost(self):
        """Total activities cost for the whole trip."""
        return round(self.daily_activities * self.duration_days, 2)

    def miscellaneous_cost(self):
        """Total miscellaneous cost for the whole trip."""
        return round(self.daily_miscellaneous * self.duration_days, 2)

    def total_budget(self):
        """Add up every category to get the full trip budget."""
        return round( self.accommodation_cost() + self.food_cost() + self.transportation_cost() + self.activities_cost() + self.miscellaneous_cost(), 2,)

    def daily_spending_limit(self):
        """The  amount you can spend per day without going over the total budget."""
        return round(self.total_budget() / self.duration_days, 2)

    def remaining_budget(self, amount_spent_so_far):
        """How much budget is left after spending so far."""
        amount_spent_so_far = validate_amount(amount_spent_so_far, "amount spent so far")
        return round(self.total_budget() - amount_spent_so_far, 2)

    def breakdown(self):
        """A dictionary summary of every cost category."""
        return {"destination": self.destination, "duration_days": self.duration_days, "currency": self.currency, "accommodation": self.accommodation_cost(), "food": self.food_cost(), "transportation": self.transportation_cost(), "activities": self.activities_cost(), "miscellaneous": self.miscellaneous_cost(), "total_budget": self.total_budget(), "daily_spending_limit": self.daily_spending_limit(),}
