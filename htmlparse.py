import lxml
import lxml.html

def htmldata(html_string, selector, index = 0, method = 'text_content', default = ''):
	# html = lxml.html.fromstring(html_string)
	html = html_string # TODO check if is string
	elements = html.cssselect(selector)
	if elements.__len__() > index:
		e = elements[index]
		if method == 'value':
			return e.value
		else:
			return e.text_content()
	else:
		return default