from correctPathModule import getCorrectPathByPyScript
import json
import os

MAIN_PATH = getCorrectPathByPyScript(__file__)

class dbWorker:
	def __init__(self, databaseFileName):
		self.databaseFileName = databaseFileName
		files = os.listdir(f'{MAIN_PATH}/')
		if databaseFileName not in files:
			dbData = self.getDefaultdbData()
			self.save(dbData)

	def get(self):
		with open(f'{MAIN_PATH}/{self.databaseFileName}') as file:
			dbData = json.load(file)
		return dbData

	def save(self, dbData):
		with open(f'{MAIN_PATH}/{self.databaseFileName}', 'w') as file:
			json.dump(dbData, file, indent=4, ensure_ascii=False)

	def getUserIds(self):
		dbData = self.get()
		userIds = [userId for userId in dbData['users']]
		return userIds

	def isAdmin(self, userId):
		dbData = self.get()
		permisson = dbData['users'][str(userId)]['permission']
		if permisson == 'admin': return True
		else: return False

	def userExists(self, userId):
		dbData = self.get()
		if str(userId) in dbData['users']: return True
		else: return False

	def addNewUser(self, userId, username, fullname, lang, permission='default'):
		dbData = self.get()
		dbData['users'][str(userId)] = dict(username=username,
									   fullname=fullname,
									   lang=lang,
									   permission=permission)
		self.save(dbData)

	def setInUser(self, userId, key, value):
		dbData = self.get()
		dbData['users'][str(userId)][str(key)] = value
		self.save(dbData)

	def getFromUser(self, userId, key):
		dbData = self.get()
		return dbData['users'][str(userId)][str(key)]

	def getDefaultdbData(self):
		return {
					"users": {}
				}

def main():
	db = dbWorker('database.json')
	print(db.get())

if __name__ == '__main__':
	main()

