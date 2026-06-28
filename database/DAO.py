from database.DB_connect import DBConnect
from model.classification import Classification
from model.gene import Gene
from model.interaction import Interaction


class DAO():

    @staticmethod
    def get_all_nodi(localization):
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """
            SELECT c.* , g.Essential AS Essential
            FROM classification c 
            JOIN genes g ON c.GeneID = g.GeneID
            WHERE c.Localization = %s 
            """
            cursor.execute(query, (localization,))

            for row in cursor:
                result.append(Classification(**row))

            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def get_all_localizations():
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """
                SELECT DISTINCT c.Localization 
                FROM classification c 
                ORDER BY c.Localization DESC 

                """
            cursor.execute(query)

            for row in cursor:
                result.append(row["Localization"])

            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def get_all_archi():
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """
            SELECT DISTINCT i.*
            FROM interactions i
            """
            cursor.execute(query)

            for row in cursor:
                result.append(Interaction(**row))

            cursor.close()
            cnx.close()
        return result

    @staticmethod
    def get_pesi_arco(id1, id2):
        cnx = DBConnect.get_connection()
        result = []
        if cnx is None:
            print("Connessione fallita")
        else:
            cursor = cnx.cursor(dictionary=True)
            query = """
            SELECT peso
            FROM
             (SELECT g.Chromosome AS peso
            FROM genes g 
            WHERE g.GeneID = %s) t
            UNION
            (SELECT  g.Chromosome AS peso
            FROM genes g 
             WHERE g.GeneID = %s)"""
            cursor.execute(query, (id1, id2))

            for row in cursor:
                result.append(row["peso"])

            cursor.close()
            cnx.close()
        return result
