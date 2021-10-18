
def generateUpdateStatement(document, changes):
    """
    This function takes a document that contains a subdocument array called posts
    Each item in the posts array also contains a subdocument array called mentions
    This function will return the limited needed update commands to satisfy the desired changes

    For the sake of time I am assuming that the document is in the form of a python dict object defined like
    doucment = {
        '_id':1,
        'name': "Johnny Content Creator",
        'posts':[
            {
                '_id':2',
                'value':"one",
                'mentions': [
                    {
                        '_id':5,
                        'text':"apple"
                    }
                ]
            }
        ]
    }

    :param document: document for content creator posts
    :param changes: document containing a set of changes to the document
    """
    if 'posts' not in changes:
        return {}
    posts = changes['posts']
    changes = {'$update': [], '$add': [], '$remove': []}
    original_post_ids = [x['_id'] for x in document['posts']]
    for post in posts:
        if '_id' in post:
            index = __get_index_or_neg1__(original_post_ids, post['_id'])
            if index > -1:
                original_post = document['posts'][index]
                if '_delete' in post:
                    changes['$remove'].append({"posts.%s" % index: True})
                else:
                    if 'value' in post and post['value'] != original_post['value']:
                        changes['$update'].append({'posts.%s.value' % index: post['value']})
                    if 'mentions' in post:
                        mention_ids = [x['_id'] for x in original_post['mentions']]
                        for mention in post['mentions']:
                            if '_id' in mention:
                                mention_index = __get_index_or_neg1__(mention_ids, mention['_id'])
                                if mention_index > -1:
                                    original_mention = original_post['mentions'][mention_index]
                                    if '_delete' in mention:
                                        changes['$remove'].append({"posts.%s.mentions.%s" % (index, mention_index): True})
                                    elif 'text' in mention and mention['text'] != original_mention['text']:
                                        changes['$update'].append(
                                            {'posts.%s.mentions.%s.text' % (index, mention_index): mention['text']}
                                        )
                            else:
                                key = "posts.%s.mentions" % index
                                key_found = False
                                for change in changes['$add']:
                                    if key in change:
                                        change[key].append(mention)
                                        key_found = True
                                        break
                                if not key_found:
                                    changes['$add'].append({key: [mention]})
        else:
            if len(changes['$add']) == 0 or "posts" not in changes['$add'][0]:
                changes['$add'].insert(0, {'posts': [post]})
            else:
                changes['$add'][0]['posts'].append(post)  # posts always inserted at index 0
    return __clean_output__(changes)


def __get_index_or_neg1__(items, element_id):
    """
    finds the index of the element or returns -1 if not found
    :param items: a list of _id values
    :param element_id: the desired _id value
    :return: index of _id value if found otherwise -1
    """
    try:
        return items.index(element_id)
    except ValueError:
        return -1


def __clean_output__(changes):
    """
    removes an update key if it is empty or changes it from a list to a dict if the list is of length one
    :param changes: document changes
    :return: document in correct format
    """
    keys = list(changes.keys())
    for x in keys:
        change_length = len(changes[x])
        if change_length == 0:
            del changes[x]
        if change_length == 1:
            changes[x] = changes[x][0]
    return changes
