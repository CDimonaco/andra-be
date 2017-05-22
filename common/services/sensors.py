from common.settings import persistenceSettings
from common.models.sensor import Sensor
from common.exceptions.sensors import SensorAddError,SensorNotFoundError
from common.models.value import Value
from bson.objectid import ObjectId
from common.exceptions.values import ValueAddError,ValueNotFoundError

class SensorService:
    def __init__(self,database):
        self.collection = database[persistenceSettings["sensorsCollection"]]


    def getAll(self):
        """
        Metodo di test, ritorna tutti i sensori e li stampa a schermo.
        :return: 
        """
        sensorcursor = self.collection.find()
        sensorlist = [user for user in sensorcursor]
        testsensors = {"count": sensorcursor.count(), "users": sensorlist}
        print(testsensors)

    def add(self,sensor):
        sensortoadd = Sensor.from_model(sensor)
        insertionResult = self.collection.insert_one(sensortoadd)
        if not insertionResult.acknowledged:
            raise SensorAddError
        print("Insertion completed", insertionResult.inserted_id)
        return insertionResult.inserted_id

    def delete(self,filter):
        """
        Questo metodo elimina dei sensori dalla collezione secondo i filtri in input.
        :param filter: SensorFilter
        :return: True
        """
        deleteResult = self.collection.delete_many(filter.getConditions())
        if deleteResult.deleted_count < 1:
            # TODO:ADD LOG TO FLASK
            raise SensorNotFoundError
        return True

    def find(self,filter,offset=0):
        """
        Trova una lista di sensori secondo i filtri inseriti.
        :param filter: SensorFilter
        :param offset: Offset per la paginazione
        :return: Una lista di sensori, more che indica che ci sono ancora elementi da paginare
        """
        sensorquery = self.collection.find(filter.getConditions(),skip=offset,limit=10)
        totalsensors = sensorquery.count()
        sensorslist = [Sensor.to_model(user) for user in sensorquery]
        more = offset >= totalsensors
        return sensorslist,not more

    def setvalue(self,sensorid,value):
        """
        Questo metodo aggiunge un valore rilevato ad un sensore, l'ordine dei valori è per timestamp,
        aggiungendo un nuovo valore all'array dobbiamo anche usare l'operatore $sort per mantenere l'ordine
        :param sensorid: Id del sensore a cui aggiungere una rilevazione
        :return: Id del sensore a cui è stata aggiunta una rilevazione
        """
        valuetoadd = Value.from_model(value)
        insertionResult = self.collection.update_one({"_id": ObjectId(sensorid)}, {"$push": {"values": {"$each":[valuetoadd],"$sort":{"timestamp":-1}}}})
        #insertionResult = self.collection.update_one({"_id": ObjectId(sensorid)}, {"$push": {"values":valuetoadd}})
        if not insertionResult.acknowledged or insertionResult.modified_count < 0:
            raise ValueAddError
        print("Insertion completed to sensor", sensorid)
        return sensorid

    def getvalues(self,filter):
        """
        Trova dei valori rilevati secondo il filtro inserito.
        :param filter: ValueFilter
        :return: Lista di valori rilevati
        """
        valuesquery = self.collection.find(projection={"_id":False,"name":False,"apikey":False,"project":False},filter=filter.getConditions())
        valueslist = [Value.to_model(value["values"][0]) for value in valuesquery]
        return valueslist

    def resetvalues(self,sensorid):
        """
        Resetta un sensore, ovvero elimina tutte le rilevazioni.
        :param sensorid: Id del sensore da resettare
        :return: True
        """
        insertionResult = self.collection.update_one(filter={"_id" : ObjectId(sensorid)},update={"$unset" : {"values" : ""}})
        if not insertionResult.acknowledged or insertionResult.modified_count < 0:
            raise SensorNotFoundError
        print("RESET ON",sensorid)
