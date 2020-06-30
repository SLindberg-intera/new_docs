import psycopg2

class DB:
    def __init__(self, constring):
        self.dsn = constring

    def transact(self, commands):
        """ connect to the database

        execute each command in commands
        then grab the last result
        """
        conn = None
        res = None
        try:
            conn = psycopg2.connect(self.dsn)
            cur = conn.cursor()
            for cmd in commands:
                cur.execute(cmd)
            conn.commit()
            res = cur.fetchall()
            cur.close()
        except psycopg2.DatabaseError as e:
            raise e
        finally:
            if conn is not None:
                conn.close()
        return res
