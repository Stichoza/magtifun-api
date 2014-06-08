import json

import urllib
import urllib2
import cookielib

import lxml
import lxml.html
import re

from htmlparse import htmldata

### Magtifun

class Magtifun(object):

	# URL patterns
	URL_SMS_SEND	= "http://www.magtifun.ge/scripts/sms_send.php"
	URL_CHECK		= "http://www.magtifun.ge/scripts/profile_check.php"
	URL_BASE		= "http://www.magtifun.ge/"
	URL_QUERY		= "index.php?lang=en&page=%s" # force english for parsing

	# URL params
	CODE_BALANCE	= 1
	CODE_CONTACTS	= 5
	CODE_ACCOUNT	= 7
	CODE_HISTORY	= 10
	CODE_LOGIN		= 11

	username	= ""
	password	= ""
	recipients	= []
	message		= ""
	cookieFile	= None
	loginStatus	= None
	msgStatus	= ""
	log			= []

	cookieJar	= None
	opener		= None

	def __init__(self, username, password):

		# cookieJar and opener
		self.cookieJar = cookielib.CookieJar()
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar))
		urllib2.install_opener(self.opener)

		self.username = username
		self.password = password
		self.authorize()

	def getUrl(self, code, full = False):
		return (self.URL_BASE if full else "") + (self.URL_QUERY %  code)

	def authorize(self):
		data = dict(
			act			= 1,
			user		= self.username,
			password	= self.password
		)
		self.sendRequest(self.CODE_LOGIN, data)
		self.loginStatus = self.sendRequest(self.URL_CHECK)

	def sendRequest(self, code, data = []):
		req = urllib2.Request(
			self.getUrl(code, True) if isinstance(code, (int, long)) else code,
			urllib.urlencode(data))
		res = urllib2.urlopen(req).read()
		return res

	def clear(self):
		self.recipients = []
		self.message = ""

	def isLoggedIn(self):
		return self.loginStatus != "not_logged_in"

	def addRecipient(self, number):
		self.recipients.append(number)
		# return self

	def setMessage(self, msg):
		self.message = msg;
		# return self

	def send(self):
		data = {
			recipients: ','.join(self.recipients),
			message_body: self.message
		}
		response = self.sendRequest(self.URL_SMS_SEND, data)
		self.msgStatus = response
		self.clear()
		return response == "success"

	def getCredits(self):
		html = lxml.html.fromstring(self.sendRequest(self.CODE_BALANCE))
		return int(htmldata(html, "span.xxlarge"))

	def getAccountInfo(self):
		result = {}
		html = lxml.html.fromstring(self.sendRequest(self.CODE_ACCOUNT))
		result["username"]	= htmldata(html, "input#user_name", 0, 'value')
		result["fullname"]	= htmldata(html, "div.tbl_header .center_text")
		result["number"]	= htmldata(html, "input[disabled]", 0, 'value')
		result["email"]		= htmldata(html, "input#mail", 0, 'value')
		result["image"]		= htmldata(html, "input#user_pic", 0, 'value')
		#if (!substr_count($result["image"], "://"))
		#	$result["image"] = "http://magtifun.ge/" . $result["image"];
		result["credits"]	= int(htmldata(html, "span.xxlarge"))
		result["balance"]	= int(htmldata(html, "form .dark", 2))
		return result

	def getContacts(self):
		html = self.sendRequest(self.CODE_CONTACTS)
		data = html.split("Generate Contacts Array")[1].split("</script>")[0]
		contacts = []
		for match in re.findall('(Array\(")+(.+)+("\);)', data):
			chunk = match[1].split('","')
			contacts.append({
				'id': int(chunk[0]),
				'names': {
					'first': chunk[1],
					'middle': chunk[2],
					'last': chunk[3]
				},
				'fullname':  chunk[1] + (' ' + chunk[2] if chunk[2].__len__() else '') + (' ' + chunk[3] if chunk[3].__len__() else ''),
				'number': chunk[4], # TODO support multiple numbers
				'gender': 'male' if chunk[5] == "1" else 'female',
				'birthday': chunk[7]
			})
		return contacts
		

	def getHistory(sefl, page = 1):
		# $result = array();
		# $html = str_get_html($this->sendRequest(self::CODE_HISTORY, array("cur_page" =>
		# 		$page)));
		# $messages = $html->find("div.sms_list table");
		# $result["curent_page"] = intval($page);
		# $result["total_pages"] = count($html->find("span.page_number"));
		# if (!$result["total_pages"])
		# 	$result["total_pages"] = 1;
		# $result["history"] = array();
		# foreach ($messages as $msg) {
		# 	$_pushArray = array();
		# 	// Contact
		# 	$_pushArray["contact"] = trim($msg->find("p.message_list_recipient span.red", 0)->
		# 		plaintext);
		# 	// Number
		# 	if (empty($_pushArray["contact"])) {
		# 		$_pushArray["number"] = $msg->find("p.message_list_recipient span.red", 1)->
		# 			plaintext;
		# 	} else {
		# 		$_pushArray["number"] = $msg->find("p.message_list_recipient span.gray", 0)->
		# 			plaintext;
		# 	}
		# 	$_pushArray["number"] = preg_replace('/[^\d+]+/', '', $_pushArray["number"]);
		# 	// Time
		# 	$_pushArray["time"] = strtotime(trim(str_replace("\r\n", " ", $msg->find(".date_div",
		# 		0)->plaintext)));
		# 	// Time string
		# 	$_pushArray["time_str"] = date("d.m.Y H:i:s", $_pushArray["time"]);
		# 	// Message text
		# 	$_pushArray["message"] = $msg->find("p.msg_text", 0)->plaintext;
		# 	// Delivery status
		# 	$_pushArray["delivered"] = !(substr_count($msg->find("p.message_list_recipient",
		# 		0)->lastChild()->plaintext, "Not") > 0);

		# 	$result["history"][] = $_pushArray;
		# }
		# return $result;
		pass