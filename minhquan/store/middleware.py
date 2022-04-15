from .models import Partner

class PartnerAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request.partner = None
        partner_id = request.session.get('partner_id', 0)
        if partner_id:
            partner = Partner.objects.get(pk=partner_id)
            if partner:
                request.partner = partner
        elif request.user.is_authenticated and request.user.email:
            Partner.objects.get_or_create(
                email=request.user.email,
                defaults={
                    'user': request.user,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'full_name': request.user.first_name + ' ' + request.user.last_name
                                if (request.user.first_name or request.user.last_name)
                                else '',
                }
            )

        response = self.get_response(request)
        
        # Code to be executed for each request/response after
        # the view is called.

        return response
    
    def process_template_response(self, request, response):
        response.context_data['partner'] = request.partner
        return response