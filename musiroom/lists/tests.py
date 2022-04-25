from django.test import TestCase

# Create your tests here.


"""
tester : après un delete d'listObj, l'ordre des objects est toujours respecté
ex : list (a 1) (b 2) (c 3) (d 4) (e 5)
    si on delete (b 2) -> (a 1) (c 2) (d 3) (e 4)

tester : un nouvel listObj est toujours placé à la fin de la liste et l'ordre est bien respecté

"""
