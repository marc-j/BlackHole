from django.conf import settings
from django.contrib.auth.models import User

from StringIO import StringIO
import logging                          # output hidden in rendered page Request Log area

DICTIONARY = u"""
ATTRIBUTE User-Name     1 string
ATTRIBUTE User-Password 2 string encrypt=1
"""

class AuthRadius(object):
    """
    Authenticate against a backend RADIUS server; return User object or None.
    RADIUS servers include the interface provided by RSA SecurID ACE server
    for one-time-password hardware-token authentication, but also common
    ones used by ISPs like FreeRADIUS.
    If we detect any error, return None so that sites without RADIUS
    or with bad configs fail gracefully, rather than preventing login.
    """

    def authenticate(self, username=None, password=None):
        """Check username against RADIUS server and return a User object or None.
        """
        # Do the import inside a method so we can 'return' None on error
        try:
            import pyrad.packet
            from pyrad.client import Client, Timeout
            from pyrad.dictionary import Dictionary
        except ImportError, e:
            logging.error("RADIUS couldn't import pyrad, need to install the egg: %s", e)
            return None

        # Have to convert login form's unicode to str for RADIUS
        username = username.encode('utf-8')
        password = password.encode('utf-8') # don't really need, PwCrypt() does it
        try:
            client = Client(server=settings.RADIUS_SERVER,
                            secret=settings.RADIUS_SECRET.encode('utf-8'), # avoid UnicodeDecodeError
                            dict=Dictionary(StringIO(DICTIONARY)),
                            )
        except AttributeError, e:
            logging.error("RADIUS couldn't find settings (check [local_]settings.py): %s" % e)
            return None

        req = client.CreateAuthPacket(code=pyrad.packet.AccessRequest,
                                      User_Name=username,)
        req["User-Password"] = req.PwCrypt(password)    

        logging.debug("RADIUS authenticate sending packet req=%s" % req)
        try:
            reply = client.SendPacket(req)
        except Timeout, e:
            logging.error("RADIUS Timeout contacting RADIUS_SERVER=%s RADIUS_PORT=%s: %s" % (
                settings.RADIUS_SERVER, settings.RADIUS_AUTHPORT, e))
            return None
        except Exception, e:
            logging.error("RADIUS Unknown error sending to RADIUS_SERVER=%s RADIUS_PORT=%s: %s" % (
                settings.RADIUS_SERVER, settings.RADIUS_AUTHPORT, e))
            return None

        logging.debug("RADIUS Authenticate check reply.code=%s" % reply.code)
        if reply.code == pyrad.packet.AccessReject:
            logging.warning("RADIUS Reject username=%s", username)
            return None
        elif reply.code != pyrad.packet.AccessAccept:
            logging.error("RADIUS Unknown Code username=%s reply.code=%s" % (username, reply.code))
            return None

        logging.info("RADIUS Accept username=%s" % username)
        try:
            logging.debug("RADIUS looking for existing DB username=%s" % username)
            user = User.objects.get(username=username)
            logging.info("RADIUS found existing DB user=%s" % user)
        except User.DoesNotExist:
            # Create user with disabled password so they can never 
            # auth against Django DB if RADIUS info removed.
            logging.info("RADIUS user username=%s did not exist, creating..." % username)
#            user = User(username=username)
#            user.set_unusable_password()
#            # Trying to log the 'User' object appears to throw Exception
            # which prevents returning it, thus causing first auth to fail.
#            logging.info("RADIUS created user username=%s" % username)
#            user.save()
            user = None
        return user
            
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            logging.warning("RADIUS get_user DoesNotExist user_id=%s" % user_id)
            return None
