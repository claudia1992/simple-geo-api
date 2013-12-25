from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from decorators import *
from api import *
from api.models import PostalCode, Recipe
import phonenumbers


from rest_framework import viewsets
# from serializers import PostalCodeSerializer

from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework import filters
from rest_framework import generics
# from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions

from rest_framework import permissions
from rest_framework.throttling import UserRateThrottle

class MyUserPermissions(permissions.BasePermission):
    """
    Handles permissions for users.  The basic rules are

     - owner may GET, PUT, POST, DELETE
     - nobody else can access
     """

    def has_object_permission(self, request, view, obj):

        # check if user is owner
        return request.user == obj


class PostalCodeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PostalCode
        fields = ('country', 'postal_code', 'region', 'latitude', 'longitude')

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')

class RecipeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Recipe
        fields = ('name', 'definition')

class PostalCodeView(generics.ListAPIView):
#    country = self.kwargs['country']
    queryset = PostalCode.objects.all()
    throttle_classes = []
#    throttle_classes = (UserRateThrottle,)
#    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PostalCodeSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_fields = ('postal_code', 'country', 'region')

class PostalCodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = PostalCode.objects.all()
    serializer_class = PostalCodeSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (MyUserPermissions, )

class RecipeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
#    model = Recipe
    permission_classes = (MyUserPermissions, )
#    serializer_class = UserSerializer

class ExampleAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        username = request.META.get('X-Mashape-Authorization')
        if not username:
            return None
        user = username
        print 'auth', user

#        try:
#            user = User.objects.get(username=username)
#        except User.DoesNotExist:
#            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)

@csrf_exempt
@rest_json()
def blerg(request, s):
    pass

@csrf_exempt
@rest_json()
def dump(request):
    resp = {}
    resp['get'] = {k:unicode(v) for k,v in request.GET.items()}
    resp['meta'] = {k:unicode(v) for k,v in request.META.items()}
    print request.user
    return resp

@csrf_exempt
@rest_json()
def phonenumber(request, s):
    country = request.GET.get('country')
    p = phonenumbers.parse(s, country)
    possible = phonenumbers.is_possible_number(p)
    valid = phonenumbers.is_valid_number(p)
    resp = {
        'isPossible' : possible,
        'isValid' : valid,
    }
    remote = request.META.get('REMOTE_ADDR')
    user = request.META.get('HTTP_X_MASHAPE_USER')

    if possible and valid:
        resp_deets = {
            'countryCode' : p.country_code,
            'nationalNumber' : p.national_number,
            'e164' : phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.E164),
            'international' : phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
            'national' : phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.NATIONAL),
            'rfc3966' : phonenumbers.format_number(p, phonenumbers.PhoneNumberFormat.RFC3966),
            'location' : geocoder.description_for_number(p, "en"),
            'country' : geocoder.country_name_for_number(p, 'en')
        }
        resp = dict(resp.items() + resp_deets.items())
    return resp
#    qs = request.META.get('QUERY_STRING', '')
#    qs = API_KEY_STRIPPER.sub('', qs)
#    if qs:
#        qs = '?' + qs
#    uri = uri + qs
#    return sources.hds.get(uri)

@csrf_exempt
@rest_json()
def postalcode(request, country_code, postal_code):
    row = PostalCode.objects.get(country=country_code, postal_code=postal_code)
    d = row.__dict__
    del d['_state']
    del d['id']
    d['latitude'] = float(d['latitude'])
    d['longitude'] = float(d['longitude'])
    print d
    return d

    try:
        row = PostalCode.objects.get(country=country_code, postal_code=postal_code)
        return row.__dict__
    except Exception as e:
        return e
