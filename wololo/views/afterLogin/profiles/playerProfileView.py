from django.shortcuts import render, redirect
from wololo.firebaseUser import firebaseUser
import urllib.request
import urllib.error
from wololo.views.auth import myuser_login_required
from wololo.commonFunctions import getGameConfig, getVillageIndex
from wololo.helperFunctions import getPlayerInfo

gameConfig = getGameConfig()

@myuser_login_required    
def playerProfile(request, player_id, village_index=None):
    user_id = request.session['userID']
    user = firebaseUser(user_id)
    if user.regionSelected is False :
        return redirect("selectRegion")

    selected_village_index = getVillageIndex(request, user, village_index)
    if(selected_village_index == 'outOfList'):
        return redirect('playerProfile')

    playerInfo = getPlayerInfo(player_id)
    print(playerInfo)

    data = { 
        'selectedVillage': user.myVillages[selected_village_index],
        'gameConfig' : gameConfig,
        'profileOfPlayerID' : player_id,
        'profileOfPlayerInfo' : playerInfo,
        'unviewedReportExists' : user.unviewedReportExists,
        'page' : 'playerProfile'
    }
    currentUser = {}
    currentUser['id'] = user_id

    return render(request, 'profiles/playerProfile.html', {'currentUser':currentUser, 'myVillages':user.myVillages, 'data' : data})
