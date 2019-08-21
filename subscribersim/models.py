from tabulate import tabulate
from helpers import *

class Customer():
    """
    Customers have a name, a password an email address,
    a subscription and a subscription renewal date.

    A customer should be able to subscribe to
    plan, move from a plan to another and manage
    websites (add/update/remove) according to his
    plan.

    Attributes:
        name (string): customer's full name
        password (string): customer's password
        email (string): customer's email
        events (list:tup): list of transactions
        websites (list:Website): list of website objects
        current_plan (Plan): current active plan
        current_plan_renewal_date (TBD):
        current_plan_website_count (int)
    """
    

    def __init__(self, name, password, email):

        self.events = [0]
        self.balances = [0]
        self.payments = [0]
        self.refunds = [0]
        self.spend = [0]
        self.websites = [0]
        self.current_plan = None
        self.current_plan_website_count = 0
        self.current_plan_renewal_date = None
        self.name = name
        self.password = password
        self.email = email


    def select_plan(self, name, now=datetime_now()):
        """ Select a plan for a new customer.

        select_plan updates the payments, balances and events buffers
        then sets the current plan and renewal date for the customer.
        """

        if self.current_plan == None:
            # Log payment, update balances, update events
            payment = self._get_price(name)
            self.payments.append(payment)
            self.balances.append(payment)
            self.events.append((now, name))

            # Set the current plan
            self.current_plan = Plan(name)
            self.current_plan_renewal_date = datetime_months_hence(now, 12)
            self._init_table()
            self._add_table_row()

        else:
            raise Exception("select plan")


    def move_to_plan(self, name, now=datetime_now()):
        """ Move customer to a different plan if they are subscribed.

        move_to_plan takes a desired plan name, and a timestamp and evaluates
        the proration on the mid-cycle subscription change.
        """
        seconds_in_year = get_seconds_in_current_year(now)

        # Verify that we already have a plan
        # Verify that we are not trying to move to the same plan
        current = self.current_plan
        plan_name = self.current_plan.name

        if current != None and plan_name != name:
            # Select the plan
            self.current_plan = Plan(name)

            # Set the new renewal date
            self.current_plan_renewal_date = datetime_months_hence(now, 12)

            # Calculate the amount spent to date while in previous plan
            prev = self.events[-1][0]
            old_price = self._get_price(plan_name)
            elapsed = datetime_to_time(now) - datetime_to_time(prev)
            amount_spent = self._get_current_spend(old_price,seconds_in_year,elapsed)
            self.spend.append(amount_spent)

            # Proration logic
            current_bal = self.balances[-1] - amount_spent
            new_plan_price = self._get_price(name)

            if (new_plan_price == current_bal):
                self.balances.append(new_plan_price)

            elif (new_plan_price > current_bal):
                payment_due = round( (new_plan_price - current_bal), 2 )
                self.payments.append(payment_due)
                self.balances.append(new_plan_price)

            else:
                balance = round( (self.balances[-1] - amount_spent), 2 )
                self._refund(balance - new_plan_price)
                self.balances.append(new_plan_price)

            self.events.append((now, name))
            self._add_table_row()

        else:
            raise Exception("move to plan")


    def add_website_to_current_plan(self, url, has_database):
       

        site_count = self.current_plan_website_count
        max_sites = self.current_plan.max_sites

        if site_count == max_sites:
            raise Exception("Reached site limit")

        self.websites.append(Website(url, has_database))
        self.current_plan_website_count += 1


    def remove_website(self, name):

        site_count = self.current_plan_website_count
        max_sites = self.current_plan.name[0]

        if site_count == 0:
            raise Exception("No sites to remove")

        for website in self.websites:
            if website.url == name:
                self.websites.remove(website)


    def _add_event(self,name,price,tim):
        """ Logs every purchase or change of subscription
        with plan name, price and timestamp.
        """
        self.events.append((name,price,tim))


    def _get_price(self, name):
        """Returns the plan price from Plan.plan (dict)"""
        return Plan.plans[name][1]


    def _get_current_spend(self, old, tp, e):
        """Returns the amount spent since the last plan purchase"""
        return round( ((old / tp) * e), 2 )


    def _refund(self, bal):
        """Logs the refund amount when applicable"""
        self.refunds.append(bal)

    
    def __str__(self):
        return f"customer: {self.name}, current plan: {self.current_plan}, active sites: {self.current_plan_website_count}, transactions: {len(self.events)}"
    
    
    ROWS = []
    
    
    def _add_table_row(self):
        self.ROWS.append([self.name, self.current_plan.name, self.current_plan_renewal_date, 
                          len(self.payments[1:]), self.payments[-1], self.spend[-1], self.refunds[-1], self.balances[-1]])
    
    
    def _init_table(self):
        self.ROWS.append(["customer", "plan", "renews on", "payments", "last payment", "last spend", "last refund", "balance"])
        
    
    def print_table(self):
        print (
                tabulate(   
                            #["customer", "plan", "payments", "last payment", "last spend", "last refund", "balance"],
                            self.ROWS,
                            
                            headers="firstrow",
                        )
              )


class Plan():
    """Has a name, a price, and a number of websites allowance.

    Attributes:
        name (string):
        price (float):
        max_sites:
    """

    plans = {"Single": (1,49), "Plus":(3,99), "Infinite":(None,249)}

    def __init__(self, name):
        if name not in Plan.plans.keys():
            raise Exception(f'Plan')
        self.name = name
        self.price = Plan.plans.get(name)[1]
        self.max_sites = Plan.plans.get(name)[0]

    def __str__(self):
        return f'{self.name}'


class Website():
    """ Has an URL, and a customer

    Attributes:
        url (string)
        customer: (Customer)
    """
    def __init__(self, domain_name, has_database):
        self.database = has_database

        if has_database:
            self.url = "https://" + domain_name
        self.url = "http://" + domain_name

    def __str__(self):
        return f'Site located at {self.url}'


if __name__ == '__main__':
    
    # Event 1
    # payments: 0, last payment: 0, current spend: 0, lastrefund 0, balance: 0
    terry = Customer("Terry Jeffords", "yoghurt", "terryjeffords@99.com")
    
    
    # Event 2
    # payments: 1, last payment: 99, current spend: 0, lastrefund 0, balance: 99
    terry.select_plan("Plus", datetime.now())
   

    # Event 3
    # payments: 1, last payment: 99, current spend: 24.75, lastrefund 25.25, balance: 49
    terry.move_to_plan("Single", datetime_months_hence(datetime_get_last_event(terry), 2))
    

    # Event 4
    # payments: 2, last payment: 208.17, current spend: 8.17, last refund 25.25, balance: 249
    terry.move_to_plan("Infinite", datetime_months_hence(datetime_get_last_event(terry), 1))
    

    # Event 5
    # payments: 2, last payment: 208.17, current spend: 62.25, refund 87.75, balance: 99
    terry.move_to_plan("Plus", datetime_months_hence(datetime_get_last_event(terry), 3))
    
    terry.print_table()
    print(terry)
    
