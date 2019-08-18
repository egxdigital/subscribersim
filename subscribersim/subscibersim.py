from customer import Customer

if (__name__ == '__main__'):
    Terry = Customer("Terry Jeffords", "yoghurt", "tjeffords@99.com")
    print(Terry)

    Terry.select_plan("Single")
    print(Terry)

    Terry.move_to_plan("Single")
    print(Terry)

    print(Terry.Order_History)

    Terry.move_to_plan("Plus")
    print(Terry)
    print(Terry.Order_History)
