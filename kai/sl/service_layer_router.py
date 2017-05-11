import os
import uuid
from flask import request, Response

import kai.res
from kai.sl.user import get_session_from_session_id, create_user, sign_in, sign_out
from kai.utility.utils import response_error, response_json, response_msg
from flask import request
from kai.parser.parser import Parser
import kai.res
import kai.sl.ask
import kai.sl.teach


parser = Parser()

# setup the service layer response handlers
def setup_sl_router(app, min_password_length):

    # curl -H "Content-Type: plain/text" -X POST --data @file.txt http://localhost:5000/api/parser
    @app.route('/sl/parse', methods=['GET', 'POST'])
    def sl_parse():
        text = request.args['text']
        if len(text) == 0:
            text = request.data.decode('utf-8')  # body text to ask
        if len(text.strip()) > 0:
            sentence_list = parser.parse_document(text)
            return response_json(sentence_list)
        else:
            return response_error('text missing / empty')

    @app.route('/sl/parse-to-png', methods=['GET'])
    def sl_parse_to_png():
        text = request.args['text']
        if len(text) == 0:
            text = request.data.decode('utf-8')  # body text to ask
        if len(text.strip()) > 0:
            return response_error("todo: implement properly")
        else:
            return response_error('text missing / empty')

    #########################################################################################
    ## teach/ask API

    # ask a question, expectes session_id as a query parameter
    @app.route('/ask', methods=['POST'])
    def ask():
        session_id_str = request.args['session']
        if len(session_id_str) > 0 and 'text' in request.form:
            text = request.form['text']  # body text to ask
            session = get_session_from_session_id(uuid.UUID("{" + session_id_str + "}"))
            if session is not None:
                result_list, err_str = kai.sl.ask.ask(session, text)
                if len(err_str) == 0:
                    return response_json({"result_list": result_list})
                else:
                    return response_error(err_str)
            else:
                return response_error("invalid session")
        else:
            return response_error("invalid request, session_id query parameter missing")

    # teach a new fact
    @app.route('/teach', methods=['POST'])
    def teach():
        session_id_str = request.args['session']
        if len(session_id_str) > 0 and 'text' in request.form:
            text = request.form['text']  # body text to teach
            session = get_session_from_session_id(uuid.UUID("{" + session_id_str + "}"))
            if session is not None:
                result_str = kai.sl.teach.teach(session, text)
                if result_str.startswith("ok, "):
                    return response_msg(result_str)
                else:
                    return response_error(result_str)
            else:
                return response_error("invalid session")
        else:
            return response_error("invalid request, session_id query parameter missing")

    # remove a previously taught fact
    @app.route('/remove/factoid/<id>', methods=['DELETE'])
    def remove_factoid(id: str):
        session_id_str = request.args['session_id']
        if len(session_id_str) > 0 and len(id) > 0:
            text = request.data.decode('utf-8')  # body text to ask
            session = get_session_from_session_id(uuid.UUID("{" + session_id_str + "}"))
            factoid_id = uuid.UUID("{" + id + "}")
            if session is not None:
                return response_msg(kai.sl.teach.delete_token_list(factoid_id, session.get_username()))
            else:
                return response_error("invalid session")
        else:
            return response_error("invalid request, session_id query parameter missing")

    #########################################################################################
    # user manager

    # create a new user account
    @app.route('/user/create', methods=['POST'])
    def user_create():
        json_dict = request.form
        if "first_name" in json_dict and "surname" in json_dict and "email" in json_dict and "password" in json_dict:
            user, err_str = create_user(json_dict['email'], json_dict['first_name'], json_dict['surname'],
                                        json_dict['password'], min_password_length)
            if len(err_str) == 0:
                # login the user and return the session id
                session, err_str = sign_in(json_dict['email'], json_dict['password'], min_password_length)
                if len(err_str) == 0:
                    return response_json(session)
                else:
                    return response_error(err_str)
            else:
                return response_error(err_str)
        else:
            return response_error("invalid paramters in /user/create, user object.")

    # sign in an existing user
    @app.route('/user/signin', methods=['POST'])
    def user_signin():
        json_dict = request.form
        if json_dict and "email" in json_dict and "password" in json_dict:
            session, err_str = sign_in(json_dict['email'], json_dict['password'], min_password_length)
            if len(err_str) == 0:
                return response_json(session)
            else:
                return response_error(err_str)
        else:
            return response_error("invalid paramters in /user/signin, user details.")

    # sign out an existing user
    @app.route('/user/signout', methods=['GET'])
    def user_signout():
        session_id_str = request.args['session']
        if len(session_id_str) > 0:
            sign_out(uuid.UUID("{" + session_id_str + "}"))
            return response_msg("logged out")
        else:
            return response_error("invalid paramters in /user/signout, session id missing.")


