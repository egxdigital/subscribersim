"""Models

This module contains the models for this simple subscription system.
When a customer moves to a new plan, a refund or charge is computed
and the customer's balance is updated.

Example:

        jake = models.Customer(fullname, password, email)
        jake.select_plan(start_plan, datetimeobj)
        jake.add_website(website, bool)
        jake.move_to_plan(end_plan, relativedeltaobj)

Attributes:
    No module level variables.

Todo:
    * Change event tuple to namedtuple to benefit from field names
    * Initialize buffers with empty list instead of zero (will simplify references to the list)

"""

from tabulate import tabulate
import helpers

class Customer():
    """
    Customers have a name, a password an email address, a subscription and a
    subscription renewal date.

    A customer should be able to subscribe to plan, move from a plan to another
    and manage websites (add/update/remove) according to their plan.

    Args:
        name (string)                       : Customer's full name
        password (string)                   : Customer's password
        email (string)                      : Customer's email

    Attributes:
        current_plan (obj:Plan)             : Current active plan
        plan_renewal_date (obj:datetime)    : Date one year from the date of last purchase

        events (list:tup(datetime,str,str)) : List of events of form (datetime, str, str)
        websites (list:Website)             : List of website objects
        website_count (int)                 : Number of active websites
        events (list:tup(datetime,str,str)) : List of events including their timestamp and type
        balances (list:float)               : Customer's account value after each event
        payments (list:float)               : Each payment is added to this list
        refunds (list:float)                : Each refund is added to this list
        spend (list:float)                  : The current spend at the time of each plan change
        ROWS (list:list)                    : Input for the tabulate method

    """

    def __init__(self, name, password, email):
        # Buffers and counters
        self.events = [0]
        self.balances = [0]
        self.payments = [0]
        self.refunds = [0]
        self.spend = [0]
        self.websites = []
        self.ROWS = []
        self.website_count = 0
        # Attributes
        self.name = name
        self.password = password
        self.email = email
        self.current_plan = None
        self.plan_renewal_date = None


    def select_plan(self, name, now=helpers.datetime_now()):
        """ Select a plan for a new customer.

        select_plan updates the payments, balances and events buffers then sets the
        current plan and renewal date for the customer.

        Args:
            name (string)  : Name of the desired plan.
            now (datetime) : A round datetime object returned by helpers.datetime_now()

        Returns:
            True if successful. Raises an exception otherwise.
        """

        if self.current_plan == None:
            # Log payment, update balances, update events
            type = "start"
            payment = self._get_price(name)
            self.payments.append(payment)
            self.balances.append(payment)
            self.events.append((now, name, type))

            # Set the current plan
            self.current_plan = Plan(name)
            self.plan_renewal_date = helpers.datetime_months_hence(now, 12)
            self._init_table()
            self._add_table_row()
            return True
        else:
            raise Exception("select plan")


    def move_to_plan(self, name, now=helpers.datetime_now()):
        """ Move customer to a different plan if they are subscribed.

        move_to_plan takes a desired plan name, and a timestamp and evaluates
        the proration on the mid-cycle subscription change. If the customer
        has more websites than maximum at the time of downgrade, the most recent
        sites are removed first. In the real world the customer would be prompted
        before website deletion after downgrade.

        Args:
            name (string)  : Name of the desired plan.
            now (datetime) : A round datetime object returned by helpers.datetime_now()

        Returns:
            True if successful. Raises an exception otherwise.
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

            # PRORATION LOGIC
            current_bal = round ((self.balances[-1] - amount_spent), 2 )
            new_plan_price = self._get_price(name)

            # Transfer
            if (new_plan_price == current_bal):
                self.balances.append(new_plan_price)

            # Upgrade
            elif (new_plan_price > current_bal):
                type = "upgrade"
                payment_due = round( (new_plan_price - current_bal), 2 )
                self.payments.append(payment_due)
                self.balances.append(new_plan_price)

            # Downgrade
            else:
                type = "downgrade"
                # Reduce the number of websites if greater than desired plan max
                site_count = self.website_count
                max_sites_allowed = Plan.plans[name][0]
                if site_count > max_sites_allowed:
                    for _ in range(site_count - max_sites_allowed):
                        self.websites.pop()
                        self.website_count -= 1

                # Refund customer and reset balance
                self._refund(current_bal - new_plan_price)
                self.balances.append(new_plan_price)

            # Set the plan
            self.current_plan = Plan(name)

            # Set the new renewal date
            self._set_renewal_date(now)

            # Queue the event and update the table
            self.events.append((now, name, type))
            self._add_table_row()

            return True

        else:
            raise Exception("move to plan")


    def add_website(self, url, has_database, now=helpers.datetime_now()):
        """Adds a website given a domain name and a database option

        Args:
            url (string)        : URL in the form 'domain.com'
            has_database (bool) : If True, 'https://' will prefix the URL else 'http://'

        Returns:
            True if successful. Raises an exception otherwise.
        """
        site_count = self.website_count
        max_sites = self.current_plan.max_sites

        if site_count == max_sites:
            raise Exception("Reached site limit")

        self.websites.append(Website(self, url, has_database))
        self.website_count += 1
        return True


    def remove_website(self, name, now=helpers.datetime_now()):
        """Removes website from the list of websites given the full url

        Args:
            name (string)        : Full URL in the form http://domain.com

        Returns:
            True if successful. Raises an exception otherwise.
        """
        site_count = self.website_count
        max_sites = self.current_plan.name[0]

        if site_count == 0:
            raise Exception("No sites to remove")

        for website in self.websites:
            if website.url == name:
                self.websites.remove(website)
                self.website_count -= 1

        return True


    def print_table(self):
        """Prints the table created by _init_table and _add_table_row"""
        print ("\n\n", tabulate(self.ROWS, headers="firstrow",),"\n\n")


    def __str__(self):
        return f"\ncustomer: {self.name}\ncurrent plan: {self.current_plan}\nactive sites: {self.website_count}\nevents: {len(self.events[1:])}\nlast spend:{self.spend[-1]}"


    def _init_table(self):
        """Initializes the header row of a table when select_plan is called"""
        self.ROWS.append(["customer", "event", "plan", "renews on", "websites", "payments", "last payment", "last spend", "last refund", "balance"])


    def _add_table_row(self):
        """Creates a table row when select_plan and move_to_plan are called"""
        self.ROWS.append([self.name, self.events[-1][2], self.current_plan, self.plan_renewal_date, self.website_count,
                          len(self.payments[1:]), self.payments[-1], self.spend[-1], self.refunds[-1], self.balances[-1]])


    def _set_renewal_date(self,now):
        self.plan_renewal_date = helpers.datetime_months_hence(now, 12)


    def _add_event(self,name,price,tim):
        """ Logs every purchase or change of subscription with plan name, price and timestamp."""
        self.events.append((name,price,tim))


    def _get_price(self, name):
        """Returns the plan price from Plan.plan(dict)"""
        return Plan.plans[name][1]


    def _get_current_spend(self, price, intervals, elapsed):
        """Returns the amount spent since the last plan purchase"""
        return round( ((price / intervals) * elapsed), 2 )


    def _refund(self, bal):
        """Logs the refund amount when applicable"""
        self.refunds.append(bal)



class Plan():
    """Plans have a name, a price, and a limited number of websites.

    Args:
        name (str)      : 'Single', 'Plus', or 'Infinite'

    Attributes:
        plans (dict)    : Contains price options and max allowed sites
        name (string)   : Name of the plan
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

    Websites are created by customers with Customer.add_website()

    Args:
        domain_name (str)       : URL in the form 'domain.com'
        customerobj (Customer)  : Customer name is read from Customer object
        has_database (bool)     : If True, 'https://' will prefix the URL else 'http://'

    Attributes:
        url (str)               : Full URL in the form http://domain.com
        customer (str)          : Taken from Customer object
        has_database (bool)     : True if database is required, False otherwises
    """
    def __init__(self, customerobj, domain_name, has_database=False):
        self.database = has_database
        self.customer = customerobj.name

        if has_database:
            self.url = "https://" + domain_name
        self.url = "http://" + domain_name


    def __str__(self):
        return f'{self.url} owned by: {self.customer}'


if __name__ == '__main__':
    pass
