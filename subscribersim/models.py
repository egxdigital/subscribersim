from tabulate import tabulate
import helpers

class Customer():
    """
    Customers have a name, a password an email address,
    a subscription and a subscription renewal date.

    A customer should be able to subscribe to
    plan, move from a plan to another and manage
    websites (add/update/remove) according to his
    plan.

    Attributes:
        name (string)                       : customer's full name
        password (string)                   : customer's password
        email (string)                      : customer's email
        events (list:tup(datetime,str))     : list of select_plan and move_to_plan events
        websites (list:Website)             : list of website objects
        current_plan (obj:Plan)             : current active plan
        plan_renewal_date (obj:datetime)    : date one year from the date of last purchase
        website_count (int)                 : number of active websites
    """


    def __init__(self, name, password, email):

        self.events = [0]
        self.balances = [0]
        self.payments = [0]
        self.refunds = [0]
        self.spend = [0]
        self.websites = []
        self.ROWS = []
        self.current_plan = None
        self.website_count = 0
        self.plan_renewal_date = None
        self.name = name
        self.password = password
        self.email = email


    def select_plan(self, name, now=helpers.datetime_now()):
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
            self.plan_renewal_date = helpers.datetime_months_hence(now, 12)
            self._init_table()
            self._add_table_row()

        else:
            raise Exception("select plan")


    def move_to_plan(self, name, now=helpers.datetime_now()):
        """ Move customer to a different plan if they are subscribed.

        move_to_plan takes a desired plan name, and a timestamp and evaluates
        the proration on the mid-cycle subscription change.
        """
        seconds_in_year = helpers.get_seconds_in_current_year(now)

        # Verify that we already have a plan
        # Verify that we are not trying to move to the same plan
        current = self.current_plan
        plan_name = self.current_plan.name

        if current != None and plan_name != name:

            # Calculate the amount spent to date while in previous plan
            prev = self.events[-1][0]
            old_price = self._get_price(plan_name)
            elapsed = helpers.datetime_to_time(now) - helpers.datetime_to_time(prev)
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

            # Select the plan
            self.current_plan = Plan(name)
            # Set the new renewal date
            self.plan_renewal_date = helpers.datetime_months_hence(now, 12)
            self.events.append((now, name))
            self._add_table_row()

        else:
            raise Exception("move to plan")


    def add_website(self, url, has_database):
        """Adds a website given a domain name and a database option"""
        site_count = self.website_count
        max_sites = self.current_plan.max_sites

        if site_count == max_sites:
            raise Exception("Reached site limit")

        self.websites.append(Website(self, url, has_database))
        self.website_count += 1


    def remove_website(self, name):
        """Removes website from the list of websites given the full url"""
        site_count = self.website_count
        max_sites = self.current_plan.name[0]

        if site_count == 0:
            raise Exception("No sites to remove")

        for website in self.websites:
            if website.url == name:
                self.websites.remove(website)
                self.website_count -= 1


    def __str__(self):
        return f"\ncustomer: {self.name}\ncurrent plan: {self.current_plan}\nactive sites: {self.website_count}\nevents: {len(self.events[1:])}\nlast spend:{self.spend[-1]}"


    def _add_event(self,name,price,tim):
        """ Logs every purchase or change of subscription with plan name, price and timestamp."""
        self.events.append((name,price,tim))


    def _get_price(self, name):
        """Returns the plan price from Plan.plan (dict)"""
        return Plan.plans[name][1]


    def _get_current_spend(self, price, intervals, elapsed):
        """Returns the amount spent since the last plan purchase"""
        return round( ((price / intervals) * elapsed), 2 )


    def _refund(self, bal):
        """Logs the refund amount when applicable"""
        self.refunds.append(bal)


    def _init_table(self):
        """Initializes the header row of a table when select_plan is called"""
        self.ROWS.append(["customer", "plan", "renews on", "payments", "last payment", "last spend", "last refund", "balance"])


    def _add_table_row(self):
        """Creates a table row when select_plan and move_to_plan are called"""
        self.ROWS.append([self.name, self.current_plan.name, self.plan_renewal_date,
                          len(self.payments[1:]), self.payments[-1], self.spend[-1], self.refunds[-1], self.balances[-1]])


    def print_table(self):
        """Prints the table created by _init_table and _add_table_row"""
        print ("\n\n",
                tabulate(
                            #["customer", "plan", "payments", "last payment", "last spend", "last refund", "balance"],
                            self.ROWS,

                            headers="firstrow",
                        )
              )


class Plan():
    """Plans have a name, a price, and a limited number of websites.

    Attributes:
        name (string)   : Name of the plan (Single, Plus, Infinite)
        price (float)   : Price in dollars
        max_sites (int) : Number of websites allowed
    """

    plans = {"Single": (1,49), "Plus":(3,99), "Infinite":(None,249)}

    def __init__(self, name):
        """Takes a plan name and sets the price and maximum number of sites"""
        if name not in Plan.plans.keys():
            raise Exception(f'Plan')
        self.name = name
        self.price = Plan.plans.get(name)[1]
        self.max_sites = Plan.plans.get(name)[0]

    def __str__(self):
        return f'{self.name}'


class Website():
    """ Websites have an URL, a database option and a customer.

    Attributes:
        url (str)           : Domain name of website
        has_database (bool) : Database option
        customer: (str)     : Customer's full name
    """
    def __init__(self, customerobj, domain_name, has_database):
        """Takes a domain name in the form name.com and database option and sets url"""
        self.database = has_database
        self.customer = customerobj.name

        if has_database:
            self.url = "https://" + domain_name
        self.url = "http://" + domain_name

    def __str__(self):
        return f'{self.url} owned by: {self.customer}'


if __name__ == '__main__':
    person = Customer("Amy Santiago", "deweydecimal", "amysantiago@99.com")
    person.select_plan("Infinite")
    person.add_website_to_current_plan("laminateheaven.com", False)
    person.add_website_to_current_plan("smallbookstore.com", False)
    person.add_website_to_current_plan("syntaxandsemantics.com", False)
    person.add_website_to_current_plan("crosswordcrazy.com", False)
    person.remove_website("http://crosswordcrazy.com")

    print (person.website_count)
    for site in person.websites:
        print(site)
