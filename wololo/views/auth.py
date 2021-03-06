from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponse
from django.contrib import messages
from wololo.initFirestore import get_db, get_auth
from wololo.firebaseUser import firebaseUser
from wololo.commonFunctions import getGameConfig
import urllib.request
import urllib.error

db = get_db()
auth = get_auth()
gameConfig = getGameConfig()

def myuser_login_required(f):
    def wrap(request, *args, **kwargs):
        #this check the session if userid key exist, if not it will redirect to login page
        if( 'loggedIn' not in request.session):
            messages.error(request,'Log in in order to continue.')
            return redirect('landingPage')
             
        return f(request, *args, **kwargs)
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

def createAccount(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        username = request.POST.get("username")
        if email is '' or password is '' or username is '':
            messages.error(request, 'Please fill all the fields.')
            return redirect("registerPage")

        print(db.collection('players').get())
        
        import urllib.request as urllib2
        try: 
            auth.create_user_with_email_and_password(email, password)
        except urllib2.HTTPError as err:
            if err.code == 400:
                messages.error(request, 'That email is already registered.')
            else:
                raise
            return redirect("registerPage")


        for player in db.collection('players').get():
            userInfo = player._data
            print (userInfo['username'])
            if userInfo['username'] == username:
                messages.error(request, 'Username exists.')
                return redirect("registerPage")

        user = auth.sign_in_with_email_and_password(email, password)
        user_id = user['localId']
        db.collection('players').document(user_id).set({
            "clan": "",
            "regionSelected": False,
            "username": username,
            "points" : 0,
            "reports" : [],
            'unviewedReportExists' : False
        })
        user = auth.refresh(user['refreshToken']) #now we have 1 hour expiry token
        auth.send_email_verification(user['idToken'])
        print(user)
        messages.error(request, 'Please verify your email.')
        return redirect("landingPage")

def verifyLogin(request):
    if request.method == 'POST':
        email=request.POST.get("email")
        password = request.POST.get("password")
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            if auth.get_account_info(auth.current_user['idToken'])['users'][0]['emailVerified'] is False:
                messages.error(request,'Email is not verified.')
                # auth.send_email_verification(user['idToken'])
                return redirect("landingPage")
                
            request.session['userID'] = user['localId']
            request.session['loggedIn'] = True
            user = firebaseUser(request.session['userID'])
            print(user.regionSelected)
            if user.regionSelected == False :
                return redirect("selectRegion")
            
        except:
            messages.error(request,'Email or password is not correct.')
            return redirect("landingPage")
        
        return redirect(settings.LOGIN_REDIRECT_URL)
    return HttpResponse("why y r here")

def logout(request):
    del request.session['userID']
    del request.session['selected_village_index']
    del request.session['loggedIn']
    request.session.modified = True

    return redirect(settings.LANDING_PAGE_REDIRECT_URL)
