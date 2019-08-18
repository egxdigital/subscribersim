import unittest
from subscribersim.models import Customer

class TestCustomer(unittest.TestCase):

    def test_new_customer(self):
        """Creates a new customer.

        Verifies that the right fields were supplied.
        """
        person = Customer("Terry Jeffords", "yoghurt", "tjeffords@99.com")

        self.assertTrue(person.name,"Customer name not provided")
        self.assertTrue(person.password, "Customer password not provided")
        self.assertTrue(person.email, "Customer email not provided")

    def test_select_plan(self):
        """Creates a new customer and selects a plan.

        Verifies that the customer's order history has only the one correct item.
        Verifies that the customer's desired plan was selected.
        """
        desired_plan = "Infinite"

        person = Customer("Jake Peralta", "diehardfan", "jperaltiago@99.com")
        person.select_plan(desired_plan)

        self.assertEqual(person.current_plan.name, desired_plan, "Plan not selected")
        self.assertEqual(len(person.order_history), 1, "Transactions incorrect")
        self.assertEqual(person.order_history[0][0], desired_plan, "Plan not selected")

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
        self.assertEqual(person.order_history[0][0], old_plan, "Plan not selected")
        self.assertEqual(person.order_history[1][0], new_plan, "Plan not moved")
        self.assertEqual(len(person.order_history), 2, "Transactions incorrect")

    def test_add_website_to_current_plan(self):
        """Creates a new customer, selects a plan, adds one website.

        Verifies that the customer's website was created.
        Verifies that customer's website list has only one entry.
        """
        desired_plan = "Plus"

        person = Customer("Raymond Holt", "gerdieforlife", "cptrayholt@99.com")
        person.select_plan(desired_plan)
        person.add_website_to_current_plan("weichelbrauniac.com", False)

        self.assertTrue(person.websites[0].url,"Website not created")
        self.assertTrue(person.websites, "Website not added")

    def test_remove_website(self):
        """
        Creates a new customer, selects a plan, adds one website
        then removes the website.

        Verifies that the site was added to the list
        Verifies that the website count is zero after removal
        """

        desired_plan = "Single"

        person = Customer("Amy Santiago", "deweydecimal", "amysantiago@99.com")
        person.select_plan(desired_plan)
        person.add_website_to_current_plan("laminateheaven.com", False)
        self.assertEqual(len(person.websites),1,"Website not removed")
        person.remove_website("http://laminateheaven.com")
        urls = [w.url for w in person.websites]
        self.assertNotIn("http://laminateheaven.com",urls,"Website not removed")


if (__name__ == '__main__'):
    unittest.main()
