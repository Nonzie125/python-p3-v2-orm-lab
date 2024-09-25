from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review  instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        if self.id is None:
        # Insert a new review into the database
            sql = '''
            INSERT INTO reviews (year, summary, employee_id)
            VALUES (?, ?, ?)
            '''
            CURSOR.execute(sql, (self.year, self.summary, self.employee_id))
            CONN.commit()
            # Get the last inserted ID and assign it to the instance
            self.id = CURSOR.lastrowid
            # Save the object in the dictionary with the primary key as the key
            Review.all[self.id] = self
        else:
            self.update()  # If the review already exists, update it

    @classmethod
    def create(cls, year, summary, employee_id):
        review = cls(year, summary, employee_id)
        review.save()  # Persist the new review
        return review  # Return the new review instance

   

    @classmethod
    def instance_from_db(cls, row):
        review_id = row[0]
        if review_id in cls.all:
            return cls.all[review_id]  # Return cached instance if exists
        # Create a new instance from the database row
        review = cls(row[1], row[2], row[3], id=review_id)
        cls.all[review_id] = review  # Cache the new instance
        return review


    @classmethod
    def find_by_id(cls, id):
        sql = '''
        SELECT * FROM reviews WHERE id = ?
        '''
        CURSOR.execute(sql, (id,))
        row = CURSOR.fetchone()
        if row:
            return cls.instance_from_db(row)  # Return instance from database row
        return None  # Return None if no row is found
    

    def update(self):
        sql = '''
        UPDATE reviews SET year = ?, summary = ?, employee_id = ? WHERE id = ?
        '''
        CURSOR.execute(sql, (self.year, self.summary, self.employee_id, self.id))
        CONN.commit()

    def delete(self):
        sql = '''
        DELETE FROM reviews WHERE id = ?
        '''
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        # Remove from the dictionary
        if self.id in Review.all:
            del Review.all[self.id]
        # Set the id attribute to None
        self.id = None

    @classmethod
    def get_all(cls):
        sql = '''
        SELECT * FROM reviews
        '''
        CURSOR.execute(sql)
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]