import time

class Customer():
    """
    Customer a name, a password an email address,
    a subscription and a subscription renewal date.

    A customer should be able to subscribe to
    plan, move from a plan to another and manage
    websites (add/update/remove) according to his
    plan.

    Attributes:
        name (string): customer's first name
        password (string):
        email (string):
        order_history (list:tup):
        websites (list:Website):
        current_plan (Plan):
        current_plan_renewal_date ():
        current_plan_website_count (int)

    Methods:
        select_plan:    Subscribe to a plan after becoming
                        a customer.
        move_to_plan:   Change plan if already subscribed
        add_website:    Add website to plan
        remove_website: Remove website from plan
        update_website: Change domain or database option
        _update_order_history
    """

    def __init__(self, name, password, email):

        self.order_history = []
        self.websites = []
        self.current_plan = None
        self.current_plan_website_count = 0
        self.name = name
        self.password = password
        self.email = email


    def __str__(self):

        return f""" Customer: {self.name},
                    Current plan: {self.current_plan},
                    Active sites: {self.current_plan_website_count},
                    Transactions: {len(self.order_history)},
                """


    def _update_order_history(self,name,price,tim):
        """
        Logs every purchase or change of subscription
        with plan name, price and timestamp.
        """

        self.order_history.append((name,price,tim))


    def select_plan(self, name='Subscription'):
        """
        Customer can select a plan if they have no
        current plan.
        """

        if self.current_plan == None:
            self.current_plan = Plan(name)
            tim = time.time()
            self._update_order_history(
                                        self.current_plan.name,
                                        self.current_plan.price,
                                        tim,
                                      )
            return
        self.current_plan = self.current_plan


    def move_to_plan(self, name):
        """
        Customer can move to a different plan if
        they currently have a plan.
        """

        current = self.current_plan
        plan_name = self.current_plan.name

        if current != None and plan_name != name:
            self.current_plan = Plan(name)
            tim = time.time()
            self._update_order_history(
                                        self.current_plan.name,
                                        self.current_plan.price,
                                        tim,
                                      )
            return
        print ("Plan not moved")


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


class Plan(object):
    """
    Has a name, a price, and a number of websites allowance.

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
