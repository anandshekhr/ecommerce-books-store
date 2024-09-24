# middleware.py

from django.utils.deprecation import MiddlewareMixin
from .models import RequestDataLog  # Import your model for storing request data
from ua_parser import user_agent_parser
# from django.contrib.gis.geoip2 import GeoIP2
from django.conf import settings
import logging
logger = logging.getLogger('middleware')

class RequestDataMiddleware(MiddlewareMixin):
    def get_client_ip(self, request):
        """
        Get the client's IP address from the request.
        """
        # Check if the IP address is provided by a proxy or load balancer
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # The first address in the list is the client's IP address
            return x_forwarded_for.split(',')[0]
        else:
            # Otherwise, use the REMOTE_ADDR header
            return request.META.get('REMOTE_ADDR', '')
        
    def process_request(self, request):
        path = request.path
        if 'admin' in path:
            return

        # Extract relevant data from the request
        method = request.method
        body = request.body
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        ip_address = self.get_client_ip(request)
        

        # Parse the user agent string to determine if it's a mobile device
        parsed_user_agent = user_agent_parser.Parse(user_agent_string)
        device_family = parsed_user_agent['device']['family']

        # Check if the device family corresponds to a mobile device
        is_mobile = True if device_family in ['iPhone', 'iPad', 'Android', 'Windows Phone', 'BlackBerry', 'Mobile'] else False

        # Determine if the user is new or repeating based on session
        session = request.session
        if 'visited_before' in session:
            is_new_user = False
        else:
            session['visited_before'] = True
            is_new_user = True
        
        # Determine the origin country based on the user's IP address
        origin_country = 'IN'
        if ip_address:
            try:
                # geoip = GeoIP2(path=settings.GEOIP_PATH)
                # origin_country = geoip.country_code(ip_address)
                pass
            
            except Exception as e:
                origin_country = 'IN'
                logger.warning(f"Error in geolocation: {e}, default country: {origin_country}")

        # Save the request data to your database
        RequestDataLog.objects.create(
            method=method,
            path=path,
            body=body,
            user_agent=user_agent_string,
            mobile=is_mobile,
            is_new_user=is_new_user,
            client_ip=ip_address,
            country=origin_country
        )
        logger.info('log saved to database.')
