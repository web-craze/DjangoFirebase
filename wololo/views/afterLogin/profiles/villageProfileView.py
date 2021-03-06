from django.shortcuts import render, redirect
from wololo.firebaseUser import firebaseUser
import urllib.request
import urllib.error
from wololo.views.auth import myuser_login_required
from wololo.commonFunctions import getGameConfig, getVillageIndex
from wololo.helperFunctions import getVillageInfo

gameConfig = getGameConfig()

@myuser_login_required    
def villageProfile(request, village_id, village_index=None):
    user_id = request.session['userID']
    user = firebaseUser(user_id)
    if user.regionSelected is False :
        return redirect("selectRegion")

    selected_village_index = getVillageIndex(request, user, village_index)
    if(selected_village_index == 'outOfList'):
        return redirect('villageProfile')

    villageInfo = getVillageInfo(village_id)
    
    data = { 
        'selectedVillage': user.myVillages[selected_village_index],
        'gameConfig' : gameConfig,
        'profileOfVillageInfo' : villageInfo,
        'unviewedReportExists' : user.unviewedReportExists,
        'page' : 'villageProfile'
    }
    currentUser = {}
    currentUser['id'] = user_id

    return render(request, 'profiles/villageProfile.html', {'currentUser':currentUser, 'myVillages':user.myVillages, 'data' : data})
