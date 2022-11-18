import psycopg2

class BotDB:
	def __init__(self, db_uri):
		""""Conectarea cu baza de date"""
		self.conn = psycopg2.connect(db_uri, sslmode="require")
		self.cursor = self.conn.cursor()

	def user_exists(self,user_id):
		""""Controlarea daca useru este in DB"""
		result = self.cursor.execute("SELECT id FROM settings WHERE (user_id) = (%s);",[user_id])
		self.conn.commit()
		return bool(self.cursor.fetchone()[0])

	def get_user_id(self, user_id):
		""""Primim id userului in basa de date dupa user_id in telegram"""
		result = self.cursor.execute("SELECT id FROM settings WHERE (user_id) = (%s)", [user_id,])
		return self.cursor.fetchone()[0]
	def get_user_bot_id(self,id):
		""""Primim tg id userului in bot dupa id in basa de date"""
		result = self.cursor.execute("SELECT user_id FROM settings WHERE (id) = (%s)", [id,])
		return self.cursor.fetchone()
	def settings_get(self,user_id):

		result = self.cursor.execute("SELECT nr_cuvinte,temperature,lang,chat_ai FROM settings WHERE user_id = (%s)",(user_id,))
		self.conn.commit()
		return self.cursor.fetchone()

	def chat_ai(self,state,user_id):
		result = self.cursor.execute("UPDATE settings SET chat_ai = (%s) WHERE user_id = (%s)",(state,user_id,))
		return self.conn.commit()

	def lungimea_textului(self,nr_cuvinte,user_id):
		result = self.cursor.execute("UPDATE settings SET nr_cuvinte = (%s) WHERE user_id = (%s)",(nr_cuvinte,user_id,))
		return self.conn.commit()
	def limba_ai(self,limba,user_id):
		result = self.cursor.execute("UPDATE settings SET lang = (%s) WHERE user_id = (%s)", (limba,user_id,))
		return self.conn.commit()
	def temperature_ai(self,temperature,user_id):
		result = self.cursor.execute("UPDATE settings SET temperature = (%s) WHERE user_id = (%s)", (temperature,user_id,))
		return self.conn.commit()
	def get_translate(self,user_id):
		result = self.cursor.execute("SELECT lang,last_response FROM settings WHERE user_id = (%s)",(user_id,))
		self.conn.commit()
		return self.cursor.fetchone()

	def get_lng(self,user_id):
		result = self.cursor.execute("SELECT lang FROM settings WHERE user_id = (%s)",(user_id,))
		self.conn.commit()
		return self.cursor.fetchone()
		
	def get_response(self,user_id):
		result = self.cursor.execute("SELECT last_response FROM settings WHERE user_id = (%s)",(user_id,))
		self.conn.commit()
		return self.cursor.fetchone()
	def add_response(self,response,user_id):
		result = self.cursor.execute("UPDATE settings SET last_response = (%s) WHERE user_id = (%s)",(response,user_id,))
		return self.conn.commit()

	def add_last_request(self,request,user_id):
		result = self.cursor.execute("UPDATE settings SET last_request = (%s) WHERE user_id = (%s)",(request,user_id,))
		return self.conn.commit()
	def get_last_request(self,user_id):
		result = self.cursor.execute("SELECT last_request FROM settings WHERE user_id = (%s)",(user_id,))
		self.conn.commit()
		return self.cursor.fetchone()[0]

	def get_all_users(self):
		result = self.cursor.execute("SELECT user_id FROM settings")
		self.conn.commit
		return self.cursor.fetchall()
	def add_user(self, user_id):
		""""Adaugam userul in baza de date"""
		self.cursor.execute("INSERT INTO settings (user_id) VALUES(%s)",(user_id,))
		return self.conn.commit()
		
	def close(self):
		#deconectarea de la db
		self.conn.close()
