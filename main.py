#!/usr/bin/env python

import webapp2
import json

### Magtifun

class ClassName(object):

	# URL patterns
	URL_SMS_SEND= "http://www.magtifun.ge/scripts/sms_send.php"
	URL_CHECK	= "http://www.magtifun.ge/scripts/profile_check.php"
	URL_BASE	= "http://www.magtifun.ge/"
	URL_QUERY	= "index.php?lang=en&page=%s"

	# URL params
	CODE_BALANCE		= 1
	CODE_CONTACTS		= 5
	CODE_ACCOUNT_INFO	= 7
	CODE_HISTORY		= 10
	CODE_LOGIN			= 11

	username	= ""
	password	= ""
	recipients	= []
	message		= ""
	cookieFile	= None
	loginStatus	= None
	msgStatus	= ""
	log			= []

	def __init__ (self, username, password):
		self.username = username
		self.password = password
		self.authorize()

	#public function __destruct() {
	#	unlink($this->cookieFile);
	#}

	def getUrl(self, code, full = False):
		return (self.URL_BASE if full else "")
			+ (self.URL_QUERY %  code)

	def logCookie(self):
		#echo "\n\n--- Cookie:\n" . file_get_contents($this->cookieFile) . "---\n\n";
		pass

	def authorize(self):
		data = {
			"act": 1,
			"user": self.username,
			"password": self.password
		}
		self.sendRequest(self.CODE_LOGIN, $data)
		self.loginStatus = self.sendRequest(self.URL_CHECK)

	def sendRequest(self, code, data = []):
		$ch = curl_init(self::URL_BASE);
		$curlConfig = array(
			CURLOPT_URL => is_integer($code) ? $this->getUrl($code, true) : $code,
			CURLOPT_POST => true,
			CURLOPT_RETURNTRANSFER => true,
			CURLOPT_POSTFIELDS => $data,
			CURLOPT_COOKIE => "user_name=" . $this->username . "; user_password=" . md5($this->
				password));
		if ($code == self::CODE_LOGIN) {
			$this->cookieFile = tempnam("/tmp", "CURLCOOKIE");
			$curlConfig[CURLOPT_COOKIEJAR] = $this->cookieFile;
		} else {
			$curlConfig[CURLOPT_COOKIEFILE] = $this->cookieFile;
		}
		curl_setopt_array($ch, $curlConfig);
		$result = curl_exec($ch);
		curl_close($ch);
		$this->log[] = (is_integer($code)) ? "(big data, not logged)" : $result;
		return $result;
	}

	private function clear() {
		$this->recipients = array();
		$this->message = "";
	}

	public function isLoggedIn() {
		return $this->loginStatus != "not_logged_in";
	}

	public function addRecipient($number) {
		$this->recipients[] = $number;
		return $this;
	}

	public function setMessage($msg) {
		$this->message = $msg;
		return $this;
	}

	public function send() {
		$msgData = array("recipients" => implode(",", $this->recipients), "message_body" =>
				$this->message);
		$response = $this->sendRequest(self::URL_SMS_SEND, $msgData);
		$this->msgStatus = $response;
		$this->clear();
		return ($response == "success");
	}

	public function getCredits() {
		$html = str_get_html($this->sendRequest(self::CODE_BALANCE));
		return trim($html->find("span.xxlarge", 0)->plaintext);
	}

	public function getAccountInfo() {
		$result = array();
		$html = str_get_html($this->sendRequest(self::CODE_ACCOUNT_INFO));
		$result["username"] = trim($html->find("input#user_name", 0)->value);
		$result["fullname"] = trim($html->find("div.tbl_header .center_text", 0)->
			plaintext);
		$result["number"] = trim($html->find("input[disabled]", 0)->value);
		$result["email"] = trim($html->find("input#mail", 0)->value);
		$result["image"] = trim($html->find(".fb_img", 0)->src);
		if (!substr_count($result["image"], "://"))
			$result["image"] = "http://magtifun.ge/" . $result["image"];
		$result["credits"] = trim($html->find("span.xxlarge", 0)->plaintext);
		$result["balance"] = trim($html->find("form .dark", 2)->plaintext);
		return $result;
	}

	public function getContacts() {
		$html = $this->sendRequest(self::CODE_CONTACTS);
		$html = explode("Generate Contacts Array", $html);
		$html = explode("</script>", $html[1]);
		$data = explode("Array(", $html[0]);
		$json = "[";
		$count = count($data);
		for ($i = 1; $i < count($data); $i++) {
			$json .= "[" . strtok($data[$i], ")") . "]";
			if ($i != $count - 1)
				$json .= ",\n";
		}
		$json .= "]";
		$contacts = json_decode($json);
		$result = array();
		foreach ($contacts as $e) {
			$result[] = array(
				"name" => $e[1] . (empty($e[2]) ? "" : " " . $e[2]) . " " . $e[3],
				"number" => $e[4],
				"gender" => $e[5] ? "male" : "female",
				);
		}
		return $result;
	}

	public function getHistory($page = 1) {
		$result = array();
		$html = str_get_html($this->sendRequest(self::CODE_HISTORY, array("cur_page" =>
				$page)));
		$messages = $html->find("div.sms_list table");
		$result["curent_page"] = intval($page);
		$result["total_pages"] = count($html->find("span.page_number"));
		if (!$result["total_pages"])
			$result["total_pages"] = 1;
		$result["history"] = array();
		foreach ($messages as $msg) {
			$_pushArray = array();
			// Contact
			$_pushArray["contact"] = trim($msg->find("p.message_list_recipient span.red", 0)->
				plaintext);
			// Number
			if (empty($_pushArray["contact"])) {
				$_pushArray["number"] = $msg->find("p.message_list_recipient span.red", 1)->
					plaintext;
			} else {
				$_pushArray["number"] = $msg->find("p.message_list_recipient span.gray", 0)->
					plaintext;
			}
			$_pushArray["number"] = preg_replace('/[^\d+]+/', '', $_pushArray["number"]);
			// Time
			$_pushArray["time"] = strtotime(trim(str_replace("\r\n", " ", $msg->find(".date_div",
				0)->plaintext)));
			// Time string
			$_pushArray["time_str"] = date("d.m.Y H:i:s", $_pushArray["time"]);
			// Message text
			$_pushArray["message"] = $msg->find("p.msg_text", 0)->plaintext;
			// Delivery status
			$_pushArray["delivered"] = !(substr_count($msg->find("p.message_list_recipient",
				0)->lastChild()->plaintext, "Not") > 0);

			$result["history"][] = $_pushArray;
		}
		return $result;
	}

	result = []	

	def get
		

### Handlers ###

class MainHandler(webapp2.RequestHandler):
	def get(self):
		obj = [14, {'as': [1,54,77]}]
		self.response.headers['Content-Type'] = 'application/json'
		self.response.write(json.dumps(obj))

# let the magic happen
app = webapp2.WSGIApplication([
	('/', MainHandler),
	('/send', MainHandler)
], debug=True)
