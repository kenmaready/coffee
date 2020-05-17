import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO (DONE) implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        return jsonify({
            "success": True,
            "drinks": drinks
            })
    except:
      abort(500)

'''
@TODO (DONE) implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
  try:
    drinks = [drink.long() for drink in Drink.query.all()]
    return jsonify({
        "success": True,
        "drinks": drinks
        })
  except:
    abort(500)

'''
@TODO (DONE) implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):

    body = request.json
    title = body['title']
    recipe = body['recipe']

    if not title or not recipe:
      abort(400)
    
    # check to see if rink with title already exists, if so abort(409)
    drink_exists = Drink.query.filter_by(title=title).scalar() is not None
    if drink_exists:
      abort(409)
  
    try:
        drink = Drink(title=title, recipe=json.dumps(recipe))
        drink.insert()
        return jsonify({ 
          "success": True,
          "drinks": [drink.long()]
          })
    except:
      abort(500)

'''
@TODO (DONE) implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
  
    body = request.json
    drink = Drink.query.get(drink_id)

    if not drink:
      abort(404)

    if 'title' in body or 'recipe' in body:
        try:
            if 'title' in body:
              drink.title = body['title']
            
            if 'recipe' in body:
              drink.recipe = json.dumps(body['recipe'])

            drink.update()
            return jsonify({
              "success": True,
              "drinks": [drink.long()]
            })
        except:
          abort(500)

    else:
      abort(400)

'''
@TODO (DONE) implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):

    drink = Drink.query.get(drink_id)
    if not drink:
      abort(404)
    
    try:
      drink.delete()
      return jsonify({
        "success": True,
        "delete": drink_id
      })
    except:
      abort(500)

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO (DONE) implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO (DONE) implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "You may have to come to terms with the very real possibility that the resource you are seeking does not exist."
    }), 404



@app.errorhandler(409)
def conflict(error):
    return jsonify({
      "success": False,
      "error": 409,
      "message": "I feel conflicted. There is already a drink by that name in my database, and so I must regretfully decline to honor your request."
    }), 409



@app.errorhandler(500)
def internal_server(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "I have to tell you something. I've screwed up somehow. I was unable to process your request.  It's not you ... it's me."
    }), 500

'''
@TODO (DONE) implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def not_authorized(AuthError):
  return jsonify({
    "success": False,
    "error": AuthError.status_code,
    "message": AuthError.error['description']

  }), AuthError.status_code