import json
from kai.parser.model import Token, Sentence
from kai.cassandra.model import Session, ATResult


# simple json encoder
class JsonSystem(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Token):
            robj = {'text': obj.text, 'index': obj.index, 'tag': obj.tag, 'dep': obj.dep}
            if len(obj.ancestor_list) > 0:
                index = 0
                while index < len(obj.ancestor_list) and int(obj.ancestor_list[index]) == obj.index:
                    index += 1
                if index < len(obj.ancestor_list):
                    robj['parent'] = int(obj.ancestor_list[index])
            if obj.synid >= 0:  robj['synid]'] = obj.synid
            if len(obj.anaphora) > 0:  robj['anaphora'] = obj.anaphora
            if len(obj.semantic) > 0:  robj['semantic'] = obj.semantic
            return robj
        elif isinstance(obj, Sentence):
            return {'token_list': obj.token_list}
        elif isinstance(obj, Session):
            return {'first_name': obj.first_name, 'surname': obj.surname, 'email': obj.email,
                    'session': str(obj.session)}
        elif isinstance(obj, ATResult):
            return {'text': obj.text, 'timestamp': obj.timestamp, 'topic': obj.topic, 'sentence_id': str(obj.sentence_id)}
        return json.JSONEncoder.default(self, obj)
