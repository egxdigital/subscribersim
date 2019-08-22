"""Subscribersim Example

This module demonstrates a sequence of interactions with the subscribersim
objects and their methods. In this example, a user selects a plan and

Example:

        $ python subscribersim.py

Attributes:
    No module level variables.

To do:
    * Add a few more interactions.

"""

import models
import helpers

start_amy = "Plus"
start_jak = "Infinite"

if (__name__ == '__main__'):
    """Jake is a character from the show Brooklyn 99. His website, password choices
    and subscription change frequency reveal who he is.
    """

    # Jake takes the infinite plan and three websites.
    # Jake is not known for being good with his finances.
    jake = models.Customer("Jake Peralta", "diehardfan", "@jakeperalta99.com")
    jake.select_plan(start_jak, helpers.datetime_now())
    jake.add_website("superdupercop.com", has_database="True")
    jake.add_website("iamjohnmclane.com", has_database="False")
    jake.add_website("iheartpuzzles.com", has_database="False")
    jake.move_to_plan("Single", helpers.datetime_months_hence(helpers.datetime_get_last_event(jake), 4))

    # Jake realizes he needs those sites again
    jake.move_to_plan("Plus", helpers.datetime_months_hence(helpers.datetime_get_last_event(jake), 2))
    jake.add_website("iamjohnmclane.com", has_database="False")
    jake.add_website("iheartpuzzles.com", has_database="False")

    # """Jake runs out of cash and decides to go back to the Single plan
    jake.move_to_plan("Single", helpers.datetime_months_hence(helpers.datetime_get_last_event(jake), 4))

    jake.print_table()
