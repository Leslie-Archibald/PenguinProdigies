from pymongo import MongoClient

#The "likes" table is going to just consist of {username,postID}.
#If an element exists in the table, then that means the user with that username has liked the post
#with that postID

def numLikes(db_likes,body):
    #returns the total number of likes a certain post has recieved

    #These are not real functions, these are just placeholders
    postID = body["id"]
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    numLikes = 0
    for like in db_likes.find({"postID":postID}):
        numLikes += 1

    return(numLikes)

def likes(db_likes, body):
    #db_likes is the database structure, specifically the table to be used for likes
    #body is a dict containing the post information

    #These are not real functions, these are just placeholders
    postID = body["id"]
    username = body["username"]
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    if(db_likes.find_one({"username":username, "postID":postID}) == None):
        #No likes element exists for this user-post pair
        print("Like added")
        db_likes.insert({"username":username,
                        "postID":postID})
        
    else: #A user-post pair does exist

        #this is for testing. coment this out later!
        print(db_likes.find_one({"username":username,
                                "postID":postID}) )

        #removes the like
        db_likes.delete({"username":username,
                        "postID":postID})
        
        #will probably need to force some kind of update on the client's POV to show that a post has been "unliked"
        totalLikes = numLikes(db_likes,body)

    return totalLikes

