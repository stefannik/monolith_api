from db_queries import db_get_articles, db_article_update_mono, db_article_update_portada, db_article_update_sense
from ai import score
from tqdm import tqdm


# for art in tqdm(db_get_articles()):
#     text = art['title'] + ' [SEP] ' + art['summary'].strip()
#     sense = score(text, 'sense')
#     portada = score(text, 'portada')
#     db_article_update_sense(art['id'], float(sense))
#     db_article_update_portada(art['id'], float(portada))


for art in tqdm(db_get_articles()):
    sense = art['sense']
    portada = art['portada']
    mono = sense + portada

    db_article_update_mono(art['id'], float(mono))
