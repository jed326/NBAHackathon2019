import pandas as pd

class Team():
	def __init__(self,team_id,players):
		self.team_id = team_id
		self.players = players

class Player():
	def __init__(self,team_id,player_id):
		self.total_game_score = 0
		self.total_game_pos = 0
		self.total_points_allowed = 0
		self.before_play_game_score = 0
		self.before_play_game_pos = 0
		self.team_id = team_id
		self.player_id = player_id

def main():
	finaldataframe  = []
	teams = {}
	Event_Codes=pd.read_table("Event_Codes.txt")
	Game_Lineup=pd.read_table("Game_Lineup.txt")
	Play_by_Play=pd.read_table("Play_by_Play.txt")

	unique_games = Game_Lineup.Game_id.unique()
	unique_teams = Game_Lineup.Team_id.unique()
	teams_to_players = {}
	players_to_teams = {}
	for t in unique_teams:
		playerslist = {}
		teams_to_players[t] = set(Game_Lineup.loc[Game_Lineup['Team_id'] == t, 'Person_id'])
		for x in teams_to_players[t]:
			playerslist[x] = Player(team_id=t,player_id=x)
			players_to_teams[x] = t

		teams[t] = Team(t,playerslist)
	
	for g in unique_games:
		df = Play_by_Play.loc[Play_by_Play['Game_id'] == g]
		df.sort_values(by=['Period', 'PC_Time','WC_Time','Event_Num'], ascending=[True,False,True,True])
		teamsInGame = set(Game_Lineup.loc[Game_Lineup['Game_id'] == g, 'Team_id'])
		gameObject = {}
		for x in teamsInGame:
			gameObject[x] = {'current_pos' : 0, 'current_score' : 0}
		checkdefensive= False
		prevteam = ''
		foulinprogress = False
		updatelist = []
		activeplayers = {}
		for index, row in df.iterrows():

			if row.Event_Msg_Type == 8 and foulinprogress == False:
				if row.Person1 not in activeplayers:
					teams[players_to_teams[row.Person1]].players[row.Person1].total_game_score += gameObject[players_to_teams[row.Person1]]['current_score']
					teams[players_to_teams[row.Person1]].players[row.Person1].total_game_pos += gameObject[players_to_teams[row.Person1]]['current_pos']
					for x in gameObject:
						if x != players_to_teams[row.Person1]:
							teams[players_to_teams[row.Person1]].players[row.Person1].total_points_allowed += gameObject[x]['current_score']
					activeplayers[row.Person2] = {'current_pos' : 0, 'current_score' : 0 , 'points_allowed' : 0 }
				else:
					teams[players_to_teams[row.Person1]].players[row.Person1].total_game_score  += activeplayers[row.Person1]['current_score']
					teams[players_to_teams[row.Person1]].players[row.Person1].total_game_pos  += activeplayers[row.Person1]['current_pos']
					teams[players_to_teams[row.Person1]].players[row.Person1].total_points_allowed += activeplayers[row.Person1]['points_allowed']
					del activeplayers[row.Person1]
					activeplayers[row.Person2] = {'current_pos' : 0, 'current_score' : 0, 'points_allowed' : 0 }
			elif row.Event_Msg_Type == 8:
				updatelist.append((row.Person1,row.Person2))


			if row.Event_Msg_Type == 1 or row.Event_Msg_Type == 3 or (row.Event_Msg_Type == 7 and row.Action_Type == 2):
				if row.Person1 in players_to_teams:
					currteam = players_to_teams[row.Person1]
				else:
					currteam = row.Team_id

				if row.Event_Msg_Type == 1:
					if foulinprogress == True:
								foulinprogress = False
								for y in updatelist:
									if y[0] not in activeplayers:
										teams[players_to_teams[y[0]]].players[y[0]].total_game_score += \
										gameObject[players_to_teams[y[0]]]['current_score']
										teams[players_to_teams[y[0]]].players[y[0]].total_game_pos += \
										gameObject[players_to_teams[y[0]]]['current_pos']
										for x in gameObject:
											if x != players_to_teams[y[0]]:
												teams[players_to_teams[y[0]]].players[
													y[0]].total_points_allowed += gameObject[x]['current_score']
										activeplayers[y[1]] = {'current_pos': 0, 'current_score': 0,
																	  'points_allowed': 0}
									else:
										teams[players_to_teams[y[0]]].players[y[0]].total_game_score += \
										activeplayers[y[0]]['current_score']
										teams[players_to_teams[y[0]]].players[y[0]].total_game_pos += \
										activeplayers[y[0]]['current_pos']
										teams[players_to_teams[y[0]]].players[
											y[0]].total_points_allowed += activeplayers[y[0]][
											'points_allowed']
										del activeplayers[y[0]]
										activeplayers[y[1]] = {'current_pos': 0, 'current_score': 0,
																	  'points_allowed': 0}
					gameObject[currteam]['current_score'] = gameObject[currteam]['current_score'] + row.Option1
					for x in activeplayers:
						if players_to_teams[x] != currteam:
							activeplayers[x]['current_score'] = activeplayers[x]['points_allowed'] + row.Option1
						if players_to_teams[x] == currteam:
							activeplayers[x]['current_score'] = activeplayers[x]['current_score'] + row.Option1
				elif row.Event_Msg_Type == 3 and row.Option1 == 1:
					gameObject[currteam]['current_score'] = gameObject[currteam]['current_score'] + row.Option1
					for x in activeplayers:
						if players_to_teams[x] != currteam:
							activeplayers[x]['current_score'] = activeplayers[x]['points_allowed'] + row.Option1
						if players_to_teams[x] == currteam:
							activeplayers[x]['current_score'] = activeplayers[x]['current_score'] + row.Option1
				elif row.Event_Msg_Type == 7:
					gameObject[currteam]['current_score'] = gameObject[currteam]['current_score'] + row.Option1
					for x in activeplayers:
						if players_to_teams[x] != currteam:
							activeplayers[x]['current_score'] = activeplayers[x]['points_allowed'] + row.Option1
						if players_to_teams[x] == currteam:
							activeplayers[x]['current_score'] = activeplayers[x]['current_score'] + row.Option1


			if row.Event_Msg_Type == 4 or row.Event_Msg_Type == 1 or row.Event_Msg_Type == 5 or row.Event_Msg_Type == 2 or row.Event_Msg_Type == 13  or row.Event_Msg_Type == 3:
				if row.Event_Msg_Type == 13:
					if foulinprogress == True:
								foulinprogress = False
								for y in updatelist:
									if y[0] not in activeplayers:
										teams[players_to_teams[y[0]]].players[y[0]].total_game_score += \
										gameObject[players_to_teams[y[0]]]['current_score']
										teams[players_to_teams[y[0]]].players[y[0]].total_game_pos += \
										gameObject[players_to_teams[y[0]]]['current_pos']
										for x in gameObject:
											if x != players_to_teams[y[0]]:
												teams[players_to_teams[y[0]]].players[
													y[0]].total_points_allowed += gameObject[x]['current_score']
										activeplayers[y[1]] = {'current_pos': 0, 'current_score': 0,
																	  'points_allowed': 0}
									else:
										teams[players_to_teams[y[0]]].players[y[0]].total_game_score += \
										activeplayers[y[0]]['current_score']
										teams[players_to_teams[y[0]]].players[y[0]].total_game_pos += \
										activeplayers[y[0]]['current_pos']
										teams[players_to_teams[y[0]]].players[
											y[0]].total_points_allowed += activeplayers[y[0]][
											'points_allowed']
										del activeplayers[y[0]]
										activeplayers[y[1]] = {'current_pos': 0, 'current_score': 0,
																	  'points_allowed': 0}
					gameObject[row.Team_id]['current_pos'] = gameObject[row.Team_id]['current_pos'] + 1
					for x in activeplayers:
						if players_to_teams[x] == row.Team_id:
							activeplayers[x]['current_pos'] = activeplayers[x]['current_pos'] + 1
				else:
					if checkdefensive == True and row.Event_Msg_Type == 4 and row.Person1 in players_to_teams and players_to_teams[row.Person1] != prevteam:
						if foulinprogress == True:
							foulinprogress = False
							for y in updatelist:
								if y[0] not in activeplayers:
									teams[players_to_teams[y[0]]].players[y[0]].total_game_score += \
										gameObject[players_to_teams[y[0]]]['current_score']
									teams[players_to_teams[y[0]]].players[y[0]].total_game_pos += \
										gameObject[players_to_teams[y[0]]]['current_pos']
									for x in gameObject:
										if x != players_to_teams[y[0]]:
											teams[players_to_teams[y[0]]].players[
												y[0]].total_points_allowed += gameObject[x]['current_score']
									activeplayers[y[1]] = {'current_pos': 0, 'current_score': 0,
														   'points_allowed': 0}
								else:
									teams[players_to_teams[y[0]]].players[y[0]].total_game_score += \
										activeplayers[y[0]]['current_score']
									teams[players_to_teams[y[0]]].players[y[0]].total_game_pos += \
										activeplayers[y[0]]['current_pos']
									teams[players_to_teams[y[0]]].players[
										y[0]].total_points_allowed += activeplayers[y[0]][
										'points_allowed']
									del activeplayers[y[0]]
									activeplayers[y[1]] = {'current_pos': 0, 'current_score': 0,
														   'points_allowed': 0}
						gameObject[prevteam]['current_pos'] = gameObject[prevteam]['current_pos'] + 1
						for x in activeplayers:
							if players_to_teams[x] == prevteam:
								activeplayers[x]['current_pos'] = activeplayers[x]['current_pos'] + 1
						
					elif checkdefensive == True and row.Event_Msg_Type == 4 and row.Team_id not in players_to_teams and row.Team_id != prevteam:
						if foulinprogress == True:
							foulinprogress = False
							for y in updatelist:
								if y[0] not in activeplayers:
									teams[players_to_teams[y[0]]].players[y[0]].total_game_score += \
										gameObject[players_to_teams[y[0]]]['current_score']
									teams[players_to_teams[y[0]]].players[y[0]].total_game_pos += \
										gameObject[players_to_teams[y[0]]]['current_pos']
									for x in gameObject:
										if x != players_to_teams[y[0]]:
											teams[players_to_teams[y[0]]].players[
												y[0]].total_points_allowed += gameObject[x]['current_score']
									activeplayers[y[1]] = {'current_pos': 0, 'current_score': 0,
														   'points_allowed': 0}
								else:
									teams[players_to_teams[y[0]]].players[y[0]].total_game_score += \
										activeplayers[y[0]]['current_score']
									teams[players_to_teams[y[0]]].players[y[0]].total_game_pos += \
										activeplayers[y[0]]['current_pos']
									teams[players_to_teams[y[0]]].players[
										y[0]].total_points_allowed += activeplayers[y[0]][
										'points_allowed']
									del activeplayers[y[0]]
									activeplayers[y[1]] = {'current_pos': 0, 'current_score': 0,
														   'points_allowed': 0}
						gameObject[prevteam]['current_pos'] = gameObject[prevteam]['current_pos'] + 1
						for x in activeplayers:
							if players_to_teams[x] == prevteam:
								activeplayers[x]['current_pos'] = activeplayers[x]['current_pos'] + 1
						
					if row.Person1 in players_to_teams:
						prevteam = players_to_teams[row.Person1]
					else:
						prevteam = row.Team_id
					checkdefensive = False

					if (row.Event_Msg_Type == 1 or row.Event_Msg_Type == 5):
						if foulinprogress == True:
							foulinprogress = False
							for y in updatelist:
								if y[0] not in activeplayers:
									teams[players_to_teams[y[0]]].players[y[0]].total_game_score += \
										gameObject[players_to_teams[y[0]]]['current_score']
									teams[players_to_teams[y[0]]].players[y[0]].total_game_pos += \
										gameObject[players_to_teams[y[0]]]['current_pos']
									for x in gameObject:
										if x != players_to_teams[y[0]]:
											teams[players_to_teams[y[0]]].players[
												y[0]].total_points_allowed += gameObject[x]['current_score']
									activeplayers[y[1]] = {'current_pos': 0, 'current_score': 0,
														   'points_allowed': 0}
								else:
									teams[players_to_teams[y[0]]].players[y[0]].total_game_score += \
										activeplayers[y[0]]['current_score']
									teams[players_to_teams[y[0]]].players[y[0]].total_game_pos += \
										activeplayers[y[0]]['current_pos']
									teams[players_to_teams[y[0]]].players[
										y[0]].total_points_allowed += activeplayers[y[0]][
										'points_allowed']
									del activeplayers[y[0]]
									activeplayers[y[1]] = {'current_pos': 0, 'current_score': 0,
														   'points_allowed': 0}
						gameObject[prevteam]['current_pos'] = gameObject[prevteam]['current_pos'] + 1
						for x in activeplayers:
							if players_to_teams[x] == prevteam:
								activeplayers[x]['current_pos'] = activeplayers[x]['current_pos'] + 1
					
					else:
						if row.Event_Msg_Type == 3 and (row.Action_Type == 12 or row.Action_Type == 15) and row.Option1 == 1:
							gameObject[players_to_teams[row.Person1]]['current_pos'] = gameObject[players_to_teams[row.Person1]]['current_pos'] + 1
							for x in activeplayers:
								if players_to_teams[x] == players_to_teams[row.Person1]:
									activeplayers[x]['current_pos'] = activeplayers[x]['current_pos'] + 1
						elif row.Event_Msg_Type == 3 and (row.Action_Type == 12 or row.Action_Type == 15):
							checkdefensive=True
						elif row.Event_Msg_Type == 2:
							checkdefensive=True
							if foulinprogress == True:
								foulinprogress = False
								for y in updatelist:
									if y[0] not in activeplayers:
										teams[players_to_teams[y[0]]].players[y[0]].total_game_score += \
										gameObject[players_to_teams[y[0]]]['current_score']
										teams[players_to_teams[y[0]]].players[y[0]].total_game_pos += \
										gameObject[players_to_teams[y[0]]]['current_pos']
										for x in gameObject:
											if x != players_to_teams[y[0]]:
												teams[players_to_teams[y[0]]].players[
													y[0]].total_points_allowed += gameObject[x]['current_score']
										activeplayers[y[1]] = {'current_pos': 0, 'current_score': 0,
																	  'points_allowed': 0}
									else:
										teams[players_to_teams[y[0]]].players[y[0]].total_game_score += \
										activeplayers[y[0]]['current_score']
										teams[players_to_teams[y[0]]].players[y[0]].total_game_pos += \
										activeplayers[y[0]]['current_pos']
										teams[players_to_teams[y[0]]].players[
											y[0]].total_points_allowed += activeplayers[y[0]][
											'points_allowed']
										del activeplayers[y[0]]
										activeplayers[y[1]] = {'current_pos': 0, 'current_score': 0,
																	  'points_allowed': 0}

			if row.Event_Msg_Type == 13:
				for x in activeplayers:
					teams[players_to_teams[x]].players[x].total_game_score += activeplayers[x]['current_score']
					teams[players_to_teams[x]].players[x].total_game_pos += activeplayers[x]['current_pos']
					teams[players_to_teams[x]].players[x].total_points_allowed += activeplayers[x]['points_allowed']
				activeplayers = {}

			if row.Event_Msg_Type == 6:
				foulinprogress = True

		for team in gameObject:
			for p in teams[team].players:
				if(teams[team].players[p].total_game_pos != 0):
					dictt = {}
					dictt['OffRtg'] = ((teams[team].players[p].total_game_score / teams[team].players[p].total_game_pos) * 100)
					dictt['DefRtg'] = ((teams[team].players[p].total_points_allowed / teams[team].players[p].total_game_pos) * 100)
					dictt['Game_ID'] = g
					dictt['Player_ID'] = p
					finaldataframe.append(dictt)
				else:
					dictt = {}
					dictt['OffRtg'] = 0
					dictt['DefRtg'] = 0
					dictt['Game_ID'] = g
					dictt['Player_ID'] = p
					finaldataframe.append(dictt)
				teams[team].players[p].total_game_score  = 0
				teams[team].players[p].total_game_pos = 0 
				teams[team].players[p].total_points_allowed = 0 
	finalz = pd.DataFrame(finaldataframe)
	print(finalz)
	finalz.to_csv('Continuous_Destroyment_Q1_BBALL.csv',index_label=False,index=False)











if __name__ ==  "__main__":
	main()