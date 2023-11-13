import flask
import util.constants as const



def getAucInfo(id, conn):
    db = conn[const.DB_AUC]
    aucEntry = db.find_one({"auction id": id})

    if aucEntry == None:
        return {}
    else:
        return aucEntry
    #endIf
#endDef

     