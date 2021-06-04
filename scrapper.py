from newspaper import Article

url = "https://hbr.org/2021/03/cyberattacks-are-inevitable-is-your-company-prepared?utm_source=feedburner&utm_medium=feed&utm_campaign=Feed%3A+harvardbusiness+%28HBR.org%29"
test_article = Article(url=url, language='en', keep_article_html=True)
test_article.download()
test_article.parse()
print(test_article.title)
print(test_article.authors)
print(test_article.text)
# test_article.nlp()
# print(test_article.summary)