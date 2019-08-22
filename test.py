import os, sys
sys.path.append(os.path.join(os.path.dirname(__file__), "subscribersim"))
import datetime
import unittest
from subscribersim.models import Customer, Plan
import helpers


class TestCustomer(unittest.TestCase):
    """Each test depends on the success of the previous test"""

    def test_new_customer(self):
        """Creates a new customer."""
        person = Customer("person Jeffords", "yoghurt", "tjeffords@99.com")

        self.assertTrue(person.name,"Customer name not provided")
        self.assertTrue(person.password, "Customer password not provided")
        self.assertTrue(person.email, "Customer email not provided")
        #print (person)

    def test_select_plan(self):
        """Creates a new customer and selects a plan.

        Verifies that the customer's order history has only the one correct item.
        Verifies that the customer's desired plan was selected.
        """
        desired_plan = "Infinite"

        person = Customer("Jake Peralta", "diehardfan", "jperaltiago@99.com")
        person.select_plan(desired_plan)

        self.assertEqual(person.current_plan.name, desired_plan, "Plan not selected")
        self.assertEqual(len(person.events[1:]), 1, "Transactions incorrect")
        self.assertEqual(person.events[-1][1], desired_plan, "Plan not selected")
        #print (person)

    def test_move_to_plan(self):
        """Creates a new customer, selects a plan, moves to a new plan.

        Verifies that the customer's current plan was updated.
        Verifies that the customer's old plan is recorded on the order history.
        Verifies that only two transactions are shown on the order history.
        """
        old_plan = "Single"
        new_plan = "Plus"

        person = Customer("Rosa Diaz", "summerskiss", "rosadiaz@99.com")
        person.select_plan(old_plan)
        person.move_to_plan(new_plan)

        self.assertEqual(person.current_plan.name, new_plan, "Plan did not move")
        self.assertEqual(person.events[1][1], old_plan, "Plan not selected")
        self.assertEqual(person.events[-1][1], new_plan, "Plan not moved")
        self.assertEqual(len(person.events[1:]), 2, "Transactions incorrect")
        #person.print_table()


    def test_add_website_to_current_plan(self):
        """Creates a new custohelpers.mer, selects a plan, adds one website.

        Verifies that the customer's website was created.
        Verifies that customer's website list has only one entry.
        """
        desired_plan = "Single"

        person = Customer("Raymond Holt", "gerdieforlife", "cptrayholt@99.com")
        person.select_plan(desired_plan)
        person.add_website_to_current_plan("weichelbrauniac.com", False)

        self.assertTrue(person.websites[-1].url,"Website not created")
        self.assertEqual(len(person.websites), 1, "Site not on list")
        #print (person)


    def test_remove_website(self):
        """Creates a new customer, selects a plan, adds one website
        then removes the website.

        Verifies that the site was added to the list
        Verifies that the website count is zero after removal
        """

        desired_plan = "Infinite"

        person = Customer("Amy Santiago", "deweydecimal", "amysantiago@99.com")
        person.select_plan(desired_plan)

        person.add_website_to_current_plan("laminateheaven.com", False)
        self.assertEqual(person.current_plan_website_count, 1, "Website not added")
        person.remove_website("http://laminateheaven.com")

        urls = [w.url for w in person.websites]
        self.assertNotIn("http://laminateheaven.com",urls,"Website not removed")
        self.assertEqual(person.current_plan_website_count, 0, "Website not removed")
        #person.print_table()


    def test_customer_downgrade(self):
        """Creates a customer, selects a plan and downgrades to a lesser plan within current year.

        Verifies that 'balance' equal to a plan price after they select or change plan
        Verifies spend since the last plan change is correct to the second
        Verifies refund after downgrade = (previous balance - last spend - new plan price)
        """

        # Cuatomer sign up and select a plan
        start_plan = "Plus"
        end_plan = "Single"
        start_price = Plan.plans[start_plan][1]
        end_price = Plan.plans[end_plan][1]
        NOW = datetime.datetime.now()

        person = Customer("Terry Jeffords", "yoghurt", "terryjeffords@99.com")
        person.select_plan(start_plan, NOW)

        # Calculate the spend since select_plan based on the seconds elapsed
        intervals = helpers.get_seconds_in_current_year(NOW)
        last_event = helpers.datetime_get_last_event(person)
        two_months_after = helpers.datetime_months_hence(last_event, 2)
        seconds_elapsed = helpers.get_seconds_difference(two_months_after, last_event)
        spend = round( (((start_price / intervals) * seconds_elapsed)), 2 )

        # Move to the plan
        person.move_to_plan("Single", two_months_after)

        self.assertEqual(person.spend[-1],spend,"Incorrect spend")
        self.assertEqual(person.balances[-1],person.current_plan.price,"Incorrent balance")
        self.assertEqual(person.balances[-1], (person.balances[-2] - person.spend[-1] - person.refunds[-1]), "Refund incorrect")

        person.print_table()

    def test_customer_upgrade(self):
        """Creates a customer, selects a plan and moves to different plans within a year.

        Verifies that no refund is applicable.
        Verifies that payment after upgrade = (new plan price  - previous balance - last spend)
        """

        # Customer sign up and select a plan
        start_plan = "Single"
        end_plan = "Infinite"
        start_price = Plan.plans[start_plan][1]
        end_price = Plan.plans[end_plan][1]
        NOW = datetime.datetime.now()

        person = Customer("Amy Santiago", "deweydecimal", "amysantiago@99.com")
        person.select_plan(start_plan, NOW)

        # Calculate the spend since select_plan based on the seconds elapsed
        intervals = helpers.get_seconds_in_current_year(NOW)
        last_event = helpers.datetime_get_last_event(person)
        four_months_after = helpers.datetime_months_hence(last_event, 4)
        seconds_elapsed = helpers.get_seconds_difference(four_months_after, last_event)
        spend = round( (((start_price / intervals) * seconds_elapsed)), 2 )

        # Move to the plan
        person.move_to_plan(end_plan, four_months_after)

        self.assertEqual(person.refunds[-1], 0, "Refund not applicable")
        self.assertEqual(person.payments[-1], round ((end_price - (person.balances[-2] - person.spend[-1])), 2), "Payment incorrect")

        person.print_table()


if (__name__ == '__main__'):
    unittest.main()
