'''
Created on Nov 14, 2012

@author: aenima
'''
from django.core.management.base import NoArgsCommand
from black_hole_db.models import UserIdentity

class Command(NoArgsCommand):
    help = "Create Inital configuration"

    def handle_noargs(self, **options):
        selfUser = "self"
        if len(UserIdentity.objects.filter(username=selfUser)) == 0:
            user_identity = UserIdentity(username=selfUser)
            user_identity.save()
        